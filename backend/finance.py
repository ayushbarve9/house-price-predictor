"""Finance logic for GrihaValue.

All constants are imported from backend.config — nothing is hardcoded here.
"""

from backend.config import (
    LTV_TIERS,
    STAMP_DUTY_BY_CITY,
    STAMP_DUTY_DEFAULT,
    GST_UNDER_CONSTRUCTION_RATE,
    GST_AFFORDABLE_RATE,
    GST_AFFORDABLE_THRESHOLD,
)


def get_ltv(loan_amount: float) -> float:
    """Return the RBI-mandated maximum LTV for a given loan amount.

    Tiers from backend/config.py:
      ≤ ₹30L  → 90%
      ≤ ₹75L  → 80%
      > ₹75L  → 75%
    """
    for threshold, ltv in LTV_TIERS:
        if loan_amount <= threshold:
            return ltv
    return LTV_TIERS[-1][1]


def compute_emi(principal: float, annual_rate_pct: float, tenure_years: int) -> float:
    """Standard reducing-balance EMI formula.

    Args:
        principal:       loan principal in INR
        annual_rate_pct: annual interest rate as a percentage (e.g. 8.5)
        tenure_years:    loan duration in years

    Returns:
        Monthly EMI in INR.
    """
    r = annual_rate_pct / 12 / 100
    n = tenure_years * 12
    if r == 0 or n == 0:
        return principal / n if n else 0.0
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def compute_stamp_duty(city: str, property_value: float) -> float:
    """Return estimated stamp duty + registration amount for a city.

    Rates are documented constants in backend/config.py.
    """
    rate = STAMP_DUTY_BY_CITY.get(city, STAMP_DUTY_DEFAULT)
    return property_value * rate


def compute_gst(property_value: float, is_under_construction: bool) -> float:
    """Return GST applicable on an under-construction property.

    Ready-to-move properties attract no GST (GST Council 2019 clarification).
    Source: GST Council notification 11/2019-CT(Rate)
    """
    if not is_under_construction:
        return 0.0
    if property_value < GST_AFFORDABLE_THRESHOLD:
        return property_value * GST_AFFORDABLE_RATE
    return property_value * GST_UNDER_CONSTRUCTION_RATE


def cost_breakdown(
    city: str,
    property_value: float,
    down_payment_pct: float,
    annual_rate_pct: float,
    tenure_years: int,
    is_under_construction: bool,
) -> dict:
    """Compute the full acquisition cost breakdown for a property.

    Returns a typed dict suitable for JSON serialisation.
    """
    down_payment = property_value * (down_payment_pct / 100)
    loan_amount = property_value - down_payment

    # Enforce RBI LTV cap
    max_ltv = get_ltv(loan_amount)
    max_loan = property_value * max_ltv
    if loan_amount > max_loan:
        loan_amount = max_loan
        down_payment = property_value - loan_amount

    stamp_duty = compute_stamp_duty(city, property_value)
    gst = compute_gst(property_value, is_under_construction)
    monthly_emi = compute_emi(loan_amount, annual_rate_pct, tenure_years)
    total_acquisition = property_value + stamp_duty + gst

    return {
        "property_value": property_value,
        "down_payment": down_payment,
        "loan_amount": loan_amount,
        "ltv_ratio": loan_amount / property_value,
        "stamp_duty": stamp_duty,
        "gst": gst,
        "total_acquisition_cost": total_acquisition,
        "monthly_emi": monthly_emi,
    }
