"""Pins for tools/w8_census_sim.py (tick 123, SON-5152).

Fixed-seed Monte Carlo operating characteristics of the frozen
stratified-census estimator menu, over the two branch worlds of the
pending blockpower arbitration. All draws are SYNTHETIC binomial counts
calibrated to committed receipts — zero kTAM trajectories. No gate is
executed; the ladder stays PAUSED; the pooled contested line stays
REPORTED-NOT-CLAIMABLE.

reproducible under the frozen stdlib Mersenne Twister seeds 20261013
(world A) / 20261014 (world B), 4000 replicates — the module is
stdlib-only because the hosted unittest workflow installs nothing (the
numpy version in d051ca5 failed hosted CI; superseded by this repair).
Pins were measured first, then frozen (house rule).

The design caveat these pins guard: in the contested world the
conservative band covers the inverse-variance estimand theta* (0.99975)
but NEVER covers every stratum share simultaneously (0.0) — it is a
theta-interval, not a stratum-simultaneous band. Per-stratum Wilson
intervals remain the only per-stratum uncertainty authority.
"""

from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_census_sim import (  # noqa: E402
    REPLICATES,
    SEED_WORLD_A,
    SEED_WORLD_B,
    run,
)


class TestCensusSimWorldA(unittest.TestCase):
    """Homogeneous six-window world (models BLOCK_MECHANISM_NOT_DETECTED)."""

    @classmethod
    def setUpClass(cls):
        cls.results = {r["world"]: r for r in run()}
        cls.a = cls.results["A_homogeneous_six_window"]

    def test_seeds_and_replicates_frozen(self):
        self.assertEqual(SEED_WORLD_A, 20261013)
        self.assertEqual(SEED_WORLD_B, 20261014)
        self.assertEqual(REPLICATES, 4000)
        self.assertEqual(self.a["replicates"], 4000)
        self.assertEqual(self.a["strata_n"],
                         [4999, 4998, 4999, 4999, 4998, 4996])

    def test_world_a_per_stratum_wilson_at_nominal(self):
        self.assertAlmostEqual(self.a["per_stratum_wilson_coverage_min"],
                               0.94675, places=5)
        for cov in self.a["per_stratum_wilson_coverage"]:
            self.assertGreaterEqual(cov, 0.94)
            self.assertLessEqual(cov, 0.96)

    def test_world_a_pooled_and_inv_var_at_nominal(self):
        self.assertAlmostEqual(self.a["pooled_wilson_coverage"],
                               0.94375, places=5)
        self.assertAlmostEqual(self.a["inv_var_coverage"], 0.94375,
                               places=5)

    def test_world_a_band_covers_everything(self):
        self.assertEqual(self.a["band_coverage_theta"], 1.0)
        self.assertEqual(self.a["band_coverage_all_strata"], 1.0)

    def test_world_a_honesty_premium_ratio(self):
        # the conservative band costs ~2.45x the pooled interval width
        self.assertAlmostEqual(self.a["width_ratio_band_over_pooled"],
                               2.448439, places=6)
        self.assertAlmostEqual(self.a["mean_band_width"], 0.024392,
                               places=6)
        self.assertAlmostEqual(self.a["mean_pooled_wilson_width"],
                               0.009962, places=6)


class TestCensusSimWorldB(unittest.TestCase):
    """Contested four-arm world (models BLOCK_MECHANISM_SUPPORTED)."""

    @classmethod
    def setUpClass(cls):
        cls.results = {r["world"]: r for r in run()}
        cls.b = cls.results["B_contested_four_arm"]

    def test_world_b_structure_and_truths(self):
        self.assertEqual(self.b["strata_n"], [500, 153, 500, 499])
        self.assertAlmostEqual(self.b["pooled_truth"], 0.747579,
                               places=6)
        # theta's probability limit differs from the size-weighted mean
        # under heterogeneity (0.749190 vs 0.747579 here)
        self.assertAlmostEqual(self.b["inv_var_truth"], 0.74919,
                               places=5)
        self.assertNotAlmostEqual(self.b["inv_var_truth"],
                                  self.b["pooled_truth"], places=4)

    def test_world_b_per_stratum_wilson_at_nominal(self):
        self.assertAlmostEqual(self.b["per_stratum_wilson_coverage_min"],
                               0.9445, places=5)
        for cov in self.b["per_stratum_wilson_coverage"]:
            self.assertGreaterEqual(cov, 0.94)
            self.assertLessEqual(cov, 0.96)

    def test_world_b_pooled_wilson_does_not_collapse_at_these_n(self):
        # honest negative: at the contested n's the pooled Wilson covers
        # the size-weighted mean at nominal within MC error (sum n_i
        # p_i(1-p_i) ~ N q(1-q) here); the stratification case is
        # interpretability + per-stratum authority, not pooled coverage
        # collapse
        self.assertAlmostEqual(self.b["pooled_wilson_coverage"],
                               0.94375, places=5)

    def test_world_b_band_is_theta_interval_not_stratum_band(self):
        # THE design caveat discovered by simulation, pinned before the
        # blockpower datum lands
        self.assertAlmostEqual(self.b["band_coverage_theta"],
                               0.99975, places=5)
        self.assertEqual(self.b["band_coverage_all_strata"], 0.0)
        self.assertGreater(self.b["band_coverage_theta"],
                           self.b["band_coverage_all_strata"])

    def test_world_b_inv_var_within_mc_noise_of_nominal(self):
        # mild delta-method under-coverage under estimated weights in the
        # heterogeneous world; recorded honestly, not promoted
        self.assertAlmostEqual(self.b["inv_var_coverage"], 0.93875,
                               places=5)
        self.assertGreaterEqual(self.b["inv_var_coverage"], 0.93)

    def test_world_b_width_ratio(self):
        self.assertAlmostEqual(self.b["width_ratio_band_over_pooled"],
                               1.927886, places=6)


if __name__ == "__main__":
    unittest.main()
