"""Pins for tools/w8_stratified_census.py (tick 122, SON-5152).

Receipt cross-checks (the point of these pins): the six-window homogeneity
numbers must reproduce the committed tick-103 receipt
(evidence/2026-10-09-w8-window-heterogeneity/run.out:
X2(5)=2.7713095514, p=0.7351922075242888, pooled 22111/29989,
Wilson-95 [0.73229, 0.74225]) and the contested four-arm pool must
reproduce the tick-118 quoted interval [0.72607, 0.76794] at 1235/1652.
Everything here is descriptive/design math: no gate is executed, the
ladder stays PAUSED, and the pooled contested line stays
REPORTED-NOT-CLAIMABLE.
"""

from __future__ import annotations

import os
import sys
import unittest
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_stratified_census import (
    CAL_STRATUM,
    CONTESTED_FOUR_ARM_STRATA,
    SIX_WINDOW_STRATA,
    Z_ALPHA,
    Z_POWER,
    chi2_sf,
    design_power,
    homogeneity_x2,
    neyman_allocation,
    pooled,
    stratified_estimators,
    summarize,
    wilson95,
)


class TestFrozenDataIntegrity(unittest.TestCase):
    def test_six_window_totals_match_receipt(self):
        self.assertEqual(sum(s.x for s in SIX_WINDOW_STRATA), 22111)
        self.assertEqual(sum(s.n for s in SIX_WINDOW_STRATA), 29989)

    def test_contested_totals_match_corrected_pool(self):
        # arm3 375:500 + arm4 106:153 + arm6 389:500 + arm7 365:499
        self.assertEqual(sum(s.x for s in CONTESTED_FOUR_ARM_STRATA), 1235)
        self.assertEqual(sum(s.n for s in CONTESTED_FOUR_ARM_STRATA), 1652)

    def test_every_stratum_wellformed_with_source(self):
        for s in (*SIX_WINDOW_STRATA, *CONTESTED_FOUR_ARM_STRATA, CAL_STRATUM):
            self.assertLessEqual(s.x, s.n)
            self.assertGreaterEqual(s.x, 0)
            self.assertTrue(s.source and s.provenance)

    def test_cal_identity_chain_anchor(self):
        # mid-w4 pair census 367:131, other=2 -> pair_n=498
        self.assertEqual(CAL_STRATUM.x, 367)
        self.assertEqual(CAL_STRATUM.n, 498)


class TestReceiptCrossChecks(unittest.TestCase):
    def test_six_window_homogeneity_reproduces_receipt(self):
        h = homogeneity_x2(SIX_WINDOW_STRATA)
        self.assertEqual(h["df"], 5)
        self.assertAlmostEqual(h["statistic"], 2.7713095513648907, places=9)
        self.assertAlmostEqual(h["p_value"], 0.7351922075242888, places=12)

    def test_six_window_pooled_share_and_wilson(self):
        x, n, share, (lo, hi) = pooled(SIX_WINDOW_STRATA)
        self.assertEqual((x, n), (22111, 29989))
        self.assertEqual(Fraction(x, n), Fraction(22111, 29989))
        self.assertAlmostEqual(share, Fraction(22111, 29989).__float__(),
                               places=15)
        self.assertAlmostEqual(lo, 0.73229, places=5)
        self.assertAlmostEqual(hi, 0.74225, places=5)

    def test_contested_pool_reproduces_tick118_quoted_interval(self):
        x, n, share, (lo, hi) = pooled(CONTESTED_FOUR_ARM_STRATA)
        self.assertEqual((x, n), (1235, 1652))
        self.assertAlmostEqual(share, 0.7475786924939467, places=12)
        self.assertAlmostEqual(lo, 0.72607, places=5)
        self.assertAlmostEqual(hi, 0.76794, places=5)

    def test_contested_x2_is_descriptive_only(self):
        # Not a gate: the frozen dispersion authority is the exact min-p
        # instrument (tick 93/99). Recorded so nobody mistakes this number.
        h = homogeneity_x2(CONTESTED_FOUR_ARM_STRATA)
        self.assertEqual(h["df"], 3)
        self.assertAlmostEqual(h["statistic"], 5.58645700972762, places=9)

    def test_cal_wilson(self):
        share = CAL_STRATUM.x / CAL_STRATUM.n
        self.assertAlmostEqual(share, 0.7369477911646586, places=12)
        lo, hi = wilson95(CAL_STRATUM.x, CAL_STRATUM.n)
        self.assertLess(lo, share)
        self.assertLess(share, hi)


