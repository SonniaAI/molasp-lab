"""Row-scope kTAM validation pins (tick 31, SON-4778).

Receipt pins on evidence/2026-10-07-row-scope-ktam/row_scope.out once
collected (skipped until it exists). The pre-registered script and
verdict gates live in the same directory (ktam_row_scope.py, landed
at fb3e08e BEFORE the job ran). v1 (nonce row-scope-v1) failed on a
task-invocation path error (exit 2, script never ran); v2 re-ran the
BYTE-IDENTICAL archive (same content hash on both receipts) with the
corrected /work/source/... invocation — pinned here so the
pre-registration lineage is machine-checkable.
"""
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE), "evidence",
                  "2026-10-07-row-scope-ktam")
OUT = os.path.join(EV, "row_scope.out")


class TestRowScopeKtamReceipt(unittest.TestCase):
    """Receipt pins — active only after the queue job is collected."""

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(OUT):
            raise unittest.SkipTest("row_scope.out not collected yet")
        cls.header = None
        cls.rows = {}
        cls.verdicts = None
        with open(OUT, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("VERDICTS "):
                    cls.verdicts = json.loads(line[len("VERDICTS "):])
                    continue
                d = json.loads(line)
                if "n_per_arm" in d:
                    cls.header = d
                elif "system" in d:
                    cls.rows[d["key"]] = d

    def test_protocol_of_record(self):
        self.assertEqual(self.header["n_per_arm"], 500)
        self.assertEqual(self.header["seed_base"], 80261107)
        self.assertEqual(self.header["seed_stride"], 20000000)
        self.assertEqual(self.header["Gse"], 9.0)
        self.assertEqual(self.header["Gmc"], 9.5)
        self.assertEqual(
            set(self.rows),
            {"family_build1", "family_Vp", "family_L3",
             "row_build1", "row_Vp", "row_L3"})
        for row in self.rows.values():
            self.assertEqual(row["n"], 500)

    def test_static_prediction_carried_by_job(self):
        """The job itself carried the tick-29/30 static claim it was
        testing: row scope zeroes lock hazards and misreads (b>=2
        holds), family keeps exactly the census squatters."""
        static = self.header["static_prediction"]
        self.assertEqual(static["row_lock_hazards"], {})
        self.assertEqual(static["row_lock_misreads"], {})
        self.assertEqual(static["family_lock_hazards"],
                         {"3,1": {"V0p": 1}, "3,2": {"Vp": 1}})
        self.assertEqual(static["repair_bonds"]["family"],
                         {"D1T": 2, "D2T": 2})
        self.assertEqual(static["repair_bonds"]["row"],
                         {"D1T": 1, "D2T": 1})

    def test_rs1_falsified(self):
        """Row squat-block is NOT eliminated: 0.144 >= the 0.10
        falsifier. b=1 transient holds still occupy lock sites at
        read time despite zero static (b>=2) hazards."""
        v = self.verdicts["RS1"]
        self.assertEqual(v["call"], "falsified")
        self.assertEqual(v["row_build1_blocked_frac"],
                         self.rows["row_build1"]["blocked_frac"])
        self.assertGreaterEqual(v["row_build1_blocked_frac"], 0.10)

    def test_rs2_falsified(self):
        """A STABLE (b>=2) D2T repair channel survives row scope at
        0.162 over all terminals — elimination is falsified; raw
        fill 0.44 rides the expected b=1 transient occupancy."""
        v = self.verdicts["RS2"]
        self.assertEqual(v["call"], "falsified")
        self.assertEqual(v["row_Vp_D2T_stable_fill_all"],
                         self.rows["row_Vp"]["vacancy_stable_fill_all"])
        self.assertGreaterEqual(v["row_Vp_D2T_stable_fill_all"], 0.10)
        self.assertEqual(v["row_Vp_raw_fill_all"], 0.44)

    def test_rs3_confirmed(self):
        """No new channel opens: row L3 misread 0.0 <= 0.02 AND row
        build1 strict-pqr >= family - 0.10 (measured: +0.18 over)."""
        v = self.verdicts["RS3"]
        self.assertEqual(v["call"], "confirmed")
        self.assertEqual(v["row_L3_misread_frac"],
                         self.rows["row_L3"]["misread_frac"])
        self.assertLessEqual(v["row_L3_misread_frac"], 0.02)
        self.assertAlmostEqual(
            v["row_minus_family_pqr_frac"],
            self.rows["row_build1"]["pqr_frac"]
            - self.rows["family_build1"]["pqr_frac"],
            places=4)
        self.assertGreaterEqual(v["row_minus_family_pqr_frac"], -0.10)

    def test_rs4_calibrated(self):
        """Protocol calibrated against the v2 references: family
        build1 blocked within 0.05 of 0.314, family Vp strict-pqr
        fill within 0.10 of 0.901."""
        v = self.verdicts["RS4"]
        self.assertEqual(v["call"], "calibrated")
        self.assertLessEqual(
            abs(v["family_build1_blocked_frac"]
                - self.header["v2_reference"]["build1_blocked"]), 0.05)
        self.assertLessEqual(
            abs(v["family_Vp_D2T_fill_strict_pqr"]
                - self.header["v2_reference"]["Vp_fill_strict_pqr"]),
            0.10)

    def test_scope_trade_numbers(self):
        """The knob's measured effect at this protocol point: halve
        the squat-block, degrade stable repair 5.6x (not eliminate),
        kill the misread channel entirely, improve canonical pqr."""
        self.assertAlmostEqual(
            self.rows["family_build1"]["blocked_frac"], 0.27, places=4)
        self.assertAlmostEqual(
            self.rows["row_build1"]["blocked_frac"], 0.144, places=4)
        self.assertAlmostEqual(
            self.rows["family_Vp"]["vacancy_stable_fill_all"], 0.908,
            places=4)
        self.assertAlmostEqual(
            self.rows["row_Vp"]["vacancy_stable_fill_all"], 0.162,
            places=4)
        self.assertEqual(self.rows["family_L3"]["misread_frac"], 0.056)
        self.assertEqual(self.rows["row_L3"]["misread_frac"], 0.0)
        self.assertAlmostEqual(
            self.rows["family_Vp"]["vacancy_pqr"]["D2T"] / 426, 0.9202,
            places=4)

    def test_row_build1_residual_squats_transient_class(self):
        """Under row scope the only squats left in row build1 are
        the b=1 transient channels Vp@(3,2) and DBr@(3,3); the V0p
        lock squat dies entirely (family carries V0p@(3,1)=62)."""
        self.assertEqual(
            self.rows["row_build1"]["lock_squats"],
            {"3,2:Vp": 72, "3,3:DBr": 72})
        self.assertEqual(
            self.rows["family_build1"]["lock_squats"]["3,1:V0p"], 62)
        self.assertEqual(
            self.rows["family_build1"]["lock_squats"]["3,2:Vp"], 109)

    def test_queue_lineage_same_pre_registered_source(self):
        """v1 failed on the task-invocation path (exit 2, script
        never ran); v2 re-ran the SAME archive content hash — the
        pre-registered script was never modified between attempts."""
        with open(os.path.join(EV, "queue-receipt-v1-failed.json"),
                  encoding="utf-8") as fh:
            v1 = json.load(fh)
        with open(os.path.join(EV, "queue-receipt-v2.json"),
                  encoding="utf-8") as fh:
            v2 = json.load(fh)
        self.assertEqual(v1["state"], "failed")
        self.assertEqual(v1["execution_status"], 2)
        self.assertEqual(
            v1["command"][1],
            "evidence/2026-10-07-row-scope-ktam/ktam_row_scope.py")
        self.assertEqual(v2["state"], "complete")
        self.assertEqual(v2["execution_status"], 0)
        self.assertTrue(v2["command"][1].startswith("/work/source/"))
        self.assertEqual(v1["archive_blob"], v2["archive_blob"])
        self.assertEqual(v1["nonce"], "row-scope-v1")
        self.assertEqual(v2["nonce"], "row-scope-v2")
