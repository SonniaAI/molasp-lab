"""Designs/009 pre-implementation baseline: AND bodies over derived
literals — today-truth of the stage-6 corpus candidates.

Tick 55 (SON-4842, run efa84230). designs/009 (tick 54) staged the
PC11 via-generalization as DESIGN ONLY; this file pins what the
current compiler actually does with its corpus candidates BEFORE
any gate moves:

  - TRUE-HEAD path (PC12-doc / PC12-n4): gate A fires exactly as
    the design's in-place correction predicted — the conjunctive-
    variant position check demands (adjacent-below, row-1 via) and
    refuses the honest (i-1, i-2) placement. Gate B (derived-hi
    re-typing) is UNREACHABLE behind gate A: the refusal message
    never mentions the derived row.
  - The design-doc PR13 text is wrong on two counts (measured):
    semantically `q2 :- s` with fact `s` makes q2 TRUE (least model
    {p,q,q2,r,s}, not the claimed {p,s,q}); structurally it refuses
    EARLIER at the unit-variant gate on q2's read of s, never
    reaching the AND gates. The honest dead-cascade shape is
    PR13-dead (`q2 :- z`, z unplaced/false).
  - THE SURPRISE: PR13-dead and PR14 both COMPILE today. A
    predicted-false AND head never reaches gates A/B/C — the
    designs/008 stage-4/5 false-row base emits dead readers
    WITHOUT the positional checks (only the width>2 refusal of
    tick 52 gates it). PR14 was registered in designs/009 §4 as a
    must-stay-LOUD refusal ("lo z not below terminal"); it is
    instead a silent acceptance whose decode happens to be
    correct — the same class of boundary tick 52 closed for
    width>2 false heads.
  - Both silent acceptances decode correctly (terminal decodes ==
    least model; every dead glue BFS-proved absent from every
    producible assembly) but are lock-incomplete (4 of 6 rows
    lock) and their emitted builds break the designs/003
    one-tile column-2 row structure (d4 census error severity,
    which reports and never gates): PR13-dead row 5 column 2
    carries [V5p, UD5q2]; PR14 row 6 column 2 carries [Fr, AD6r].

All numbers below are measured probe output (2026-10-08 tick 55),
not design predictions. Nothing here is a validated result; these
pins are the baseline the stage-6 gates must move against.
"""

import unittest

from molasp.compiler import (CompileError, UnsupportedGeometry,
                             compile_program, least_model,
                             parse_program)
from molasp.parity import check_program, decode, producible


PC12_DOC = "p. s. q. q2 :- p. r :- q2, q."
PC12_N4 = "p. q. q2 :- p. r :- q2, q."
PR13_DOC = "p. s. q. q2 :- s. r :- q2, q."
PR13_DEAD = "p. s. q. q2 :- z. r :- q2, q."
PR14_DOC = "p. s. q. q2 :- p. r :- q2, z."


def _model(text):
    facts, derived, _order = parse_program(text)
    return set(least_model(facts, derived))


class AndOverDerivedTrueHeadRefusals(unittest.TestCase):
    """Gate A fires on the honest (i-1, i-2) placement; gate B is
    unreachable behind it (PR9-flavor refusal, first)."""

    def test_pc12_doc_refuses_gate_a_with_rows_4_3(self):
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program(PC12_DOC, name="PC12doc")
        msg = str(cm.exception)
        self.assertIn("conjunctive variant of 'r'", msg)
        self.assertIn("row-1 via", msg)
        self.assertIn("got rows (4, 3)", msg)
        self.assertNotIn("derived row", msg)  # gate B never speaks

    def test_pc12_n4_refuses_gate_a_with_rows_3_2(self):
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program(PC12_N4, name="PC12n4")
        msg = str(cm.exception)
        self.assertIn("conjunctive variant of 'r'", msg)
        self.assertIn("row-1 via", msg)
        self.assertIn("got rows (3, 2)", msg)
        self.assertNotIn("derived row", msg)

    def test_both_least_models_are_full(self):
        # semantic ground truth: both PC12 shapes carry q2 and r
        self.assertEqual(_model(PC12_DOC), {"p", "s", "q", "q2", "r"})
        self.assertEqual(_model(PC12_N4), {"p", "q", "q2", "r"})


