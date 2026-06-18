"""Custom decorators for authentication and authorization"""
from functools import wraps
from flask import redirect, url_for, flash, request, abort
from flask_login import current_user
from models.audit_log import AuditLog


def login_required(f):
    """Require user to be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return {'success': False, 'message': 'Authentication required'}, 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission_code):
    """Require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return {'success': False, 'message': 'Authentication required'}, 401
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.has_permission(permission_code) and not current_user.is_super_admin():
                if request.is_json:
                    return {'success': False, 'message': 'Permission denied'}, 403
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def super_admin_required(f):
    """Require super admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return {'success': False, 'message': 'Authentication required'}, 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_super_admin():
            if request.is_json:
                return {'success': False, 'message': 'Super admin access required'}, 403
            flash('Super admin access required.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def audit_log_action(action, entity_type, module=None):
    """Log action to audit log"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                
                # Try to get entity info from result or kwargs
                entity_id = kwargs.get('id') or kwargs.get('entity_id')
                entity_name = kwargs.get('name') or kwargs.get('entity_name')
                
                AuditLog.log_action(
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_name=entity_name,
                    description=f"{action} {entity_type}" + (f" - {entity_name}" if entity_name else ""),
                    user_id=current_user.id if current_user.is_authenticated else None,
                    user_name=current_user.get_full_name() if current_user.is_authenticated else None,
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string if request.user_agent else None,
                    module=module or entity_type
                )
                return result
            except Exception as e:
                AuditLog.log_action(
                    action=action,
                    entity_type=entity_type,
                    description=f"{action} {entity_type} failed",
                    user_id=current_user.id if current_user.is_authenticated else None,
                    ip_address=request.remote_addr,
                    status='failed',
                    error_message=str(e),
                    module=module or entity_type
                )
                raise
        return decorated_function
    return decorator


def api_response(f):
    """Format function return as API response"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            if isinstance(result, tuple):
                return result
            return {'success': True, 'data': result}, 200
        except Exception as e:
            return {'success': False, 'message': str(e)}, 500
    return decorated_function
