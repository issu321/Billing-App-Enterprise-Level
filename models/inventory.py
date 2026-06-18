"""Inventory, Warehouse, and Stock Management Models"""
from . import db
from datetime import datetime


class Warehouse(db.Model):
    """Warehouse/Branch model for multi-location inventory"""
    __tablename__ = 'warehouses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    manager_name = db.Column(db.String(100))
    is_primary = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'phone': self.phone,
            'email': self.email,
            'manager_name': self.manager_name,
            'is_primary': self.is_primary,
            'is_active': self.is_active,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Inventory(db.Model):
    """Inventory record for a product in a warehouse"""
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    quantity = db.Column(db.Numeric(15, 4), default=0)
    reserved_quantity = db.Column(db.Numeric(15, 4), default=0)  # Reserved for orders
    available_quantity = db.Column(db.Numeric(15, 4), default=0)
    
    # Location within warehouse
    aisle = db.Column(db.String(20))
    rack = db.Column(db.String(20))
    shelf = db.Column(db.String(20))
    bin_location = db.Column(db.String(20))
    
    # Tracking
    batch_number = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    manufacturing_date = db.Column(db.Date)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    warehouse = db.relationship('Warehouse', backref='inventory_items')
    
    def to_dict(self):
        from .product import Product
        product = Product.query.get(self.product_id)
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': product.name if product else None,
            'product_sku': product.sku if product else None,
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse.name if self.warehouse else None,
            'quantity': float(self.quantity) if self.quantity else 0,
            'reserved_quantity': float(self.reserved_quantity) if self.reserved_quantity else 0,
            'available_quantity': float(self.available_quantity) if self.available_quantity else 0,
            'aisle': self.aisle,
            'rack': self.rack,
            'shelf': self.shelf,
            'bin_location': self.bin_location,
            'batch_number': self.batch_number,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'manufacturing_date': self.manufacturing_date.isoformat() if self.manufacturing_date else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class InventoryTransaction(db.Model):
    """Inventory transaction log"""
    __tablename__ = 'inventory_transactions'
    
    TRANSACTION_TYPES = [
        'purchase', 'sale', 'return', 'adjustment', 'transfer_in', 'transfer_out',
        'opening_stock', 'damage', 'expired', 'production', 'stock_count'
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    transaction_type = db.Column(db.String(30), nullable=False)
    quantity = db.Column(db.Numeric(15, 4), nullable=False)
    unit_cost = db.Column(db.Numeric(15, 4))
    total_cost = db.Column(db.Numeric(15, 4))
    
    # Reference
    reference_type = db.Column(db.String(50))  # sale, purchase, adjustment
    reference_id = db.Column(db.Integer)
    reference_number = db.Column(db.String(100))
    
    # Details
    notes = db.Column(db.Text)
    batch_number = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    
    # Running balance
    balance_after = db.Column(db.Numeric(15, 4))
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    product = db.relationship('Product', backref='inventory_transactions')
    warehouse = db.relationship('Warehouse', backref='transactions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if hasattr(self, 'product') and self.product else None,
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse.name if hasattr(self, 'warehouse') and self.warehouse else None,
            'transaction_type': self.transaction_type,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'total_cost': float(self.total_cost) if self.total_cost else None,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'reference_number': self.reference_number,
            'notes': self.notes,
            'batch_number': self.batch_number,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'balance_after': float(self.balance_after) if self.balance_after else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class StockAdjustment(db.Model):
    """Stock adjustment record"""
    __tablename__ = 'stock_adjustments'
    
    ADJUSTMENT_TYPES = [
        'damage', 'expired', 'lost', 'found', 'count', 'system', 'other'
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    adjustment_number = db.Column(db.String(50), unique=True, nullable=False)
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    
    adjustment_type = db.Column(db.String(20), nullable=False)
    quantity_before = db.Column(db.Numeric(15, 4), nullable=False)
    quantity_after = db.Column(db.Numeric(15, 4), nullable=False)
    difference = db.Column(db.Numeric(15, 4), nullable=False)
    
    # Cost impact
    unit_cost = db.Column(db.Numeric(15, 4))
    total_cost_impact = db.Column(db.Numeric(15, 4))
    
    reason = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    
    status = db.Column(db.String(20), default='draft')  # draft, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    product = db.relationship('Product', backref='stock_adjustments')
    warehouse = db.relationship('Warehouse', backref='stock_adjustments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'adjustment_number': self.adjustment_number,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse.name if self.warehouse else None,
            'adjustment_type': self.adjustment_type,
            'quantity_before': float(self.quantity_before) if self.quantity_before else 0,
            'quantity_after': float(self.quantity_after) if self.quantity_after else 0,
            'difference': float(self.difference) if self.difference else 0,
            'unit_cost': float(self.unit_cost) if self.unit_cost else None,
            'total_cost_impact': float(self.total_cost_impact) if self.total_cost_impact else None,
            'reason': self.reason,
            'notes': self.notes,
            'status': self.status,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
