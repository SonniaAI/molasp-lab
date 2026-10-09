"""Pins for tools/w8_datum_noise.py (tick 88 — measured 2026-10-09,
BEFORE the w8 datum exists).  Every constant below is pinned from the
tool's own output (measure-then-pin)."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.w8_datum_noise import (BAND, CENSUSES, CEIL, FLOOR, PRIMARY,
                                  _max_x_below, _p_le, _wilson95,
                                  compute)

OUT = compute()
F500 = OUT["verdict_flip_risks"]["floor"][5]     # k=500 block
C500 = OUT["verdict_flip_risks"]["ceiling"][5]   # k=500 block


class W8DatumNoisePins(unittest.TestCase):

    def test_wilson_pins_and_shrinkage(self):
        self.assertEqual(OUT["wilson95"]["k500_s0.83376"],
                         [0.79886, 0.86404, 0.06518])
        self.assertEqual(OUT["wilson95"]["k100_s0.83376"],
                         [0.74452, 0.89107, 0.14655])
        self.assertEqual(OUT["wilson95"]["k50_s0.83376"],
                         [0.71486, 0.91663, 0.20177])
        w500 = OUT["wilson95"]["k500_s0.83376"][2]
        self.assertEqual(round(w500 / 2.0 / BAND, 4), 0.6518)  # 65% of halfwidth

    def test_wilson_helper_identity_with_tick87(self):
        lo, hi = _wilson95(232, 461)
        self.assertEqual(round(lo, 5), 0.45777)
        self.assertEqual(round(hi, 5), 0.54868)

    def test_fraction_exact_gate_thresholds(self):
        self.assertEqual(_max_x_below(500, "0.78376"), 391)
        self.assertEqual(_max_x_below(500, "0.88376"), 441)
        # exact-integer edge: 78/100 == edge is the HELD side
        self.assertEqual(_max_x_below(100, "0.78"), 77)
        self.assertEqual(F500["x_threshold"], 391)
        self.assertEqual(C500["x_threshold"], 441)

    def test_floor_flip_pins(self):
        self.assertEqual(round(F500["false_refuted_+0.010"], 5), 0.27372)
        self.assertEqual(round(F500["false_held_+0.010"], 5), 0.31336)
        self.assertEqual(round(F500["false_refuted_+0.030"], 5), 0.04063)
        self.assertEqual(F500["side"], "lo")

    def test_ceiling_orientation_pins(self):
        self.assertEqual(C500["side"], "hi")
        self.assertEqual(round(C500["false_refuted_+0.010"], 5), 0.27036)
        self.assertEqual(round(C500["false_held_+0.010"], 5), 0.21524)
        self.assertEqual(round(C500["false_refuted_+0.030"], 5), 0.02932)

    def test_edge_coincidence_is_fifty_fifty(self):
        # orientation guard: AT a gate edge both verdicts are ~50/50
        mid = _p_le(500, 0.88376, 441)
        self.assertGreater(mid, 0.45)
        self.assertLess(mid, 0.55)
        mid2 = _p_le(500, 0.78376, 391)
        self.assertGreater(mid2, 0.45)
        self.assertLess(mid2, 0.55)

    def test_flips_strictly_monotone_and_alive(self):
        # tick-86/87 guard: a perturbation that changes nothing is a
        # bug smell — every flip risk is strictly interior and shrinks
        # as the true share moves away from the edge.
        for block in (F500, C500):
            fr = [block["false_refuted_%+.3f" % d] for d in
                  (0.005, 0.010, 0.020, 0.030)]
            fh = [block["false_held_%+.3f" % d] for d in
                  (0.005, 0.010, 0.020, 0.030)]
            for series in (fr, fh):
                for v in series:
                    self.assertGreater(v, 0.0)
                    self.assertLess(v, 1.0)
                self.assertEqual(series, sorted(series, reverse=True))

    def test_quiet_core_pin(self):
        self.assertEqual(OUT["quiet_core_k500"], [0.81743, 0.85263])
        self.assertLess(OUT["quiet_core_k500"][0], PRIMARY)
        self.assertGreater(OUT["quiet_core_k500"][1], PRIMARY)
        # empty at the MIN_EVENTS floor census
        q50 = compute()["quiet_core_k500"]  # determinism re-check
        self.assertEqual(q50, OUT["quiet_core_k500"])

    def test_resolvability_pins(self):
        r = OUT["resolvability"][500]["region_form_ambiguous"]
        self.assertEqual(r["width"], 0.03039)
        self.assertEqual(r["wilson95_width_at_k"], 0.07026)
        self.assertEqual(r["resolvable_at_k"], False)
        self.assertEqual(r["k_needed_point_estimate"], 2673)
        h = OUT["resolvability"][500]["region_held_hold_only"]
        self.assertEqual(h["resolvable_at_k"], True)
        self.assertEqual(h["k_needed_point_estimate"], 407)
        self.assertEqual(
            OUT["resolvability"][50]["region_form_ambiguous"]
            ["resolvable_at_k"], False)

    def test_quiet_core_empty_at_min_events(self):
        from tools.w8_datum_noise import _quiet_edge
        self.assertIsNone(_quiet_edge(50, "0.78376", FLOOR, "lo"))
        self.assertIsNone(_quiet_edge(50, "0.88376", CEIL, "hi"))

    def test_p_le_extremes(self):
        self.assertEqual(_p_le(10, 0.5, -1), 0.0)
        self.assertEqual(_p_le(10, 0.5, 10), 1.0)

    def test_overlay_names_the_discipline(self):
        ov = OUT["reading_overlay"]
        self.assertIn("region-ambiguous", ov)
        self.assertIn("untouched", ov)
        self.assertIn("VERDICT", ov)


if __name__ == "__main__":
    unittest.main()
