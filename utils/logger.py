"""Logging configuration"""
import logging
import os
from logging.handlers import RotatingFileHandler
from flask import has_request_context, request


class RequestFormatter(logging.Formatter):
    """Custom formatter that adds request context"""
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
        return super().format(record)


def setup_logger(app):
    """Setup application logging"""
    log_dir = app.config.get('LOG_DIR', os.path.join(app.root_path, 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    
    # Create formatters
    formatter = RequestFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(method)s %(url)s - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handlers
    # Application log
    app_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    app_handler.setFormatter(formatter)
    app_handler.setLevel(logging.INFO)
    
    # Error log
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10485760,
        backupCount=10
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Audit log
    audit_handler = RotatingFileHandler(
        os.path.join(log_dir, 'audit.log'),
        maxBytes=10485760,
        backupCount=20
    )
    audit_handler.setFormatter(simple_formatter)
    audit_handler.setLevel(logging.INFO)
    
    # Access log
    access_handler = RotatingFileHandler(
        os.path.join(log_dir, 'access.log'),
        maxBytes=10485760,
        backupCount=10
    )
    access_handler.setFormatter(formatter)
    access_handler.setLevel(logging.INFO)
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Get loggers
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.INFO)
    app_logger.addHandler(app_handler)
    app_logger.addHandler(error_handler)
    app_logger.addHandler(console_handler)
    
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.addHandler(audit_handler)
    
    access_logger = logging.getLogger('access')
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(access_handler)
    
    # Flask app logger
    app.logger.addHandler(app_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    return {
        'app': app_logger,
        'audit': audit_logger,
        'access': access_logger
    }


# Global logger instances
app_logger = logging.getLogger('app')
audit_logger = logging.getLogger('audit')
access_logger = logging.getLogger('access')


def log_app_event(message, level='info', extra=None):
    """Log application event"""
    if level == 'debug':
        app_logger.debug(message, extra=extra)
    elif level == 'warning':
        app_logger.warning(message, extra=extra)
    elif level == 'error':
        app_logger.error(message, extra=extra)
    elif level == 'critical':
        app_logger.critical(message, extra=extra)
    else:
        app_logger.info(message, extra=extra)


def log_audit_event(message, user=None, entity_type=None, entity_id=None, action=None):
    """Log audit event"""
    extra = {
        'user': user,
        'entity_type': entity_type,
        'entity_id': entity_id,
        'action': action
    }
    audit_logger.info(message, extra=extra)


def log_access(message, level='info'):
    """Log access event"""
    if level == 'error':
        access_logger.error(message)
    elif level == 'warning':
        access_logger.warning(message)
    else:
        access_logger.info(message)