class TestChiSquareTail(unittest.TestCase):
    def test_df5_critical_value_matches_tick102_note(self):
        # tick-102 prereg quotes the df=5 alpha=.05 critical value
        # 11.0704977; survival there must be 0.05.
        self.assertAlmostEqual(chi2_sf(11.0704977, 5), 0.05, places=4)

    def test_extremes(self):
        self.assertEqual(chi2_sf(0.0, 5), 1.0)
        self.assertLess(chi2_sf(100.0, 5), 1e-15)


class TestWilson(unittest.TestCase):
    def test_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            wilson95(3, 2)
        with self.assertRaises(ValueError):
            wilson95(-1, 5)
        with self.assertRaises(ValueError):
            wilson95(0, 0)


class TestStratifiedEstimators(unittest.TestCase):
    def test_six_window_inverse_variance_numbers(self):
        e = stratified_estimators(SIX_WINDOW_STRATA)
        self.assertAlmostEqual(e["inv_var_share"], 0.7373466747655051,
                               places=12)
        self.assertAlmostEqual(e["inv_var_se"], 0.0025411275605887553,
                               places=12)
        self.assertAlmostEqual(
            e["conservative_band_halfwidth"], 0.012196475604294248,
            places=12)

    def test_conservative_band_covers_all_stratum_point_estimates(self):
        e = stratified_estimators(SIX_WINDOW_STRATA)
        theta = e["inv_var_share"]
        half = e["conservative_band_halfwidth"]
        for s in SIX_WINDOW_STRATA:
            self.assertLessEqual(abs(s.x / s.n - theta), half + 1e-12)

    def test_per_stratum_wilson_count(self):
        e = stratified_estimators(SIX_WINDOW_STRATA)
        self.assertEqual(len(e["per_stratum_wilson95"]), 6)


class TestNeymanAllocation(unittest.TestCase):
    def test_worst_case_two_stratum_equal_split(self):
        from tools.w8_stratified_census import Stratum
        strata = (Stratum("a", 75, 100, "t", "p"), Stratum("b", 75, 100, "t", "p"))
        out = neyman_allocation(strata, 100, worst_case=True)
        self.assertEqual(out["allocation"], {"a": 50, "b": 50})

    def test_equal_sigma_largest_remainder(self):
        from tools.w8_stratified_census import Stratum
        strata = tuple(Stratum(f"s{i}", 30, 40, "t", "p") for i in range(3))
        out = neyman_allocation(strata, 10, worst_case=True)
        self.assertEqual(sum(out["allocation"].values()), 10)
        self.assertEqual(sorted(out["allocation"].values()), [3, 3, 4])

    def test_measured_six_window_orders_block8_first(self):
        # block8 has the most extreme share (0.7289) -> largest sigma
        # -> largest Neyman allocation at equal n.
        out = neyman_allocation(SIX_WINDOW_STRATA, 6000, worst_case=False)
        alloc = out["allocation"]
        self.assertEqual(sum(alloc.values()), 6000)
        self.assertEqual(max(alloc, key=alloc.get), "block8")
        self.assertEqual(min(alloc, key=alloc.get), "block9")


class TestDesignPower(unittest.TestCase):
    def test_n3560_numbers(self):
        d = design_power(0.74, 3560)
        self.assertAlmostEqual(d["se"], 0.010396628667046326, places=12)
        self.assertAlmostEqual(d["mde90"], 0.02585095581481785, places=12)

    def test_required_n_at_delta_030(self):
        # One-sided minimal n at the tick-120 delta_target; the frozen
        # (0.040/0.030)^2 x 2000 rule gave 3560 (more conservative, and it
        # stays the authority). This pin documents the cross-check only.
        d = design_power(0.74, 3560)
        self.assertEqual(d["required_n_at"](0.030), 2644)

    def test_power_convention_matches_blockpower_prereg(self):
        self.assertAlmostEqual(Z_ALPHA, 1.6448536269514722, places=12)
        self.assertAlmostEqual(Z_POWER, 0.8416212335729143, places=12)

    def test_rejects_bad_p(self):
        with self.assertRaises(ValueError):
            design_power(0.0, 100)
        with self.assertRaises(ValueError):
            design_power(0.5, 1)


class TestSummarizeContract(unittest.TestCase):
    def test_summarize_has_both_families_and_cal(self):
        s = summarize()
        self.assertIn("six_window_pooled", s)
        self.assertIn("contested_four_arm_descriptive", s)
        self.assertIn("cal", s)
        self.assertAlmostEqual(
            s["contested_four_arm_descriptive"]["share"],
            0.7475786924939467, places=12)


if __name__ == "__main__":
    unittest.main()
