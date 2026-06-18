"""Customer and Customer Group Models"""
from . import db
from datetime import datetime


class CustomerGroup(db.Model):
    """Customer group for pricing tiers"""
    __tablename__ = 'customer_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    discount_percent = db.Column(db.Numeric(5, 2), default=0)
    price_level = db.Column(db.String(20), default='retail')  # retail, wholesale, dealer
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'discount_percent': float(self.discount_percent) if self.discount_percent else 0,
            'price_level': self.price_level,
            'is_active': self.is_active,
            'customer_count': len(self.customers) if hasattr(self, 'customers') else 0
        }


class Customer(db.Model):
    """Customer model with complete details"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic info
    customer_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    
    # Classification
    group_id = db.Column(db.Integer, db.ForeignKey('customer_groups.id'))
    group = db.relationship('CustomerGroup', backref='customers')
    customer_type = db.Column(db.String(20), default='retail')  # retail, wholesale, corporate
    
    # Address
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    
    # GST/Tax info
    gst_number = db.Column(db.String(20))
    tax_number = db.Column(db.String(50))
    pan_number = db.Column(db.String(20))
    
    # Credit
    credit_limit = db.Column(db.Numeric(15, 2), default=0)
    credit_days = db.Column(db.Integer, default=0)
    current_balance = db.Column(db.Numeric(15, 2), default=0)
    total_sales = db.Column(db.Numeric(15, 2), default=0)
    total_payments = db.Column(db.Numeric(15, 2), default=0)
    
    # Contact person (for corporate customers)
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    
    # Additional info
    date_of_birth = db.Column(db.Date)
    anniversary_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    ledger_entries = db.relationship('CustomerLedger', backref='customer', cascade='all, delete-orphan', lazy='dynamic')
    
    def get_balance(self):
        """Calculate current balance"""
        from decimal import Decimal
        total_sales = db.session.query(db.func.sum(CustomerLedger.amount)).filter(
            CustomerLedger.customer_id == self.id,
            CustomerLedger.entry_type.in_(['sale', 'debit'])
        ).scalar() or Decimal('0')
        
        total_payments = db.session.query(db.func.sum(CustomerLedger.amount)).filter(
            CustomerLedger.customer_id == self.id,
            CustomerLedger.entry_type.in_(['payment', 'credit'])
        ).scalar() or Decimal('0')
        
        return float(total_sales) - float(total_payments)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_code': self.customer_code,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'group_id': self.group_id,
            'group_name': self.group.name if self.group else None,
            'customer_type': self.customer_type,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'gst_number': self.gst_number,
            'tax_number': self.tax_number,
            'pan_number': self.pan_number,
            'credit_limit': float(self.credit_limit) if self.credit_limit else 0,
            'credit_days': self.credit_days,
            'current_balance': self.get_balance(),
            'total_sales': float(self.total_sales) if self.total_sales else 0,
            'total_payments': float(self.total_payments) if self.total_payments else 0,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'anniversary_date': self.anniversary_date.isoformat() if self.anniversary_date else None,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CustomerLedger(db.Model):
    """Customer ledger for tracking all transactions"""
    __tablename__ = 'customer_ledger'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    entry_type = db.Column(db.String(20), nullable=False)  # sale, payment, debit, credit, return
    reference_type = db.Column(db.String(50))  # sale, payment, adjustment
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
            'customer_id': self.customer_id,
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
