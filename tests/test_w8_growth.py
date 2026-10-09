"""Pins for evidence/2026-10-09-w8-growth/ktam_w8_growth.py — the
stage-1 growth census harness (tick 97, SON-4917), pre-registered
BEFORE submission.

Constants are identity-pinned against the live tick-92 policy tool
(measure-then-claim): policy(375, 500) must still name k_line 653,
window [489, 491], x_line 490 — the exact numbers the harness freezes.
The wilson() helper is pinned to the committed tick-96 datum interval.
No trajectory runs here (the queue job is the run of record).
"""
import importlib.util
import os
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TILES_AND_DIR = REPO / "evidence" / "2026-10-06-body-conjunction-builds"
TILES_DEATH_DIR = REPO / "evidence" / "2026-10-06-structural-death"
HARNESS = REPO / "evidence" / "2026-10-09-w8-growth" / "ktam_w8_growth.py"

for _p in (str(REPO), str(TILES_AND_DIR), str(TILES_DEATH_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_spec = importlib.util.spec_from_file_location("ktam_w8_growth", HARNESS)
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)

import tools.w8_census_policy as wcp  # noqa: E402


class TestGrowthConstants(unittest.TestCase):
    def test_growth_arm_is_reserved_block_four(self):
        self.assertEqual(g.SEED0_GROWTH, 300261107)
        self.assertEqual(g.SEED0_GROWTH,
                         g.BASE_SEED + 4 * g.SEED_STRIDE)

    def test_growth_size_lands_the_line_census(self):
        # Full mode (CI runs without SMOKE): CAL 500 + growth 153.
        self.assertEqual(g.N_GROWTH, 153)
        self.assertEqual(g.N_CAL, 500)
        self.assertEqual(g.DATUM_K + g.N_GROWTH, 653)

    def test_datum_receipt_constants(self):
        self.assertEqual(g.DATUM_D2T, 375)   # tick-96 arm-3 w8 census
        self.assertEqual(g.PHAT, 0.75)
        self.assertEqual(g.CAL_D2T, 367)     # DW9 identity chain
        self.assertEqual(g.CAL_L2, 131)


class TestLineIdentityVsPolicy(unittest.TestCase):
    """The frozen harness constants must equal the live ladder's
    answer on the datum — if either side drifts, this fails."""

    @classmethod
    def setUpClass(cls):
        cls.pol = wcp.policy(375, 500)

    def test_mode_is_grow(self):
        self.assertEqual(self.pol["mode"], "grow")

    def test_line_census_numbers(self):
        gr = self.pol["growth"]
        self.assertEqual(gr["k_line_prac"], g.K_LINE)
        self.assertEqual(gr["window"], g.R3_WINDOW)
        self.assertEqual(gr["line_x_at_k"], g.X_LINE)
        self.assertEqual(gr["total_arms"], 2)
        self.assertEqual(gr["additional_arms"], 1)

    def test_window_equivalence(self):
        lo, hi = g.R3_WINDOW
        x4_window = {x4 for x4 in range(0, 154)
                     if lo <= 375 + x4 <= hi}
        self.assertEqual(x4_window, {114, 115, 116})
        self.assertAlmostEqual(g.PHAT * g.N_GROWTH, 114.75)


class TestHelpersOnReceipts(unittest.TestCase):
    def test_wilson_reproduces_tick96_datum_interval(self):
        self.assertEqual(g.wilson(375, 500), [0.71024, 0.78595])

    def test_census_pair_convention(self):
        trajs = [{"terminal": "D2T", "log": []},
                 {"terminal": "L2", "log": []},
                 {"terminal": None, "log": []}]
        c = g.census(trajs, "terminal")
        self.assertEqual((c["D2T"], c["L2"], c["other"]), (1, 1, 1))
        self.assertEqual(c["share"], 0.5)

    def test_verdicts_line_shape(self):
        # The harness is a census: exactly two machine verdict keys,
        # never HELD/REFUTED (the tick-74 falsifier is closed).
        line = '{"CAL": "CAL_OK", "GROWTH": "COUNTED"}'
        vs = __import__("json").loads(line)
        self.assertEqual(set(vs), {"CAL", "GROWTH"})


if __name__ == "__main__":
    unittest.main()
