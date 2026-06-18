"""Audit Log and Activity Tracking Models"""
from . import db
from datetime import datetime


class AuditLog(db.Model):
    """Comprehensive audit log for all system activities"""
    __tablename__ = 'audit_logs'
    
    ACTION_TYPES = [
        'create', 'update', 'delete', 'view', 'login', 'logout',
        'export', 'import', 'print', 'backup', 'restore', 'settings_change',
        'approve', 'reject', 'cancel', 'refund', 'transfer', 'other'
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Action details
    action = db.Column(db.String(20), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # product, sale, user, etc.
    entity_id = db.Column(db.Integer)
    entity_name = db.Column(db.String(200))
    
    # Description
    description = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text)  # JSON string of changed fields
    
    # User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_name = db.Column(db.String(100))
    
    # IP and device info
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    device_type = db.Column(db.String(20))  # desktop, mobile, tablet
    
    # Module/Feature
    module = db.Column(db.String(50))  # products, sales, inventory, etc.
    
    # Severity
    severity = db.Column(db.String(10), default='info')  # info, warning, error, critical
    
    # Status
    status = db.Column(db.String(20), default='success')  # success, failed
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'entity_name': self.entity_name,
            'description': self.description,
            'details': self.details,
            'user_id': self.user_id,
            'user_name': self.user_name or (self.actor.get_full_name() if self.actor else 'System'),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'device_type': self.device_type,
            'module': self.module,
            'severity': self.severity,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def log_action(action, entity_type, entity_id=None, entity_name=None,
                   description=None, details=None, user_id=None, user_name=None,
                   ip_address=None, user_agent=None, module=None, severity='info',
                   status='success', error_message=None):
        """Helper method to create audit log entry"""
        try:
            log = AuditLog(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                entity_name=entity_name,
                description=description or f"{action} {entity_type}",
                details=details,
                user_id=user_id,
                user_name=user_name,
                ip_address=ip_address,
                user_agent=user_agent,
                module=module,
                severity=severity,
                status=status,
                error_message=error_message
            )
            db.session.add(log)
            db.session.commit()
            return log
        except Exception:
            db.session.rollback()
            return None
