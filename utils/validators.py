import re

def validate_address(address: str) -> bool:
    """
    Basic address validation.
    Returns True if address seems valid.
    """
    if not address or len(address.strip()) < 5:
        return False
    
    # Address should contain at least some alphanumeric characters
    if not re.search(r'[a-zA-Z0-9א-ת]', address):
        return False
    
    return True

def validate_phone_number(phone_number: str) -> bool:
    """
    Validate phone number format.
    Accepts formats like: +972501234567, whatsapp:+972501234567, etc.
    """
    if not phone_number:
        return False
    
    # Remove whatsapp: prefix if present
    cleaned = phone_number.replace('whatsapp:', '').replace('whatsapp', '')
    
    # Should start with + and contain digits
    if not re.match(r'^\+[1-9]\d{6,14}$', cleaned):
        return False
    
    return True

