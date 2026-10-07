"""Receipt pins for the tick-33 recombination study (SON-4778).

Pins the raw receipt (evidence/2026-10-07-recombination/
recombination.out + queue-receipt.json) to the pre-registration
script in this tree and to the machine verdicts. Any change to
these numbers is a scientific claim and must go through a new
pre-registered run.
"""
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE), "evidence",
                  "2026-10-07-recombination")
OUT = os.path.join(EV, "recombination.out")
RECEIPT = os.path.join(EV, "queue-receipt.json")
SCRIPT = os.path.join(EV, "ktam_recombination.py")


def load_out():
    rows = []
    verdicts = None
    with open(OUT) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith("VERDICTS "):
                verdicts = json.loads(line[len("VERDICTS "):])
            else:
                rows.append(json.loads(line))
    return rows, verdicts


def load_receipt():
    with open(RECEIPT) as fh:
        return json.load(fh)


class RecombinationReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.verdicts = load_out()
        cls.by_key = {r["key"]: r for r in cls.rows if "key" in r}
        cls.header = cls.rows[0]
        cls.receipt = load_receipt()

    def test_files_exist(self):
        self.assertTrue(os.path.exists(OUT))
        self.assertTrue(os.path.exists(RECEIPT))
        self.assertTrue(os.path.exists(SCRIPT))

    def test_header_matches_pre_registration(self):
        h = self.header
        self.assertEqual(h["n_per_arm"], 1000)
        self.assertEqual(h["seed_base"], 100261107)
        self.assertEqual(h["seed_stride"], 20000000)
        self.assertEqual(len(h["predictions"]), 6)
        self.assertEqual(h["references"], {
            "row_build1_blocked": 0.144,
            "row_Vp_stable_fill": 0.162,
            "family_build1_blocked": 0.27,
            "family_Vp_stable_fill": 0.908})
        # the in-tree script IS the pre-registration (same tree the
        # archive blob pins): registered constants agree
        src = open(SCRIPT).read()
        self.assertIn("BASE_SEED = 100261107", src)
        self.assertIn("N_PER_ARM = 1000", src)

    def test_receipt_pins(self):
        r = self.receipt
        self.assertEqual(r["id"],
                         "e38ad7f3d5f377b9345dd9f376f49208508"
                         "e0e8af2a6fb724369808a0404b957")
        self.assertEqual(r["archive_blob"],
                         "4684430d9030cd7d0a7a60717a74b736b8a9c1821a536"
                         "5bb38f99fb94a78d67a")
        self.assertEqual(r["pre_registration_commit"],
                         "3fa1b4a3a17c667a3b4b230c0086ebf8b3c842f3")
        self.assertEqual(r["execution_status"], 0)
        self.assertEqual(r["hx_queue_exit"], 0)
        self.assertEqual(r["nonce"], "recombination-v1")
        self.assertEqual(r["image"], "paperclip-test")
        self.assertEqual(r["command"],
                         ["python3",
                          "/work/source/evidence/2026-10-07-"
                          "recombination/ktam_recombination.py"])

    def test_machine_verdicts(self):
        v = self.verdicts
        self.assertEqual(v["H4"]["call"], "calibrated")
        self.assertLessEqual(max(v["H4"]["deviations"].values()), 0.007)
        self.assertEqual(v["H1"]["call"], "falsified")
        self.assertEqual(v["H1"]["n_stable"], 155)
        self.assertEqual(v["H1"]["lb_any_frac"], 0.0129)
        self.assertEqual(v["H1b"]["call"], "confirmed")
        self.assertEqual(v["H1b"]["lb_noncanon_frac"], 0.0485)
        self.assertEqual(v["H1c"]["call"], "falsified")
        self.assertEqual(v["H2"]["call"], "no_events")
        self.assertEqual(v["H2"]["n_pair"], 0)
        self.assertEqual(v["H3"]["call"], "falsified")
        self.assertEqual(v["H3"]["blocked_frac"], 0.141)
        self.assertEqual(v["H3"]["mutual_pair_frac_of_blocked"], 0.0)

    def test_row_vp_redundant_stack(self):
        r = self.by_key["row_Vp"]
        self.assertEqual(r["n"], 1000)
        self.assertEqual(r["d2t22_stable_fill_all"], 0.155)
        sc = r["stable_cohort"]
        self.assertEqual(sc["n"], 155)
        self.assertEqual(sc["b22_hist"], {"2": 2, "3": 153})
        self.assertEqual(sc["b_ge3_frac"], 0.9871)
        self.assertEqual(sc["lb_any_frac"], 0.0129)
        # the three relay partners: squatter N, canonical S, squatter W
        self.assertEqual(sc["all_partners"]["N@2,3:DAr:1"], 153)
        self.assertEqual(sc["all_partners"]["S@2,1:V0p:1"], 155)
        self.assertEqual(sc["all_partners"]["W@1,2:S2:1"], 155)
        self.assertNotIn("E@3,2:L2:1", sc["all_partners"])
        # (3,2) is never squatted in Vp-missing under row scope
        self.assertEqual(r["ever_noncanon32_frac"], 0.0)

    def test_row_build1_vertical_stack_block(self):
        r = self.by_key["row_build1"]
        self.assertEqual(r["blocked_frac"], 0.141)
        self.assertEqual(r["lock_squats"],
                         {"3,2:Vp": 141, "3,3:DBr": 141})
        self.assertEqual(r["mutual_pair_link_n"], 0)
        self.assertEqual(r["occ22_read"]["D2T"], 142)
        sc = r["stable_cohort"]
        self.assertEqual(sc["n"], 142)
        self.assertEqual(sc["all_partners"]["E@3,2:Vp:1"], 141)
        self.assertEqual(sc["b_ge3_frac"], 0.993)

    def test_family_contrast(self):
        r = self.by_key["family_Vp"]
        self.assertEqual(r["d2t22_stable_fill_all"], 0.886)
        sc = r["stable_cohort"]
        self.assertEqual(sc["n"], 886)
        self.assertEqual(sc["b22_hist"], {"2": 711, "3": 5, "4": 170})
        self.assertEqual(sc["lb_noncanon_frac"], 0.0485)
        self.assertEqual(sc["load_bearing_partners"]["E@3,2:L2"], 711)
        b = self.by_key["family_build1"]
        self.assertEqual(b["blocked_frac"], 0.273)


if __name__ == "__main__":
    unittest.main()
