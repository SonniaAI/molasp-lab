"""Pins for tools/w8_sensitivity.py — the pre-registered w8
extrapolation-form sensitivity (tick 86, 2026-10-09, BEFORE the datum).

Every constant below was read from the tool's output on the committed
VH_BASIS receipts (measure-then-claim).  The near-miss guard (test C
differs from A) exists because the first scratch implementation capped
the phase index at 4 (copying _vh_share's hold-last semantics), so the
alternative-arm branches never executed and every arm 'coincided'
with the primary at delta exactly 0.0 — a false insensitivity claim
caught before anything was committed.
"""
import json
import math
import unittest

from molasp.offchannel import VH_BASIS, _vh_share, marginal_window_pricing
import tools.w8_sensitivity as ws


class TestArms(unittest.TestCase):
    def setUp(self):
        self.out = ws.compute()

    def test_primary_identity(self):
        # Arm A must reproduce the committed primary exactly.
        self.assertEqual(self.out["primary"], 0.83376)
        self.assertLess(abs(ws._share(
            ws._integrate(lambda p: (VH_BASIS["haz_d2t"][min(p, 4)],
                                     VH_BASIS["haz_l2"][min(p, 4)]))[0])
            - _vh_share(8)), 1e-12)

    def test_bracket_identity(self):
        b = [a for a in self.out["arms"] if a["arm"] == "B hazard95-d2t"][0]
        self.assertEqual(b["w8"],
                         round(marginal_window_pricing()["windows"]["8"]
                               ["hazard95_share"], 5))

    def test_arm_values_pinned(self):
        got = {a["arm"]: a["w8"] for a in self.out["arms"]}
        self.assertEqual(got["A hold-last"], 0.83376)
        self.assertEqual(got["B hazard95-d2t"], 0.81585)
        self.assertEqual(got["C l2-loglinear-trend"], 0.76415)
        self.assertEqual(got["D l2-zero-beyond-w4"], 0.62767)

    def test_arms_actually_differ_from_primary(self):
        # The near-miss guard: capping phase at 4 makes C and D equal A.
        got = {a["arm"]: a["w8"] for a in self.out["arms"]}
        self.assertGreater(abs(got["C l2-loglinear-trend"]
                               - got["A hold-last"]), 0.05)
        self.assertGreater(abs(got["D l2-zero-beyond-w4"]
                               - got["A hold-last"]), 0.05)

    def test_not_all_forms_inside_primary_band(self):
        # The headline: hazard-form choice is decision-relevant.
        self.assertFalse(self.out["all_forms_inside_primary_band"])
        self.assertEqual(self.out["hazard_form_spread"], 0.20609)

    def test_reading_map_bounds(self):
        rb = self.out["reading_map"]["region_bounds_computed"]
        self.assertEqual(rb["primary_band"], [0.78376, 0.88376])
        self.assertEqual(rb["trend_band"], [0.71415, 0.81415])
        self.assertEqual(rb["overlap_A_and_C"], [0.78376, 0.81415])
        regions = {r["s"]: r["verdict"] for r in
                   self.out["reading_map"]["regions"]}
        self.assertEqual(len(regions), 5)
        self.assertEqual(regions["[0.71415, 0.78376)"], "REFUTED")
        self.assertEqual(regions["[0.78376, 0.81415]"], "HELD")

    def test_stationary_ceiling_anchor(self):
        self.assertEqual(self.out["stationary_ceiling_hold_last"], 0.97865)

    def test_attach_odds_and_trend_hazards(self):
        self.assertEqual(self.out["attach_odds_pair_share"], 0.52045)
        t = self.out["trend_l2_hazards_5_to_8"]
        self.assertEqual(t["5"], "2.1915e-08")
        # The trend must be monotonically decreasing beyond w4 and
        # strictly below the held phase-4 hazard.
        h4 = VH_BASIS["haz_l2"][4]
        vals = [float(t[str(p)]) for p in (5, 6, 7, 8)]
        self.assertTrue(all(v < h4 for v in vals))
        self.assertEqual(vals, sorted(vals, reverse=True))

    def test_basis_unmutated(self):
        snap = json.dumps(
            {k: VH_BASIS[k] for k in ("haz_d2t", "haz_l2", "v0", "p")},
            sort_keys=True)
        ws.compute()
        self.assertEqual(snap, json.dumps(
            {k: VH_BASIS[k] for k in ("haz_d2t", "haz_l2", "v0", "p")},
            sort_keys=True))

    def test_deterministic(self):
        self.assertEqual(json.dumps(ws.compute(), sort_keys=True),
                         json.dumps(self.out, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
