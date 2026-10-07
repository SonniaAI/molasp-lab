"""Tick-44 pins: the compiler-facing contention severity ranking
WITH the dG axis (designs/007 closure).  Every number quoted here is
measured — REGIME_ANCHORS replicate contention_dg.out verbatim
(n=500/arm), and the BUILD1/2 tier pins must reproduce the tick-42/43
stories (minting over a family fill; family floor collapse at dG 4).
Static arithmetic only — no cluster job (tick-37 rule)."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

if REPO not in sys.path:
    sys.path.insert(0, REPO)
SIB_AND = os.path.join(REPO, "evidence",
                       "2026-10-06-body-conjunction-builds")
if SIB_AND not in sys.path:
    sys.path.insert(0, SIB_AND)

from tiles_and import BUILD1, BUILD2, BUILD3        # noqa: E402
from molasp import offchannel as oc                 # noqa: E402


class TestRegimeAnchors(unittest.TestCase):
    """The anchors ARE the sweep receipt — quoted verbatim."""

    def test_anchors_verbatim(self):
        self.assertEqual(oc.REGIME_ANCHORS["frozen"], {
            "dg": 0.5, "family_fill": 0.904, "knob_fill": 0.412,
            "family_persist": 0.542, "knob_persist": 0.872,
            "site_dwell": 0.994,
            "source": "contention_dg.out fam_dg0.5/s2_dg0.5"})
        self.assertEqual(oc.REGIME_ANCHORS["marginal"], {
            "dg": 2.0, "family_fill": 0.97, "knob_fill": 0.464,
            "family_persist": 0.088, "knob_persist": 0.52,
            "reroll_split": "D2T 232 : L2 229",
            "source": "contention_dg.out fam_dg2/s2_dg2"})
        self.assertEqual(oc.REGIME_ANCHORS["churn"], {
            "dg": 4.0, "family_fill": 0.074, "knob_fill": 0.564,
            "family_dwell": 0.113, "knob_dwell": 0.967,
            "family_partial": 0.633,
            "win4_family_fill": 0.054, "win4_knob_fill": 0.798,
            "source": "contention_dg.out fam_dg4/s2_dg4(/_win4)"})
        self.assertEqual(oc.REGIME_ANCHORS["starvation"], {
            "dg": 7.0, "family_fill": 0.0, "knob_fill": 0.0,
            "partial": 0.0008, "persist_n": 1,
            "source": "contention_dg.out s2_dg7"})

    def test_regime_at_boundaries(self):
        # midpoints of measured 0.5/2/4/7; measured points exact
        for dg, reg, interp in [
                (0.5, "frozen", False), (0.9, "frozen", True),
                (2.0, "marginal", False), (1.5, "marginal", True),
                (4.0, "churn", False), (3.7, "churn", True),
                (7.0, "starvation", False), (9.0, "starvation", True)]:
            self.assertEqual(oc.regime_at(dg), (reg, interp), dg)

    def test_knob_verdicts(self):
        self.assertEqual(oc.KNOB_VERDICTS["frozen"], "hazard")
        self.assertEqual(oc.KNOB_VERDICTS["marginal"], "hazard")
        self.assertEqual(oc.KNOB_VERDICTS["churn"], "mitigation")
        self.assertEqual(oc.KNOB_VERDICTS["starvation"], "moot")


class TestSeverityTiers(unittest.TestCase):
    """Tier logic on the measured BUILD1 story (tick 42 + 43)."""

    @classmethod
    def setUpClass(cls):
        cls.canon = oc.canonical_assembly(BUILD1)

    def test_build1_vp_frozen_critical(self):
        # minted {D1T,DBr,V0p} over family fill D2T (0.904->0.412)
        s = oc.contention_severity(BUILD1, dg=0.5, canon=self.canon)
        self.assertEqual(s["regime"], "frozen")
        self.assertFalse(s["interpolated"])
        v = s["vacancies"]["Vp"]["2,2"]
        self.assertEqual(v["tier"], "critical")
        self.assertEqual(v["minted"], ["D1T", "DBr", "V0p"])
        self.assertEqual(v["family_stable"], ["D2T", "L2"])

    def test_build1_vp_marginal_still_critical(self):
        # the lottery survives as a stationary split (232:229)
        s = oc.contention_severity(BUILD1, dg=2.0, canon=self.canon)
        self.assertEqual(s["regime"], "marginal")
        self.assertEqual(s["vacancies"]["Vp"]["2,2"]["tier"],
                         "critical")

    def test_build1_vp_churn_mitigating(self):
        # principle #7: knob sign flips — the growth carrier at dG 4
        s = oc.contention_severity(BUILD1, dg=4.0, canon=self.canon)
        self.assertEqual(s["regime"], "churn")
        self.assertEqual(s["knob_verdict"], "mitigation")
        v = s["vacancies"]["Vp"]["2,2"]
        self.assertEqual(v["tier"], "mitigating")
        self.assertIn("D2T", v["s2_stable"])

    def test_build1_vp_starvation_moot(self):
        s = oc.contention_severity(BUILD1, dg=7.0, canon=self.canon)
        self.assertEqual(s["knob_verdict"], "moot")
        self.assertEqual(s["vacancies"]["Vp"]["2,2"]["tier"], "moot")
        self.assertIn("refuse the operating point",
                      s["vacancies"]["Vp"]["2,2"]["note"])

    def test_lock_vacancy_frozen_high(self):
        # lock vacancies mint with NO family fill (first-come among
        # squatters; tick-42: 0 -> 3-6 frozen contenders)
        s = oc.contention_severity(BUILD1, dg=0.5, canon=self.canon)
        v = s["vacancies"]["L3"]["3,3"]
        self.assertEqual(v["tier"], "high")
        self.assertEqual(v["family_stable"], [])
        self.assertTrue(len(v["minted"]) >= 3)

    def test_interpolated_flag_and_boundary_notes(self):
        s = oc.contention_severity(BUILD1, dg=1.5, canon=self.canon)
        self.assertTrue(s["interpolated"])
        joined = " ".join(s["boundary_notes"])
        self.assertIn("dG-2 window arm is untested", joined)
        self.assertIn("persist_n=1", joined)
        self.assertIn("outside the tick-42 five-name", joined)


class TestSeverityIntegration(unittest.TestCase):
    """check_d4 auto-attachment + report lines; generality."""

    def test_check_d4_carries_severity_at_default_dg(self):
        rep = oc.check_d4(BUILD1)
        sev = rep["contention_severity"]
        self.assertEqual(sev["dg"], oc.DEFAULT_DG)
        self.assertEqual(sev["regime"], "frozen")
        self.assertEqual(sev["knob_verdict"], "hazard")

    def test_report_lines_name_regime_and_tier(self):
        lines = oc.d4_report_lines(oc.check_d4(BUILD1))
        self.assertTrue(
            any("contention severity at dG 0.5" in ln
                and "regime frozen" in ln
                and "verdict: hazard" in ln for ln in lines))
        self.assertTrue(
            any("Vp-missing @2,2: tier critical" in ln for ln in lines))

    def test_build2_minting_generalises(self):
        s = oc.contention_severity(BUILD2, dg=0.5)
        v = s["vacancies"]["Vp"]["2,2"]
        self.assertEqual(v["tier"], "critical")
        self.assertIn("D3F", v["minted"])
        self.assertIn("Fr", v["minted"])

    def test_build3_tiers_valid_and_minting_constructional(self):
        s = oc.contention_severity(BUILD3, dg=0.5)
        allowed = {"critical", "high", "moderate", "low"}
        tiers = [x["tier"]
                 for sites in s["vacancies"].values()
                 for x in sites.values()]
        self.assertTrue(tiers)
        self.assertTrue(set(tiers) <= allowed)
        self.assertTrue(
            any(x["tier"] in ("critical", "high")
                for sites in s["vacancies"].values()
                for x in sites.values()))

    def test_deterministic(self):
        a = oc.contention_severity(BUILD1, dg=2.0)
        b = oc.contention_severity(BUILD1, dg=2.0)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
