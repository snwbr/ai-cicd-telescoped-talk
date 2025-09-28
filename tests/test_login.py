from app.login import authenticate

def test_login_success():
    assert authenticate("admin", "secret") is True

def test_login_failure_wrong_pass():
    assert authenticate("admin", "bad") is False
