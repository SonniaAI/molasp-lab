"""Compiler pass v0.1 acceptance tests (tick 21, SON-4765).

The pass in molasp/compiler.py emits tile inventories from program
text.  Its acceptance criterion is structural parity with the
hand-built, BFS-machine-checked builds of the tick-20 OR-AND corpus
(evidence/2026-10-06-or-and-composition): assembly behaviour depends
only on (rows, seed, per-row face-glue multisets), so parity with a
verified build implies the identical assembly system and therefore
the identical BFS verdicts (G1-G3, d1-d3 already recorded there).

Pins:
  P1-P3   compiled P_OA / P_OA-q / P_OA-p are structurally identical
          to BUILD1 / BUILD2 / BUILD3 respectively (14/13/9 tile
          types at the same rows, same seed, same face glues).
  P4      least-model prediction: compile with no override predicts
          {p,q,r} / {p,r} / {q} for the three programs.
  D3a     the tick-20 wrong compile W2 (solver model {p} for
          P_OA-q) is REFUSED at emit time — d3 completeness fires on
          the live unit rule r :- p.
  D3b     an underivable predicted-true atom is refused — d3 support.
  D3c     a fact omitted from the prediction is refused.
  ORD     row order is topological with first-appearance tie-break:
          P_OA-p compiles rows q < p < r (tick-14 discipline).
  U1      b >= 3 bodies are refused (slot widening untested).
  U2      a unit variant whose literal is not via-carried is refused.
  U3      a rule atom at a non-terminal row is refused (readers
          occupy the via column; multi-derived-row chains untested).
  POL     emission policy: in BUILD2 the dead conjunctive variant is
          EMITTED with true-typed reads (rule-local emission, killed
          by value typing — tick 20 point 3), and the false q row
          relays the via north rather than capping.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "evidence", "2026-10-06-or-and-composition")
sys.path.insert(0, D)

from molasp.compiler import (  # noqa: E402
    CompileError,
    UnsupportedGeometry,
    compile_program,
    least_model,
    parse_program,
    structural_signature,
)
from tiles_orand import BUILDS, PROGRAMS  # noqa: E402


def compiled(name, program):
    return compile_program(program, name=name)


class TestParity(unittest.TestCase):
    def _parity(self, hand, program):
        got = structural_signature(compiled("x", program))
        want = structural_signature(BUILDS[hand])
        self.assertEqual(got, want,
                         f"{hand}: compiled signature differs from hand build")

    def test_p1_build1(self):
        self._parity("build1", PROGRAMS["P_OA"])

    def test_p2_build2(self):
        self._parity("build2", PROGRAMS["P_OA_minus_q"])

    def test_p3_build3(self):
        # Stage 3 (tick 50) moves the terminal F-cap basis: compiled
        # build3 is the hand BUILD3 plus the emitted terminal dead
        # reader UD3r (predicted-false r, unit body p).  Minus that
        # one tile the compiled signature equals the hand build.
        b = compiled("x", PROGRAMS["P_OA_minus_p"])
        self.assertEqual(b["tiles"]["UD3r"],
                         {"W": "unit1_r", "S": "p-t-done",
                          "E": "r-t", "N": "r-t-done"})
        self.assertEqual(b["row_of"]["UD3r"], 3)
        merged = dict(b)
        merged["tiles"] = {k: v for k, v in b["tiles"].items()
                           if k != "UD3r"}
        merged["row_of"] = {k: v for k, v in b["row_of"].items()
                            if k != "UD3r"}
        self.assertEqual(structural_signature(merged),
                         structural_signature(BUILDS["build3"]),
                         "build3 minus UD3r: compiled signature differs "
                         "from hand build")

    def test_p4_tile_counts(self):
        self.assertEqual(len(compiled("x", PROGRAMS["P_OA"])["tiles"]), 14)
        self.assertEqual(
            len(compiled("x", PROGRAMS["P_OA_minus_q"])["tiles"]), 14)
        self.assertEqual(
            len(compiled("x", PROGRAMS["P_OA_minus_p"])["tiles"]), 13)
        # 13 = 12 + UD3r: stage 3 (tick 50) emits the terminal dead
        # reader for predicted-false r (unit body p); BUILD1/2 count
        # unmoved.

    def test_p4_least_model_prediction(self):
        for prog, want in (("P_OA", {"p", "q", "r"}),
                           ("P_OA_minus_q", {"p", "r"}),
                           ("P_OA_minus_p", {"q"})):
            b = compiled("x", PROGRAMS[prog])
            self.assertEqual(b["predicted"], want, prog)


class TestChecksFire(unittest.TestCase):
    def test_d3a_wrong_model_refused(self):
        # W2: the miscompiling solver's model {p} for P_OA-q.
        with self.assertRaises(CompileError) as cm:
            compile_program(PROGRAMS["P_OA_minus_q"], predicted={"p"})
        self.assertIn("d3 completeness", str(cm.exception))

    def test_d3b_unsupported_prediction_refused(self):
        with self.assertRaises(CompileError) as cm:
            compile_program("p. r :- p, q.", predicted={"p", "q", "r"})
        self.assertIn("d3 support", str(cm.exception))

    def test_d3c_missing_fact_refused(self):
        with self.assertRaises(CompileError) as cm:
            compile_program("p. q. r :- p, q.", predicted={"p", "r"})
        self.assertIn("d3 completeness", str(cm.exception))

    def test_ord_row_order_topological(self):
        b = compiled("x", PROGRAMS["P_OA_minus_p"])
        self.assertEqual([b["rows"][i] for i in (1, 2, 3)], ["q", "p", "r"])

    def test_u1_wide_body_refused(self):
        with self.assertRaises(UnsupportedGeometry):
            compile_program("p. q. s. r :- p, q, s.")

    def test_u2_non_via_unit_literal_refused(self):
        # r :- q with q at row 2 (adjacent-below, not via-carried).
        with self.assertRaises(UnsupportedGeometry):
            compile_program("p. q. r :- q.")

    def test_u3_nonterminal_rule_atom_refused(self):
        # s :- r puts a rule atom at a non-terminal row.
        with self.assertRaises(UnsupportedGeometry):
            compile_program("p. q. r :- p, q. s :- r.")


class TestEmissionPolicy(unittest.TestCase):
    def test_pol_dead_variant_emitted_true_typed(self):
        b = compiled("x", PROGRAMS["P_OA_minus_q"])
        reads = [t for t, f in b["tiles"].items()
                 if f.get("S") == "q-t-done" and f.get("E") == "and1_r"]
        self.assertEqual(len(reads), 1, "dead conjunctive variant must be emitted")

    def test_pol_false_row_relays_via(self):
        b = compiled("x", PROGRAMS["P_OA_minus_q"])
        relays = [t for t, f in b["tiles"].items()
                  if f.get("W") == "q-f" and f.get("N") == "p-t-done"]
        self.assertEqual(len(relays), 1,
                         "non-terminal false row must relay the via north")
        caps = [t for t, f in b["tiles"].items() if f.get("N") == "rf-relay"]
        self.assertEqual(caps, [],
                         "rf-relay cap is terminal-only in this build")


class TestParserModel(unittest.TestCase):
    def test_parse_and_model(self):
        facts, rules, order = parse_program(PROGRAMS["P_OA"])
        self.assertEqual(facts, ["p", "q"])
        self.assertEqual(rules, {"r": [["p", "q"], ["p"]]})
        self.assertEqual(order, ["p", "q", "r"])
        self.assertEqual(least_model(facts, rules), {"p", "q", "r"})


if __name__ == "__main__":
    unittest.main()
