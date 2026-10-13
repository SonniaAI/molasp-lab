"""Pins for evidence/2026-10-13-w8-arm6/ktam_w8_arm6.py — the
arm-6 ladder growth harness (tick 111, SON-5138), pre-registered
BEFORE submission.

Constants are identity-pinned against the committed receipts
(tick-96 arm-3 datum 375/500, tick-97 arm-4 growth 106/153, the
claimable pooled line datum 481/653, the DW9 CAL identity chain
367:131) and against the live dispersion tool's receipt /
exact_two_sided_p (VERBATIM duplication is the point — the
identity pin catches drift in either copy).  Branch bands were
MEASURED before pinning (tick-73 lesson): the pinned p-values are
the formula's own output at n6=153, printed to 6 decimals.
No trajectory runs here (the queue job is the run of record).
"""
import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TILES_AND_DIR = REPO / "evidence" / "2026-10-06-body-conjunction-builds"
TILES_DEATH_DIR = REPO / "evidence" / "2026-10-06-structural-death"
HARNESS = REPO / "evidence" / "2026-10-13-w8-arm6" / "ktam_w8_arm6.py"

for _p in (str(REPO), str(TILES_AND_DIR), str(TILES_DEATH_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_spec = importlib.util.spec_from_file_location("ktam_w8_arm6", HARNESS)
a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a)

import tools.w8_dispersion_receipt as wdr  # noqa: E402


class TestArm6Constants(unittest.TestCase):
    def test_arm6_is_reserved_block_six(self):
        self.assertEqual(a.SEED0_ARM6, 340261107)
        self.assertEqual(a.SEED0_ARM6,
                         a.BASE_SEED + 6 * a.SEED_STRIDE)

    def test_full_mode_sizes(self):
        # CI runs without SMOKE: CAL 500 + arm-6 153 (frozen stride
        # of the tick-110 named action).
        self.assertEqual(a.N_CAL, 500)
        self.assertEqual(a.N_ARM6, 153)

    def test_reference_receipts(self):
        self.assertEqual((a.ARM3_X, a.ARM3_K), (375, 500))   # tick-96
        self.assertEqual((a.ARM4_X, a.ARM4_K), (106, 153))   # tick-97
        self.assertEqual((a.POOL_X, a.POOL_K), (481, 653))   # pooled line
        self.assertEqual((a.CAL_D2T, a.CAL_L2), (367, 131))  # DW9 chain

    def test_alpha_pre_registered(self):
        self.assertEqual(a.ALPHA, 0.05)
        self.assertEqual(a.MIN_EVENTS, 50)


class TestExactPIdentity(unittest.TestCase):
    def test_matches_dispersion_tool(self):
        for k, p, x in [(153, 481 / 653, 112),
                        (500, 106 / 153, 375),
                        (153, 0.75, 106),
                        (500, 0.7366, 370)]:
            self.assertEqual(a.exact_two_sided_p(k, p, x),
                             wdr.exact_two_sided_p(k, p, x))

    def test_receipt_matches_dispersion_tool(self):
        for arms in ([(375, 500), (106, 153), (370, 500)],
                     [(375, 500), (106, 153), (112, 153)],
                     [(375, 500), (106, 153), (140, 153)],
                     [(417, 500), (390, 500), (2, 7)]):
            self.assertEqual(a.dispersion_receipt(arms, 0.05),
                             wdr.receipt(list(arms), 0.05))


class TestGateBranchMap(unittest.TestCase):
    # Bands measured before pinning: same formula, n6=153,
    # 6 decimals.  POOLING_CONTINUES for x6 in [112, 122];
    # POOLING_CONTESTED for x6 <= 111 or x6 >= 123.
    def test_continues_left_edge(self):
        branch, rep = a.gate(153, 112)
        self.assertEqual(branch, "POOLING_CONTINUES")
        self.assertAlmostEqual(rep["min_exact_p"], 6.744905e-02,
                               delta=5e-8)

    def test_continues_interior(self):
        branch, rep = a.gate(153, 115)
        self.assertEqual(branch, "POOLING_CONTINUES")
        self.assertAlmostEqual(rep["min_exact_p"], 1.118018e-01,
                               delta=5e-8)

    def test_continues_right_edge(self):
        self.assertEqual(a.gate(153, 122)[0], "POOLING_CONTINUES")

    def test_contested_below_band(self):
        branch, rep = a.gate(153, 111)
        self.assertEqual(branch, "POOLING_CONTESTED")
        branch100, rep100 = a.gate(153, 100)
        self.assertEqual(branch100, "POOLING_CONTESTED")
        self.assertAlmostEqual(rep100["min_exact_p"], 1.961877e-04,
                               delta=5e-10)

    def test_contested_above_band(self):
        branch, rep = a.gate(153, 123)
        self.assertEqual(branch, "POOLING_CONTESTED")
        branch140, rep140 = a.gate(153, 140)
        self.assertEqual(branch140, "POOLING_CONTESTED")
        self.assertAlmostEqual(rep140["min_exact_p"], 3.653524e-08,
                               delta=5e-14)

    def test_min_events_floor(self):
        self.assertEqual(a.gate(49, 40)[0], "NO_EVENTS")
        branch, rep = a.gate(50, 40)
        self.assertNotEqual(branch, "NO_EVENTS")
        self.assertIsNotNone(rep)

    def test_gate_exhaustive_and_disjoint(self):
        # Every x6 at n6=153 maps to exactly one branch — the map
        # has no default arm and no gap.
        branches = {a.gate(153, x)[0] for x in range(0, 154)}
        self.assertEqual(branches,
                         {"POOLING_CONTINUES", "POOLING_CONTESTED"})
        # The pre-registered band is exactly [112, 122].
        band = [x for x in range(0, 154)
                if a.gate(153, x)[0] == "POOLING_CONTINUES"]
        self.assertEqual(band, list(range(112, 123)))


class TestPooledDatumArithmetic(unittest.TestCase):
    def test_pooled_line_datum_pre(self):
        # 481/653 = arm-3 + arm-4 sums; arm-5 (370/500) is NOT a
        # line arm (tick-98 arbitration instrument, out of pool).
        self.assertEqual(a.POOL_X, a.ARM3_X + a.ARM4_X)
        self.assertEqual(a.POOL_K, a.ARM3_K + a.ARM4_K)


if __name__ == "__main__":
    unittest.main()
