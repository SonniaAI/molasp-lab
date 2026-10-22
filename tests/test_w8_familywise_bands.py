"""Pins for tools/w8_familywise_bands.py (tick 151, SON-5152).

All numbers below are transcribed from the tool's own deterministic
output over the receipt-pinned counts in tools.w8_stratified_census
(cross-checked by tests/test_w8_stratified_census.py). The module adds
no new data; these pins exist so that any drift in the Bonferroni
convention, the Wilson math, or the frozen arm counts fails loudly.
"""

from __future__ import annotations

import os
import sys
import unittest
from statistics import NormalDist

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_familywise_bands import (
    ALPHA,
    K,
    TIER_BOUNDARY,
    TIER_FLOOR,
    Z_ONE_SIDED,
    Z_TWO_SIDED,
    familywise_bands,
)
from tools.w8_stratified_census import CONTESTED_FOUR_ARM_STRATA


class TestConvention(unittest.TestCase):
    def test_k_is_four_and_alpha_five_percent(self):
        self.assertEqual(K, 4)
        self.assertEqual(ALPHA, 0.05)

    def test_z_quantiles_pinned_and_reproducible(self):
        # Bonferroni: two-sided per-arm level 1-0.05/4 (per-side 0.00625);
        # one-sided per-arm tail 0.0125.
        self.assertAlmostEqual(
            Z_TWO_SIDED, NormalDist().inv_cdf(1 - 0.05 / 8), places=15)
        self.assertAlmostEqual(
            Z_ONE_SIDED, NormalDist().inv_cdf(1 - 0.05 / 4), places=15)
        self.assertAlmostEqual(Z_TWO_SIDED, 2.4977054744123737, places=12)
        self.assertAlmostEqual(Z_ONE_SIDED, 2.2414027276049464, places=12)
        # simultaneous bands must be WIDER than the pointwise z=1.96 receipt convention
        self.assertGreater(Z_TWO_SIDED, 1.96)
        self.assertGreater(Z_ONE_SIDED, 1.96)


class TestCounts(unittest.TestCase):
    def test_counts_come_from_the_receipt_pinned_strata(self):
        out = familywise_bands()
        self.assertEqual(
            sum(a["x"] for a in out["arms"].values()),
            sum(s.x for s in CONTESTED_FOUR_ARM_STRATA))  # 1235
        self.assertEqual(
            sum(a["n"] for a in out["arms"].values()),
            sum(s.n for s in CONTESTED_FOUR_ARM_STRATA))  # 1652
        self.assertEqual(sum(s.x for s in CONTESTED_FOUR_ARM_STRATA), 1235)
        self.assertEqual(sum(s.n for s in CONTESTED_FOUR_ARM_STRATA), 1652)


class TestBands(unittest.TestCase):
    def test_arm3_band_pinned(self):
        a = familywise_bands()["arms"]["arm3"]
        self.assertEqual((a["x"], a["n"]), (375, 500))
        self.assertAlmostEqual(a["share"], 0.75, places=15)
        self.assertAlmostEqual(a["band_simultaneous_95"][0], 0.6987516378654017, places=12)
        self.assertAlmostEqual(a["band_simultaneous_95"][1], 0.795086708847941, places=12)
        self.assertAlmostEqual(a["lower_one_sided_family_95"], 0.7042533527316307, places=12)

    def test_arm4_band_pinned(self):
        a = familywise_bands()["arms"]["arm4"]
        self.assertEqual((a["x"], a["n"]), (106, 153))
        self.assertAlmostEqual(a["share"], 106.0 / 153.0, places=15)
        self.assertAlmostEqual(a["band_simultaneous_95"][0], 0.5936328162363759, places=12)
        self.assertAlmostEqual(a["band_simultaneous_95"][1], 0.7768805200961678, places=12)
        self.assertAlmostEqual(a["lower_one_sided_family_95"], 0.6041962950374502, places=12)

    def test_arm6_band_pinned(self):
        a = familywise_bands()["arms"]["arm6"]
        self.assertEqual((a["x"], a["n"]), (389, 500))
        self.assertAlmostEqual(a["share"], 0.778, places=15)
        self.assertAlmostEqual(a["band_simultaneous_95"][0], 0.7283121615988308, places=12)
        self.assertAlmostEqual(a["band_simultaneous_95"][1], 0.8208360799464063, places=12)
        self.assertAlmostEqual(a["lower_one_sided_family_95"], 0.7336918119823952, places=12)

    def test_arm7_band_pinned(self):
        a = familywise_bands()["arms"]["arm7"]
        self.assertEqual((a["x"], a["n"]), (365, 499))
        self.assertAlmostEqual(a["share"], 365.0 / 499.0, places=15)
        self.assertAlmostEqual(a["band_simultaneous_95"][0], 0.67927372697521, places=12)
        self.assertAlmostEqual(a["band_simultaneous_95"][1], 0.7779360562817776, places=12)
        self.assertAlmostEqual(a["lower_one_sided_family_95"], 0.6848478037683055, places=12)


class TestFamilyStatements(unittest.TestCase):
    def test_no_arm_has_familywise_stable_tier_label(self):
        out = familywise_bands()
        self.assertTrue(out["family_statements"]["no_arm_has_familywise_stable_tier_label"])
        for label, a in out["arms"].items():
            lo, hi = a["band_simultaneous_95"]
            self.assertLess(lo, TIER_BOUNDARY, label)
            self.assertGreater(hi, TIER_BOUNDARY, label)

    def test_every_arm_above_floor_familywise(self):
        out = familywise_bands()
        self.assertTrue(out["family_statements"]["every_arm_above_floor_familywise"])
        for label, a in out["arms"].items():
            self.assertGreater(a["lower_one_sided_family_95"], TIER_FLOOR, label)
            self.assertGreater(a["band_simultaneous_95"][0], TIER_FLOOR, label)

    def test_minima_are_arm4(self):
        out = familywise_bands()
        fs = out["family_statements"]
        self.assertAlmostEqual(fs["min_two_sided_lower_endpoint"], 0.5936328162363759, places=12)
        self.assertAlmostEqual(fs["min_one_sided_lower_bound"], 0.6041962950374502, places=12)
        self.assertEqual(
            min(out["arms"], key=lambda l: out["arms"][l]["band_simultaneous_95"][0]),
            "arm4")

    def test_deterministic(self):
        self.assertEqual(familywise_bands(), familywise_bands())


if __name__ == "__main__":
    unittest.main()
