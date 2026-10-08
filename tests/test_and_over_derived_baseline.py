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
    producible assembly).  Tick-55 baseline: lock-incomplete (4 of 6
    rows lock, spine cap).  Since the stage-7 spine closure
    (designs/010 §10.4-3, tick 62) PR13-dead locks all 6 rows; the
    emitted builds still break the designs/003 one-tile column-2 row
    structure (d4 census error severity, which reports and never
    gates): PR13-dead row 5 column 2 carries [V5p, UD5q2]; PR14 row
    6 column 2 carries [Fr, AD6r].

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


class AndOverDerivedTrueHeadPositionalArm(unittest.TestCase):
    """Stage 6 (designs/009 §9.3, tick 60): the derived-hi positional
    i-2 arm ACCEPTS the honest (i-1, i-2) placement the baseline
    refused.  PC12-N4 (n=4) is the first fully-assembling
    AND-over-derived build: unique terminal, full locks, decode ==
    least model.  PC12-DOC (n=5) was SPINE-CAPPED at row 5 through
    tick 61 (the enumerated STRENGTH table stopped at SP4, so S5
    bonded at 1 < TAU 2; the 4-row prefix decoded correctly —
    designs/009 §9.4).  The stage-7 class closure (designs/010,
    tick 62) removed the cap: measured full locks at n=5, decode ==
    the FULL least model {p,q,q2,r,s}."""

    def test_pc12_n4_compiles_decodes_full_model_with_locks(self):
        v = check_program("PC12n4", PC12_N4, {"p", "q", "q2", "r"})
        self.assertEqual(v["predicted"], ["p", "q", "q2", "r"])
        self.assertEqual(v["terminal_decodes"], [["p", "q", "q2", "r"]])
        self.assertEqual((v["n_rows"], v["tiles"], v["assemblies"],
                          v["terminals"]), (4, 16, 70, 1))
        self.assertTrue(v["full_locks"])
        self.assertTrue(v["ok"])

    def test_pc12_doc_full_locks_at_n5_after_spine_closure(self):
        v = check_program("PC12doc", PC12_DOC,
                          {"p", "q", "q2", "r", "s"})
        self.assertEqual((v["n_rows"], v["tiles"], v["assemblies"],
                          v["terminals"]), (5, 20, 126, 1))
        self.assertTrue(v["full_locks"])  # L5 attaches: SP5 class
        self.assertEqual(v["terminal_decodes"],
                         [["p", "q", "q2", "r", "s"]])

    def test_pc12_doc_reader_swap_layout_measured(self):
        build = compile_program(PC12_DOC, name="PC12doc")
        # consumer-aware passthrough + reader swap (designs/009 §9.2)
        self.assertEqual(build["tiles"]["Cq2"]["N"], "q-t-done")
        self.assertEqual(build["tiles"]["DAr"]["S"], "q-t-done")
        self.assertEqual(build["tiles"]["DBr"]["S"], "q2-t-done")

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
    d4-reported row-structure break in the emitted build — full locks
    since the stage-7 spine closure (designs/010 §10.4-3, tick 62);
    the dead readers stay BFS-absent (falsifier not triggered)."""

    def test_pr13_dead_compiles_and_decodes_least_model(self):
        v = check_program("PR13dead", PR13_DEAD, {"p", "q", "s"})
        self.assertEqual(v["predicted"], ["p", "q", "s"])
        self.assertEqual(v["terminal_decodes"], [["p", "q", "s"]])
        self.assertEqual(v["dead_variant_glues"], ["and1_r", "unit1_q2"])
        self.assertTrue(all(v["dead_glues_absent"].values()))
        # measured shape of the silent acceptance (stage-7 closure:
        # assemblies grew from the prefix-capped 70, all rows lock)
        self.assertEqual((v["n_rows"], v["tiles"], v["assemblies"],
                          v["terminals"]), (6, 26, 210, 1))
        self.assertTrue(v["full_locks"])  # 6 of 6 rows lock
        self.assertEqual(v["d4_severity"], "error")

    def test_pr13_dead_all_six_rows_lock_after_spine_closure(self):
        build = compile_program(PR13_DEAD, name="PR13dead")
        self.assertEqual(build["rows"], {1: "p", 2: "s", 3: "q",
                                         4: "z", 5: "q2", 6: "r"})
        _seen, terminals = producible(build)
        _atoms, locked = decode(build, terminals[0])
        self.assertEqual(locked, 6)
        self.assertIn("V5p", build["tiles"])   # emitted column-2
        self.assertIn("UD5q2", build["tiles"])  # collision pair
        self.assertIn("column 2 is not one-tile",
                      build["d4"]["detail"])

    def test_pr14_refuses_gate_a_union_naming_both_arms(self):
        # stage 6 closes the tick-55 silent acceptance (loud refusal
        # restored; message names both accepted placements).
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program(PR14_DOC, name="PR14doc")
        msg = str(cm.exception)
        self.assertIn("conjunctive variant of false head 'r'", msg)
        self.assertIn("gate A union", msg)
        self.assertIn("row-1 via (fact hi)", msg)
        self.assertIn("positional i-2 passthrough", msg)
        self.assertIn("got rows (hi 5, lo 4, derived 4)", msg)


if __name__ == "__main__":
    unittest.main()
