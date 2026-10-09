"""Pins for tools/w8_census_policy.py (tick 92 — measured 2026-10-09,
BEFORE the w8 datum exists).  Every constant below is pinned from the
tool's own output (measure-then-pin); cross-checks against the tick-87/88
Wilson receipts, the tick-89 atlas window cells, and the tick-91 planner
openings are asserted explicitly."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.w8_census_planner import (
    REGIONS,
    aim_window,
    arms_for_k,
    grown_primary_attribution,
    serial_wall_hours,
    wilson,
)
from tools.w8_census_policy import (
    P50,
    P80,
    aim_window_fast,
    attribution_probability,
    collection_report,
    point_regions,
    policy,
    prob_scan,
    round_half_up,
)

R1, R2, R3, R4, R5 = REGIONS


class WilsonReceipts(unittest.TestCase):
    def test_tick87_receipt_reproduced(self):
        lo, hi = wilson(232, 461)
        self.assertEqual((round(lo, 5), round(hi, 5)), (0.45777, 0.54868))

    def test_tick88_primary_datum_reproduced(self):
        lo, hi = wilson(417, 500)
        self.assertEqual((round(lo, 5), round(hi, 5)), (0.79886, 0.86404))


class WindowIdentities(unittest.TestCase):
    def test_fast_window_matches_planner_cells(self):
        cells = [
            (R2, 500, [425, 427]),      # tick-89 razor window receipt
            (R1, 500, None),
            (R3, 500, None),
            (R4, 500, [0, 337]),        # tick-91 planner receipt
            (R5, 500, [456, 500]),      # tick-91 planner receipt
            (R2, 1442, [1203, 1250]),   # canonical line census window
            (R2, 1476, [1231, 1280]),   # tick-91 p0-line opening
            (R2, 2806, [2325, 2446]),   # tick-91 practical R1-neighbour cell
            (R4, 50, [0, 29]),
            (R5, 59, [57, 59]),
            (R1, 2806, [2242, 2244]),   # tick-91 practical R1 window
        ]
        for region, k, expected in cells:
            slow = aim_window(region, k)
            slow_pair = [slow[0], slow[-1]] if slow else None
            self.assertEqual(
                aim_window_fast(region, k),
                slow_pair,
                (region[0], k),
            )
            self.assertEqual(slow_pair, expected, (region[0], k))


class RoundingAndPoints(unittest.TestCase):
    def test_round_half_up_ties_away_from_zero(self):
        self.assertEqual(
            [round_half_up(v) for v in (0.5, 1.5, 2.5, 2.4, 0.0)],
            [1, 2, 3, 2, 0],
        )

    def test_point_regions_edge_conventions(self):
        self.assertEqual([r[0] for r in point_regions(0.834)], ["R2"])
        self.assertEqual(point_regions(0.81415), [])  # no-man's point
        self.assertEqual([r[0] for r in point_regions(0.78)], ["R3"])
        self.assertEqual([r[0] for r in point_regions(0.70)], ["R4"])
        self.assertEqual([r[0] for r in point_regions(0.90)], ["R5"])
        self.assertEqual([r[0] for r in point_regions(0.88376)], ["R2"])  # hi closed
        self.assertEqual([r[0] for r in point_regions(0.71415)], ["R3"])  # lo closed


class VerdictReadyCells(unittest.TestCase):
    def test_tick89_razor_window_reads_verdict_ready(self):
        d = policy(426, 500)
        self.assertEqual(d["mode"], "verdict_ready")
        self.assertEqual(d["regions"], ["R2"])

    def test_destructive_windows_at_k500(self):
        self.assertEqual(policy(100, 500)["regions"], ["R4"])
        self.assertEqual(policy(337, 500)["regions"], ["R4"])
        self.assertEqual(policy(456, 500)["regions"], ["R5"])
        self.assertEqual(policy(470, 500)["regions"], ["R5"])

    def test_degenerate_datums(self):
        self.assertEqual(policy(0, 500)["regions"], ["R4"])
        self.assertEqual(policy(500, 500)["regions"], ["R5"])


class CanonicalGrowCell(unittest.TestCase):
    def test_tick88_89_expected_reading_417_500(self):
        d = policy(417, 500)
        self.assertEqual(d["mode"], "grow")
        self.assertEqual(d["k_line_theo"], 1442)
        g = d["growth"]
        self.assertEqual(g["k_line_prac"], 1442)
        self.assertEqual(g["line_x_at_k"], 1203)
        self.assertEqual(g["region"], "R2")
        self.assertEqual(g["window"], (1203, 1250))
        self.assertEqual(g["total_arms"], 3)
        self.assertEqual(g["additional_arms"], 2)
        self.assertAlmostEqual(g["growth_wall_hours"], 2 * 2400 / 3600.0)

    def test_continuity_with_tick91_p0_line(self):
        g = grown_primary_attribution()
        self.assertEqual((g["k"], g["x"]), (1476, 1231))
        # Same arm count as the tick-91 primary line (3 arms); the k
        # differs only through the p-hat=0.834 vs p0=0.83376 rounding.
        self.assertEqual(arms_for_k(policy(417, 500)["growth"]["k_line_prac"]), 3)

    def test_arm_pricing_semantics(self):
        self.assertEqual(arms_for_k(1442), 3)
        self.assertAlmostEqual(serial_wall_hours(1442), 2.0)


class R1PointGrows(unittest.TestCase):
    def test_400_500_grows_to_r1(self):
        d = policy(400, 500)
        self.assertEqual(d["mode"], "grow")
        self.assertEqual(d["growth"]["region"], "R1")


class StageTwoLadder(unittest.TestCase):
    def test_probability_receipts(self):
        p50, p80, at = prob_scan(417 / 500.0, 500, at_k=1442)
        self.assertEqual(p50["k"], 1419)
        self.assertGreaterEqual(p50["p"], P50)
        self.assertEqual(p80["k"], 2895)
        self.assertGreaterEqual(p80["p"], P80)
        self.assertEqual(at["k"], 1442)
        self.assertEqual(round(at["p"], 3), 0.507)
        self.assertLessEqual(p80["k"], 6000)

    def test_probability_in_unit_range_and_monotone_cells(self):
        for k in (1000, 1442, 2000, 2895):
            p = attribution_probability(k, 417 / 500.0)
            self.assertTrue(0.0 <= p <= 1.0)
        self.assertGreaterEqual(
            attribution_probability(2895, 417 / 500.0),
            attribution_probability(1442, 417 / 500.0),
        )


class EdgePointingEscalation(unittest.TestCase):
    def test_407_500_is_stage3(self):
        d = policy(407, 500)
        self.assertEqual(d["mode"], "escalate_dispersion")
        self.assertIsNone(d["k_line_theo"])
        self.assertIn("0.81400", d["reason"])

    def test_report_carries_outside_cap_extrapolation(self):
        text = collection_report(407, 500)
        self.assertIn("outside-cap extrapolation", text)
        self.assertIn("k ~ 25849433", text)  # measure-then-pin
        self.assertIn("recommended path", text)


class PolicyTotality(unittest.TestCase):
    def test_total_over_first_arm_counts(self):
        for x1 in range(0, 501):
            d = policy(x1, 500)
            self.assertIn(
                d["mode"],
                ("verdict_ready", "grow", "escalate_dispersion"),
                x1,
            )
            if d["mode"] == "verdict_ready":
                self.assertTrue(d["regions"], x1)
            elif d["mode"] == "grow":
                self.assertGreaterEqual(d["growth"]["additional_arms"], 1, x1)
                self.assertLessEqual(d["growth"]["k_line_prac"], 6000, x1)


class ReportSmoke(unittest.TestCase):
    def test_canonical_report_lines(self):
        text = collection_report(417, 500)
        self.assertIn("region-ambiguous", text)
        self.assertIn("line k=1442", text)
        self.assertIn("0.507", text)
        self.assertIn("P>=0.80 (stage-2 decisive census) at k=2895", text)

    def test_verdict_ready_report_lines(self):
        text = collection_report(426, 500)
        self.assertIn("VERDICT-READY: CI inside R2", text)


if __name__ == "__main__":
    unittest.main()
