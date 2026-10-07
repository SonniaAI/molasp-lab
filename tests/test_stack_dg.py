"""Stack-channel dG sweep pins (tick 34, SON-4778) — receipt pins
for evidence/2026-10-07-stack-dg-sweep/stack_dg.out (job
hxq-1751ba31889ec345, request 1751ba31889...cae0d, nonce
stack-dg-v1, archive blob 1193bab6... = sha256 of the tarball built
from committed HEAD 7000301, so the pre-registration precedes the
job).

Pre-registered S1-S4 at 7000301 BEFORE submission; machine verdicts
in the receipt's final line:

- S1 CONFIRMED — row read-block starves monotonically with dG
  (0.14 -> 0.006 -> 0.000) and at every dG with events the blocked
  cohort IS the Vp@(3,2)+DBr@(3,3) vertical stack (co-occurrence
  1.0).  Redundancy does NOT survive thermodynamics: the 2-of-3
  stack closes by dG 4 like the solo family channel did (R4).
- S2 CONFIRMED — the relay-stack repair starves monotonically
  (0.128 -> 0.04 -> 0.000).
- S3 CONFIRMED — among surviving stable holds the redundant b>=3
  fan is the channel at every dG with events (0.9844 / 0.9); mean
  relay contacts ~3.
- S4 CALIBRATED — dG 0.5 deviations 0.001 (blocked) / 0.027 (fill)
  vs the recombination.out references.
"""
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EV = os.path.join(ROOT, "evidence", "2026-10-07-stack-dg-sweep")


def receipt():
    arms, verdicts, config = {}, None, None
    with open(os.path.join(EV, "stack_dg.out")) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("VERDICTS "):
                verdicts = json.loads(line[len("VERDICTS "):])
            elif line:
                rec = json.loads(line)
                if "key" in rec:
                    arms[(rec["key"], rec["dG"])] = rec
                else:
                    config = rec
    if not arms or verdicts is None:
        raise unittest.SkipTest("stack dG sweep receipt not present")
    return config, arms, verdicts


class ConfigPins(unittest.TestCase):

    def test_protocol_and_pre_registration(self):
        config, _, _ = receipt()
        self.assertEqual(config["n_per_arm"], 500)
        self.assertEqual(config["seed_base"], 120261107)
        self.assertEqual(config["dG_grid"], [0.5, 2.0, 4.0])
        self.assertEqual(len(config["predictions"]), 4)


class SciencePins(unittest.TestCase):

    def test_s1_read_block_starves_and_is_the_vertical_stack(self):
        _, arms, verdicts = receipt()
        b05 = arms[("row_build1", 0.5)]
        b2 = arms[("row_build1", 2.0)]
        b4 = arms[("row_build1", 4.0)]
        self.assertAlmostEqual(b05["blocked_frac"], 0.14, places=3)
        self.assertGreater(b05["blocked_frac"], b2["blocked_frac"])
        self.assertEqual(b4["blocked_frac"], 0.0)
        # the class is the WHOLE read-block wherever it fires
        self.assertEqual(b05["vstack_of_blocked"], 1.0)
        self.assertEqual(b2["vstack_of_blocked"], 1.0)
        self.assertEqual(verdicts["S1"]["call"], "confirmed")

    def test_s2_relay_repair_starves(self):
        _, arms, verdicts = receipt()
        f = [arms[("row_Vp", d)]["stable_fill"] for d in (0.5, 2.0, 4.0)]
        self.assertGreater(f[0], f[1])
        self.assertEqual(f[2], 0.0)
        self.assertEqual(verdicts["S2"]["call"], "confirmed")

    def test_s3_redundant_fan_is_the_last_channel(self):
        _, arms, verdicts = receipt()
        for d in (0.5, 2.0):
            arm = arms[("row_Vp", d)]
            self.assertGreaterEqual(arm["stable_n"], 10)
            self.assertGreaterEqual(arm["b_ge3_frac"], 0.8)
            self.assertLess(arm["lb_any_frac"], 0.11)
            self.assertGreaterEqual(arm["mean_relay_contacts"], 2.9)
        self.assertEqual(verdicts["S3"]["call"], "confirmed")

    def test_s4_calibrated_against_recombination_refs(self):
        _, arms, verdicts = receipt()
        v = verdicts["S4"]
        self.assertEqual(v["call"], "calibrated")
        self.assertLessEqual(v["dev_blocked"], 0.05)
        self.assertLessEqual(v["dev_fill"], 0.05)


if __name__ == "__main__":
    unittest.main()
