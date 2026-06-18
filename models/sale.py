"""Sale, Invoice, and Return Models"""
from . import db
from datetime import datetime


class Sale(db.Model):
    """Sale/POS transaction model"""
    __tablename__ = 'sales'
    
    PAYMENT_STATUS_CHOICES = ['pending', 'partial', 'paid', 'overdue', 'cancelled']
    STATUS_CHOICES = ['draft', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'returned']
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Invoice info
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_prefix = db.Column(db.String(20), default='INV')
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    
    # Customer
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    customer_name = db.Column(db.String(150))
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(120))
    customer_address = db.Column(db.Text)
    customer_gst = db.Column(db.String(20))
    
    # Amounts
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    shipping_amount = db.Column(db.Numeric(15, 2), default=0)
    round_off = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    paid_amount = db.Column(db.Numeric(15, 2), default=0)
    balance_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Discount
    discount_type = db.Column(db.String(20), default='none')
    discount_value = db.Column(db.Numeric(10, 2), default=0)
    
    # Tax
    tax_type = db.Column(db.String(20), default='inclusive')  # inclusive, exclusive
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    
    # Payment
    payment_method = db.Column(db.String(50), default='cash')
    payment_status = db.Column(db.String(20), default='paid')
    payment_reference = db.Column(db.String(100))
    
    # POS specific
    is_pos_sale = db.Column(db.Boolean, default=False)
    pos_session_id = db.Column(db.String(50))
    counter_number = db.Column(db.String(20))
    cashier_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status
    status = db.Column(db.String(20), default='confirmed')
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    # Delivery
    delivery_method = db.Column(db.String(50))
    tracking_number = db.Column(db.String(100))
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    customer = db.relationship('Customer', backref='sales')
    cashier = db.relationship('User', foreign_keys=[cashier_id], backref='pos_sales')
    items = db.relationship('SaleItem', backref='sale', cascade='all, delete-orphan', lazy='dynamic')
    
    def calculate_totals(self):
        """Recalculate sale totals"""
        from decimal import Decimal
        subtotal = sum(Decimal(str(item.total_price)) for item in self.items)
        self.subtotal = subtotal
        
        # Calculate discount
        discount = Decimal('0')
        if self.discount_type == 'percentage' and self.discount_value:
            discount = subtotal * (Decimal(str(self.discount_value)) / Decimal('100'))
        elif self.discount_type == 'fixed' and self.discount_value:
            discount = Decimal(str(self.discount_value))
        self.discount_amount = discount
        
        # Calculate tax
        taxable_amount = subtotal - discount
        tax = Decimal('0')
        if self.tax_rate:
            if self.tax_type == 'exclusive':
                tax = taxable_amount * (Decimal(str(self.tax_rate)) / Decimal('100'))
            # For inclusive, tax is already in the price
        self.tax_amount = tax
        
        # Total
        if self.tax_type == 'exclusive':
            self.total_amount = taxable_amount + tax + Decimal(str(self.shipping_amount or 0)) + Decimal(str(self.round_off or 0))
        else:
            self.total_amount = taxable_amount + Decimal(str(self.shipping_amount or 0)) + Decimal(str(self.round_off or 0))
        
        self.balance_amount = self.total_amount - Decimal(str(self.paid_amount or 0))
        
        # Update payment status
        if self.balance_amount <= 0:
            self.payment_status = 'paid'
        elif self.paid_amount and self.paid_amount > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'pending'
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'invoice_prefix': self.invoice_prefix,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name or (self.customer.name if self.customer else 'Walk-in Customer'),
            'customer_phone': self.customer_phone,
            'customer_email': self.customer_email,
            'customer_address': self.customer_address,
            'customer_gst': self.customer_gst,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'shipping_amount': float(self.shipping_amount) if self.shipping_amount else 0,
            'round_off': float(self.round_off) if self.round_off else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'paid_amount': float(self.paid_amount) if self.paid_amount else 0,
            'balance_amount': float(self.balance_amount) if self.balance_amount else 0,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value) if self.discount_value else 0,
            'tax_type': self.tax_type,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'payment_reference': self.payment_reference,
            'is_pos_sale': self.is_pos_sale,
            'pos_session_id': self.pos_session_id,
            'counter_number': self.counter_number,
            'cashier_id': self.cashier_id,
            'status': self.status,
            'notes': self.notes,
            'internal_notes': self.internal_notes,
            'item_count': self.items.count(),
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SaleItem(db.Model):
    """Individual line item in a sale"""
    __tablename__ = 'sale_items'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    
    # Product
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product_name = db.Column(db.String(200), nullable=False)
    product_sku = db.Column(db.String(100))
    product_barcode = db.Column(db.String(100))
    
    # Variant
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'))
    variant_name = db.Column(db.String(100))
    
    # Pricing
    quantity = db.Column(db.Numeric(10, 4), nullable=False)
    unit_price = db.Column(db.Numeric(15, 4), nullable=False)
    cost_price = db.Column(db.Numeric(15, 4), default=0)
    mrp = db.Column(db.Numeric(15, 4), default=0)
    
    # Discount
    discount_percent = db.Column(db.Numeric(5, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 4), default=0)
    
    # Tax
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 4), default=0)
    hsn_code = db.Column(db.String(20))
    
    # Totals
    total_price = db.Column(db.Numeric(15, 4), default=0)
    
    # Warehouse
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='sale_items')
    variant = db.relationship('ProductVariant', backref='sale_items')
    warehouse = db.relationship('Warehouse', backref='sale_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_sku': self.product_sku,
            'product_barcode': self.product_barcode,
            'variant_id': self.variant_id,
            'variant_name': self.variant_name,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'cost_price': float(self.cost_price) if self.cost_price else 0,
            'mrp': float(self.mrp) if self.mrp else 0,
            'discount_percent': float(self.discount_percent) if self.discount_percent else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'hsn_code': self.hsn_code,
            'total_price': float(self.total_price) if self.total_price else 0,
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse.name if self.warehouse else None
        }


