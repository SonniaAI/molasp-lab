"""Regression tests for the v3 tile system (designs/001, tick 5).

Fast, stdlib-only, no MC: locks the aTAM guarantee and the
evidence-checking-lock property into CI, so a future tile-set edit
that reintroduces a value-blind bond fails a test, not a grid.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.join(HERE, "..", "evidence", "2026-10-06-c2-ktam-v3-locks")
sys.path.insert(0, V3)

from tiles_v3 import TILES, SEED_TILES, matched_strength, glue_strength  # noqa: E402
from atam_check_v3 import producible, decode, value_blind_bonds  # noqa: E402


def correct_assembly():
    asm = dict(SEED_TILES)
    asm.update({(0, 1): "S1", (1, 1): "D1T", (2, 1): "L1",
                (0, 2): "S2", (1, 2): "D2F", (2, 2): "L2"})
    return asm


class TestATAMInvariants(unittest.TestCase):
    def test_grows_and_single_terminal_decodes_a(self):
        seen, terminals = producible()
        self.assertEqual(len(seen), 10)
        self.assertEqual(len(terminals), 1)
        self.assertEqual(decode(terminals[0]), "a")

    def test_wrong_tiles_never_producible(self):
        seen, _ = producible()
        values = {t for a in seen for t in dict(a).values()}
        self.assertNotIn("D1F", values)
        self.assertNotIn("D2T", values)


class TestEvidenceCheckingLocks(unittest.TestCase):
    def test_value_side_glue_pairs_are_strength_zero(self):
        blind = value_blind_bonds()
        for pair, strength in blind["pair_strengths"].items():
            self.assertEqual(strength, 0, pair)

    def test_wrong_contexts_keep_only_structural_bonds(self):
        blind = value_blind_bonds()
        for wrong_key, wrong_b, correct_key, correct_b in blind["context_totals"]:
            self.assertLess(wrong_b, correct_b, wrong_key)

    def test_wrong_tiles_un_lockable_in_full_correct_context(self):
        asm = correct_assembly()
        # Correct decision tiles bond every face they have in the
        # finished assembly: D1T (W,S,E,N) = 4, D2F (W,S,E) = 3.
        self.assertEqual(matched_strength(asm, (1, 1), "D1T"), 4)
        self.assertEqual(matched_strength(asm, (1, 2), "D2F"), 3)
        # Wrong values keep ONLY the structural spine bond: no context,
        # however complete, raises them to b >= 2 — un-lockable.
        self.assertEqual(matched_strength(asm, (1, 1), "D1F"), 1)
        self.assertEqual(matched_strength(asm, (1, 2), "D2T"), 1)

    def test_no_glue_table_entry_matches_wrong_values(self):
        for lock_glue, wrong_glue in [("rd1t", "rd1f"),
                                      ("rd1t-done", "rd1f-done"),
                                      ("rd2f", "rd2t")]:
            self.assertEqual(glue_strength(lock_glue, wrong_glue), 0)


if __name__ == "__main__":
    unittest.main()
