"""Supplier Management Service"""
from models import db
from models.supplier import Supplier, SupplierLedger
from utils.validators import validate_required


class SupplierService:
    """Service for supplier management"""
    
    @staticmethod
    def get_all_suppliers(page=1, per_page=20, search=None, supplier_type=None, is_active=None):
        """Get all suppliers with filters"""
        query = Supplier.query
        
        if search:
            query = query.filter(
                db.or_(
                    Supplier.name.ilike(f'%{search}%'),
                    Supplier.company_name.ilike(f'%{search}%'),
                    Supplier.email.ilike(f'%{search}%'),
                    Supplier.phone.ilike(f'%{search}%'),
                    Supplier.supplier_code.ilike(f'%{search}%')
                )
            )
        
        if supplier_type:
            query = query.filter(Supplier.supplier_type == supplier_type)
        if is_active is not None:
            query = query.filter(Supplier.is_active == is_active)
        
        return query.order_by(Supplier.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_supplier_by_id(supplier_id):
        """Get supplier by ID"""
        return Supplier.query.get(supplier_id)
    
    @staticmethod
    def create_supplier(data, created_by=None):
        """Create a new supplier"""
        is_valid, message = validate_required(data.get('name'), "Supplier name")
        if not is_valid:
            return None, message
        
        supplier_code = data.get('supplier_code')
        if not supplier_code:
            last = Supplier.query.order_by(Supplier.id.desc()).first()
            next_id = (last.id + 1) if last else 1
            supplier_code = f"SUP{next_id:05d}"
        
        if Supplier.query.filter_by(supplier_code=supplier_code).first():
            return None, "Supplier code already exists"
        
        supplier = Supplier(
            supplier_code=supplier_code,
            name=data['name'],
            company_name=data.get('company_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            mobile=data.get('mobile'),
            fax=data.get('fax'),
            website=data.get('website'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            country=data.get('country'),
            postal_code=data.get('postal_code'),
            gst_number=data.get('gst_number'),
            tax_number=data.get('tax_number'),
            pan_number=data.get('pan_number'),
            cin_number=data.get('cin_number'),
            credit_limit=data.get('credit_limit', 0),
            credit_days=data.get('credit_days', 0),
            bank_name=data.get('bank_name'),
            bank_account=data.get('bank_account'),
            bank_ifsc=data.get('bank_ifsc'),
            bank_branch=data.get('bank_branch'),
            upi_id=data.get('upi_id'),
            contact_person=data.get('contact_person'),
            contact_phone=data.get('contact_phone'),
            contact_email=data.get('contact_email'),
            contact_designation=data.get('contact_designation'),
            supplier_type=data.get('supplier_type', 'regular'),
            category=data.get('category'),
            lead_time_days=data.get('lead_time_days', 0),
            minimum_order_value=data.get('minimum_order_value', 0),
            notes=data.get('notes'),
            is_active=data.get('is_active', True),
            is_preferred=data.get('is_preferred', False),
            created_by=created_by
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        return supplier, "Supplier created successfully"
    
    @staticmethod
    def update_supplier(supplier_id, data):
        """Update supplier"""
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return None, "Supplier not found"
        
        updatable_fields = [
            'name', 'company_name', 'email', 'phone', 'mobile', 'fax', 'website',
            'address', 'city', 'state', 'country', 'postal_code',
            'gst_number', 'tax_number', 'pan_number', 'cin_number',
            'credit_limit', 'credit_days',
            'bank_name', 'bank_account', 'bank_ifsc', 'bank_branch', 'upi_id',
            'contact_person', 'contact_phone', 'contact_email', 'contact_designation',
            'supplier_type', 'category', 'lead_time_days', 'minimum_order_value',
            'notes', 'is_active', 'is_preferred'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(supplier, field, data[field])
        
        db.session.commit()
        return supplier, "Supplier updated successfully"
    
    @staticmethod
    def delete_supplier(supplier_id):
        """Delete supplier"""
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return False, "Supplier not found"
        
        db.session.delete(supplier)
        db.session.commit()
        return True, "Supplier deleted successfully"
    
    @staticmethod
    def get_supplier_ledger(supplier_id, page=1, per_page=20):
        """Get supplier ledger"""
        return SupplierLedger.query.filter_by(supplier_id=supplier_id)\
            .order_by(SupplierLedger.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_supplier_stats():
        """Get supplier statistics"""
        total = Supplier.query.count()
        active = Supplier.query.filter_by(is_active=True).count()
        preferred = Supplier.query.filter_by(is_preferred=True).count()
        
        return {
            'total': total,
            'active': active,
            'preferred': preferred
        }