class AndOverDerivedDesignDocCorrection(unittest.TestCase):
    """The designs/009 §4 PR13 row is wrong in-place: measured, not
    silently rewritten (the design itself models this discipline)."""

    def test_pr13_doc_least_model_has_q2_true(self):
        # `q2 :- s` with fact `s` derives q2 — the claimed
        # {p,s,q} model (q2 false, "no support from p") is a
        # hand-arithmetic slip in designs/009 §4.
        self.assertEqual(_model(PR13_DOC), {"p", "q", "q2", "r", "s"})

    def test_pr13_doc_refuses_at_unit_gate_not_and_gate(self):
        # q2's own read of s (fact at row 2, non-adjacent, not the
        # row-1 via) fires the unit-variant refusal BEFORE any AND
        # gate: the design-doc text exercises the wrong gate.
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program(PR13_DOC, name="PR13doc")
        msg = str(cm.exception)
        self.assertIn("unit variant of 'q2'", msg)
        self.assertIn("direct-below FACT readers", msg)

    def test_pr13_dead_is_the_honest_dead_cascade(self):
        # q2 :- z with z unplaced: q2 false, r's AND body dead on
        # one conjunct — the shape PR13 was meant to pin.
        self.assertEqual(_model(PR13_DEAD), {"p", "q", "s"})


class AndOverDerivedFalseHeadSilentAcceptance(unittest.TestCase):
    """PR13-dead and PR14 COMPILE today: false AND heads bypass
    gates A/B/C entirely (dead-reader emission is unconditional
    below the width>2 refusal). Correct decode, incomplete locks,
    d4-reported row-structure break in the emitted build."""

    def test_pr13_dead_compiles_and_decodes_least_model(self):
        v = check_program("PR13dead", PR13_DEAD, {"p", "q", "s"})
        self.assertEqual(v["predicted"], ["p", "q", "s"])
        self.assertEqual(v["terminal_decodes"], [["p", "q", "s"]])
        self.assertEqual(v["dead_variant_glues"], ["and1_r", "unit1_q2"])
        self.assertTrue(all(v["dead_glues_absent"].values()))
        # measured shape of the silent acceptance
        self.assertEqual((v["n_rows"], v["tiles"], v["assemblies"],
                          v["terminals"]), (6, 26, 70, 1))
        self.assertFalse(v["full_locks"])  # 4 of 6 rows lock
        self.assertEqual(v["d4_severity"], "error")

    def test_pr13_dead_unlocked_rows_are_the_false_derived_rows(self):
        build = compile_program(PR13_DEAD, name="PR13dead")
        self.assertEqual(build["rows"], {1: "p", 2: "s", 3: "q",
                                         4: "z", 5: "q2", 6: "r"})
        _seen, terminals = producible(build)
        _atoms, locked = decode(build, terminals[0])
        self.assertEqual(locked, 4)
        self.assertIn("V5p", build["tiles"])   # emitted column-2
        self.assertIn("UD5q2", build["tiles"])  # collision pair
        self.assertIn("column 2 is not one-tile",
                      build["d4"]["detail"])

    def test_pr14_compiles_and_decodes_least_model(self):
        # designs/009 §4 registered PR14 as a must-stay-LOUD
        # refusal; measured: it silently compiles.
        v = check_program("PR14doc", PR14_DOC, {"p", "q", "q2", "s"})
        self.assertEqual(v["predicted"], ["p", "q", "q2", "s"])
        self.assertEqual(v["terminal_decodes"], [["p", "q", "q2", "s"]])
        self.assertEqual(v["dead_variant_glues"], ["and1_r"])
        self.assertTrue(all(v["dead_glues_absent"].values()))
        self.assertEqual((v["n_rows"], v["tiles"], v["assemblies"],
                          v["terminals"]), (6, 25, 70, 1))
        self.assertFalse(v["full_locks"])  # z and r rows lock-free
        self.assertEqual(v["d4_severity"], "error")

    def test_pr14_unlocked_rows_are_z_and_r(self):
        build = compile_program(PR14_DOC, name="PR14doc")
        self.assertEqual(build["rows"], {1: "p", 2: "s", 3: "q",
                                         4: "q2", 5: "z", 6: "r"})
        _seen, terminals = producible(build)
        _atoms, locked = decode(build, terminals[0])
        self.assertEqual(locked, 4)
        self.assertIn("Fr", build["tiles"])   # false-cap relay
        self.assertIn("AD6r", build["tiles"])  # AND dead reader
        self.assertIn("column 2 is not one-tile",
                      build["d4"]["detail"])


if __name__ == "__main__":
    unittest.main()
