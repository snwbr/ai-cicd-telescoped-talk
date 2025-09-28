import re
from typing import List, Optional, Dict, Any
from datetime import datetime

def button_label(base: str) -> str:
    """Convert button text to uppercase"""
    return str(base).upper()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_phone(phone: str) -> str:
    """Format phone number"""
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return original if can't format

def sanitize_input(text: str, max_length: int = 100) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

def generate_form_id(prefix: str = "form") -> str:
    """Generate unique form ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{prefix}_{timestamp}"

def validate_form_data(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, str]:
    """Validate form data and return errors"""
    errors = {}
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors[field] = f"{field} is required"
    
    # Email validation
    if 'email' in data and data['email']:
        if not validate_email(data['email']):
            errors['email'] = "Invalid email format"
    
    # Phone validation
    if 'phone' in data and data['phone']:
        phone_digits = re.sub(r'\D', '', data['phone'])
        if len(phone_digits) < 10:
            errors['phone'] = "Phone number must have at least 10 digits"
    
    return errors

def create_button_config(text: str, style: str = "primary", disabled: bool = False) -> Dict[str, Any]:
    """Create button configuration"""
    return {
        "text": button_label(text),
        "style": style,
        "disabled": disabled,
        "id": generate_form_id("btn")
    }

def format_user_display_name(first_name: str, last_name: str) -> str:
    """Format user display name"""
    if not first_name and not last_name:
        return "Anonymous User"
    
    first = first_name.strip() if first_name else ""
    last = last_name.strip() if last_name else ""
    
    if first and last:
        return f"{first} {last}"
    elif first:
        return first
    else:
        return last

def validate_password_ui(password: str) -> Dict[str, Any]:
    """Validate password for UI display"""
    result = {
        "valid": True,
        "errors": [],
        "strength": "weak"
    }
    
    if len(password) < 8:
        result["errors"].append("Password must be at least 8 characters")
        result["valid"] = False
    
    if not re.search(r'[A-Z]', password):
        result["errors"].append("Password must contain uppercase letter")
        result["valid"] = False
    
    if not re.search(r'[a-z]', password):
        result["errors"].append("Password must contain lowercase letter")
        result["valid"] = False
    
    if not re.search(r'\d', password):
        result["errors"].append("Password must contain a number")
        result["valid"] = False
    
    # Calculate strength
    if len(password) >= 12 and len(result["errors"]) == 0:
        result["strength"] = "strong"
    elif len(password) >= 8 and len(result["errors"]) <= 1:
        result["strength"] = "medium"
    
    return result

def create_notification(message: str, level: str = "info") -> Dict[str, str]:
    """Create notification object"""
    return {
        "message": sanitize_input(message),
        "level": level,
        "timestamp": datetime.now().isoformat(),
        "id": generate_form_id("notif")
    }
