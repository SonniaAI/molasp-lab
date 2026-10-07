"""Receipt pins for the via-site lock placement kinetics study
(tick 40, SON-4805; designs/007).

Pins the collected cluster receipt
evidence/2026-10-07-viasite-lock-ktam/viasite.out (job
hxq-380801377b9433e5, request 380801377b9433e5...9ef1, nonce
viasite-v2, exit 0).  Pre-registration landed at c286cb6 BEFORE the
job (archive blob 165acee8...c9371e).  The failed viasite-v1 attempt
(exit 2: command path ran from /work while the archive mounts at
/work/source) is kept as queue-receipt-v1-failed.txt and pinned too
— the path lesson is part of the record.
"""
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE),
                  "evidence", "2026-10-07-viasite-lock-ktam")


def load_arms():
    arms = {}
    verdicts = None
    with open(os.path.join(EV, "viasite.out")) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("VERDICTS"):
                verdicts = json.loads(line[len("VERDICTS "):])
            elif line:
                rec = json.loads(line)
                arms[rec["arm"]] = rec
    return arms, verdicts


class TestViasiteLockReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arms, cls.verdicts = load_arms()

    def test_receipt_shapes(self):
        for arm in ("fam_b1", "s2_b1", "s2_b1_dG2", "fam_unit",
                    "s2_unit"):
            self.assertIn(arm, self.arms)
            self.assertEqual(self.arms[arm]["n"], 500)

    def test_verdicts_recorded(self):
        self.assertEqual(self.verdicts, {
            "V1": "CONFIRMED", "V2": "INCONCLUSIVE",
            "V3": "CONFIRMED", "V4": "INCONCLUSIVE",
            "V5": "CONFIRMED", "V6": "CONFIRMED"})

    def test_v1_flip_is_large(self):
        """The census's b=1->b=2 flip, measured: s2 stable via-lock
        0.416 vs family 0.082 (gate band was >= fam+0.02)."""
        s = self.arms["s2_b1"]["via_lock_stable_frac"]
        f = self.arms["fam_b1"]["via_lock_stable_frac"]
        self.assertGreaterEqual(s, 0.05)
        self.assertGreaterEqual(s, f + 0.02)
        self.assertAlmostEqual(s, 0.416)
        self.assertAlmostEqual(f, 0.082, places=3)

    def test_v2_race_mechanism(self):
        """Many-transient vs rare-frozen: family attach events 3425
        with dwell 0.18; s2 events 526 with dwell 0.96 (frozen).
        The 0.15 fam band was too tight -> INCONCLUSIVE, but the
        falsifier bands (fam < 0.5, s2 > 0.5) hold decisively."""
        f = self.arms["fam_b1"]
        s = self.arms["s2_b1"]
        self.assertGreater(f["via_attach_events"],
                           5 * s["via_attach_events"])
        self.assertLess(f["mean_via_dwell_frac"], 0.5)
        self.assertGreater(s["mean_via_dwell_frac"], 0.8)
        self.assertAlmostEqual(f["via_attach_events"], 3425)
        self.assertAlmostEqual(s["via_attach_events"], 526)

    def test_v3_dominant_completion_hazard(self):
        """43% of not-strict_filled s2_b1 terminals carry a stable
        via-lock (gate >= 0.10)."""
        s = self.arms["s2_b1"]
        ratio = s["nonstrict_via"] / float(s["nonstrict_n"])
        self.assertGreaterEqual(ratio, 0.10)
        self.assertEqual(s["nonstrict_n"], 480)
        self.assertEqual(s["nonstrict_via"], 208)

    def test_v4_calibration_band(self):
        """fam blocked 0.240 vs tick-38 ref 0.308: inside the 0.05-0.10
        INCONCLUSIVE band, NOT protocol drift (>= 0.10)."""
        d = abs(self.arms["fam_b1"]["blocked_frac"] - 0.308)
        self.assertLess(d, 0.10)

    def test_v5_dg_direction(self):
        self.assertLess(
            self.arms["s2_b1_dG2"]["via_lock_stable_frac"],
            self.arms["s2_b1"]["via_lock_stable_frac"])

    def test_v6_generality(self):
        self.assertAlmostEqual(
            self.arms["s2_unit"]["via_lock_stable_frac"], 0.448)
        self.assertGreaterEqual(
            self.arms["s2_unit"]["via_lock_stable_frac"], 0.05)
        self.assertAlmostEqual(
            self.arms["fam_unit"]["via_lock_stable_frac"], 0.086,
            places=3)

    def test_strict_filled_refines_decode(self):
        """strict_filled (full canonical occupancy) is the stricter
        instrument: 0.148 fam vs 0.614 decode-only.  Both recorded;
        V3 uses strict_filled."""
        f = self.arms["fam_b1"]
        self.assertAlmostEqual(f["strict_filled_frac"], 0.148,
                               places=3)
        self.assertAlmostEqual(f["strict_decode_frac"], 0.614,
                               places=3)
        self.assertLess(f["strict_filled_frac"],
                        f["strict_decode_frac"])

    def test_queue_receipt_v2_pinned(self):
        with open(os.path.join(EV, "queue-receipt-v2.json")) as fh:
            r = json.load(fh)
        self.assertEqual(r["execution_status"], 0)
        self.assertEqual(r["nonce"], "viasite-v2")
        self.assertTrue(r["job"].startswith("hxq-380801377b9433e5"))
        self.assertEqual(
            r["verdicts"]["V1"], "CONFIRMED")

    def test_v1_failure_receipt_kept(self):
        """The exit-2 path lesson: archive mounts at /work/source,
        commands run with cwd /work."""
        with open(os.path.join(EV,
                               "queue-receipt-v1-failed.txt")) as fh:
            txt = fh.read()
        self.assertIn("/work/evidence/", txt)
        self.assertIn("HX-QUEUE-EXIT:2", txt)


if __name__ == "__main__":
    unittest.main()
