import unittest
import math
from config import FINANCE

def calculate_ltv_local(property_value: float) -> float:
    for threshold, ltv in FINANCE["ltv_tiers"]:
        if property_value <= threshold:
            return ltv
    return FINANCE["ltv_tiers"][-1][1]

def estimate_emi_local(principal: float, annual_rate_pct: float, years: int) -> float:
    r = annual_rate_pct / 12 / 100
    n = years * 12
    if r == 0:
        return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)

class TestMath(unittest.TestCase):
    def test_calculate_ltv(self):
        self.assertEqual(calculate_ltv_local(2_500_000), 0.90)
        self.assertEqual(calculate_ltv_local(3_000_000), 0.90)
        self.assertEqual(calculate_ltv_local(5_000_000), 0.80)
        self.assertEqual(calculate_ltv_local(7_500_000), 0.80)
        self.assertEqual(calculate_ltv_local(10_000_000), 0.75)

    def test_estimate_emi(self):
        emi = estimate_emi_local(100000, 8.5, 20)
        self.assertTrue(math.isclose(emi, 867.82, rel_tol=1e-3))
        
        emi_zero = estimate_emi_local(120000, 0, 10)
        self.assertEqual(emi_zero, 1000.0)

if __name__ == '__main__':
    unittest.main()
