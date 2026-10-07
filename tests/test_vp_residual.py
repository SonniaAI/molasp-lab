"""Vp-residual dissection pins (tick 27, SON-4778).

Receipt pins on evidence/2026-10-07-vp-residual/vp_residual.out once
collected (skipped until it exists). The pre-registered script and
verdict gates live in the same directory (ktam_mc_vp_residual.py,
landed at 295fbf8 BEFORE the job ran); the queue receipt is
queue-receipt.json (job hxq-12ce8d979f6f5070, nonce vp-residual-v1).
"""
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE), "evidence",
                  "2026-10-07-vp-residual")
OUT = os.path.join(EV, "vp_residual.out")


class TestVpResidualReceipt(unittest.TestCase):
    """Receipt pins — active only after the queue job is collected."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(OUT):
            raise unittest.SkipTest("vp_residual.out not collected yet")
        cls.header = None
        cls.rows = {}
        cls.verdicts = None
        with open(OUT, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                if "n_per_arm" in d:
                    cls.header = d
                elif "verdicts" in d:
                    cls.verdicts = d["verdicts"]
                elif "system" in d:
                    cls.rows[d["key"]] = d

    def test_protocol_of_record(self):
        self.assertEqual(self.header["n_per_arm"], 2000)
        self.assertEqual(self.header["seed_base"], 40261107)
        self.assertEqual(self.header["Gse"], 9.0)
        self.assertEqual(self.header["Gmc"], 9.5)
        self.assertEqual(set(self.rows), {"build1", "Vp"})
        for row in self.rows.values():
            self.assertEqual(row["n"], 2000)

    def test_p1_real(self):
        """The clean-conditional gap clears the 0.10 target at
        n=2000 — the Vp residual is not n=500 selection noise."""
        v = self.verdicts["P1"]
        self.assertEqual(v["call"], "real")
        self.assertGreaterEqual(v["gap"], 0.10)
        self.assertAlmostEqual(
            v["gap"], v["Vp_clean"] - v["build1_clean"], places=4)
        self.assertEqual(v["build1_clean"],
                         self.rows["build1"]["pqr_clean_frac"])
        self.assertEqual(v["Vp_clean"], self.rows["Vp"]["pqr_clean_frac"])

    def test_p2_delay(self):
        """Read-clean non-pqr trajectories dwell >= 2x longer in
        lock squats — the residual's signature is time, not death."""
        v = self.verdicts["P2"]
        self.assertEqual(v["call"], "delay")
        self.assertGreaterEqual(v["ratio"], 2.0)
        b = self.rows["build1"]
        self.assertEqual(v["clean_pqr_dwell_lock"],
                         b["clean_pqr"]["mean_dwell_lock"])
        self.assertEqual(v["clean_nonpqr_dwell_lock"],
                         b["clean_nonpqr"]["mean_dwell_lock"])

    def test_p3_calibrated(self):
        v = self.verdicts["P3"]
        self.assertEqual(v["call"], "calibrated")
        self.assertLessEqual(v["build1_dev"], 0.05)
        self.assertLessEqual(v["Vp_dev"], 0.05)
        ref = self.header["v2_reference_clean"]
        self.assertEqual(ref, {"build1": 0.7813, "Vp": 0.927})

    def test_build1_lock_squatters_reproduce_census(self):
        """The census's two named lock squatters are the two top
        trajectory squatters at n=2000, in census order."""
        sq = self.rows["build1"]["lock_squats"]
        self.assertEqual(sq["3,2:Vp"], 429)
        self.assertEqual(sq["3,1:V0p"], 259)
        self.assertGreater(sq["3,2:Vp"], sq["3,1:V0p"])

    def test_d2t_fills_vp_vacancy(self):
        """R3b_Vp's substitution-repair fraction reproduces at
        n=2000 (90.1% at n=500 -> 89.9% here)."""
        vp = self.rows["Vp"]
        self.assertAlmostEqual(vp["vacancy_pqr"]["D2T"] / vp["pqr"],
                               0.899, delta=0.001)

    def test_misread_present_build1_absent_without_vp(self):
        """The L2@(3,3) structural misread rides build1 strict-pqr
        terminals; the Vp-missing arm has no lock squats in strict
        pqr at all — no Vp west enabler, no misread."""
        self.assertEqual(
            self.rows["build1"]["lock_squats_pqr"].get("3,3:L2"), 42)
        self.assertEqual(self.rows["Vp"]["lock_squats_pqr"], {})

    def test_blocking_collapses_without_vp(self):
        b1 = self.rows["build1"]["blocked_frac"]
        vp = self.rows["Vp"]["blocked_frac"]
        self.assertGreater(b1, 0.25)
        self.assertLess(vp, 0.10)


if __name__ == "__main__":
    unittest.main()
