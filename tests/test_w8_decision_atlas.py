"""Pins for tools/w8_decision_atlas.py (tick 89 — measured 2026-10-09,
BEFORE the w8 datum exists; queued falsifier ed50c7ba...4daa85).
Every constant below is pinned from the tool's own measured output
(measure-then-pin) and cross-pinned to the tick-86/88 receipts."""
import sys
import unittest
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.w8_decision_atlas import (CEIL, FLOOR, MIN_EVENTS,
                                     PRIMARY, QUIET_CORE_K500,
                                     TREND_HI, TREND_LO,
                                     attribution_windows,
                                     region_of, reading, wilson95)
from tools.w8_datum_noise import (CEIL as DN_CEIL, FLOOR as DN_FLOOR,
                                  PRIMARY as DN_PRIMARY, compute as dn_compute)
from tools.w8_sensitivity import compute as sens_compute

DN = dn_compute()
SENS = sens_compute()
RB = SENS["reading_map"]["region_bounds_computed"]


class W8DecisionAtlasPins(unittest.TestCase):

    # --- identity pins: duplicated constants == receipts ----------
    def test_constants_match_tick86_88_modules(self):
        self.assertEqual((FLOOR, CEIL, PRIMARY), (DN_FLOOR, DN_CEIL,
                                                  DN_PRIMARY))
        self.assertEqual([TREND_LO, TREND_HI],
                         [RB["trend_band"][0], RB["overlap_A_and_C"][1]])
        self.assertEqual(QUIET_CORE_K500, DN["quiet_core_k500"])
        self.assertEqual(QUIET_CORE_K500, [0.81743, 0.85263])

    def test_wilson_helper_identity_anchor(self):
        # tick-87/88 anchor: the w1 census bracket 232:461
        self.assertEqual([round(v, 5) for v in wilson95(232, 461)],
                         [0.45777, 0.54868])

    # --- verdict: Fraction-exact at the k=500 gate edges -----------
    def test_verdict_fraction_exact_edges_k500(self):
        self.assertEqual(reading(391, 500)["verdict"], "REFUTED")
        self.assertEqual(reading(391, 500)["side"], "low")
        self.assertEqual(reading(392, 500)["verdict"], "HELD")
        self.assertEqual(reading(441, 500)["verdict"], "HELD")
        self.assertEqual(reading(442, 500)["verdict"], "REFUTED")
        self.assertEqual(reading(442, 500)["side"], "high")

    def test_region_map_five_regions(self):
        cases = [(392, 1, "form-ambiguous"), (435, 2, "hold-only"),
                 (375, 3, "trend-alive"), (340, 4, "chain-falsified"),
                 (460, 5, "unmodeled-acceleration")]
        for x, rid, name in cases:
            r = reading(x, 500)
            self.assertEqual(r["region"]["id"], rid, x)
            self.assertEqual(r["region"]["name"], name, x)

    def test_region_of_is_fraction_exact(self):
        self.assertEqual(region_of(Fraction(392, 500))["id"], 1)
        self.assertEqual(region_of(Fraction(391, 500))["id"], 3)
        self.assertEqual(region_of(Fraction(442, 500))["id"], 5)

    # --- attribution overlay (tick-88 rule, measured) --------------
    def test_center_datum_is_region_ambiguous_k500(self):
        # THE honest headline: the exact-center datum 417/500 = 0.834
        # cannot claim hold-only attribution — its Wilson-95 dips
        # below 0.81415 into the overlap.
        r = reading(417, 500)
        self.assertEqual(r["verdict"], "HELD")
        self.assertEqual(r["datum_wilson95_k500"], [0.79886, 0.86404])
        self.assertFalse(r["attribution"]["allowed"])
        self.assertEqual(r["attribution"]["else"],
                         "region-ambiguous at census k=500")

    def test_attribution_windows_k500_measured(self):
        w = attribution_windows(500)
        self.assertEqual(w["region2_hold-only"], [425, 427])
        self.assertEqual(w["region1_form-ambiguous"], [])
        self.assertEqual(w["region3_trend-alive"], [])
        # the window extremes satisfy the rule; just outside does not
        self.assertTrue(reading(425, 500)["attribution"]["allowed"])
        self.assertTrue(reading(427, 500)["attribution"]["allowed"])
        self.assertFalse(reading(424, 500)["attribution"]["allowed"])
        self.assertFalse(reading(428, 500)["attribution"]["allowed"])

    def test_attribution_windows_empty_at_min_events_floor(self):
        self.assertEqual(attribution_windows(50),
                         {"region1_form-ambiguous": [],
                          "region2_hold-only": [],
                          "region3_trend-alive": []})

    def test_high_held_datum_fails_ceiling_side(self):
        r = reading(440, 500)
        self.assertEqual(r["region"]["name"], "hold-only")
        self.assertEqual(r["datum_wilson95_k500"],
                         [0.84858, 0.90563])
        self.assertFalse(r["attribution"]["allowed"])

    # --- quiet core + refusal guards --------------------------------
    def test_quiet_core_membership_and_scope(self):
        self.assertIs(reading(417, 500)["quiet_core_k500"], True)
        self.assertIs(reading(392, 500)["quiet_core_k500"], False)
        r100 = reading(84, 100)
        self.assertIsNone(r100["quiet_core_k500"])
        self.assertIn("k=500 only", r100["quiet_core_note"])

    def test_no_events_refusal_below_protocol_floor(self):
        r = reading(20, 49)
        self.assertEqual(r["verdict"], "NO_EVENTS")
        self.assertIn("MIN_EVENTS", r["refusal"])
        r50 = reading(42, 50)      # exactly at the floor: reads
        self.assertEqual(r50["verdict"], "HELD")

    def test_input_guards(self):
        with self.assertRaises(ValueError):
            reading(5, 3)
        with self.assertRaises(TypeError):
            reading(0.5, 500)

    # --- fit-axis framing per branch ---------------------------------
    def test_fit_axis_lines_per_branch(self):
        self.assertIn("0.02481", reading(417, 500)["fit_axis"])
        self.assertIn("haz_l2[4]", reading(375, 500)["fit_axis"])
        self.assertIn("unmodeled acceleration",
                      reading(460, 500)["fit_axis"])
        for x in (417, 375, 460):
            self.assertIn("gate",
                          reading(x, 500)["gate_untouched"])


if __name__ == "__main__":
    unittest.main()
