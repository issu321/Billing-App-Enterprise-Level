"""Purchase and Purchase Return Models"""
from . import db
from datetime import datetime


class Purchase(db.Model):
    """Purchase order/invoice model"""
    __tablename__ = 'purchases'
    
    STATUS_CHOICES = ['draft', 'ordered', 'partial', 'received', 'cancelled', 'returned']
    PAYMENT_STATUS_CHOICES = ['pending', 'partial', 'paid', 'overdue']
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Invoice info
    purchase_number = db.Column(db.String(50), unique=True, nullable=False)
    reference_number = db.Column(db.String(100))
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    expected_date = db.Column(db.DateTime)
    
    # Supplier
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    supplier_name = db.Column(db.String(150))
    supplier_address = db.Column(db.Text)
    supplier_gst = db.Column(db.String(20))
    
    # Amounts
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0)
    shipping_amount = db.Column(db.Numeric(15, 2), default=0)
    other_charges = db.Column(db.Numeric(15, 2), default=0)
    round_off = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    paid_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Discount
    discount_type = db.Column(db.String(20), default='none')
    discount_value = db.Column(db.Numeric(10, 2), default=0)
    
    # Tax
    tax_type = db.Column(db.String(20), default='exclusive')
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    
    # Payment
    payment_status = db.Column(db.String(20), default='pending')
    payment_terms = db.Column(db.String(100))
    
    # Status
    status = db.Column(db.String(20), default='draft')
    
    # Delivery
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))
    delivery_method = db.Column(db.String(50))
    
    notes = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    supplier = db.relationship('Supplier', backref='purchases')
    warehouse = db.relationship('Warehouse', backref='purchases')
    items = db.relationship('PurchaseItem', backref='purchase', cascade='all, delete-orphan', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'purchase_number': self.purchase_number,
            'reference_number': self.reference_number,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'expected_date': self.expected_date.isoformat() if self.expected_date else None,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier_name or (self.supplier.name if self.supplier else ''),
            'supplier_address': self.supplier_address,
            'supplier_gst': self.supplier_gst,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'shipping_amount': float(self.shipping_amount) if self.shipping_amount else 0,
            'other_charges': float(self.other_charges) if self.other_charges else 0,
            'round_off': float(self.round_off) if self.round_off else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'paid_amount': float(self.paid_amount) if self.paid_amount else 0,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value) if self.discount_value else 0,
            'tax_type': self.tax_type,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'payment_status': self.payment_status,
            'payment_terms': self.payment_terms,
            'status': self.status,
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse.name if self.warehouse else None,
            'delivery_method': self.delivery_method,
            'notes': self.notes,
            'internal_notes': self.internal_notes,
            'item_count': self.items.count(),
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PurchaseItem(db.Model):
    """Individual line item in a purchase"""
    __tablename__ = 'purchase_items'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    
    # Product
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product_name = db.Column(db.String(200), nullable=False)
    product_sku = db.Column(db.String(100))
    
    # Quantity
    quantity = db.Column(db.Numeric(10, 4), nullable=False)
    received_quantity = db.Column(db.Numeric(10, 4), default=0)
    unit = db.Column(db.String(20))
    
    # Pricing
    unit_price = db.Column(db.Numeric(15, 4), nullable=False)
    mrp = db.Column(db.Numeric(15, 4), default=0)
    selling_price = db.Column(db.Numeric(15, 4), default=0)
    
    # Tax
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 4), default=0)
    hsn_code = db.Column(db.String(20))
    
    # Discount
    discount_percent = db.Column(db.Numeric(5, 2), default=0)
    discount_amount = db.Column(db.Numeric(15, 4), default=0)
    
    # Totals
    total_price = db.Column(db.Numeric(15, 4), default=0)
    
    # Batch
    batch_number = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    manufacturing_date = db.Column(db.Date)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, partial, received
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='purchase_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'purchase_id': self.purchase_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_sku': self.product_sku,
            'quantity': float(self.quantity) if self.quantity else 0,
            'received_quantity': float(self.received_quantity) if self.received_quantity else 0,
            'unit': self.unit,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'mrp': float(self.mrp) if self.mrp else 0,
            'selling_price': float(self.selling_price) if self.selling_price else 0,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'hsn_code': self.hsn_code,
            'discount_percent': float(self.discount_percent) if self.discount_percent else 0,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'batch_number': self.batch_number,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'manufacturing_date': self.manufacturing_date.isoformat() if self.manufacturing_date else None,
            'status': self.status
        }


class PurchaseReturn(db.Model):
    """Purchase return to supplier"""
    __tablename__ = 'purchase_returns'
    
    id = db.Column(db.Integer, primary_key=True)
    return_number = db.Column(db.String(50), unique=True, nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    
    # Supplier
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    supplier_name = db.Column(db.String(150))
    
    # Amounts
    subtotal = db.Column(db.Numeric(15, 2), default=0)
    tax_amount = db.Column(db.Numeric(15, 2), default=0)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, sent, approved, rejected
    
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    purchase = db.relationship('Purchase', backref='returns')
    supplier = db.relationship('Supplier', backref='purchase_returns')
    items = db.relationship('PurchaseReturnItem', backref='purchase_return', cascade='all, delete-orphan', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'return_number': self.return_number,
            'purchase_id': self.purchase_id,
            'purchase_number': self.purchase.purchase_number if self.purchase else None,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier_name,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'status': self.status,
            'reason': self.reason,
            'notes': self.notes,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class PurchaseReturnItem(db.Model):
    """Individual item in a purchase return"""
    __tablename__ = 'purchase_return_items'
    
    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('purchase_returns.id'), nullable=False)
    purchase_item_id = db.Column(db.Integer, db.ForeignKey('purchase_items.id'))
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product_name = db.Column(db.String(200))
    
    quantity = db.Column(db.Numeric(10, 4), nullable=False)
    unit_price = db.Column(db.Numeric(15, 4), nullable=False)
    total_price = db.Column(db.Numeric(15, 4), default=0)
    
    reason = db.Column(db.String(255))
    condition = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'return_id': self.return_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit_price': float(self.unit_price) if self.unit_price else 0,
            'total_price': float(self.total_price) if self.total_price else 0,
            'reason': self.reason,
            'condition': self.condition
        }
