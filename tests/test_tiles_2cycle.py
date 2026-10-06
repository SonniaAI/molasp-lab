"""Regression tests for the designs/002 tile system (2-cycle witness
`a. p :- q. q :- p.`, tick 13).

Fast, stdlib-only, no MC: pins the aTAM guarantee, the cut-edge and
transitive-death mechanisms, and the row-by-row carryover of the v3
evidence-checking-lock rule (designs/001 catalogue entry (a)) into CI.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "evidence", "2026-10-06-atom-order-2cycle")
sys.path.insert(0, D)

from tiles_2cycle import TILES, SEED_TILES, matched_strength, glue_strength  # noqa: E402
from atam_check_2cycle import (producible, decode, value_blind_bonds,  # noqa: E402
                               glue_occurrences, exposes_glue)


def correct_assembly():
    asm = dict(SEED_TILES)
    asm.update({(0, 1): "S1", (1, 1): "D1T", (2, 1): "L1",
                (0, 2): "S2", (1, 2): "D2F", (2, 2): "L2",
                (0, 3): "S3", (1, 3): "D3F", (2, 3): "L3"})
    return asm


class TestATAMInvariants(unittest.TestCase):
    def test_grows_and_single_terminal_decodes_a(self):
        seen, terminals = producible()
        self.assertEqual(len(seen), 20)
        self.assertEqual(len(terminals), 1)
        self.assertEqual(decode(terminals[0]), "a")

    def test_wrong_tiles_never_producible(self):
        seen, _ = producible()
        values = {t for a in seen for t in dict(a).values()}
        for wrong in ("D1F", "D2T", "D3T"):
            self.assertNotIn(wrong, values)


class TestAtomOrderMechanisms(unittest.TestCase):
    """The two ways a rule with a false head dies, made structural."""

    def test_cut_edge_glue_is_unique_name_inert(self):
        # q-true (D2T's south glue) appears exactly once in the whole
        # system: nothing can ever expose it as a witness.
        occ = glue_occurrences()
        self.assertEqual(occ["q-true"], 1)
        self.assertEqual(occ["SP4"], 1)

    def test_wired_edge_witness_exposed_only_by_dead_tile(self):
        # rd2t-done (D3T's south glue, the wired p->q edge) is exposed
        # north by exactly one tile: D2T, itself never producible.
        exp = exposes_glue("rd2t-done")
        self.assertEqual(exp["north"], ["D2T"])
        self.assertEqual(exp["seed"], [])

    def test_wired_edge_cannot_ride_the_false_row(self):
        # p's false tile exposes rd2f-done north; D3T needs rd2t-done.
        self.assertEqual(glue_strength("rd2t-done", "rd2f-done"), 0)

    def test_falsity_chain_bonds_the_row_below(self):
        asm = correct_assembly()
        # D2F.S bonds D1T.N (a=true done); D3F.S bonds D2F.N (p=false done).
        self.assertEqual(glue_strength("rd1t-done", "rd1t-done"), 1)
        self.assertEqual(matched_strength(asm, (1, 2), "D2F"), 4)
        self.assertEqual(matched_strength(asm, (1, 3), "D3F"), 3)


class TestEvidenceCheckingLocksCarryOver(unittest.TestCase):
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
        # finished assembly: D1T = 4 (W,S,E,N), D2F = 4 (row 3 bonds
        # its north), D3F = 3 (nothing above row 3).
        self.assertEqual(matched_strength(asm, (1, 1), "D1T"), 4)
        self.assertEqual(matched_strength(asm, (1, 2), "D2F"), 4)
        self.assertEqual(matched_strength(asm, (1, 3), "D3F"), 3)
        # Wrong values keep ONLY the structural spine bond: no context,
        # however complete, raises them to b >= 2 — un-lockable.
        for wrong, site in (("D1F", (1, 1)), ("D2T", (1, 2)), ("D3T", (1, 3))):
            self.assertEqual(matched_strength(asm, site, wrong), 1, wrong)


if __name__ == "__main__":
    unittest.main()
