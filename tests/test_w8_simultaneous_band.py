"""Pins for tools/w8_simultaneous_band.py (tick 124, SON-5152).

Bonferroni per-stratum Wilson bands for the frozen stratified census,
measured over the SAME paired fixed-seed datasets as the tick-123 OC
simulation (seeds 20261013 / 20261014, 4000 replicates, identical
_BinomialCDF draw order — the first-replicate counts are pinned below as
the pairing fingerprint). All draws are SYNTHETIC binomial counts
calibrated to committed receipts — zero kTAM trajectories, no gate
executed, ladder stays PAUSED, pooled contested line stays
REPORTED-NOT-CLAIMABLE. Pins measured first, then frozen (house rule).

The scientific claim these pins guard: plain per-stratum Wilson-95 is
NOT simultaneous (all-strata coverage 0.73675 world A / 0.81625 world B,
tracking 0.95^m), while Bonferroni-Wilson at family level 0.95 restores
all-strata coverage to 0.94975 / 0.95275 at a per-stratum width price of
1.3458x (m=6) / 1.2700x (m=4). The conservative band from tick 122/123
remains the theta-interval honesty summary; this is the missing
per-stratum simultaneous authority, priced BEFORE the blockpower
arbitration datum lands.
"""

from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.w8_simultaneous_band import (  # noqa: E402
    bonferroni_z,
    run,
    simultaneous_band_world,
)
from tools.w8_stratified_census import (  # noqa: E402
    CONTESTED_FOUR_ARM_STRATA,
    SIX_WINDOW_STRATA,
)


class TestBonferroniZ(unittest.TestCase):
    def test_single_stratum_matches_wilson_z(self):
        self.assertAlmostEqual(bonferroni_z(1), 1.959963984540054, places=12)

    def test_six_strata(self):
        self.assertAlmostEqual(bonferroni_z(6), 2.638257273476751, places=12)

    def test_four_strata(self):
        self.assertAlmostEqual(bonferroni_z(4), 2.4977054744123737,
                               places=12)

    def test_rejects_bad_input(self):
        for bad in (0, -1, True, 2.5):
            with self.assertRaises(ValueError):
                bonferroni_z(bad)
        for bad_family in (0.0, 1.0, 1.5):
            with self.assertRaises(ValueError):
                bonferroni_z(4, bad_family)


class SimBandWorlds(unittest.TestCase):
    """Shared full-precision results for both pinned worlds."""

    @classmethod
    def setUpClass(cls):
        cls.a, cls.b = run()


class TestWorldA(SimBandWorlds):
    """Homogeneous six-window world (models BLOCK_MECHANISM_NOT_DETECTED)."""

    def test_z_and_levels(self):
        self.assertEqual(self.a["strata"], 6)
        self.assertAlmostEqual(self.a["z_bonferroni"],
                               2.638257273476751, places=12)
        self.assertEqual(self.a["family_level"], 0.95)

    def test_all_strata_coverage_pins(self):
        self.assertAlmostEqual(
            self.a["all_strata_coverage_nominal95"], 0.73675, places=12)
        self.assertAlmostEqual(
            self.a["all_strata_coverage_bonferroni"], 0.94975, places=12)
        self.assertAlmostEqual(
            self.a["per_stratum_coverage_bonferroni_min"], 0.9895,
            places=12)

    def test_width_pins_and_ratio(self):
        self.assertAlmostEqual(
            self.a["mean_per_stratum_width_nominal"],
            0.024394190338389524, places=12)
        self.assertAlmostEqual(
            self.a["mean_per_stratum_width_bonferroni"],
            0.032828531666159004, places=12)
        self.assertAlmostEqual(
            self.a["width_ratio_bonf_over_nominal"],
            1.345752050417358, places=12)

    def test_first_draw_row_pairing_fingerprint(self):
        self.assertEqual(self.a["first_draw_row"],
                         [3695, 3658, 3722, 3728, 3671, 3682])


