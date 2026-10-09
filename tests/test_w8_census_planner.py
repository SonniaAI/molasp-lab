"""Pins for tools/w8_census_planner.py (tick 91 — measured 2026-10-09,
BEFORE the w8 datum exists).  Every constant below is pinned from the
tool's own output (measure-then-pin); cross-checks against the tick-87/88
Wilson receipts and the tick-89 atlas window are asserted explicitly."""
import sys
import unittest
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.w8_census_planner import (
    REGIONS,
    aim_window,
    arms_for_k,
    build_report,
    first_open,
    grown_primary_attribution,
    practical_open,
    serial_wall_hours,
    wilson,
)

R1, R2, R3, R4, R5 = REGIONS


class WilsonIdentities(unittest.TestCase):
    def test_tick88_primary_datum_reproduced(self):
        lo, hi = wilson(417, 500)
        self.assertEqual((round(lo, 5), round(hi, 5)), (0.79886, 0.86404))

    def test_tick87_cross_check_identity(self):
        lo, hi = wilson(232, 461)
        self.assertEqual((round(lo, 5), round(hi, 5)), (0.45777, 0.54868))

    def test_primary_datum_is_region_ambiguous_at_500(self):
        lo, hi = wilson(417, 500)
        self.assertLess(lo, 0.81415)
        self.assertGreater(hi, 0.81415)


class AimWindows(unittest.TestCase):
    def test_atlas_crosscheck_r2_window_at_500(self):
        self.assertEqual(aim_window(R2, 500), [425, 426, 427])

    def test_r1_r3_empty_at_500(self):
        self.assertEqual(aim_window(R1, 500), [])
        self.assertEqual(aim_window(R3, 500), [])

    def test_r4_r5_windows_at_500(self):
        r4 = aim_window(R4, 500)
        r5 = aim_window(R5, 500)
        self.assertEqual((r4[0], r4[-1]), (0, 337))
        self.assertEqual((r5[0], r5[-1]), (456, 500))


class TheoreticalOpenings(unittest.TestCase):
    def test_r1_opens_2677_single_count(self):
        op = first_open(R1)
        self.assertEqual(op["k"], 2677)
        self.assertEqual(op["window"], (2140, 2140))

    def test_r2_opens_406(self):
        op = first_open(R2)
        self.assertEqual(op["k"], 406)
        self.assertEqual(op["window"], (346, 346))

    def test_r3_opens_597(self):
        op = first_open(R3)
        self.assertEqual(op["k"], 597)
        self.assertEqual(op["window"], (448, 448))

    def test_destructive_regions_open_at_event_floor(self):
        self.assertEqual(first_open(R4)["k"], 50)
        self.assertEqual(first_open(R5)["k"], 50)


class PracticalOpenings(unittest.TestCase):
    def test_r1_practical_2806(self):
        p = practical_open(R1)
        self.assertEqual((p["k"], p["window"]), (2806, (2242, 2244)))

    def test_r2_practical_460(self):
        p = practical_open(R2)
        self.assertEqual((p["k"], p["window"]), (460, (391, 393)))

    def test_r3_practical_653(self):
        p = practical_open(R3)
        self.assertEqual((p["k"], p["window"]), (653, (489, 491)))

    def test_r5_practical_59_r4_at_floor(self):
        self.assertEqual((practical_open(R5)["k"], practical_open(R5)["window"]),
                         (59, (57, 59)))
        self.assertEqual((practical_open(R4)["k"], practical_open(R4)["window"]),
                         (50, (0, 29)))


class ArmsAndWall(unittest.TestCase):
    def test_arm_math(self):
        self.assertEqual(arms_for_k(406), 1)
        self.assertEqual(arms_for_k(460), 1)
        self.assertEqual(arms_for_k(1476), 3)
        self.assertEqual(arms_for_k(2677), 6)

    def test_serial_wall_hours(self):
        self.assertAlmostEqual(serial_wall_hours(1476), 2.0)
        self.assertAlmostEqual(serial_wall_hours(2806), 4.0)
        # 460 terminals is still ONE arm (ceil(460/500)=1): wall is per-arm,
        # not per-terminal — 1 x 2400 s = 0.667 h.
        self.assertAlmostEqual(serial_wall_hours(460), 2400 / 3600.0)
        self.assertEqual(arms_for_k(460), 1)


class GrownPrimary(unittest.TestCase):
    def test_first_attribution_1476(self):
        g = grown_primary_attribution()
        self.assertEqual((g["k"], g["x"]), (1476, 1231))
        self.assertEqual((round(g["lo"], 5), round(g["hi"], 5)),
                         (0.81417, 0.85212))

    def test_k500_growth_point_not_attributed(self):
        # the k=500 point on the growth line must NOT attribute (the atlas-
        # expected region-ambiguous reading); first attribution comes later.
        from tools.w8_census_planner import contained
        lo, hi = wilson(417, 500)
        self.assertFalse(contained(lo, hi, R2))


class ReportDeterminism(unittest.TestCase):
    def test_report_is_deterministic(self):
        self.assertEqual(build_report(), build_report())

    def test_report_carries_planner_headlines(self):
        text = build_report()
        for needle in ("opens at k=2677", "opens at k=406", "opens at k=597",
                       "first k=1476 (x=1231)", "SON-4895"):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
