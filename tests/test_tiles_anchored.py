"""Regression tests for the designs/002 order falsifier (anchored
cycle `a. p :- a. p :- q. q :- p.`, OR construction, tick 14).

Fast, stdlib-only: pins the three-build aTAM outcome (correct stage
order decodes the stable model; both wrong builds terminate in
NON-models), the OR shared-output construction, value typing, and the
growth-dead vs un-lockable taxonomy.  clingo semantics are CI-enforced
wherever the module exists (tick 7 pattern).
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "evidence", "2026-10-06-anchored-cycle-order")
sys.path.insert(0, D)

from tiles_anchored import (CORRECT, WRONG_CUT, WRONG_ROWS,  # noqa: E402
                            SEED_TILES, matched_strength, glue_strength,
                            decode, locked_rows, true_variants)
from atam_check_anchored import (producible, glue_occurrences,  # noqa: E402
                                 exposes_north, full_correct_assembly,
                                 clingo_semantics)

try:
    import clingo  # noqa: F401
    HAS_CLINGO = True
except ImportError:
    HAS_CLINGO = False


class TestCorrectBuild(unittest.TestCase):
    def test_grows_and_single_terminal_decodes_stable_model(self):
        seen, terminals = producible(CORRECT)
        self.assertEqual(len(seen), 20)
        self.assertEqual(len(terminals), 1)
        self.assertEqual(decode(CORRECT, terminals[0]), "apq")
        self.assertEqual(locked_rows(CORRECT, terminals[0]), 3)

    def test_wrong_and_dead_tiles_never_producible(self):
        seen, _ = producible(CORRECT)
        placed = {t for asm in seen for _, t in asm}
        for wrong in ("D1F", "D2F", "D2TQ", "D3F"):
            self.assertNotIn(wrong, placed, wrong)


class TestORConstruction(unittest.TestCase):
    def test_variants_share_value_outputs_and_differ_only_in_read(self):
        t = CORRECT["tiles"]
        self.assertEqual(t["D2TA"]["E"], t["D2TQ"]["E"])
        self.assertEqual(t["D2TA"]["N"], t["D2TQ"]["N"])
        self.assertNotEqual(t["D2TA"]["S"], t["D2TQ"]["S"])
        self.assertEqual(sorted(true_variants(CORRECT, 2)), ["D2TA", "D2TQ"])

    def test_wired_edge_witness_exposed_exactly_by_or_pair(self):
        self.assertEqual(exposes_north(CORRECT, "rp-t-done"),
                         ["D2TA", "D2TQ"])


class TestWrongBuildsAreTerminalButWrong(unittest.TestCase):
    """designs/002 criterion 4: stage order (and the cut discipline)
    must be load-bearing — no wrong build may decode {a,p,q}."""

    def test_wrong_cut_terminates_at_ap(self):
        seen, terminals = producible(WRONG_CUT)
        self.assertEqual(len(terminals), 1)
        self.assertEqual(decode(WRONG_CUT, terminals[0]), "ap")
        self.assertEqual(locked_rows(WRONG_CUT, terminals[0]), 2)

    def test_wrong_rows_terminates_at_a(self):
        # Stronger failure: q's row between a and p severs the anchor
        # edge p :- a — the decode collapses to the stable model of
        # the program WITHOUT the anchor rule.
        seen, terminals = producible(WRONG_ROWS)
        self.assertEqual(len(terminals), 1)
        self.assertEqual(decode(WRONG_ROWS, terminals[0]), "a")
        self.assertEqual(locked_rows(WRONG_ROWS, terminals[0]), 1)

    def test_no_wrong_build_decodes_the_stable_model(self):
        for build in (WRONG_CUT, WRONG_ROWS):
            _, terminals = producible(build)
            for term in terminals:
                self.assertNotEqual(decode(build, term), "apq", build["name"])


class TestValueTypingAndTaxonomy(unittest.TestCase):
    def test_cross_value_glue_pairs_are_strength_zero(self):
        for a, b in (("ra-t-done", "ra-f-done"), ("rp-t-done", "rp-f-done"),
                     ("rq-t-done", "rq-f-done"), ("ra-t", "ra-f"),
                     ("rp-t", "rp-f"), ("rq-t", "rq-f")):
            self.assertEqual(glue_strength(a, b), 0, (a, b))

    def test_wrong_value_tiles_un_lockable_in_full_context(self):
        asm = full_correct_assembly()
        for wrong, site in (("D1F", (1, 1)), ("D2F", (1, 2)), ("D3F", (1, 3))):
            self.assertEqual(matched_strength(CORRECT, asm, site, wrong),
                             1, wrong)

    def test_growth_dead_variant_is_lock_compatible_not_growth_reachable(self):
        # D2TQ (the cut-edge variant) bonds 3 of 4 faces in the
        # finished context — every face except its dead rule-read
        # south glue.  It is value-equivalent (OR) and dies by growth
        # order alone; un-lockability is a wrong-VALUE property.
        asm = full_correct_assembly()
        self.assertEqual(matched_strength(CORRECT, asm, (1, 2), "D2TA"), 4)
        self.assertEqual(matched_strength(CORRECT, asm, (1, 2), "D2TQ"), 3)

    def test_unique_name_glues_inert_in_every_build(self):
        for build in (CORRECT, WRONG_CUT, WRONG_ROWS):
            occ = glue_occurrences(build)
            for g in ("q-true", "u-a", "u-p", "u-q", "u-cut", "SP4", "cap3"):
                if g in occ:
                    self.assertEqual(occ[g], 1, (build["name"], g))


@unittest.skipUnless(HAS_CLINGO, "clingo module not installed")
class TestSemanticsAnchor(unittest.TestCase):
    def test_unique_stable_model_is_apq(self):
        sem = clingo_semantics()
        self.assertTrue(sem["available"])
        self.assertEqual(sem["stable_models"], [["a.", "p.", "q."]])
        self.assertFalse(sem["ap_satisfiable_under_assumptions"])


if __name__ == "__main__":
    unittest.main()
