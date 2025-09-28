from app.login import (
    authenticate, get_user_role, is_admin, get_user_info, 
    validate_password_strength, hash_password
)

def test_login_success():
    assert authenticate("admin", "secret") is True

def test_login_failure_wrong_pass():
    assert authenticate("admin", "bad") is False

def test_login_nonexistent_user():
    assert authenticate("nonexistent", "password") is False

def test_get_user_role():
    assert get_user_role("admin") == "admin"
    assert get_user_role("user") == "user"
    assert get_user_role("guest") == "guest"
    assert get_user_role("nonexistent") is None

def test_is_admin():
    assert is_admin("admin") is True
    assert is_admin("user") is False
    assert is_admin("guest") is False
    assert is_admin("nonexistent") is False

def test_get_user_info():
    info = get_user_info("admin")
    assert info is not None
    assert info["role"] == "admin"
    assert "password" not in info  # Password should not be exposed
    
    assert get_user_info("nonexistent") is None

def test_validate_password_strength():
    assert validate_password_strength("Password123") is True
    assert validate_password_strength("Password1") is True
    assert validate_password_strength("short") is False
    assert validate_password_strength("nouppercase123") is False
    assert validate_password_strength("NOLOWERCASE123") is False
    assert validate_password_strength("NoNumbers") is False

def test_hash_password():
    hash1 = hash_password("test")
    hash2 = hash_password("test")
    hash3 = hash_password("different")
    
    assert hash1 == hash2  # Same input should produce same hash
    assert hash1 != hash3  # Different input should produce different hash
    assert len(hash1) == 64  # SHA-256 produces 64 character hex string
