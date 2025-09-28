import math
from app.payment import apply_discount

def test_payment_discount_10pct():
    assert apply_discount(200, 10) == 180.0

def test_payment_discount_rounding():
    # check floating math around discounts
    val = apply_discount(99.99, 15)
    assert math.isclose(val, 84.9915, rel_tol=1e-6)
