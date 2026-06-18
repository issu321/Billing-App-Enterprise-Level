"""Authentication and User Management Service"""
from datetime import datetime, timedelta
from models import db
from models.user import User, Role, Permission, UserRole
from models.audit_log import AuditLog
from utils.validators import validate_email, validate_username, validate_password, validate_required
from utils.helpers import generate_random_password


class AuthService:
    """Service for authentication and user management"""
    
    @staticmethod
    def authenticate_user(username_or_email, password):
        """Authenticate user with username/email and password"""
        user = User.query.filter(
            db.or_(
                User.username == username_or_email,
                User.email == username_or_email
            )
        ).first()
        
        if not user:
            return None, "Invalid username or password"
        
        if not user.is_active:
            return None, "Account is deactivated"
        
        if user.is_locked():
            return None, f"Account is locked until {user.locked_until}"
        
        if not user.check_password(password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            db.session.commit()
            return None, "Invalid username or password"
        
        # Successful login
        user.last_login = datetime.utcnow()
        user.login_count += 1
        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()
        
        return user, "Login successful"
    
    @staticmethod
    def create_user(data, created_by=None):
        """Create a new user"""
        # Validate required fields
        is_valid, errors = validate_required(data.get('username'), "Username")
        if not is_valid:
            return None, errors
        
        is_valid, errors = validate_required(data.get('email'), "Email")
        if not is_valid:
            return None, errors
        
        is_valid, errors = validate_required(data.get('password'), "Password")
        if not is_valid:
            return None, errors
        
        # Validate format
        is_valid, message = validate_username(data['username'])
        if not is_valid:
            return None, message
        
        is_valid, message = validate_email(data['email'])
        if not is_valid:
            return None, message
        
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return None, message
        
        # Check uniqueness
        if User.query.filter_by(username=data['username']).first():
            return None, "Username already exists"
        
        if User.query.filter_by(email=data['email']).first():
            return None, "Email already exists"
        
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            phone=data.get('phone', ''),
            is_active=data.get('is_active', True),
            language=data.get('language', 'en'),
            timezone=data.get('timezone', 'UTC'),
            created_by=created_by
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Assign roles if provided
        if 'role_ids' in data and data['role_ids']:
            for role_id in data['role_ids']:
                role = Role.query.get(role_id)
                if role:
                    user_role = UserRole(user_id=user.id, role_id=role.id, assigned_by=created_by)
                    db.session.add(user_role)
            db.session.commit()
        
        return user, "User created successfully"
    
    @staticmethod
    def update_user(user_id, data, updated_by=None):
        """Update user details"""
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"
        
        # Update fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'email' in data and data['email'] != user.email:
            is_valid, message = validate_email(data['email'])
            if not is_valid:
                return None, message
            if User.query.filter_by(email=data['email']).first():
                return None, "Email already exists"
            user.email = data['email']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'language' in data:
            user.language = data['language']
        if 'timezone' in data:
            user.timezone = data['timezone']
        
        # Update password if provided
        if 'password' in data and data['password']:
            is_valid, message = validate_password(data['password'])
            if not is_valid:
                return None, message
            user.set_password(data['password'])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Update roles if provided
        if 'role_ids' in data:
            # Remove existing roles
            UserRole.query.filter_by(user_id=user.id).delete()
            # Add new roles
            for role_id in data['role_ids']:
                role = Role.query.get(role_id)
                if role:
                    user_role = UserRole(user_id=user.id, role_id=role.id, assigned_by=updated_by)
                    db.session.add(user_role)
            db.session.commit()
        
        return user, "User updated successfully"
    
    @staticmethod
    def delete_user(user_id):
        """Delete a user"""
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        db.session.delete(user)
        db.session.commit()
        return True, "User deleted successfully"
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_all_users(page=1, per_page=20, search=None, role_id=None, is_active=None):
        """Get all users with filters"""
        query = User.query
        
        if search:
            query = query.filter(
                db.or_(
                    User.username.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    User.first_name.ilike(f'%{search}%'),
                    User.last_name.ilike(f'%{search}%')
                )
            )
        
        if role_id:
            query = query.join(UserRole).filter(UserRole.role_id == role_id)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_all_roles():
        """Get all roles"""
        return Role.query.all()
    
    @staticmethod
    def get_all_permissions():
        """Get all permissions"""
        return Permission.query.all()
    
    @staticmethod
    def create_role(data):
        """Create a new role"""
        if Role.query.filter_by(name=data['name']).first():
            return None, "Role name already exists"
        
        role = Role(
            name=data['name'],
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        
        # Assign permissions
        if 'permission_ids' in data:
            for perm_id in data['permission_ids']:
                perm = Permission.query.get(perm_id)
                if perm:
                    role.permissions.append(perm)
        
        db.session.add(role)
        db.session.commit()
        
        return role, "Role created successfully"
    
    @staticmethod
    def update_role(role_id, data):
        """Update a role"""
        role = Role.query.get(role_id)
        if not role:
            return None, "Role not found"
        
        if 'name' in data:
            existing = Role.query.filter_by(name=data['name']).first()
            if existing and existing.id != role_id:
                return None, "Role name already exists"
            role.name = data['name']
        
        if 'description' in data:
            role.description = data['description']
        if 'is_active' in data:
            role.is_active = data['is_active']
        
        # Update permissions
        if 'permission_ids' in data:
            role.permissions = []
            for perm_id in data['permission_ids']:
                perm = Permission.query.get(perm_id)
                if perm:
                    role.permissions.append(perm)
        
        db.session.commit()
        return role, "Role updated successfully"
    
    @staticmethod
    def delete_role(role_id):
        """Delete a role"""
        role = Role.query.get(role_id)
        if not role:
            return False, "Role not found"
        
        if role.is_super_admin:
            return False, "Cannot delete super admin role"
        
        db.session.delete(role)
        db.session.commit()
        return True, "Role deleted successfully"
