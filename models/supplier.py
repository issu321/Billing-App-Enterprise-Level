"""Supplier Model"""
from . import db
from datetime import datetime


class Supplier(db.Model):
    """Supplier/Vendor model"""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic info
    supplier_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(150))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    fax = db.Column(db.String(20))
    website = db.Column(db.String(255))
    
    # Address
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    
    # Tax info
    gst_number = db.Column(db.String(20))
    tax_number = db.Column(db.String(50))
    pan_number = db.Column(db.String(20))
    cin_number = db.Column(db.String(30))  # Corporate Identification Number
    
    # Credit
    credit_limit = db.Column(db.Numeric(15, 2), default=0)
    credit_days = db.Column(db.Integer, default=0)
    current_balance = db.Column(db.Numeric(15, 2), default=0)
    total_purchases = db.Column(db.Numeric(15, 2), default=0)
    total_payments = db.Column(db.Numeric(15, 2), default=0)
    
    # Bank details
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(50))
    bank_ifsc = db.Column(db.String(20))
    bank_branch = db.Column(db.String(100))
    upi_id = db.Column(db.String(100))
    
    # Contact person
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    contact_designation = db.Column(db.String(50))
    
    # Additional
    supplier_type = db.Column(db.String(20), default='regular')  # regular, manufacturer, distributor
    category = db.Column(db.String(50))  # raw_material, finished_goods, service, etc.
    lead_time_days = db.Column(db.Integer, default=0)
    minimum_order_value = db.Column(db.Numeric(15, 2), default=0)
    notes = db.Column(db.Text)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_preferred = db.Column(db.Boolean, default=False)
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    ledger_entries = db.relationship('SupplierLedger', backref='supplier', cascade='all, delete-orphan', lazy='dynamic')
    
    def get_balance(self):
        """Calculate current balance"""
        from decimal import Decimal
        total_purchases = db.session.query(db.func.sum(SupplierLedger.amount)).filter(
            SupplierLedger.supplier_id == self.id,
            SupplierLedger.entry_type.in_(['purchase', 'debit'])
        ).scalar() or Decimal('0')
        
        total_payments = db.session.query(db.func.sum(SupplierLedger.amount)).filter(
            SupplierLedger.supplier_id == self.id,
            SupplierLedger.entry_type.in_(['payment', 'credit'])
        ).scalar() or Decimal('0')
        
        return float(total_purchases) - float(total_payments)
    
    def to_dict(self):
        return {
            'id': self.id,
            'supplier_code': self.supplier_code,
            'name': self.name,
            'company_name': self.company_name,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'fax': self.fax,
            'website': self.website,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'gst_number': self.gst_number,
            'tax_number': self.tax_number,
            'pan_number': self.pan_number,
            'cin_number': self.cin_number,
            'credit_limit': float(self.credit_limit) if self.credit_limit else 0,
            'credit_days': self.credit_days,
            'current_balance': self.get_balance(),
            'total_purchases': float(self.total_purchases) if self.total_purchases else 0,
            'total_payments': float(self.total_payments) if self.total_payments else 0,
            'bank_name': self.bank_name,
            'bank_account': self.bank_account,
            'bank_ifsc': self.bank_ifsc,
            'bank_branch': self.bank_branch,
            'upi_id': self.upi_id,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'contact_designation': self.contact_designation,
            'supplier_type': self.supplier_type,
            'category': self.category,
            'lead_time_days': self.lead_time_days,
            'minimum_order_value': float(self.minimum_order_value) if self.minimum_order_value else 0,
            'notes': self.notes,
            'is_active': self.is_active,
            'is_preferred': self.is_preferred,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SupplierLedger(db.Model):
    """Supplier ledger for tracking all transactions"""
    __tablename__ = 'supplier_ledger'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    entry_type = db.Column(db.String(20), nullable=False)  # purchase, payment, debit, credit, return
    reference_type = db.Column(db.String(50))
    reference_id = db.Column(db.Integer)
    reference_number = db.Column(db.String(100))
    
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    balance = db.Column(db.Numeric(15, 2))
    
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'entry_type': self.entry_type,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'reference_number': self.reference_number,
            'amount': float(self.amount) if self.amount else 0,
            'balance': float(self.balance) if self.balance else 0,
            'description': self.description,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
