"""
All financial and business constants for GrihaValue.

Every constant here has a source comment and date. Do NOT move these
into route handlers, the model loader, or the frontend.
"""

# ---------------------------------------------------------------------------
# LTV Tiers (Loan-to-Value caps)
# Source: RBI Master Direction – Housing Finance (updated 2023)
# https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx?id=12513
# Retrieved: October 2026
# Rule: Apply the cap for the loan amount bracket, not the property value.
# ---------------------------------------------------------------------------
LTV_TIERS: list[tuple[float, float]] = [
    (3_000_000, 0.90),    # Loan up to ₹30L → 90% LTV
    (7_500_000, 0.80),    # Loan ₹30L–75L  → 80% LTV
    (float("inf"), 0.75), # Loan above ₹75L → 75% LTV
]

# ---------------------------------------------------------------------------
# Home Loan Interest Rate Bounds (% per annum)
# Source: SBI and HDFC published floating-rate slabs, October 2026
# ---------------------------------------------------------------------------
INTEREST_RATE_DEFAULT_PCT: float = 8.5
INTEREST_RATE_MIN_PCT: float = 6.5
INTEREST_RATE_MAX_PCT: float = 14.0

# ---------------------------------------------------------------------------
# Loan Tenure Bounds (years)
# ---------------------------------------------------------------------------
TENURE_DEFAULT_YRS: int = 20
TENURE_MIN_YRS: int = 5
TENURE_MAX_YRS: int = 30

# ---------------------------------------------------------------------------
# Stamp Duty & Registration (as % of property value, per state)
# Source: respective state government schedules, October 2026
# Males pay full rate; females/joint often get 1–2% rebate (not modelled here).
# ---------------------------------------------------------------------------
STAMP_DUTY_BY_CITY: dict[str, float] = {
    "Bengaluru":    0.065,  # Karnataka: 5% SD + 1% reg + 0.5% other
    "Mumbai (MMR)": 0.060,  # Maharashtra: 5% SD + 1% reg (municipal premium applies)
    "Delhi NCR":    0.060,  # Delhi: 6% (male) / 4% (female) + 1% reg — using male rate
    "Hyderabad":    0.075,  # Telangana: 4% SD + 0.5% reg + 1.5% transfer duty + other
    "Pune":         0.060,  # Maharashtra (same as Mumbai bracket)
    "Chennai":      0.070,  # Tamil Nadu: 7% SD + 4% reg → capped; using blended ~7%
    "Kolkata":      0.060,  # West Bengal: 5–7% SD + 1% reg; using mid estimate
}
STAMP_DUTY_DEFAULT: float = 0.065  # Fallback if city not in map

# ---------------------------------------------------------------------------
# GST on Under-Construction Properties
# Source: GST Council notification 11/2019-CT(Rate), March 2019
# Retrieved: October 2026
# ---------------------------------------------------------------------------
GST_UNDER_CONSTRUCTION_RATE: float = 0.05   # 5% on property value
GST_AFFORDABLE_RATE: float = 0.01           # 1% for affordable housing (value < ₹45L)
GST_AFFORDABLE_THRESHOLD: float = 4_500_000 # ₹45 Lakhs

# ---------------------------------------------------------------------------
# Default city for UI (read by frontend via /api/meta)
# ---------------------------------------------------------------------------
DEFAULT_CITY: str = "Bengaluru"

# ---------------------------------------------------------------------------
# Model bundle path (relative to project root)
# ---------------------------------------------------------------------------
MODEL_BUNDLE_PATH: str = "models/grihavalue.joblib"
