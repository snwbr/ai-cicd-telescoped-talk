import hashlib
import time
from typing import Optional, Dict

# Simple in-memory user store for demo
USERS = {
    "admin": {"password": "2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b", "role": "admin", "last_login": None},  # "secret"
    "user": {"password": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f", "role": "user", "last_login": None},   # "password"
    "guest2": {"password": "356a192b7913b04c54574d18c28d46e6395428ab", "role": "guest", "last_login": None}  # "hello"
}

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(user: str, password: str) -> bool:
    """Authenticate user with password"""
    if user not in USERS:
        return False
    
    hashed_input = hash_password(password)
    stored_hash = USERS[user]["password"]
    
    if hashed_input == stored_hash:
        USERS[user]["last_login"] = time.time()
        return True
    return False

def get_user_role(user: str) -> Optional[str]:
    """Get user role if user exists"""
    return USERS.get(user, {}).get("role")

def is_admin(user: str) -> bool:
    """Check if user has admin privileges"""
    return get_user_role(user) == "admin"

def get_user_info(user: str) -> Optional[Dict]:
    """Get user information"""
    if user not in USERS:
        return None
    
    user_data = USERS[user].copy()
    user_data.pop("password")  # Don't expose password hash
    return user_data

def validate_password_strength(password: str) -> bool:
    """Basic password strength validation"""
    if len(password) < 6:
        return False
    if not any(c.isalpha() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    return True
