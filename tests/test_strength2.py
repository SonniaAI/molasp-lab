"""Receipt pins for the strength-2 lock-read encoding study
(tick 38, SON-4778; designs/005 deferred item (b)).

Pins the collected cluster receipt
evidence/2026-10-07-strength2-lock/strength2.out (job
hxq-2791e8805defef75, request 2791e8805defef754...c1122, nonce
strength2-v1, exit 0) and the queue wrapper.  Pre-registration landed
at 63d12d9 BEFORE the job (archive blob 9c7e7a52...c4ae5e = sha256 of
the committed-HEAD tarball)."""
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE),
                  "evidence", "2026-10-07-strength2-lock")


def load_arms():
    arms = {}
    verdicts = None
    with open(os.path.join(EV, "strength2.out")) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("VERDICTS"):
                verdicts = json.loads(line[len("VERDICTS "):])
            elif line:
                rec = json.loads(line)
                arms[rec["arm"]] = rec
    return arms, verdicts


class Strength2ReceiptPins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arms, cls.verdicts = load_arms()

    def test_eight_arms_n500(self):
        self.assertEqual(
            set(self.arms),
            {"fam_b1", "s2_b1", "fam_b1_Vp", "s2_b1_Vp",
             "s2_b1_dG2", "s2_b1_Vp_dG2", "fam_unit", "s2_unit"})
        for rec in self.arms.values():
            self.assertEqual(rec["n"], 500)

    def test_calibration_family_refs(self):
        """K5 CONFIRMED: family arms reproduce the published trade
        table (blocked 0.27 / stable fill 0.908 within 0.05)."""
        self.assertAlmostEqual(self.arms["fam_b1"]["blocked_frac"],
                               0.308, places=3)
        self.assertAlmostEqual(self.arms["fam_b1_Vp"]["fill_frac"],
                               0.904, places=3)

    def test_k1_read_block_not_reduced(self):
        """K1 FALSIFIED: s2 blocked 0.314 vs family 0.308 — no drop."""
        self.assertAlmostEqual(self.arms["s2_b1"]["blocked_frac"],
                               0.314, places=3)

    def test_k2_repair_channel_collapses(self):
        """K2 FALSIFIED: s2 Vp-missing stable fill 0.412 vs family
        0.904 — the substitution repair collapses under s2."""
        self.assertAlmostEqual(self.arms["s2_b1_Vp"]["fill_frac"],
                               0.412, places=3)

    def test_squatter_class_migrates_to_lock_tiles(self):
        """The falsification mechanism: V-class squatters give way to
        misplaced LOCK tiles riding the site-agnostic strength-2 W
        read + base relays."""
        fam = self.arms["fam_b1"]["squatters"]
        s2 = self.arms["s2_b1"]["squatters"]
        self.assertEqual(fam["Vp@3,2"], 123)
        self.assertEqual(fam["V0p@3,1"], 75)
        self.assertEqual(s2["L2@3,3"], 67)
        self.assertEqual(s2["L3@3,2"], 43)
        self.assertEqual(s2["Vp@3,2"], 49)

    def test_k3_lo_read_stack_dies(self):
        """K3 FALSIFIED: the Vp+DBr stack is no longer the blocked
        cohort (co-occurrence 0.0955 under s2 vs 0.3052 family)."""
        self.assertAlmostEqual(
            self.arms["fam_b1"]["vstack_of_blocked"], 0.3052, places=4)
        self.assertAlmostEqual(
            self.arms["s2_b1"]["vstack_of_blocked"], 0.0955, places=4)

    def test_k8_lock_capture_accelerates(self):
        """K8 CONFIRMED: median first-passage of L2@(3,2) strictly
        lower under s2 — the encoding does what it mechanically
        promises, and that is not enough."""
        self.assertLess(self.arms["s2_b1"]["median_t_first_L2_32"],
                        self.arms["fam_b1"]["median_t_first_L2_32"])

    def test_k7_generality_reverses(self):
        """K7 FALSIFIED: s2_unit blocked 0.352 > fam_unit 0.268 —
        the failure mode is corpus-general, not BUILD1-specific."""
        self.assertAlmostEqual(
            self.arms["fam_unit"]["blocked_frac"], 0.268, places=3)
        self.assertAlmostEqual(
            self.arms["s2_unit"]["blocked_frac"], 0.352, places=3)

    def test_k6_dG_direction_mixed(self):
        """K6 FALSIFIED: blocked starves with dG (0.314 -> 0.146)
        but the s2 fill RISES (0.412 -> 0.464)."""
        self.assertLess(self.arms["s2_b1_dG2"]["blocked_frac"],
                        self.arms["s2_b1"]["blocked_frac"])
        self.assertGreater(self.arms["s2_b1_Vp_dG2"]["fill_frac"],
                           self.arms["s2_b1_Vp"]["fill_frac"])

    def test_verdict_line(self):
        self.assertEqual(self.verdicts, {
            "K1": "FALSIFIED", "K2": "FALSIFIED", "K3": "FALSIFIED",
            "K4": "INCONCLUSIVE", "K5": "CONFIRMED",
            "K6": "FALSIFIED", "K7": "FALSIFIED", "K8": "CONFIRMED"})

    def test_queue_receipt_wrapper(self):
        with open(os.path.join(EV, "queue-receipt.json")) as fh:
            wrap = fh.read()
        self.assertIn("HX-QUEUE-EXIT:0", wrap)
        self.assertIn("2791e8805defef754a40597e91136d9d0f4f2793920"
                      "71352f51622fd422c1122", wrap)


if __name__ == "__main__":
    unittest.main()
