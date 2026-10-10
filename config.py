# config.py

FINANCE = {
    "default_rate_pct": 8.5,
    "rate_min": 6.5,
    "rate_max": 12.0,
    "default_tenure_yrs": 20,
    "tenure_min": 5,
    "tenure_max": 30,
    "ltv_tiers": [
        (3_000_000, 0.90),
        (7_500_000, 0.80),
        (float("inf"), 0.75)
    ],
}
DEFAULT_CITY = "Bengaluru"
