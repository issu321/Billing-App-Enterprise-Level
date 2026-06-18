"""Payment, Account, and Currency Models"""
from . import db
from datetime import datetime


class Currency(db.Model):
    """Currency configuration"""
    __tablename__ = 'currencies'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(3), unique=True, nullable=False)  # USD, INR, EUR
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    exchange_rate = db.Column(db.Numeric(15, 6), default=1.0)  # Rate against base currency
    is_base = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'symbol': self.symbol,
            'exchange_rate': float(self.exchange_rate) if self.exchange_rate else 1.0,
            'is_base': self.is_base,
            'is_active': self.is_active
        }


class Account(db.Model):
    """Financial account (bank, cash, etc.)"""
    __tablename__ = 'accounts'
    
    ACCOUNT_TYPES = ['cash', 'bank', 'wallet', 'upi', 'card', 'other']
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50))
    account_type = db.Column(db.String(20), nullable=False)  # cash, bank, wallet, upi
    
    # Bank details
    bank_name = db.Column(db.String(100))
    branch_name = db.Column(db.String(100))
    ifsc_code = db.Column(db.String(20))
    swift_code = db.Column(db.String(20))
    
    # UPI
    upi_id = db.Column(db.String(100))
    
    # Balance
    opening_balance = db.Column(db.Numeric(15, 2), default=0)
    current_balance = db.Column(db.Numeric(15, 2), default=0)
    
    currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'))
    
    # Status
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    currency = db.relationship('Currency', backref='accounts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'account_number': self.account_number,
            'account_type': self.account_type,
            'bank_name': self.bank_name,
            'branch_name': self.branch_name,
            'ifsc_code': self.ifsc_code,
            'swift_code': self.swift_code,
            'upi_id': self.upi_id,
            'opening_balance': float(self.opening_balance) if self.opening_balance else 0,
            'current_balance': float(self.current_balance) if self.current_balance else 0,
            'currency_id': self.currency_id,
            'currency_code': self.currency.code if self.currency else None,
            'currency_symbol': self.currency.symbol if self.currency else None,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PaymentMethod(db.Model):
    """Payment method configuration"""
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Cash, Credit Card, UPI, etc.
    code = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    
    # Configuration
    requires_reference = db.Column(db.Boolean, default=False)
    auto_deposit_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    processing_fee_percent = db.Column(db.Numeric(5, 2), default=0)
    
    # For digital payments
    gateway_name = db.Column(db.String(50))  # Razorpay, Stripe, etc.
    gateway_config = db.Column(db.Text)  # JSON configuration
    
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    auto_deposit_account = db.relationship('Account', backref='payment_methods')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'icon': self.icon,
            'requires_reference': self.requires_reference,
            'processing_fee_percent': float(self.processing_fee_percent) if self.processing_fee_percent else 0,
            'gateway_name': self.gateway_name,
            'is_active': self.is_active,
            'sort_order': self.sort_order
        }


class Payment(db.Model):
    """Payment record"""
    __tablename__ = 'payments'
    
    PAYMENT_TYPES = ['sale', 'purchase', 'refund', 'expense', 'income', 'transfer', 'other']
    STATUS_CHOICES = ['pending', 'completed', 'failed', 'cancelled', 'refunded']
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Payment info
    payment_number = db.Column(db.String(50), unique=True, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Type and reference
    payment_type = db.Column(db.String(20), nullable=False)  # sale, purchase, refund, expense
    reference_type = db.Column(db.String(50))  # sale, purchase, invoice
    reference_id = db.Column(db.Integer)
    reference_number = db.Column(db.String(100))
    
    # Party info
    party_type = db.Column(db.String(20))  # customer, supplier
    party_id = db.Column(db.Integer)
    party_name = db.Column(db.String(150))
    
    # Amount
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'))
    exchange_rate = db.Column(db.Numeric(15, 6), default=1.0)
    base_amount = db.Column(db.Numeric(15, 2))
    
    # Payment method
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'))
    payment_method_name = db.Column(db.String(50))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    
    # Reference numbers
    cheque_number = db.Column(db.String(50))
    cheque_date = db.Column(db.Date)
    transaction_id = db.Column(db.String(100))
    upi_transaction_id = db.Column(db.String(100))
    card_last_four = db.Column(db.String(4))
    bank_reference = db.Column(db.String(100))
    
    # For QR/UPI payments
    qr_code = db.Column(db.String(255))
    upi_id = db.Column(db.String(100))
    
    # Status
    status = db.Column(db.String(20), default='completed')
    
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    payment_method = db.relationship('PaymentMethod', backref='payments')
    account = db.relationship('Account', backref='payments')
    currency = db.relationship('Currency', backref='payments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'payment_number': self.payment_number,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_type': self.payment_type,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'reference_number': self.reference_number,
            'party_type': self.party_type,
            'party_id': self.party_id,
            'party_name': self.party_name,
            'amount': float(self.amount) if self.amount else 0,
            'currency_id': self.currency_id,
            'currency_code': self.currency.code if self.currency else None,
            'currency_symbol': self.currency.symbol if self.currency else None,
            'payment_method_id': self.payment_method_id,
            'payment_method_name': self.payment_method_name or (self.payment_method.name if self.payment_method else ''),
            'account_id': self.account_id,
            'account_name': self.account.name if self.account else None,
            'cheque_number': self.cheque_number,
            'transaction_id': self.transaction_id,
            'upi_transaction_id': self.upi_transaction_id,
            'upi_id': self.upi_id,
            'status': self.status,
            'description': self.description,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Transaction(db.Model):
    """General ledger transaction"""
    __tablename__ = 'transactions'
    
    TRANSACTION_TYPES = ['income', 'expense', 'asset', 'liability', 'equity']
    
    id = db.Column(db.Integer, primary_key=True)
    
    transaction_number = db.Column(db.String(50), unique=True, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    transaction_type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50))  # sale, purchase, salary, rent, utilities, etc.
    
    # Amount
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currencies.id'))
    
    # Accounts
    debit_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    credit_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    
    # Reference
    reference_type = db.Column(db.String(50))
    reference_id = db.Column(db.Integer)
    reference_number = db.Column(db.String(100))
    
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Status
    is_reconciled = db.Column(db.Boolean, default=False)
    reconciled_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    currency = db.relationship('Currency', backref='transactions')
    debit_account = db.relationship('Account', foreign_keys=[debit_account_id], backref='debit_transactions')
    credit_account = db.relationship('Account', foreign_keys=[credit_account_id], backref='credit_transactions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_number': self.transaction_number,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'transaction_type': self.transaction_type,
            'category': self.category,
            'amount': float(self.amount) if self.amount else 0,
            'currency_id': self.currency_id,
            'currency_code': self.currency.code if self.currency else None,
            'debit_account_id': self.debit_account_id,
            'debit_account_name': self.debit_account.name if self.debit_account else None,
            'credit_account_id': self.credit_account_id,
            'credit_account_name': self.credit_account.name if self.credit_account else None,
            'reference_type': self.reference_type,
            'reference_number': self.reference_number,
            'description': self.description,
            'is_reconciled': self.is_reconciled,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
