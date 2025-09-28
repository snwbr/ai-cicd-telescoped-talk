from app.ui import (
    button_label, validate_email, format_phone, sanitize_input,
    generate_form_id, validate_form_data, create_button_config,
    format_user_display_name, validate_password_ui, create_notification
)

def test_ui_button_label_caps():
    assert button_label("click") == "CLICK"

def test_validate_email():
    assert validate_email("test@example.com") is True
    assert validate_email("user.name+tag@domain.co.uk") is True
    assert validate_email("invalid-email") is False
    assert validate_email("@domain.com") is False
    assert validate_email("user@") is False

def test_format_phone():
    assert format_phone("1234567890") == "(123) 456-7890"
    assert format_phone("11234567890") == "+1 (123) 456-7890"
    assert format_phone("123-456-7890") == "(123) 456-7890"
    assert format_phone("invalid") == "invalid"  # Returns original if can't format

def test_sanitize_input():
    assert sanitize_input("normal text") == "normal text"
    assert sanitize_input("<script>alert('xss')</script>") == "scriptalert(xss)/script"
    assert sanitize_input("") == ""
    assert sanitize_input("a" * 150) == "a" * 100  # Truncated to max_length

def test_generate_form_id():
    id1 = generate_form_id("test")
    id2 = generate_form_id("test")
    assert id1.startswith("test_")
    assert id2.startswith("test_")
    assert id1 != id2  # Should be unique

def test_validate_form_data():
    # Valid data
    valid_data = {"name": "John", "email": "john@example.com", "phone": "1234567890"}
    errors = validate_form_data(valid_data, ["name", "email"])
    assert len(errors) == 0
    
    # Missing required field
    invalid_data = {"name": "John"}
    errors = validate_form_data(invalid_data, ["name", "email"])
    assert "email" in errors
    
    # Invalid email
    invalid_email_data = {"name": "John", "email": "invalid-email"}
    errors = validate_form_data(invalid_email_data, ["name", "email"])
    assert "email" in errors

def test_create_button_config():
    config = create_button_config("Submit", "primary", False)
    assert config["text"] == "SUBMIT"
    assert config["style"] == "primary"
    assert config["disabled"] is False
    assert "id" in config

def test_format_user_display_name():
    assert format_user_display_name("John", "Doe") == "John Doe"
    assert format_user_display_name("John", "") == "John"
    assert format_user_display_name("", "Doe") == "Doe"
    assert format_user_display_name("", "") == "Anonymous User"

def test_validate_password_ui():
    # Strong password
    result = validate_password_ui("StrongPass123")
    assert result["valid"] is True
    assert result["strength"] == "strong"
    
    # Weak password
    result = validate_password_ui("weak")
    assert result["valid"] is False
    assert result["strength"] == "weak"
    assert len(result["errors"]) > 0
    
    # Medium password
    result = validate_password_ui("MediumPass1")
    assert result["strength"] in ["medium", "strong"]

def test_create_notification():
    notification = create_notification("Test message", "info")
    assert notification["message"] == "Test message"
    assert notification["level"] == "info"
    assert "timestamp" in notification
    assert "id" in notification
