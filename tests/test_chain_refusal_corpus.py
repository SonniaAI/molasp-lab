"""Designs/008 stage-1 acceptance pins: the v0.2 unit-chain fragment.

Tick 47 pinned v0.1's today-truth for the twice-derived-chain corpus
programs (G1 refusals for PC9/PC11, cycle refusal, PC10's fact-false-
row surprise). This file pins the FLIPPED truth after the v0.2 stage-1
relaxation landed in molasp/compiler.py (tick 48):

  - PC9 (live two-link unit chain) now COMPILES and BFS-verifies:
    unique terminal decode = least model {p,q,r}, full locks, first
    intermediate derived row. Measured: 3 rows, 12 tiles, 35
    assemblies, 1 terminal, no dead variants.
  - The old PR3 program (middle-fact chain `p. q. r :- p. s :- r.`)
    is legal chain geometry now and verifies: 4 rows, 16 tiles, 70
    assemblies, 1 terminal.
  - PC10 keeps its v0.1 fact-false-row basis VERBATIM (16 tiles / 70
    assemblies pinned tick 47): stage 1 rules predicted-false rule
    atoms keep the plain false row — that row IS the false-cap relay;
    explicit dead-reader emission for false derived heads is deferred.
  - CYC survives untouched (order falsifier is geometry-independent).
  - PC11 still refuses — now honestly: its AND lo-literal sits at row
    3, not the row-1 via (PR9). The derived-hi conduit hazard is
    separately pinned (PR10): a slot-A AND conduit over a derived row
    would read its variant glue, not a truth-typed value.
  - New refusals the relaxation must add (PR3/PR7/PR8): non-adjacent
    chain reads, OR at an intermediate derived row, chain depth > 2.

All numbers below are measured probe output (2026-10-07 tick 48),
not design predictions.
"""

import unittest

from molasp.compiler import CompileError, UnsupportedGeometry
from molasp.parity import check_program, compile_program


class TestChainCorpusV02(unittest.TestCase):
    """PC9 and the middle-fact chain: refusal -> verified entries."""

    @classmethod
    def setUpClass(cls):
        cls.pc9 = check_program("PC9", "p. q :- p. r :- q.",
                                {"p", "q", "r"})
        cls.mid = check_program("PC12", "p. q. r :- p. s :- r.",
                                {"p", "q", "r", "s"})

    def test_pc9_ok_model_and_unique_decode(self):
        self.assertTrue(self.pc9["ok"])
        self.assertEqual(self.pc9["predicted"], ["p", "q", "r"])
        self.assertEqual(self.pc9["terminal_decodes"], [["p", "q", "r"]])

    def test_pc9_full_locks_and_no_dead_variants(self):
        self.assertTrue(self.pc9["full_locks"])
        self.assertEqual(self.pc9["dead_variant_glues"], [])

    def test_pc9_scale(self):
        # 3 rows, 12 tiles (4 per row: S, conduit, reader, lock — the
        # intermediate row reuses the terminal unit pair verbatim),
        # 35 assemblies, 1 terminal.
        self.assertEqual(self.pc9["n_rows"], 3)
        self.assertEqual(self.pc9["tiles"], 12)
        self.assertEqual(self.pc9["assemblies"], 35)
        self.assertEqual(self.pc9["terminals"], 1)

    def test_middle_fact_chain_ok(self):
        # The old PR3 program: a fact row between the two chain links
        # relays the chain glue up the V column unchanged.
        self.assertTrue(self.mid["ok"])
        self.assertEqual(self.mid["terminal_decodes"],
                         [["p", "q", "r", "s"]])
        self.assertTrue(self.mid["full_locks"])
        self.assertEqual((self.mid["n_rows"], self.mid["tiles"],
                          self.mid["assemblies"], self.mid["terminals"]),
                         (4, 16, 70, 1))


