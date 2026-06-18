"""Business Settings and Configuration Models"""
from . import db
from datetime import datetime


class BusinessSettings(db.Model):
    """Main business/store configuration"""
    __tablename__ = 'business_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Business info
    business_name = db.Column(db.String(200))
    store_name = db.Column(db.String(200))
    tagline = db.Column(db.String(255))
    
    # Owner
    owner_name = db.Column(db.String(150))
    owner_email = db.Column(db.String(120))
    owner_phone = db.Column(db.String(20))
    
    # Address
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    
    # Tax
    gst_number = db.Column(db.String(20))
    vat_number = db.Column(db.String(20))
    tin_number = db.Column(db.String(20))
    pan_number = db.Column(db.String(20))
    
    # Contact
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(255))
    
    # Logo and branding
    logo = db.Column(db.String(255))
    favicon = db.Column(db.String(255))
    receipt_header = db.Column(db.Text)
    receipt_footer = db.Column(db.Text)
    
    # Regional
    currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'))
    timezone = db.Column(db.String(50), default='UTC')
    date_format = db.Column(db.String(20), default='%Y-%m-%d')
    time_format = db.Column(db.String(10), default='24')
    language = db.Column(db.String(10), default='en')
    
    # Invoice settings
    invoice_prefix = db.Column(db.String(20), default='INV')
    invoice_suffix = db.Column(db.String(20))
    invoice_starting_number = db.Column(db.Integer, default=1)
    invoice_terms = db.Column(db.Text)
    invoice_footer = db.Column(db.Text)
    show_logo_on_invoice = db.Column(db.Boolean, default=True)
    auto_email_invoice = db.Column(db.Boolean, default=False)
    
    # POS settings
    default_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))
    enable_pos = db.Column(db.Boolean, default=True)
    pos_receipt_printer = db.Column(db.String(100))
    auto_print_receipt = db.Column(db.Boolean, default=False)
    
    # Features
    enable_inventory_tracking = db.Column(db.Boolean, default=True)
    enable_negative_stock = db.Column(db.Boolean, default=False)
    enable_multi_warehouse = db.Column(db.Boolean, default=False)
    enable_barcode = db.Column(db.Boolean, default=True)
    enable_qr_payments = db.Column(db.Boolean, default=True)
    enable_customer_loyalty = db.Column(db.Boolean, default=False)
    enable_serial_tracking = db.Column(db.Boolean, default=False)
    enable_batch_tracking = db.Column(db.Boolean, default=False)
    enable_expiry_tracking = db.Column(db.Boolean, default=False)
    
    # Tax settings
    default_tax_rate = db.Column(db.Numeric(5, 2), default=0)
    tax_inclusive_pricing = db.Column(db.Boolean, default=True)
    enable_multiple_tax = db.Column(db.Boolean, default=True)
    
    # Decimal places
    quantity_decimal_places = db.Column(db.Integer, default=2)
    price_decimal_places = db.Column(db.Integer, default=2)
    amount_decimal_places = db.Column(db.Integer, default=2)
    
    # Theme
    theme_primary_color = db.Column(db.String(7), default='#4F46E5')
    theme_secondary_color = db.Column(db.String(7), default='#10B981')
    theme_mode = db.Column(db.String(10), default='light')  # light, dark, auto
    
    # First launch
    setup_completed = db.Column(db.Boolean, default=False)
    setup_completed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    currency = db.relationship('Currency', foreign_keys=[currency_id], backref='business_settings')
    default_warehouse = db.relationship('Warehouse', backref='business_settings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'business_name': self.business_name,
            'store_name': self.store_name,
            'tagline': self.tagline,
            'owner_name': self.owner_name,
            'owner_email': self.owner_email,
            'owner_phone': self.owner_phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'gst_number': self.gst_number,
            'vat_number': self.vat_number,
            'tin_number': self.tin_number,
            'pan_number': self.pan_number,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'logo': self.logo,
            'favicon': self.favicon,
            'receipt_header': self.receipt_header,
            'receipt_footer': self.receipt_footer,
            'currency_id': self.currency_id,
            'currency_code': self.currency.code if self.currency else 'INR',
            'timezone': self.timezone,
            'date_format': self.date_format,
            'time_format': self.time_format,
            'language': self.language,
            'invoice_prefix': self.invoice_prefix,
            'invoice_suffix': self.invoice_suffix,
            'invoice_starting_number': self.invoice_starting_number,
            'invoice_terms': self.invoice_terms,
            'invoice_footer': self.invoice_footer,
            'show_logo_on_invoice': self.show_logo_on_invoice,
            'auto_email_invoice': self.auto_email_invoice,
            'default_warehouse_id': self.default_warehouse_id,
            'enable_pos': self.enable_pos,
            'enable_inventory_tracking': self.enable_inventory_tracking,
            'enable_negative_stock': self.enable_negative_stock,
            'enable_multi_warehouse': self.enable_multi_warehouse,
            'enable_barcode': self.enable_barcode,
            'enable_qr_payments': self.enable_qr_payments,
            'enable_customer_loyalty': self.enable_customer_loyalty,
            'enable_serial_tracking': self.enable_serial_tracking,
            'enable_batch_tracking': self.enable_batch_tracking,
            'enable_expiry_tracking': self.enable_expiry_tracking,
            'default_tax_rate': float(self.default_tax_rate) if self.default_tax_rate else 0,
            'tax_inclusive_pricing': self.tax_inclusive_pricing,
            'enable_multiple_tax': self.enable_multiple_tax,
            'quantity_decimal_places': self.quantity_decimal_places,
            'price_decimal_places': self.price_decimal_places,
            'amount_decimal_places': self.amount_decimal_places,
            'theme_primary_color': self.theme_primary_color,
            'theme_secondary_color': self.theme_secondary_color,
            'theme_mode': self.theme_mode,
            'setup_completed': self.setup_completed,
            'setup_completed_at': self.setup_completed_at.isoformat() if self.setup_completed_at else None
        }


