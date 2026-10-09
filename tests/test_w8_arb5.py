"""Pins for evidence/2026-10-09-w8-arb5/ktam_w8_arb5.py — the
arm-5 pairwise arbitration harness (tick 98, SON-4919),
pre-registered BEFORE submission.

Constants are identity-pinned against the committed receipts
(tick-96 arm-3 datum 375/500, tick-97 arm-4 growth 106/153, the
DW9 CAL identity chain 367:131) and against the live dispersion
tool's exact_two_sided_p (VERBATIM duplication is the point — the
identity pin catches drift in either copy).  Branch bands were
MEASURED before pinning (tick-73 lesson): the pinned p-values are
the formula's own output at n=500, printed to 6 decimals.
No trajectory runs here (the queue job is the run of record).
"""
import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TILES_AND_DIR = REPO / "evidence" / "2026-10-06-body-conjunction-builds"
TILES_DEATH_DIR = REPO / "evidence" / "2026-10-06-structural-death"
HARNESS = REPO / "evidence" / "2026-10-09-w8-arb5" / "ktam_w8_arb5.py"

for _p in (str(REPO), str(TILES_AND_DIR), str(TILES_DEATH_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_spec = importlib.util.spec_from_file_location("ktam_w8_arb5", HARNESS)
a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a)

import tools.w8_dispersion_receipt as wdr  # noqa: E402


class TestArb5Constants(unittest.TestCase):
    def test_arm5_is_reserved_block_five(self):
        self.assertEqual(a.SEED0_ARM5, 320261107)
        self.assertEqual(a.SEED0_ARM5,
                         a.BASE_SEED + 5 * a.SEED_STRIDE)

    def test_full_mode_sizes(self):
        # CI runs without SMOKE: CAL 500 + arm-5 500.
        self.assertEqual(a.N_CAL, 500)
        self.assertEqual(a.N_ARM5, 500)

    def test_reference_receipts(self):
        self.assertEqual((a.ARM3_X, a.ARM3_K), (375, 500))   # tick-96
        self.assertEqual((a.ARM4_X, a.ARM4_K), (106, 153))   # tick-97
        self.assertEqual((a.CAL_D2T, a.CAL_L2), (367, 131))  # DW9 chain

    def test_alpha_pre_registered(self):
        self.assertEqual(a.ALPHA, 0.05)
        self.assertEqual(a.MIN_EVENTS, 50)


class TestExactPIdentity(unittest.TestCase):
    def test_matches_dispersion_tool(self):
        for k, p, x in [(500, 0.75, 375),
                        (500, 106 / 153, 375),
                        (153, 0.75, 106),
                        (500, 0.75, 400)]:
            self.assertEqual(a.exact_two_sided_p(k, p, x),
                             wdr.exact_two_sided_p(k, p, x))


class TestBranchMap(unittest.TestCase):
    # Bands measured before pinning: same formula, n=500, 6 decimals.
    def test_arm4_smalln(self):
        b, p3, p4 = a.arbitrate(500, 375)
        self.assertEqual(b, "ARM4_SMALLN")
        self.assertAlmostEqual(p3, 1.000000, places=5)
        self.assertAlmostEqual(p4, 0.005667, places=5)

    def test_block_structure(self):
        b, p3, p4 = a.arbitrate(500, 340)
        self.assertEqual(b, "BLOCK_STRUCTURE")
        self.assertAlmostEqual(p3, 0.000433, places=5)
        self.assertAlmostEqual(p4, 0.528965, places=5)

    def test_ambiguous_middle(self):
        b, p3, p4 = a.arbitrate(500, 360)
        self.assertEqual(b, "AMBIGUOUS_MIDDLE")
        self.assertAlmostEqual(p3, 0.121534, places=5)
        self.assertAlmostEqual(p4, 0.191016, places=5)

    def test_outside_both(self):
        b, p3, p4 = a.arbitrate(500, 400)
        self.assertEqual(b, "OUTSIDE_BOTH")
        self.assertAlmostEqual(p3, 0.009734, places=5)
        self.assertLess(p4, a.ALPHA)

    def test_min_events_floor(self):
        self.assertEqual(a.arbitrate(49, 40)[0], "NO_EVENTS")
        b, p3, p4 = a.arbitrate(50, 40)
        self.assertNotEqual(b, "NO_EVENTS")
        self.assertIsNotNone(p3)
        self.assertIsNotNone(p4)

    def test_branches_exhaustive_and_disjoint(self):
        # Every (p3-side, p4-side) combination maps to exactly one
        # branch — the map has no default arm and no gap.
        branches = {a.arbitrate(500, x)[0] for x in range(250, 451, 5)}
        self.assertEqual(
            branches,
            {"ARM4_SMALLN", "BLOCK_STRUCTURE",
             "AMBIGUOUS_MIDDLE", "OUTSIDE_BOTH"})


if __name__ == "__main__":
    unittest.main()
