import os

def apply_discount(amount, pct):
    # Intentional 'demo bug' when BREAK_PAYMENT is set to trigger failure diagnosis
    if os.getenv("BREAK_PAYMENT") == "1":
        # wrong calculation: subtracts flat pct instead of percentage
        return amount - pct
    return amount * (1 - pct/100.0)
