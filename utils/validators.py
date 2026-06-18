"""Validation utility functions"""
import re
from datetime import datetime


def validate_email(email):
    """Validate email address format"""
    if not email:
        return False, "Email is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, "Valid email"


def validate_phone(phone, country='IN'):
    """Validate phone number"""
    if not phone:
        return False, "Phone number is required"
    
    # Remove all non-digit characters
    cleaned = ''.join(c for c in phone if c.isdigit())
    
    if country == 'IN':
        # Indian phone numbers: 10 digits
        if len(cleaned) < 10:
            return False, "Phone number must be at least 10 digits"
        if len(cleaned) > 12:
            return False, "Phone number must not exceed 12 digits"
    else:
        if len(cleaned) < 7:
            return False, "Phone number must be at least 7 digits"
        if len(cleaned) > 15:
            return False, "Phone number must not exceed 15 digits"
    
    return True, "Valid phone number"


def validate_required(value, field_name="Field"):
    """Validate required field"""
    if value is None or (isinstance(value, str) and not value.strip()):
        return False, f"{field_name} is required"
    return True, "Valid"


def validate_length(value, min_length=None, max_length=None, field_name="Field"):
    """Validate string length"""
    if value is None:
        return True, "Valid"
    
    if not isinstance(value, str):
        value = str(value)
    
    if min_length and len(value) < min_length:
        return False, f"{field_name} must be at least {min_length} characters"
    
    if max_length and len(value) > max_length:
        return False, f"{field_name} must not exceed {max_length} characters"
    
    return True, "Valid"


def validate_number(value, min_value=None, max_value=None, field_name="Field", allow_zero=True):
    """Validate numeric value"""
    if value is None or value == '':
        return False, f"{field_name} is required"
    
    try:
        num = float(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number"
    
    if not allow_zero and num == 0:
        return False, f"{field_name} cannot be zero"
    
    if min_value is not None and num < min_value:
        return False, f"{field_name} must be at least {min_value}"
    
    if max_value is not None and num > max_value:
        return False, f"{field_name} must not exceed {max_value}"
    
    return True, "Valid"


def validate_positive_integer(value, field_name="Field"):
    """Validate positive integer"""
    if value is None or value == '':
        return False, f"{field_name} is required"
    
    try:
        num = int(value)
        if num <= 0:
            return False, f"{field_name} must be a positive integer"
        return True, "Valid"
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid integer"


def validate_gst_number(gst):
    """Validate GST number (India)"""
    if not gst:
        return True, "Valid"  # GST is optional
    
    # GST format: 22AAAAA0000A1Z5 (15 characters)
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    if not re.match(pattern, gst):
        return False, "Invalid GST number format. Expected: 22AAAAA0000A1Z5"
    
    return True, "Valid"


def validate_pan_number(pan):
    """Validate PAN number (India)"""
    if not pan:
        return True, "Valid"  # PAN is optional
    
    # PAN format: ABCDE1234F (10 characters)
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    if not re.match(pattern, pan):
        return False, "Invalid PAN number format. Expected: ABCDE1234F"
    
    return True, "Valid"


def validate_date(date_str, format='%Y-%m-%d', field_name="Date"):
    """Validate date string"""
    if not date_str:
        return True, "Valid"  # Date is optional
    
    try:
        datetime.strptime(date_str, format)
        return True, "Valid"
    except ValueError:
        return False, f"{field_name} must be in format {format}"


def validate_password(password, min_length=8):
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    # Check for at least one uppercase, one lowercase, one digit
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    
    return True, "Valid"


def validate_username(username, min_length=3, max_length=80):
    """Validate username"""
    if not username:
        return False, "Username is required"
    
    if len(username) < min_length:
        return False, f"Username must be at least {min_length} characters"
    
    if len(username) > max_length:
        return False, f"Username must not exceed {max_length} characters"
    
    # Only alphanumeric, underscore, and hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, "Valid"


def validate_sku(sku):
    """Validate SKU format"""
    if not sku:
        return False, "SKU is required"
    
    if len(sku) < 2:
        return False, "SKU must be at least 2 characters"
    
    if len(sku) > 100:
        return False, "SKU must not exceed 100 characters"
    
    # Allow alphanumeric, hyphen, underscore, and period
    if not re.match(r'^[a-zA-Z0-9._-]+$', sku):
        return False, "SKU can only contain letters, numbers, periods, underscores, and hyphens"
    
    return True, "Valid"


def validate_barcode(barcode_str):
    """Validate barcode format"""
    if not barcode_str:
        return True, "Valid"  # Barcode is optional
    
    if len(barcode_str) < 8:
        return False, "Barcode must be at least 8 characters"
    
    if len(barcode_str) > 100:
        return False, "Barcode must not exceed 100 characters"
    
    # Allow alphanumeric
    if not re.match(r'^[a-zA-Z0-9]+$', barcode_str):
        return False, "Barcode can only contain letters and numbers"
    
    return True, "Valid"


def validate_url(url):
    """Validate URL format"""
    if not url:
        return True, "Valid"  # URL is optional
    
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    if not re.match(pattern, url):
        return False, "Invalid URL format"
    
    return True, "Valid"


def validate_json(data):
    """Validate if data is valid JSON-serializable"""
    import json
    try:
        json.dumps(data)
        return True, "Valid"
    except (TypeError, ValueError):
        return False, "Invalid JSON data"


def validate_file_size(file_size, max_size_mb=16):
    """Validate file size"""
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"File size must not exceed {max_size_mb}MB"
    return True, "Valid"


def validate_currency_code(code):
    """Validate currency code"""
    if not code:
        return False, "Currency code is required"
    
    if len(code) != 3:
        return False, "Currency code must be 3 characters (ISO 4217)"
    
    if not code.isalpha():
        return False, "Currency code must contain only letters"
    
    return True, "Valid"


def run_validations(validations):
    """Run multiple validations and return combined result"""
    errors = {}
    
    for field_name, (is_valid, message) in validations.items():
        if not is_valid:
            errors[field_name] = message
    
    if errors:
        return False, errors
    
    return True, {}
