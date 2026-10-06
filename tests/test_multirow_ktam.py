"""CI invariants for the per-row multi-row kTAM grid (tick 15).

Pins the taxonomy the grid measured (evidence/
2026-10-06-multirow-ktam-grid/run.out, designs/002):
  1. WRONG_CUT capture channel is STRUCTURAL: the cut kills the south
     glue of q's true tile (u-cut, inert) but leaves its value outputs
     intact, and the lock chain below it is value-complete — L3 bonds
     rq-t (west) and base3 (south, from L2's north face).  The wrong-
     cut true tile therefore has a b=2 lock path: value-equivalent and
     lock-compatible, the same family as tick 14's growth-dead
     variants.  A b=1 transient rides this path into a locked
     terminal decoding {a,p,q} — the cut is NOT kinetically
     load-bearing for the read-out.
  2. WRONG_ROWS is geometrically severed: its swapped lock rows
     (L2=L_Q S=base3 over L1 N=base2; L3=L_P S=base2 over L2 N=cap3)
     mismatch every south face above row 1, so no lock above row 1 can
     reach b=2 via geometry — even though the kTAM value channel
     (D3TQ bonding row 2's transient rq-t-done) exists, it dead-ends
     without lockable south faces.  The build stays dead ({a}, empty
     upper rows).  Row order IS kinetically load-bearing.
  3. Behavioural, fixed-seed small MC at dG=2: 2cycle strict decodes
     are clean ({a}/partial only); anchored CORRECT completes or is
     partial; WRONG_CUT captures {a,p,q} at high rate; WRONG_ROWS
     never strict-decodes {a,p,q}.

CI-safe: 30 trajectories total, dG=2 only; the full 16-point grid
lives in evidence, not in CI.
"""
import collections
import math
import os
import sys
import unittest

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
EV = os.path.join(HERE, "evidence", "2026-10-06-multirow-ktam-grid")
sys.path.insert(0, EV)

from ktam_mc_multirow import SYSTEMS, run_assembly, GSE  # noqa: E402
from tiles_anchored import (  # noqa: E402
    BUILDS, CORRECT, WRONG_CUT, WRONG_ROWS, glue_strength)

T_READ = 400.0 * math.exp(11.0)  # dG = 2 read time, grid rule


def mc(api, n, seed0):
    return collections.Counter(
        run_assembly(api, 11.0, GSE, T_READ, seed0 + i).split("|")[0]
        for i in range(n))


class TestWrongCutCaptureIsStructural(unittest.TestCase):
    def test_lock_chain_is_value_complete(self):
        tiles = WRONG_CUT["tiles"]
        # q's true tile keeps its value outputs despite the dead south glue
        self.assertEqual(tiles["D3T"]["S"], "u-cut")   # cut: inert south
        self.assertEqual(tiles["D3T"]["E"], "rq-t")    # value output intact
        # L3 bonds q-true (west) and base3 (south) — a b=2 path exists
        self.assertEqual(glue_strength(tiles["L3"]["W"], tiles["D3T"]["E"]), 1)
        self.assertEqual(tiles["L2"]["N"], "base3")
        self.assertEqual(glue_strength(tiles["L3"]["S"], tiles["L2"]["N"]), 1)

    def test_wrong_cut_true_tile_is_not_wrong_value(self):
        # contrast with the wrong-VALUE family (v3 falsifier): the cut
        # tile's outputs are exactly the lock's inputs, so un-lockability
        # (the b=1 wrong-value property) does not apply to it.
        tiles = WRONG_CUT["tiles"]
        wrong_value_pairs = [(tiles["D3T"]["E"], tiles["L3"]["W"])]
        for out, lock in wrong_value_pairs:
            self.assertEqual(out, lock)


class TestWrongRowsSevered(unittest.TestCase):
    def test_lock_chain_severed_above_row1(self):
        # WRONG_ROWS swaps the lock rows (L2=L_Q, L3=L_P): every south
        # face above row 1 mismatches the north face below it, so no
        # lock can reach b=2 — the geometry severance that keeps the
        # wrong row order dead under kTAM as well as aTAM.
        tiles = WRONG_ROWS["tiles"]
        self.assertEqual(tiles["L3"]["S"], "base2")   # L3 is L_P here
        self.assertEqual(tiles["L2"]["N"], "cap3")    # L2 is L_Q here
        self.assertEqual(glue_strength(tiles["L3"]["S"], tiles["L2"]["N"]), 0)
        self.assertEqual(glue_strength(tiles["L2"]["S"], tiles["L1"]["N"]), 0)
        # contrast: the CORRECT build's lock chain bonds both south faces
        ctiles = CORRECT["tiles"]
        self.assertEqual(glue_strength(ctiles["L3"]["S"], ctiles["L2"]["N"]), 1)
        self.assertEqual(glue_strength(ctiles["L2"]["S"], ctiles["L1"]["N"]), 1)

    def test_value_channel_exists_but_cannot_lock(self):
        # the kTAM capture channel that saves WRONG_CUT exists here too:
        # D3TQ bonds row 2's transient north output rq-t-done (strength 1).
        # What kills WRONG_ROWS is that this value channel dead-ends —
        # severed lock south faces (previous test) — so transients never
        # graduate into a locked terminal.
        tiles = WRONG_ROWS["tiles"]
        self.assertEqual(tiles["D3TQ"]["S"], "rq-t-done")
        self.assertEqual(tiles["D2T"]["N"], "rq-t-done")
        self.assertEqual(glue_strength(tiles["D3TQ"]["S"], tiles["D2T"]["N"]), 1)
        # and the west partner for L3 exists only on row-3 decision tiles,
        # which are themselves at most b=1-with-stable-D3TQ transients
        self.assertEqual(tiles["L3"]["W"], "rp-t")


class TestBehaviouralSmoke(unittest.TestCase):
    def test_2cycle_strict_clean(self):
        c = mc(SYSTEMS[0], 10, 20261015)
        for k in c:
            self.assertIn(k, ("a", "partial"), c)
        self.assertEqual(sum(v for k, v in c.items() if k not in ("a", "partial")), 0)

    def test_anchored_correct_completes_or_partial(self):
        c = mc(SYSTEMS[1], 10, 20261015 + 10000000)
        for k in c:
            self.assertIn(k, ("apq", "partial"), c)

    def test_wrong_cut_captures_stable_model(self):
        c = mc(SYSTEMS[2], 10, 20261015 + 20000000)
        self.assertGreaterEqual(c.get("apq", 0), 7, c)

    def test_wrong_rows_never_decodes_stable_model(self):
        c = mc(SYSTEMS[3], 10, 20261015 + 30000000)
        self.assertEqual(c.get("apq", 0), 0, c)


if __name__ == "__main__":
    unittest.main()
