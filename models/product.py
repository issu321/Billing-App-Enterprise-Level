"""Product, Category, and related models"""
from . import db
from datetime import datetime


class UnitOfMeasure(db.Model):
    """Unit of measure for products"""
    __tablename__ = 'units_of_measure'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'is_active': self.is_active
        }


class Category(db.Model):
    """Product category model"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    image = db.Column(db.String(255))
    color = db.Column(db.String(7), default='#4F46E5')
    icon = db.Column(db.String(50))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    parent = db.relationship('Category', remote_side=[id], backref='subcategories')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_full_path(self):
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'parent_id': self.parent_id,
            'parent_name': self.parent.name if self.parent else None,
            'image': self.image,
            'color': self.color,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'product_count': len(self.products) if hasattr(self, 'products') else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Product(db.Model):
    """Product model with unit_id foreign key (unchanged - no DB migration needed)"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic info
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    barcode = db.Column(db.String(100), unique=True, index=True)
    qr_code = db.Column(db.String(255), unique=True)
    description = db.Column(db.Text)
    short_description = db.Column(db.String(500))
    
    # Categorization
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', backref='products')
    tags = db.Column(db.String(500))
    brand = db.Column(db.String(100))
    
    # Unit of measure (foreign key - unchanged)
    unit_id = db.Column(db.Integer, db.ForeignKey('units_of_measure.id'))
    unit = db.relationship('UnitOfMeasure')
    
    # Pricing
    cost_price = db.Column(db.Numeric(15, 4), default=0)
    selling_price = db.Column(db.Numeric(15, 4), default=0)
    mrp = db.Column(db.Numeric(15, 4), default=0)
    wholesale_price = db.Column(db.Numeric(15, 4), default=0)
    dealer_price = db.Column(db.Numeric(15, 4), default=0)
    
    # Tax
    tax_rate = db.Column(db.Numeric(5, 2), default=0)
    tax_inclusive = db.Column(db.Boolean, default=True)
    hsn_code = db.Column(db.String(20))
    
    # Discount
    discount_type = db.Column(db.String(20), default='none')
    discount_value = db.Column(db.Numeric(10, 2), default=0)
    
    # Inventory
    track_inventory = db.Column(db.Boolean, default=True)
    reorder_level = db.Column(db.Numeric(10, 2), default=10)
    reorder_quantity = db.Column(db.Numeric(10, 2), default=50)
    
    # Physical
    weight = db.Column(db.Numeric(10, 3), default=0)
    weight_unit = db.Column(db.String(10), default='kg')
    dimensions = db.Column(db.String(50))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Expiry
    expiry_date = db.Column(db.Date)
    batch_number = db.Column(db.String(100))
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    images = db.relationship('ProductImage', backref='product', cascade='all, delete-orphan', lazy='dynamic')
    variants = db.relationship('ProductVariant', backref='product', cascade='all, delete-orphan', lazy='dynamic')
    inventory_items = db.relationship('Inventory', backref='product', lazy='dynamic')
    
    def get_final_price(self, quantity=1):
        price = float(self.selling_price)
        if self.discount_type == 'percentage' and self.discount_value:
            price = price * (1 - float(self.discount_value) / 100)
        elif self.discount_type == 'fixed' and self.discount_value:
            price = max(0, price - float(self.discount_value))
        return round(price * quantity, 2)
    
    def get_stock_quantity(self):
        from .inventory import Inventory
        total = db.session.query(db.func.sum(Inventory.quantity)).filter_by(product_id=self.id).scalar()
        return float(total) if total else 0
    
    def get_stock_status(self):
        stock = self.get_stock_quantity()
        if stock <= 0:
            return 'out_of_stock'
        elif stock <= float(self.reorder_level):
            return 'low_stock'
        return 'in_stock'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'barcode': self.barcode,
            'qr_code': self.qr_code,
            'description': self.description,
            'short_description': self.short_description,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'category_color': self.category.color if self.category else None,
            'tags': self.tags,
            'brand': self.brand,
            'unit_id': self.unit_id,
            'unit_name': self.unit.name if self.unit else None,
            'cost_price': float(self.cost_price) if self.cost_price else 0,
            'selling_price': float(self.selling_price) if self.selling_price else 0,
            'mrp': float(self.mrp) if self.mrp else 0,
            'wholesale_price': float(self.wholesale_price) if self.wholesale_price else 0,
            'dealer_price': float(self.dealer_price) if self.dealer_price else 0,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0,
            'tax_inclusive': self.tax_inclusive,
            'hsn_code': self.hsn_code,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value) if self.discount_value else 0,
            'track_inventory': self.track_inventory,
            'reorder_level': float(self.reorder_level) if self.reorder_level else 0,
            'reorder_quantity': float(self.reorder_quantity) if self.reorder_quantity else 0,
            'weight': float(self.weight) if self.weight else 0,
            'weight_unit': self.weight_unit,
            'dimensions': self.dimensions,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'batch_number': self.batch_number,
            'stock_quantity': self.get_stock_quantity(),
            'stock_status': self.get_stock_status(),
            'final_price': self.get_final_price(),
            'images': [img.to_dict() for img in self.images],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ProductVariant(db.Model):
    """Product variant for products with options"""
    __tablename__ = 'product_variants'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    barcode = db.Column(db.String(100), unique=True, index=True)
    
    cost_price = db.Column(db.Numeric(15, 4), default=0)
    selling_price = db.Column(db.Numeric(15, 4), default=0)
    mrp = db.Column(db.Numeric(15, 4), default=0)
    
    option1 = db.Column(db.String(100))
    option2 = db.Column(db.String(100))
    option3 = db.Column(db.String(100))
    
    quantity = db.Column(db.Numeric(10, 2), default=0)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'name': self.name,
            'sku': self.sku,
            'barcode': self.barcode,
            'cost_price': float(self.cost_price) if self.cost_price else 0,
            'selling_price': float(self.selling_price) if self.selling_price else 0,
            'mrp': float(self.mrp) if self.mrp else 0,
            'option1': self.option1,
            'option2': self.option2,
            'option3': self.option3,
            'quantity': float(self.quantity) if self.quantity else 0,
            'is_active': self.is_active
        }


class ProductImage(db.Model):
    """Product image model"""
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    is_primary = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'is_primary': self.is_primary,
            'sort_order': self.sort_order,
            'url': f'/static/uploads/{self.filename}' if self.filename else None
        }