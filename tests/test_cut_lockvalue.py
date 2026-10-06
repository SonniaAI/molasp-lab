"""CI invariants for the WRONG_CUT lock-on-false build (tick 16,
designs/002 F2 boundary — evidence/2026-10-06-cut-lockvalue/).

Pins the taxonomy row this tick measured (run.out, 1933/2000 strict
"ap", 0/2000 "apq" anywhere, loose 500/500 "ap" at every point):
  1. The tick-15 WRONG_CUT self-correction channel is STRUCTURALLY
     absent in the lock-on-false build: no tile bonds rq-t from the
     lock side (L3.W = rq-f), so the true tile's b=1 transient has
     no cooperative capture partner — in contrast with WRONG_CUT,
     where glue_strength(L3.W, D3T.E) == 1 is the capture channel.
  2. The compile is CONSISTENT with its own (wrong) post-cut
     prediction: D3F's falsity-chain south glue bonds row 2's
     predicted-true north face (b=2 direct attach), and L3 bonds the
     false output.  A consistent-but-wrong compile is kinetically
     stable: the substrate executes the compile's error faithfully.
  3. The true tile stays b=1 in the finished wrong terminal (spine
     only) — same un-lockability as the wrong-VALUE family, but for
     a different reason (no capture partner, not value mismatch on
     the lock's own input).
  4. Behavioural, fixed-seed small MC at dG=2: strict decodes are
     {"ap", "partial"} only, never "apq".

CI-safe: 12 trajectories, dG=2 only; the full 2000-trajectory grid
lives in evidence, not in CI.
"""
import collections
import math
import os
import sys
import unittest

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
EV = os.path.join(HERE, "evidence", "2026-10-06-cut-lockvalue")
MULTIROW = os.path.join(HERE, "evidence", "2026-10-06-multirow-ktam-grid")
for p in (EV, MULTIROW):
    if p not in sys.path:
        sys.path.insert(0, p)

from ktam_mc_multirow import AnchoredAPI, run_assembly, GSE  # noqa: E402
from tiles_anchored import WRONG_CUT, glue_strength, matched_strength  # noqa: E402
from tiles_cutlock import WRONG_CUT_LOCKFALSE  # noqa: E402

T_READ = 400.0 * math.exp(11.0)  # dG = 2 read time, grid rule


class TestCaptureChannelGone(unittest.TestCase):
    def test_no_tile_bonds_true_output_from_lock_side(self):
        tiles = WRONG_CUT_LOCKFALSE["tiles"]
        # the lock is keyed to the predicted (false) value
        self.assertEqual(tiles["L3"]["W"], "rq-f")
        # capture channel contrast: WRONG_CUT has it, this build does not
        self.assertEqual(
            glue_strength(tiles["L3"]["W"], tiles["D3T"]["E"]), 0)
        self.assertEqual(
            glue_strength(WRONG_CUT["tiles"]["L3"]["W"],
                          WRONG_CUT["tiles"]["D3T"]["E"]), 1)
        # and no OTHER tile bonds rq-t either — no partner at all
        self.assertEqual(
            sorted(t for t, f in tiles.items() if f.get("W") == "rq-t"), [])

    def test_false_tile_chain_anchored_and_lockable(self):
        tiles = WRONG_CUT_LOCKFALSE["tiles"]
        # falsity chain: D3F.S bonds row 2's predicted-true north face
        self.assertEqual(tiles["D3F"]["S"], "rp-t-done")
        self.assertEqual(tiles["D2TA"]["N"], "rp-t-done")
        self.assertEqual(glue_strength(tiles["D3F"]["S"],
                                       tiles["D2TA"]["N"]), 1)
        # lock bonds the false output — the compile is self-consistent
        self.assertEqual(glue_strength(tiles["L3"]["W"],
                                       tiles["D3F"]["E"]), 1)

    def test_true_tile_spine_only_in_finished_wrong_terminal(self):
        b = WRONG_CUT_LOCKFALSE
        # the finished wrong terminal, by hand
        finished = {
            (0, 1): "S1", (1, 1): "D1T", (2, 1): "L1",
            (0, 2): "S2", (1, 2): "D2TA", (2, 2): "L2",
            (0, 3): "S3", (1, 3): "D3F", (2, 3): "L3",
        }
        tiles = b["tiles"]
        # D3T bonds: W go3 (spine) only; S u-cut inert; E rq-t unbonded
        self.assertEqual(tiles["D3T"]["S"], "u-cut")
        self.assertEqual(tiles["D3T"]["W"], "go3")
        self.assertEqual(tiles["S3"]["E"], "go3")
        # D3F reaches b=2 with W+S in that context
        self.assertEqual(matched_strength(b, finished, (1, 3), "D3F"), 3)
        self.assertEqual(matched_strength(b, finished, (1, 3), "D3T"), 1)

    def test_expected_decode_is_the_wrong_non_model(self):
        # aTAM: unique terminal decodes {a,p} — aTAM check this tick;
        # semantically {a,p} is not a model of P (q :- p violated)
        self.assertEqual(
            WRONG_CUT_LOCKFALSE["expected_terminal_decode"], "ap")


class TestBehaviouralSmallMC(unittest.TestCase):
    def test_dg2_no_reassertion_of_true_model(self):
        api = AnchoredAPI(WRONG_CUT_LOCKFALSE)
        decodes = collections.Counter(
            run_assembly(api, 11.0, GSE, T_READ, 20261016 + i).split("|")[0]
            for i in range(12))
        self.assertTrue(set(decodes) <= {"ap", "partial"}, decodes)
        self.assertGreater(decodes.get("ap", 0), 0)


if __name__ == "__main__":
    unittest.main()
