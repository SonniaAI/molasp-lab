"""Pins for tools/w8_q0_sensitivity.py (tick 115, SON-5146).

All pinned values are exact-function outputs of the committed module; the
scenario rates and flag probabilities are deterministic arithmetic on
committed receipt counts (no simulation)."""

import math
import sys
import unittest

sys.path.insert(0, "tools")

from w8_q0_sensitivity import (  # noqa: E402
    ALPHA,
    DELTA_DESC,
    FAMILY_N,
    FAMILY_X,
    Q0,
    SHARE_REST,
    binom_cdf,
    critical_low,
    false_flag_rate,
    family_rate_under_decline,
    normal_power_one_sided,
    wilson95,
)


class TestQ0Facts(unittest.TestCase):
    def test_family_pool_receipt_counts(self):
        self.assertEqual((FAMILY_X, FAMILY_N), (1110, 1499))
        self.assertAlmostEqual(Q0, 0.7404937, places=6)

    def test_descriptive_gap_anchors(self):
        self.assertAlmostEqual(SHARE_REST, 0.7110844, places=6)
        self.assertAlmostEqual(DELTA_DESC, 0.0689156, places=6)

    def test_wilson_on_family_pool(self):
        lo, hi = wilson95(FAMILY_X, FAMILY_N)
        self.assertAlmostEqual(lo, 0.71771, places=4)
        self.assertAlmostEqual(hi, 0.76205, places=4)

    def test_first_window_only_composition(self):
        # arms 3/5/7 are the only contributors; each is full-n.
        self.assertEqual(375 + 370 + 365, FAMILY_X)
        self.assertEqual(500 + 500 + 499, FAMILY_N)


class TestDeclineScenarios(unittest.TestCase):
    def test_two_window_family_rate(self):
        rate = family_rate_under_decline(DELTA_DESC, 0.5)
        self.assertAlmostEqual(rate, 0.7060359, places=6)

    def test_ten_window_block_rate(self):
        rate = family_rate_under_decline(DELTA_DESC, 0.1)
        self.assertAlmostEqual(rate, 0.6784697, places=6)

    def test_half_effect_rate(self):
        rate = family_rate_under_decline(DELTA_DESC / 2.0, 0.5)
        self.assertAlmostEqual(rate, 0.7232648, places=6)

    def test_rejects_bad_weight(self):
        with self.assertRaises(ValueError):
            family_rate_under_decline(0.05, 0.0)


class TestLowGateCalibration(unittest.TestCase):
    def test_critical_value_717(self):
        self.assertEqual(critical_low(1000, Q0), 717)

    def test_calibration_level(self):
        # gate holds alpha at or below 0.05; one step up breaks it
        self.assertLessEqual(binom_cdf(717, 1000, Q0), ALPHA)
        self.assertGreater(binom_cdf(718, 1000, Q0), ALPHA)

    def test_false_flag_two_window_decline(self):
        rate = family_rate_under_decline(DELTA_DESC, 0.5)
        self.assertAlmostEqual(false_flag_rate(1000, rate, Q0), 0.7864,
                               places=3)

    def test_false_flag_half_effect(self):
        rate = family_rate_under_decline(DELTA_DESC / 2.0, 0.5)
        self.assertAlmostEqual(false_flag_rate(1000, rate, Q0), 0.3402,
                               places=3)

    def test_false_flag_ten_window_block(self):
        rate = family_rate_under_decline(DELTA_DESC, 0.1)
        self.assertAlmostEqual(false_flag_rate(1000, rate, Q0), 0.9962,
                               places=3)


class TestCensusPowerSensitivity(unittest.TestCase):
    def test_power_at_q0(self):
        self.assertAlmostEqual(normal_power_one_sided(0.02, 5000, Q0),
                               0.7377, places=3)

    def test_power_at_two_window_decline_rate(self):
        rate = family_rate_under_decline(DELTA_DESC, 0.5)
        self.assertAlmostEqual(normal_power_one_sided(0.02, 5000, rate),
                               0.7089, places=3)

    def test_power_shift_is_second_order(self):
        p_q0 = normal_power_one_sided(0.02, 5000, Q0)
        p_lo = normal_power_one_sided(
            0.02, 5000, family_rate_under_decline(DELTA_DESC, 0.1))
        self.assertLess(p_q0 - p_lo, 0.05)
        self.assertGreater(p_q0 - p_lo, 0.04)


class TestBinomialExactness(unittest.TestCase):
    def test_cdf_boundaries(self):
        self.assertEqual(binom_cdf(-1, 100, 0.3), 0.0)
        self.assertEqual(binom_cdf(100, 100, 0.3), 1.0)

    def test_cdf_symmetric_case_against_direct_sum(self):
        # tiny-n cross-check against exact fractions arithmetic
        from fractions import Fraction
        n, p = 20, 0.25
        num = Fraction(1, 4)
        direct = sum(
            Fraction(math.comb(n, i)) * num ** i * (1 - num) ** (n - i)
            for i in range(11))
        self.assertAlmostEqual(binom_cdf(10, n, p), float(direct), places=12)


if __name__ == "__main__":
    unittest.main()
