"""Database initialization and model registry"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()

# Import all models to ensure they're registered with SQLAlchemy
from .user import User, Role, Permission, UserRole
from .product import Product, Category, ProductVariant, ProductImage, UnitOfMeasure
from .inventory import Inventory, InventoryTransaction, Warehouse, StockAdjustment
from .customer import Customer, CustomerGroup, CustomerLedger
from .supplier import Supplier, SupplierLedger
from .sale import Sale, SaleItem, SaleReturn, SaleReturnItem, Invoice, InvoiceItem
from .purchase import Purchase, PurchaseItem, PurchaseReturn, PurchaseReturnItem
from .payment import Payment, PaymentMethod, Transaction, Account, Currency
from .audit_log import AuditLog
from .settings import BusinessSettings, TaxSetting, NotificationSetting, BackupSetting

__all__ = [
    'db', 'login_manager',
    'User', 'Role', 'Permission', 'UserRole',
    'Product', 'Category', 'ProductVariant', 'ProductImage', 'UnitOfMeasure',
    'Inventory', 'InventoryTransaction', 'Warehouse', 'StockAdjustment',
    'Customer', 'CustomerGroup', 'CustomerLedger',
    'Supplier', 'SupplierLedger',
    'Sale', 'SaleItem', 'SaleReturn', 'SaleReturnItem', 'Invoice', 'InvoiceItem',
    'Purchase', 'PurchaseItem', 'PurchaseReturn', 'PurchaseReturnItem',
    'Payment', 'PaymentMethod', 'Transaction', 'Account', 'Currency',
    'AuditLog',
    'BusinessSettings', 'TaxSetting', 'NotificationSetting', 'BackupSetting'
]


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    from .user import User
    return User.query.get(int(user_id))


def init_app(app):
    """Initialize the database and login manager with the Flask app"""
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    with app.app_context():
        db.create_all()
        _create_default_data()


def _create_default_data():
    """Create default data if not exists"""
    from .user import Role, Permission, User
    from .settings import BusinessSettings, TaxSetting
    
    # Create default roles
    if not Role.query.filter_by(name='Super Admin').first():
        super_admin = Role(name='Super Admin', description='Full system access', is_super_admin=True)
        db.session.add(super_admin)
    
    if not Role.query.filter_by(name='Admin').first():
        admin = Role(name='Admin', description='Administrator with most permissions')
        db.session.add(admin)
    
    if not Role.query.filter_by(name='Manager').first():
        manager = Role(name='Manager', description='Manager with limited admin access')
        db.session.add(manager)
    
    if not Role.query.filter_by(name='Cashier').first():
        cashier = Role(name='Cashier', description='POS and billing operations only')
        db.session.add(cashier)
    
    if not Role.query.filter_by(name='Viewer').first():
        viewer = Role(name='Viewer', description='Read-only access')
        db.session.add(viewer)
    
    # Create default permissions
    default_permissions = [
        ('dashboard_view', 'View Dashboard'),
        ('products_manage', 'Manage Products'),
        ('categories_manage', 'Manage Categories'),
        ('inventory_manage', 'Manage Inventory'),
        ('customers_manage', 'Manage Customers'),
        ('suppliers_manage', 'Manage Suppliers'),
        ('pos_access', 'Access POS'),
        ('billing_manage', 'Manage Billing'),
        ('reports_view', 'View Reports'),
        ('analytics_view', 'View Analytics'),
        ('barcode_manage', 'Manage Barcodes'),
        ('payments_manage', 'Manage Payments'),
        ('backup_manage', 'Manage Backups'),
        ('settings_manage', 'Manage Settings'),
        ('users_manage', 'Manage Users'),
        ('roles_manage', 'Manage Roles'),
        ('audit_logs_view', 'View Audit Logs'),
    ]
    
    for code, name in default_permissions:
        if not Permission.query.filter_by(code=code).first():
            perm = Permission(code=code, name=name)
            db.session.add(perm)
    
    db.session.commit()
    
    # Create default tax settings
    if not TaxSetting.query.first():
        default_tax = TaxSetting(
            name='GST',
            rate=18.0,
            is_default=True,
            is_active=True
        )
        db.session.add(default_tax)
    
    db.session.commit()
