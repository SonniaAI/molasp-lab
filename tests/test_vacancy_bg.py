"""Receipt pins for the tick-41 vacancy-background probe
(evidence/2026-10-07-vacancy-background/).  Verdicts as REGISTERED
in the pre-registered script header (commit aeb3fe0) — including the
two INCONCLUSIVEs and the FALSIFIED, which carry the finding."""

import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE), "evidence",
                  "2026-10-07-vacancy-background")


def _load():
    recs = {}
    verdicts = None
    with open(os.path.join(EV, "vacancy_bg.out")) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            body = line[9:] if line.startswith("VERDICTS ") else line
            d = json.loads(body)
            if "arm" in d:
                recs[d["arm"]] = d
            else:
                verdicts = d
    with open(os.path.join(EV, "queue-receipt.json")) as fh:
        receipt = json.load(fh)
    return recs, verdicts, receipt


class TestVacancyBackgroundReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recs, cls.verdicts, cls.receipt = _load()
        cls.s2 = cls.recs["s2_b1_Vp"]
        cls.fam = cls.recs["fam_b1_Vp"]

    def test_vb1_calibration_confirmed(self):
        self.assertEqual(self.verdicts["VB1"], "CONFIRMED")
        self.assertLess(abs(self.s2["fill_frac"] - 0.412), 0.07)
        self.assertLess(abs(self.s2["L3_term_frac"] - 0.164), 0.08)

    def test_vb2_every_terminal_l3_is_west_dbr_enabled(self):
        self.assertEqual(self.verdicts["VB2"], "CONFIRMED")
        self.assertEqual(self.s2["west_match_of_L3"], 1.0)
        self.assertEqual(self.s2["L3_matched_faces"], {"W->DBr": 78})
        self.assertEqual(
            round(self.s2["L3_term_frac"] * self.s2["n"]), 78)

    def test_vb3_registered_inconclusive_starvation_is_multichannel(self):
        # As registered: fn=0.481 < 0.70 fails CONFIRM; fg=0.0 is far
        # below fn-0.05 so not FALSIFIED either. The residual is the
        # second channel: the via-site L2 squatter at the west site.
        self.assertEqual(self.verdicts["VB3"], "INCONCLUSIVE")
        self.assertEqual(self.s2["fill_given_L3"], 0.0)
        self.assertLess(self.s2["fill_given_noL3"], 0.70)
        self.assertGreaterEqual(
            self.s2["west_site_occupants"]["L2"], 100)

    def test_vb4_registered_inconclusive_dwell_clause_miscalibrated(self):
        # Stable clause passes outright (frozen when present); the
        # dwell clause divided the L3 dwell by ALL n=500 trajectories,
        # so it can never reach 0.5 at a 0.16 carrier rate. Verdict
        # stays INCONCLUSIVE as registered; no post-hoc promotion.
        self.assertEqual(self.verdicts["VB4"], "INCONCLUSIVE")
        self.assertEqual(self.s2["L3_stable_of_term"], 1.0)
        self.assertLess(self.s2["mean_L3_dwell_over_read"], 0.5)

    def test_vb5_falsified_accretion_not_race(self):
        self.assertEqual(self.verdicts["VB5"], "FALSIFIED")
        self.assertLessEqual(self.s2["race_L3_first_frac"], 0.5)
        # Family contrast: L3 attaches FIRST in 72% of double-event
        # trajectories yet is NEVER terminal there — the transient
        # class predates s2; s2 freezes it, it does not speed it.
        self.assertGreaterEqual(self.fam["race_L3_first_frac"], 0.6)
        self.assertEqual(self.fam["L3_term_frac"], 0.0)

    def test_fam_reference_calibration(self):
        self.assertLess(abs(self.fam["fill_frac"] - 0.904), 0.05)

    def test_queue_receipt_pinned(self):
        r = self.receipt
        self.assertEqual(r["execution_status"], 0)
        self.assertEqual(r["nonce"], "vacancy-bg-v1")
        self.assertEqual(r["image"], "paperclip-test")
        self.assertEqual(r["pre_registration_commit"], "aeb3fe0")
        self.assertTrue(r["request_id"].startswith(
            r["job"].replace("hxq-", "")))
        self.assertEqual(
            r["command"],
            ["python3",
             "source/evidence/2026-10-07-vacancy-background/"
             "ktam_vacancy_bg.py"])


if __name__ == "__main__":
    unittest.main()
