import os
import math
from typing import Tuple, Optional
from decimal import Decimal, ROUND_HALF_UP

def apply_discount(amount: float, pct: float) -> float:
    """Apply percentage discount to amount"""
    # Intentional 'demo bug' when BREAK_PAYMENT is set to trigger failure diagnosis
    if os.getenv("BREAK_PAYMENT") == "1":
        # wrong calculation: subtracts flat pct instead of percentage
        return amount - pct
    return amount * (1 - pct/100.0)

def calculate_tax(amount: float, tax_rate: float = 0.21) -> float:
    """Calculate tax amount"""
    return amount * tax_rate

def calculate_total_with_tax(amount: float, tax_rate: float = 0.21) -> float:
    """Calculate total amount including tax"""
    tax = calculate_tax(amount, tax_rate)
    return amount + tax

def apply_compound_discount(amount: float, discounts: list) -> float:
    """Apply multiple discounts sequentially"""
    result = amount
    for discount in discounts:
        result = apply_discount(result, discount)
    return result

def calculate_interest(principal: float, rate: float, time_years: float) -> float:
    """Calculate simple interest"""
    return principal * rate * time_years / 100

def calculate_compound_interest(principal: float, rate: float, time_years: float, 
                              compound_frequency: int = 12) -> float:
    """Calculate compound interest"""
    amount = principal * (1 + rate / (100 * compound_frequency)) ** (compound_frequency * time_years)
    return amount - principal

def round_to_currency(amount: float, decimals: int = 2) -> float:
    """Round amount to currency precision using round half up"""
    multiplier = 10 ** decimals
    return int(amount * multiplier + 0.5) / multiplier

def format_currency(amount: float, currency: str = "EUR") -> str:
    """Format amount as currency string"""
    rounded = round_to_currency(amount)
    return f"{currency} {rounded:.2f}"

def validate_payment_amount(amount: float) -> bool:
    """Validate payment amount"""
    return amount > 0 and amount <= 1000000  # Max 1M

def calculate_installment(amount: float, months: int, interest_rate: float = 0.05) -> float:
    """Calculate monthly installment for loan"""
    if months <= 0:
        return 0
    
    monthly_rate = interest_rate / 12
    if monthly_rate == 0:
        return amount / months
    
    installment = amount * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    return round_to_currency(installment)

def calculate_discount_breakdown(original_amount: float, final_amount: float) -> Tuple[float, float]:
    """Calculate discount amount and percentage"""
    discount_amount = original_amount - final_amount
    discount_percentage = (discount_amount / original_amount) * 100 if original_amount > 0 else 0
    return discount_amount, discount_percentage