class TestChainRefusalsV02(unittest.TestCase):
    """What stage 1 still refuses, and why (messages are the design)."""

    def test_cycle_refused_by_order_falsifier(self):
        # Must SURVIVE the relaxation untouched (tick-14 discipline).
        with self.assertRaises(CompileError) as cm:
            compile_program("q :- r. r :- q.", name="CYC")
        self.assertIn("dependency cycle", str(cm.exception))

    def test_pc11_refused_on_and_lo_row(self):
        # designs/008 PC11: q2 is legal intermediate geometry now, but
        # r's AND reads s at row 3 — not the row-1 via.
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program(
                "p. q. s. q2 :- p. r :- q2, s. r :- q2.",
                name="PC11", predicted={"p", "q", "s", "q2", "r"})
        self.assertIn("conjunctive variant of 'r'", str(cm.exception))
        self.assertIn("row-1 via", str(cm.exception))

    def test_non_adjacent_chain_refused(self):
        # The old G1-before-G2 probe shape: q at row 2 is legal, but
        # r reads it from row 4 — two rows up, non-adjacent.
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program("p. q :- p. s. r :- q.", name="G2inchain",
                            predicted={"p", "q", "s", "r"})
        self.assertIn("non-adjacent", str(cm.exception))

    def test_or_at_intermediate_refused(self):
        # Two unit bodies at a non-terminal row: each variant conduit
        # exposes its own north glue — no truth-OR relay exists.
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program("p. z. q :- p. q :- p. r :- q.",
                            name="ORmid")
        self.assertIn("truth-OR relay", str(cm.exception))

    def test_chain_depth_over_2_refused(self):
        # designs/008 §6 boundary: chain length 2 only.
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program("p. q :- p. r :- q. s :- r.", name="DEPTH3")
        self.assertIn("chain depth", str(cm.exception))

    def test_and_over_derived_hi_refused(self):
        # The slot-A AND conduit over a derived row would read its
        # variant glue (unit1_q2-done), not a truth-typed value.
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program("p. s. q2 :- p. r :- q2, p.", name="ANDhi")
        self.assertIn("is a derived row", str(cm.exception))

    def test_via_suspended_refused(self):
        # A row-1 via read above a derived row: the V column carries
        # the chain link now, the via is suspended.
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program("p. q :- p. z. w :- p.", name="VIAsusp")
        self.assertIn("suspended", str(cm.exception))

    def test_adjacent_below_fact_unit_still_refused(self):
        # designs/002 geometry, unwired in stage 1 (PR4 pin kept).
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program("p. q. r :- q.", name="PR4")
        self.assertIn("via-carried", str(cm.exception))
        self.assertIn("designs/002", str(cm.exception))


class TestPC10BaselineV02(unittest.TestCase):
    """PC10 keeps the v0.1 fact-false-row basis verbatim in stage 1:
    a predicted-false rule atom's plain false row IS the false-cap
    relay (V-column relay + f-typed value); explicit dead-reader
    emission for false derived heads is deferred to a later stage.
    The tick-47 baseline numbers must not move."""

    @classmethod
    def setUpClass(cls):
        cls.rep = check_program("PC10", "p. q :- z. r :- q.", {"p"})

    def test_baseline_ok_and_model(self):
        self.assertTrue(self.rep["ok"])
        self.assertEqual(self.rep["predicted"], ["p"])
        self.assertEqual(self.rep["terminal_decodes"], [["p"]])

    def test_baseline_full_locks_and_dead_reader(self):
        self.assertTrue(self.rep["full_locks"])
        self.assertEqual(self.rep["dead_variant_glues"], ["unit1_r"])
        self.assertTrue(self.rep["dead_glues_absent"]["unit1_r"])

    def test_baseline_scale_unchanged(self):
        # 4 rows, 16 tiles, 70 assemblies, 1 terminal — identical to
        # the v0.1 probe (tick 47): the basis swap did not move them.
        self.assertEqual(self.rep["n_rows"], 4)
        self.assertEqual(self.rep["tiles"], 16)
        self.assertEqual(self.rep["assemblies"], 70)
        self.assertEqual(self.rep["terminals"], 1)


if __name__ == "__main__":
    unittest.main()
