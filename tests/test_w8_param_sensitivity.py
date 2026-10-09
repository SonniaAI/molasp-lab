"""Pins for tools/w8_param_sensitivity.py (tick 87 — measured
2026-10-09, BEFORE the w8 datum exists).  Every constant below is
pinned from the tool's own output (measure-then-pin)."""
import json
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from molasp.offchannel import _vh_share
from tools.w8_param_sensitivity import (BAND, PRIMARY, _integrate,
                                        _wilson95, compute)

OUT = compute()


class W8ParamSensitivityPins(unittest.TestCase):

    def test_baseline_identity_with_vh_share(self):
        self.assertAlmostEqual(_integrate(), _vh_share(8), places=12)
        self.assertEqual(OUT["baseline_w8"], 0.83376)
        self.assertEqual(abs(OUT["baseline_w8"] - PRIMARY) < 5e-6, True)

    def test_wilson_bounds_pinned(self):
        lo, hi = _wilson95(232, 461)
        self.assertEqual(round(lo, 5), 0.45777)
        self.assertEqual(round(hi, 5), 0.54868)
        bc = OUT["v0_census_bracket"]
        self.assertEqual(bc["wilson95"], [0.45777, 0.54868])

    def test_v0_bracket_subdominant(self):
        bc = OUT["v0_census_bracket"]
        self.assertEqual(bc["w8_at_lo"], 0.82807)
        self.assertEqual(bc["w8_at_hi"], 0.85288)
        self.assertEqual(bc["induced_width"], 0.02481)
        # the ONLY quotable fit-uncertainty moves w8 by less than half
        # the frozen band halfwidth — initial conditions cannot create
        # or rescue a verdict
        self.assertLess(bc["induced_width"], 0.5 * BAND)
        # and the whole bracket stays inside the HELD region
        self.assertGreater(bc["w8_at_lo"], PRIMARY - BAND)
        self.assertLess(bc["w8_at_hi"], PRIMARY + BAND)

    def test_odds_probes_pinned(self):
        arms = {a["delta"]: a["w8"] for a in OUT["attach_odds_probes"]["arms"]}
        self.assertEqual(arms[-0.04], 0.81664)
        self.assertEqual(arms[-0.01], 0.82963)
        self.assertEqual(arms[0.01], 0.8378)
        self.assertEqual(arms[0.04], 0.84939)
        self.assertEqual(OUT["attach_odds_probes"]["induced_width_pm0.04"],
                         0.03275)
        # perturbations actually reach the computation (tick-86 guard)
        self.assertGreater(abs(arms[-0.04] - OUT["baseline_w8"]), 0.01)
        self.assertGreater(abs(arms[0.04] - OUT["baseline_w8"]), 0.01)
        # monotone increasing in odds
        seq = [arms[d] for d in (-0.04, -0.02, -0.01, 0.01, 0.02, 0.04)]
        self.assertEqual(seq, sorted(seq))

    def test_odds_probes_cannot_reach_refutation(self):
        # no odds probe within +/-0.04 reaches below the frozen floor:
        # a REFUTED-low datum is NOT explainable by an attach-odds miss
        # at this scale — it indicts the L2 leak (form or fit)
        arms = [a["w8"] for a in OUT["attach_odds_probes"]["arms"]]
        self.assertGreater(min(arms), PRIMARY - BAND)

    def test_l2_scale_arms_pinned_and_monotone(self):
        arms = {a["factor"]: a["w8"]
                for a in OUT["haz_l2_4_scale_probes"]["arms"]}
        self.assertEqual(arms[0.5], 0.77699)   # BELOW the frozen floor
        self.assertEqual(arms[0.75], 0.80753)
        self.assertEqual(arms[1.25], 0.85628)
        self.assertEqual(arms[1.5], 0.87563)
        self.assertEqual(arms[2.0], 0.90655)   # ABOVE the frozen ceiling
        self.assertEqual(OUT["haz_l2_4_scale_probes"]
                         ["induced_width_x0.5_to_x2"], 0.12956)
        seq = [arms[f] for f in (0.5, 0.75, 1.25, 1.5, 2.0)]
        self.assertEqual(seq, sorted(seq))

    def test_l2_x05_crosses_the_frozen_floor(self):
        arms = {a["factor"]: a["w8"]
                for a in OUT["haz_l2_4_scale_probes"]["arms"]}
        self.assertLess(arms[0.5], PRIMARY - BAND)
        self.assertGreater(arms[0.75], PRIMARY - BAND)
        self.assertGreater(arms[2.0], PRIMARY + BAND)

    def test_d2t_hazard_is_share_weak(self):
        self.assertEqual(OUT["haz_d2t_4_x2"]["w8"], 0.82614)
        self.assertLess(abs(OUT["haz_d2t_4_x2"]["dev"]), 0.01)

    def test_l2_grid_x2_outside_band(self):
        self.assertEqual(OUT["haz_l2_grid_x2"]["w8"], 0.94351)
        self.assertGreater(OUT["haz_l2_grid_x2"]["dev"], 2 * BAND)

    def test_elasticity_ranking(self):
        e = OUT["elasticities_d_ln_s8_d_ln_param"]
        self.assertEqual(e["odds"], 0.255)
        self.assertEqual(e["haz_l2[4]"], 0.116)
        self.assertEqual(e["haz_d2t[4]"], -0.009)
        self.assertEqual(e["lam"], 0.0)
        self.assertGreater(e["odds"], e["haz_l2[4]"])
        self.assertGreater(e["haz_l2[4]"], abs(e["haz_d2t[4]"]))

    def test_lam_ratio_cancellation_explained_not_dead(self):
        lc = OUT["lam_ratio_cancellation"]
        # the perturbation reaches the computation: E mass HALVES
        # under lam x2 (quasi-steady E ~ 1/lam) ...
        self.assertAlmostEqual(float(lc["E_mass_base_w8"])
                               / float(lc["E_mass_lam_x2_w8"]),
                               2.0, delta=0.01)
        # ... while the share residual stays 4 orders below the odds
        # elasticity's unit effect (measured, not asserted equality)
        self.assertEqual(lc["residual_abs_x2"], 4.215e-05)
        self.assertLess(lc["residual_abs_x2"], 1e-4)
        self.assertEqual(lc["share_base"], 0.83376036)
        self.assertEqual(lc["share_lam_x2"], 0.83380251)

    def test_output_shape(self):
        for key in ("registered", "frozen_gate", "baseline_w8",
                    "v0_census_bracket", "attach_odds_probes",
                    "haz_l2_4_scale_probes", "haz_d2t_4_x2",
                    "haz_l2_grid_x2", "elasticities_d_ln_s8_d_ln_param",
                    "lam_ratio_cancellation", "for_comparison_tick86"):
            self.assertIn(key, OUT)
        self.assertIn("BEFORE the w8 datum exists", OUT["registered"])
        fc = OUT["for_comparison_tick86"]
        self.assertEqual(fc["hazard_form_spread"], 0.20609)
        self.assertEqual(fc["band_halfwidth"], BAND)


if __name__ == "__main__":
    unittest.main()