class SaleReturn(db.Model):
    """Sale return/credit note"""
    __tablename__ = 'sale_returns'
    
    id = db.Column(db.Integer, primary_key=True)
    return_number = db.Column(db.String(50), unique=True, nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    
    # Customer
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer_name = db.Column(db.String(150))
    
    # Amounts
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, refunded
    refund_method = db.Column(db.String(50))
    refund_reference = db.Column(db.String(100))
    
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    sale = db.relationship('Sale', backref='returns')
    customer = db.relationship('Customer', backref='sale_returns')
    items = db.relationship('SaleReturnItem', backref='sale_return', cascade='all, delete-orphan', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'return_number': self.return_number,
            'sale_id': self.sale_id,
            'sale_invoice_number': self.sale.invoice_number if self.sale else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'status': self.status,
            'refund_method': self.refund_method,
            'reason': self.reason,
            'notes': self.notes,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SaleReturnItem(db.Model):
    """Individual item in a sale return"""
    __tablename__ = 'sale_return_items'
    
    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('sale_returns.id'), nullable=False)
    sale_item_id = db.Column(db.Integer, db.ForeignKey('sale_items.id'))
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product_name = db.Column(db.String(200))
    
    quantity = db.Column(db.Numeric(10, 4), nullable=False)
    unit_price = db.Column(db.Numeric(15, 4), nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    total_price = db.Column(db.Numeric(15, 4), default=0)
    
    reason = db.Column(db.String(255))
    condition = db.Column(db.String(50))  # good, damaged, defective
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'return_id': self.return_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'reason': self.reason,
            'condition': self.condition
        }


class Invoice(db.Model):
    """Invoice model for detailed invoice management"""
    __tablename__ = 'invoices'
    
    STATUS_CHOICES = ['draft', 'sent', 'viewed', 'paid', 'overdue', 'cancelled', 'refunded']
    
    id = db.Column(db.Integer, primary_key=True)
    
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'))
    
    # Customer info (snapshot)
    customer_name = db.Column(db.String(150))
    customer_email = db.Column(db.String(120))
    customer_address = db.Column(db.Text)
    customer_gst = db.Column(db.String(20))
    
    # Invoice details
    issue_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)
    
    # Amounts
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    paid_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Status
    status = db.Column(db.String(20), default='draft')
    sent_at = db.Column(db.DateTime)
    viewed_at = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    
    notes = db.Column(db.Text)
    terms = db.Column(db.Text)
    footer_note = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sale = db.relationship('Sale', backref='invoice_detail')
    items = db.relationship('InvoiceItem', backref='invoice', cascade='all, delete-orphan', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'sale_id': self.sale_id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_address': self.customer_address,
            'customer_gst': self.customer_gst,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'paid_amount': float(self.paid_amount) if self.paid_amount else 0,
            'status': self.status,
            'notes': self.notes,
            'terms': self.terms,
            'footer_note': self.footer_note,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class InvoiceItem(db.Model):
    """Individual item in an invoice"""
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Numeric(10, 4), nullable=False)
    unit_price = db.Column(db.Numeric(15, 4), nullable=False)
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    total_price = db.Column(db.Numeric(15, 4), default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'total_price': float(self.total_price) if self.total_price else 0
        }