class TaxSetting(db.Model):
    """Tax/GST rate configuration"""
    __tablename__ = 'tax_settings'
    
    TAX_TYPES = ['gst', 'vat', 'sales_tax', 'service_tax', 'custom', 'none']
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tax_type = db.Column(db.String(20), default='gst')
    rate = db.Column(db.Numeric(5, 2), default=0)
    cgst_rate = db.Column(db.Numeric(5, 2), default=0)
    sgst_rate = db.Column(db.Numeric(5, 2), default=0)
    igst_rate = db.Column(db.Numeric(5, 2), default=0)
    cess_rate = db.Column(db.Numeric(5, 2), default=0)
    hsn_code_prefix = db.Column(db.String(10))
    
    description = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_effective_rate(self):
        """Get total effective tax rate"""
        if self.tax_type == 'gst':
            return float(self.cgst_rate or 0) + float(self.sgst_rate or 0) + float(self.igst_rate or 0) + float(self.cess_rate or 0)
        return float(self.rate or 0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'tax_type': self.tax_type,
            'rate': float(self.rate) if self.rate else 0,
            'cgst_rate': float(self.cgst_rate) if self.cgst_rate else 0,
            'sgst_rate': float(self.sgst_rate) if self.sgst_rate else 0,
            'igst_rate': float(self.igst_rate) if self.igst_rate else 0,
            'cess_rate': float(self.cess_rate) if self.cess_rate else 0,
            'effective_rate': self.get_effective_rate(),
            'hsn_code_prefix': self.hsn_code_prefix,
            'description': self.description,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class NotificationSetting(db.Model):
    """Notification configuration"""
    __tablename__ = 'notification_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Email notifications
    email_low_stock = db.Column(db.Boolean, default=True)
    email_new_sale = db.Column(db.Boolean, default=False)
    email_daily_summary = db.Column(db.Boolean, default=False)
    email_backup_complete = db.Column(db.Boolean, default=True)
    
    # In-app notifications
    notify_low_stock = db.Column(db.Boolean, default=True)
    notify_new_order = db.Column(db.Boolean, default=True)
    notify_payment_received = db.Column(db.Boolean, default=True)
    notify_system_updates = db.Column(db.Boolean, default=True)
    
    # Thresholds
    low_stock_threshold = db.Column(db.Integer, default=10)
    
    # Recipients
    notification_email = db.Column(db.String(120))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email_low_stock': self.email_low_stock,
            'email_new_sale': self.email_new_sale,
            'email_daily_summary': self.email_daily_summary,
            'email_backup_complete': self.email_backup_complete,
            'notify_low_stock': self.notify_low_stock,
            'notify_new_order': self.notify_new_order,
            'notify_payment_received': self.notify_payment_received,
            'notify_system_updates': self.notify_system_updates,
            'low_stock_threshold': self.low_stock_threshold,
            'notification_email': self.notification_email
        }


class BackupSetting(db.Model):
    """Backup and restore configuration"""
    __tablename__ = 'backup_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Auto backup
    auto_backup_enabled = db.Column(db.Boolean, default=False)
    backup_frequency = db.Column(db.String(20), default='daily')  # hourly, daily, weekly, monthly
    backup_time = db.Column(db.Time)
    backup_day = db.Column(db.Integer, default=0)  # 0=Sunday for weekly
    
    # Retention
    keep_backups_count = db.Column(db.Integer, default=10)
    
    # Storage
    backup_location = db.Column(db.String(255), default='local')
    cloud_provider = db.Column(db.String(50))  # s3, dropbox, google_drive
    cloud_config = db.Column(db.Text)  # JSON config
    
    # Encryption
    encrypt_backups = db.Column(db.Boolean, default=False)
    encryption_key_hint = db.Column(db.String(255))
    
    # Include
    include_uploads = db.Column(db.Boolean, default=True)
    include_logs = db.Column(db.Boolean, default=False)
    
    # Last backup
    last_backup_at = db.Column(db.DateTime)
    last_backup_status = db.Column(db.String(20))
    last_backup_path = db.Column(db.String(500))
    last_backup_size = db.Column(db.BigInteger)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'auto_backup_enabled': self.auto_backup_enabled,
            'backup_frequency': self.backup_frequency,
            'keep_backups_count': self.keep_backups_count,
            'backup_location': self.backup_location,
            'cloud_provider': self.cloud_provider,
            'encrypt_backups': self.encrypt_backups,
            'include_uploads': self.include_uploads,
            'include_logs': self.include_logs,
            'last_backup_at': self.last_backup_at.isoformat() if self.last_backup_at else None,
            'last_backup_status': self.last_backup_status,
            'last_backup_path': self.last_backup_path,
            'last_backup_size': self.last_backup_size
        }
