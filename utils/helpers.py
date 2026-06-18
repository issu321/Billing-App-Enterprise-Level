"""Helper utility functions"""
import random
import string
import barcode
from barcode.writer import ImageWriter
import qrcode
from io import BytesIO
import base64
from datetime import datetime, timedelta
from flask import current_app


def format_currency(amount, currency_code=None):
    """Format amount with currency symbol"""
    if amount is None:
        amount = 0
    
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        amount = 0
    
    if currency_code is None:
        currency_code = current_app.config.get('DEFAULT_CURRENCY', 'INR')
    
    symbols = current_app.config.get('CURRENCY_SYMBOLS', {})
    symbol = symbols.get(currency_code, currency_code)
    
    return f"{symbol}{amount:,.2f}"


def format_date(date_obj, format_str=None):
    """Format date object to string"""
    if date_obj is None:
        return ''
    
    if format_str is None:
        format_str = '%Y-%m-%d'
    
    try:
        if isinstance(date_obj, str):
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        return date_obj.strftime(format_str)
    except (ValueError, AttributeError):
        return str(date_obj)


def format_datetime(datetime_obj, format_str=None):
    """Format datetime object to string"""
    if datetime_obj is None:
        return ''
    
    if format_str is None:
        format_str = '%Y-%m-%d %H:%M:%S'
    
    try:
        if isinstance(datetime_obj, str):
            datetime_obj = datetime.fromisoformat(datetime_obj.replace('Z', '+00:00'))
        return datetime_obj.strftime(format_str)
    except (ValueError, AttributeError):
        return str(datetime_obj)


def generate_code(prefix='REF', length=8):
    """Generate a random code with prefix"""
    timestamp = datetime.now().strftime('%y%m%d')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}-{timestamp}-{random_part}"


def generate_invoice_number(prefix='INV', last_number=None):
    """Generate sequential invoice number"""
    if last_number:
        next_number = last_number + 1
    else:
        next_number = 1
    
    timestamp = datetime.now().strftime('%Y%m%d')
    return f"{prefix}-{timestamp}-{next_number:06d}"


def generate_barcode(data, barcode_type='code128'):
    """Generate barcode image as base64 string"""
    try:
        if barcode_type == 'code128':
            code_class = barcode.get_barcode_class('code128')
        elif barcode_type == 'ean13':
            code_class = barcode.get_barcode_class('ean13')
        elif barcode_type == 'code39':
            code_class = barcode.get_barcode_class('code39')
        else:
            code_class = barcode.get_barcode_class('code128')
        
        # Create barcode
        rv = BytesIO()
        code = code_class(data, writer=ImageWriter())
        code.write(rv, options={
            'write_text': True,
            'module_height': 15,
            'module_width': 0.5,
            'font_size': 10,
        })
        rv.seek(0)
        
        # Convert to base64
        img_str = base64.b64encode(rv.read()).decode('utf-8')
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        return None


def generate_qr_code(data, size=10):
    """Generate QR code image as base64 string"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=size,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        return None


def generate_upi_qr(upi_id, name=None, amount=None, transaction_note=None):
    """Generate UPI payment QR code data"""
    # UPI URI format
    upi_data = f"upi://pay?pa={upi_id}"
    
    if name:
        upi_data += f"&pn={name.replace(' ', '%20')}"
    if amount:
        upi_data += f"&am={amount}"
    if transaction_note:
        upi_data += f"&tn={transaction_note.replace(' ', '%20')}"
    
    upi_data += "&cu=INR"
    
    return generate_qr_code(upi_data)


def get_date_range(period='today'):
    """Get start and end dates for a period"""
    now = datetime.now()
    
    if period == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'yesterday':
        start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start = (now - timedelta(days=7))
        end = now
    elif period == 'month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif period == 'last_month':
        last_month = now.replace(day=1) - timedelta(days=1)
        start = last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = last_month.replace(day=last_month.day, hour=23, minute=59, second=59)
    elif period == 'year':
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    
    return start, end


def truncate_string(text, max_length=50, suffix='...'):
    """Truncate string to max length"""
    if not text:
        return ''
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_divide(numerator, denominator, default=0):
    """Safe division with default value"""
    try:
        if denominator == 0 or denominator is None:
            return default
        return float(numerator) / float(denominator)
    except (TypeError, ValueError, ZeroDivisionError):
        return default


def calculate_percentage(value, total, decimal_places=2):
    """Calculate percentage safely"""
    if not total or total == 0:
        return 0
    try:
        return round((float(value) / float(total)) * 100, decimal_places)
    except (TypeError, ValueError):
        return 0


def parse_boolean(value):
    """Parse various boolean representations"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 't', 'y')
    return bool(value)


def clean_phone_number(phone):
    """Clean and format phone number"""
    if not phone:
        return ''
    # Remove all non-digit characters
    cleaned = ''.join(c for c in phone if c.isdigit())
    return cleaned


def generate_random_password(length=12):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(random.choice(characters) for _ in range(length))


def get_file_extension(filename):
    """Get file extension from filename"""
    if not filename:
        return ''
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if not filename:
        return False
    ext = get_file_extension(filename)
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
    return ext in allowed_extensions


def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def calculate_age(date_of_birth):
    """Calculate age from date of birth"""
    if not date_of_birth:
        return None
    today = datetime.now().date()
    if hasattr(date_of_birth, 'date'):
        date_of_birth = date_of_birth.date()
    age = today.year - date_of_birth.year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    return age


def slugify(text):
    """Convert text to slug"""
    if not text:
        return ''
    text = text.lower()
    text = ''.join(c if c.isalnum() or c == ' ' else '-' for c in text)
    text = '-'.join(text.split())
    return text
