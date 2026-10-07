"""Receipt pins for the contention dG/read-window sweep (tick 43).

Every number below quotes evidence/2026-10-07-contention-dg-sweep/
contention_dg.out at quote precision (3 decimals) — comparisons use
the same rounding so a float-serialization drift cannot fire a pin
(tick-25/tick-42 lesson).  Queue identity pins live in the same
directory's queue-receipt.json.
"""
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.join(os.path.dirname(HERE), "evidence",
                    "2026-10-07-contention-dg-sweep")


def _load():
    arms = {}
    verdicts = None
    path = os.path.join(EVID, "contention_dg.out")
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("{"):
                continue
            rec = json.loads(line)
            if "arm" in rec:
                arms[rec["arm"]] = rec
            elif "DW1" in rec:
                verdicts = rec
    return arms, verdicts


class TestContentionDgReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arms, cls.verdicts = _load()

    def test_out_has_nine_arms_and_verdicts(self):
        self.assertEqual(len(self.arms), 9)
        self.assertIsNotNone(self.verdicts)
        self.assertEqual(
            sorted(self.verdicts),
            ["DW1", "DW2", "DW3", "DW4", "DW5", "DW6", "DW7"])

    def test_calibration_dw1_cross_seed_replication(self):
        self.assertEqual(round(self.arms["fam_dg0.5"]["fill_frac"], 3),
                         0.904)
        self.assertEqual(round(self.arms["s2_dg0.5"]["fill_frac"], 3),
                         0.412)
        self.assertEqual(self.verdicts["DW1"], "CONFIRMED")

    def test_recovery_dw2_three_regimes(self):
        self.assertEqual(round(self.arms["s2_dg0.5"]["fill_frac"], 3),
                         0.412)
        self.assertEqual(round(self.arms["s2_dg2"]["fill_frac"], 3),
                         0.464)
        self.assertEqual(round(self.arms["s2_dg4"]["fill_frac"], 3),
                         0.564)
        self.assertEqual(self.verdicts["DW2"], "CONFIRMED")

    def test_churn_dw3_ratio(self):
        hi = self.arms["s2_dg4"]["churn_per_read"]
        lo = self.arms["s2_dg0.5"]["churn_per_read"]
        self.assertGreater(hi / lo, 5.0)
        self.assertEqual(self.verdicts["DW3"], "CONFIRMED")

    def test_persistence_dw4_first_come_collapse(self):
        self.assertEqual(
            round(self.arms["s2_dg0.5"]["first_stable_persist"], 3),
            0.872)
        self.assertEqual(
            round(self.arms["s2_dg4"]["first_stable_persist"], 3),
            0.288)
        self.assertEqual(self.verdicts["DW4"], "CONFIRMED")

    def test_window_dw5_helps_s2_only(self):
        self.assertEqual(
            round(self.arms["s2_dg4_win4"]["fill_frac"], 3), 0.798)
        self.assertEqual(
            round(self.arms["fam_dg4_win4"]["fill_frac"], 3), 0.054)
        self.assertEqual(self.verdicts["DW5"], "CONFIRMED")

    def test_family_floor_dw6_falsified_at_dg4(self):
        self.assertEqual(round(self.arms["fam_dg4"]["fill_frac"], 3),
                         0.074)
        self.assertLess(self.arms["fam_dg4"]["fill_frac"], 0.70)
        self.assertEqual(
            round(self.arms["fam_dg4"]["site_dwell_frac"], 3), 0.113)
        self.assertEqual(
            round(self.arms["s2_dg4"]["site_dwell_frac"], 3), 0.967)
        self.assertEqual(self.verdicts["DW6"], "FALSIFIED")

    def test_starvation_dw7_total(self):
        self.assertEqual(round(self.arms["s2_dg7"]["fill_frac"], 3),
                         0.0)
        self.assertEqual(
            self.arms["s2_dg7"]["site_occupants"]["None"], 500)
        self.assertEqual(self.verdicts["DW7"], "CONFIRMED")

    def test_marginal_coin_is_near_fair(self):
        occ = self.arms["s2_dg2"]["site_occupants"]
        self.assertEqual(occ["D2T"], 232)
        self.assertEqual(occ["L2"], 229)

    def test_frozen_regime_minted_classes(self):
        occ = self.arms["s2_dg0.5"]["site_occupants"]
        self.assertEqual(occ["D2T"], 206)
        self.assertEqual(occ["L2"], 149)
        self.assertEqual(occ["DBr"], 82)


class TestContentionDgQueueReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(EVID, "queue-receipt.json")) as fh:
            cls.receipt = json.load(fh)

    def test_job_identity(self):
        self.assertEqual(self.receipt["job"],
                         "hxq-05864a1974ee155e")
        self.assertEqual(self.receipt["nonce"], "contention-dg-v1")
        self.assertEqual(self.receipt["state"], "complete")
        self.assertEqual(self.receipt["exit_status"], 0)
        self.assertEqual(self.receipt["n_per_arm"], 500)
        self.assertEqual(self.receipt["seed_base"], 200261107)

    def test_pre_registration_head(self):
        self.assertEqual(self.receipt["pre_registration_commit"],
                         "236f91beaa603e78126a27f69af4edd8cb99c82e")
        self.assertEqual(self.receipt["archive_head"],
                         self.receipt["pre_registration_commit"])

    def test_command_matches_out_location(self):
        cmd = self.receipt["command"]
        self.assertEqual(cmd[0], "python3")
        self.assertTrue(cmd[1].endswith(
            "evidence/2026-10-07-contention-dg-sweep/"
            "ktam_contention_dg.py"))


if __name__ == "__main__":
    unittest.main()
