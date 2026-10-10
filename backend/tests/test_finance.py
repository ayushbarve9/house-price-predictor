"""Unit tests for finance.py — verified against SBI EMI calculator and RBI LTV rules."""

import math
from backend.finance import compute_emi, get_ltv, compute_stamp_duty, compute_gst, cost_breakdown


class TestGetLtv:
    def test_below_30l(self):
        assert get_ltv(2_500_000) == 0.90

    def test_exactly_30l(self):
        assert get_ltv(3_000_000) == 0.90

    def test_between_30l_and_75l(self):
        assert get_ltv(5_000_000) == 0.80

    def test_exactly_75l(self):
        assert get_ltv(7_500_000) == 0.80

    def test_above_75l(self):
        assert get_ltv(10_000_000) == 0.75

    def test_very_large_loan(self):
        assert get_ltv(100_000_000) == 0.75


class TestComputeEmi:
    def test_standard_case(self):
        # ₹50L loan, 8.5% p.a., 20 years → verified against SBI EMI calculator
        emi = compute_emi(5_000_000, 8.5, 20)
        assert math.isclose(emi, 43_391.0, rel_tol=1e-3), f"Got {emi:.2f}"

    def test_zero_interest(self):
        emi = compute_emi(1_200_000, 0, 10)
        assert math.isclose(emi, 10_000.0, rel_tol=1e-9)

    def test_short_tenure(self):
        emi = compute_emi(1_000_000, 9.0, 5)
        # 5 year, 9% → approx ₹20,758/mo
        assert 20_000 < emi < 22_000, f"Out of expected range: {emi:.2f}"


class TestComputeStampDuty:
    def test_bengaluru_rate(self):
        duty = compute_stamp_duty("Bengaluru", 5_000_000)
        assert math.isclose(duty, 325_000.0, rel_tol=1e-9)  # 6.5%

    def test_unknown_city_uses_default(self):
        duty_default = compute_stamp_duty("Unknown City", 1_000_000)
        duty_bengaluru = compute_stamp_duty("Bengaluru", 1_000_000)
        assert duty_default == duty_bengaluru  # both use 6.5%


class TestComputeGst:
    def test_ready_to_move_no_gst(self):
        assert compute_gst(10_000_000, is_under_construction=False) == 0.0

    def test_under_construction_above_threshold(self):
        gst = compute_gst(10_000_000, is_under_construction=True)
        assert math.isclose(gst, 500_000.0, rel_tol=1e-9)  # 5%

    def test_affordable_under_construction(self):
        gst = compute_gst(4_000_000, is_under_construction=True)
        assert math.isclose(gst, 40_000.0, rel_tol=1e-9)  # 1%


class TestCostBreakdown:
    def test_returns_all_keys(self):
        result = cost_breakdown("Bengaluru", 5_000_000, 20.0, 8.5, 20, False)
        for key in ("property_value", "down_payment", "loan_amount", "ltv_ratio",
                    "stamp_duty", "gst", "total_acquisition_cost", "monthly_emi"):
            assert key in result, f"Missing key: {key}"

    def test_ltv_cap_enforced(self):
        # 1% down on a large property should be capped by RBI LTV rule
        result = cost_breakdown("Bengaluru", 10_000_000, 1.0, 8.5, 20, False)
        assert result["ltv_ratio"] <= 0.75 + 1e-9
