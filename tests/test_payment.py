import math
import os
from app.payment import (
    apply_discount, calculate_tax, calculate_total_with_tax,
    apply_compound_discount, calculate_interest, calculate_compound_interest,
    round_to_currency, format_currency, validate_payment_amount,
    calculate_installment, calculate_discount_breakdown
)

def test_payment_discount_10pct():
    assert apply_discount(200, 10) == 180.0

def test_payment_discount_rounding():
    # check floating math around discounts
    val = apply_discount(99.99, 15)
    assert math.isclose(val, 84.9915, rel_tol=1e-6)

def test_calculate_tax():
    assert calculate_tax(100, 0.21) == 21.0
    assert calculate_tax(50, 0.10) == 5.0

def test_calculate_total_with_tax():
    assert calculate_total_with_tax(100, 0.21) == 121.0
    assert calculate_total_with_tax(50, 0.10) == 55.0

def test_apply_compound_discount():
    discounts = [10, 5]  # 10% then 5%
    result = apply_compound_discount(100, discounts)
    # 100 -> 90 (10% off) -> 85.5 (5% off remaining)
    assert math.isclose(result, 85.5, rel_tol=1e-6)

def test_calculate_interest():
    assert calculate_interest(1000, 5, 2) == 100.0  # 1000 * 5% * 2 years
    assert calculate_interest(500, 10, 1) == 50.0

def test_calculate_compound_interest():
    # Test with simple case
    result = calculate_compound_interest(1000, 5, 1, 12)  # Monthly compounding
    assert result > 50  # Should be more than simple interest
    assert result < 60  # Should be reasonable

def test_round_to_currency():
    assert round_to_currency(123.456) == 123.46
    assert round_to_currency(123.454) == 123.45
    assert round_to_currency(123.455) == 123.46

def test_format_currency():
    assert format_currency(123.45) == "EUR 123.45"
    assert format_currency(1000.0) == "EUR 1000.00"

def test_validate_payment_amount():
    assert validate_payment_amount(100) is True
    assert validate_payment_amount(0.01) is True
    assert validate_payment_amount(1000000) is True
    assert validate_payment_amount(0) is False
    assert validate_payment_amount(-100) is False
    assert validate_payment_amount(1000001) is False

def test_calculate_installment():
    # Test zero interest case
    assert calculate_installment(1200, 12, 0) == 100.0
    
    # Test normal case
    installment = calculate_installment(1000, 12, 0.05)
    assert installment > 80  # Should be reasonable monthly payment
    assert installment < 100  # Should be less than principal/12

def test_calculate_discount_breakdown():
    amount, percentage = calculate_discount_breakdown(100, 80)
    assert amount == 20.0
    assert percentage == 20.0
    
    amount, percentage = calculate_discount_breakdown(200, 150)
    assert amount == 50.0
    assert percentage == 25.0

def test_payment_demo_bug():
    # Test the intentional demo bug
    os.environ["BREAK_PAYMENT"] = "1"
    try:
        # This should trigger the bug
        result = apply_discount(200, 10)
        assert result == 190  # Wrong calculation: 200 - 10 instead of 200 * 0.9
    finally:
        # Clean up
        if "BREAK_PAYMENT" in os.environ:
            del os.environ["BREAK_PAYMENT"]