class TestWorldB(SimBandWorlds):
    """Contested four-arm world (models BLOCK_MECHANISM_SUPPORTED)."""

    def test_z_and_levels(self):
        self.assertEqual(self.b["strata"], 4)
        self.assertAlmostEqual(self.b["z_bonferroni"],
                               2.4977054744123737, places=12)

    def test_all_strata_coverage_pins(self):
        self.assertAlmostEqual(
            self.b["all_strata_coverage_nominal95"], 0.81625, places=12)
        self.assertAlmostEqual(
            self.b["all_strata_coverage_bonferroni"], 0.95275, places=12)
        self.assertAlmostEqual(
            self.b["per_stratum_coverage_bonferroni_min"], 0.9865,
            places=12)

    def test_width_pins_and_ratio(self):
        self.assertAlmostEqual(
            self.b["mean_per_stratum_width_nominal"],
            0.0924646380977798, places=12)
        self.assertAlmostEqual(
            self.b["mean_per_stratum_width_bonferroni"],
            0.11743459439426238, places=12)
        self.assertAlmostEqual(
            self.b["width_ratio_bonf_over_nominal"],
            1.2700487106225113, places=12)

    def test_first_draw_row_pairing_fingerprint(self):
        self.assertEqual(self.b["first_draw_row"], [381, 101, 396, 374])


class TestClaims(SimBandWorlds):
    def test_bonferroni_realizations_within_mc_error_of_family_level(self):
        # Union bound: >= 0.95 in EXPECTATION. The frozen realizations are
        # 0.94975 (A, one replicate short) and 0.95275 (B); MC SE at a 0.95
        # proportion with 4000 reps is ~0.0034 (95% ~0.0068) — both inside.
        for res in (self.a, self.b):
            self.assertLessEqual(
                abs(res["all_strata_coverage_bonferroni"] - 0.95), 0.0068)
        self.assertGreaterEqual(self.b["all_strata_coverage_bonferroni"],
                                0.95)
        self.assertAlmostEqual(
            self.a["all_strata_coverage_bonferroni"], 0.94975, places=12)

    def test_nominal_wilson_is_not_simultaneous_either_world(self):
        self.assertLess(self.a["all_strata_coverage_nominal95"], 0.95)
        self.assertLess(self.b["all_strata_coverage_nominal95"], 0.95)

    def test_width_ratio_tracks_z_ratio_within_one_percent(self):
        for res in (self.a, self.b):
            z_ratio = res["z_bonferroni"] / res["z_nominal"]
            self.assertLess(
                abs(res["width_ratio_bonf_over_nominal"] - z_ratio), 0.01)

    def test_determinism_small_replicates(self):
        rates = [s.x / s.n for s in CONTESTED_FOUR_ARM_STRATA]
        ns = [s.n for s in CONTESTED_FOUR_ARM_STRATA]
        first = simultaneous_band_world("det", rates, ns, 20261014,
                                        replicates=400)
        second = simultaneous_band_world("det", rates, ns, 20261014,
                                         replicates=400)
        self.assertEqual(first, second)

    def test_world_shapes_match_frozen_strata(self):
        self.assertEqual(self.a["strata_n"],
                         [s.n for s in SIX_WINDOW_STRATA])
        self.assertEqual(self.b["strata_n"],
                         [s.n for s in CONTESTED_FOUR_ARM_STRATA])

    def test_rejects_bad_input(self):
        rates = [0.75, 0.69]
        with self.assertRaises(ValueError):
            simultaneous_band_world("bad", rates, [500], 0)
        with self.assertRaises(ValueError):
            simultaneous_band_world("bad", rates, [500, 153], -1)
        with self.assertRaises(ValueError):
            simultaneous_band_world("bad", rates, [500, 153], 0,
                                    replicates=0)


if __name__ == "__main__":
    unittest.main()
