"""CI invariants for the v3p value-agnostic blind cage (tick 11).

Pins the structural facts behind the value-agnostic locking lemma in
designs/001 (catalogue entry (b) amendment):
  1. the value-agnostic premise: every lock interface bonds the correct
     and wrong value with EQUAL strength (blindness is real, not partial);
  2. the stripped support bonds stay stripped (cap1/cap3 bond nothing);
  3. the structural concession: the correct terminal {a} is unreachable
     at tau=2 (exactly one terminal, decode \"partial\", wrong tiles
     attach 0 times).
"""
import os
import sys
import unittest

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                    "evidence", "2026-10-06-v3p-blind-cage")
sys.path.insert(0, HERE)

from tiles_v3p import (  # noqa: E402
    TILES, enumerate_aTAM, glue_strength, matched_strength, decode)


class TestBlindnessSymmetry(unittest.TestCase):
    def test_lock_interfaces_are_value_blind(self):
        # L1.W bonds D1T.E and D1F.E equally
        self.assertEqual(glue_strength(TILES["L1"]["W"], TILES["D1T"]["E"]), 1)
        self.assertEqual(glue_strength(TILES["L1"]["W"], TILES["D1F"]["E"]), 1)
        # L2.W bonds D2F.E and D2T.E equally
        self.assertEqual(glue_strength(TILES["L2"]["W"], TILES["D2F"]["E"]), 1)
        self.assertEqual(glue_strength(TILES["L2"]["W"], TILES["D2T"]["E"]), 1)
        # row-1 N channel is blind in the glue names themselves
        self.assertEqual(TILES["D1T"]["N"], TILES["D1F"]["N"])

    def test_stripped_bonds_bond_nothing(self):
        # glues bond by name identity, so a glue appearing on exactly ONE
        # face in the whole system (tiles + seed) can never match anything:
        # cap1/cap3 are structurally inert by uniqueness.
        from tiles_v3p import SEED_N
        counts = {}
        for t in TILES.values():
            for g in t.values():
                counts[g] = counts.get(g, 0) + 1
        for g in SEED_N.values():
            counts[g] = counts.get(g, 0) + 1
        for cap in ("cap1", "cap3"):
            self.assertEqual(counts.get(cap), 1,
                             "%s must appear exactly once" % cap)
        # and their single occurrence is on the stripped support faces
        self.assertEqual(TILES["L1"]["S"], "cap1")
        self.assertEqual(TILES["D2F"]["S"], "cap3")


class TestStructuralConcession(unittest.TestCase):
    def test_single_partial_terminal_no_correct_growth(self):
        terminals, max_b = enumerate_aTAM(tau=2)
        self.assertEqual(len(terminals), 1)
        self.assertEqual(decode(terminals[0]), "partial")
        # the reachable terminal carries the founded row-1 value only
        vals = set(terminals[0].values())
        self.assertIn("D1T", vals)
        self.assertNotIn("D1F", vals)
        self.assertNotIn("D2F", vals)
        self.assertNotIn("D2T", vals)

    def test_wrong_tiles_never_reach_tau(self):
        # D1F/D2T alone are b=1 next to their best-founded neighbours
        seed_row = {(0, 0): "seed0", (1, 0): "seed1", (2, 0): "seed2",
                    (0, 1): "S1", (0, 2): "S2", (1, 1): "D1T"}
        self.assertEqual(matched_strength(seed_row, (1, 1), "D1F"), 1)
        self.assertEqual(matched_strength(seed_row, (1, 2), "D2T"), 1)
        self.assertEqual(matched_strength(seed_row, (1, 2), "D2F"), 1)
        self.assertEqual(matched_strength(seed_row, (2, 1), "L1"), 1)


if __name__ == "__main__":
    unittest.main()
