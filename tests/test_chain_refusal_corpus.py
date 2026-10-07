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
  - PC10 in stage 2 (designs/008 §3, this tick): the intermediate
    false derived head q now CARRIES ITS DEAD READER EXPLICITLY —
    tile UD3q (W=unit1_q, S=z-t-done) is emitted machinery whose
    zero matchable faces (match strength 1 < TAU 2 each) BFS-prove
    it can never realize: 17 tiles / 70 assemblies / 1 terminal /
    full locks, model {p} unchanged.  The terminal false row keeps
    the v0.1 F-cap basis (PC4 pins it); terminal dead-reader
    emission and AND-bodied false heads stay deferred.
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
from molasp.parity import CORPUS, check_program, compile_program, producible


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


class TestPC10Stage2V02(unittest.TestCase):
    """PC10 after the stage-2 dead-reader emission (designs/008 §3):
    the intermediate false derived row (q at row 3) keeps the plain
    false row as its false-cap relay AND now emits its dead reader
    tile UD3q explicitly — the dead link is emitted machinery whose
    absence from every producible assembly is BFS-proved, not
    vacuous non-emission.  Measured tick 49 (2026-10-07): 4 rows,
    17 tiles, 70 assemblies, 1 terminal."""

    @classmethod
    def setUpClass(cls):
        cls.rep = check_program("PC10", "p. q :- z. r :- q.", {"p"})

    def test_baseline_ok_and_model(self):
        self.assertTrue(self.rep["ok"])
        self.assertEqual(self.rep["predicted"], ["p"])
        self.assertEqual(self.rep["terminal_decodes"], [["p"]])

    def test_full_locks_and_both_dead_paths_reported(self):
        # Stage 2 extended dead_variant_glues past the terminal head;
        # stage 3 (tick 50) makes r's link EMITTED machinery too —
        # both dead paths are now reported, emitted, and proven
        # absent rather than vacuously non-emitted.
        self.assertTrue(self.rep["full_locks"])
        self.assertEqual(self.rep["dead_variant_glues"],
                         ["unit1_q", "unit1_r"])
        self.assertTrue(self.rep["dead_glues_absent"]["unit1_q"])
        self.assertTrue(self.rep["dead_glues_absent"]["unit1_r"])

    def test_scale_after_emission(self):
        # 16 -> 17 tiles (UD3q, tick 49) -> 18 (UD4r, tick 50 stage
        # 3); assemblies/terminals unmoved — neither dead reader can
        # attach, so neither adds a growth path.
        self.assertEqual(self.rep["n_rows"], 4)
        self.assertEqual(self.rep["tiles"], 18)
        self.assertEqual(self.rep["assemblies"], 70)
        self.assertEqual(self.rep["terminals"], 1)


class TestDeadReaderEmissionStage2(unittest.TestCase):
    """The emitted dead reader itself (designs/008 §3 machinery):
    exact faces, BFS-proved non-realization, the false-cap basis it
    sits alongside, the deferred terminal boundary, and v0.1/v0.2
    byte-stability against the registered tick-46/48 receipt counts
    (hardcoded here so regeneration of run.out cannot make the
    stability pin vacuous)."""

    @classmethod
    def setUpClass(cls):
        cls.build = compile_program("p. q :- z. r :- q.", name="PC10")
        cls.seen, cls.terminals = producible(cls.build)

    def test_dead_reader_emitted_with_exact_faces(self):
        # q sits at row 3 (rows: p, z, q, r).  W is the vj conduit
        # glue the false basis never emits; S is the dead literal's
        # truth-typed done glue, emitted nowhere because z is false.
        self.assertEqual(
            self.build["tiles"].get("UD3q"),
            {"W": "unit1_q", "S": "z-t-done",
             "E": "q-t", "N": "q-t-done"})

    def test_dead_reader_never_realizes(self):
        # With match strength 1 < TAU 2 per face and every face a
        # glue no tile exposes, UD3q can never attach: it appears in
        # NO producible assembly (stacked dead readers would mutually
        # give 1 each — still below TAU).
        placed = {name for asm in self.seen for _pos, name in asm}
        self.assertNotIn("UD3q", placed)

    def test_false_cap_basis_sits_alongside(self):
        # The plain false row stays the false-cap relay (designs/008
        # stage 1): D-column conduit, V-column relay, lock all kept.
        for t in ("D3Fq", "V3p", "L3"):
            self.assertIn(t, self.build["tiles"])

    def test_terminal_false_head_emits_dead_reader(self):
        # Stage 3 (tick 50): the terminal predicted-false head r
        # (row 4, unit body q, q false) emits its dead reader; the
        # plain false row stays the false-cap relay (stage 1).  The
        # reader is emitted machinery and BFS-proved absent.
        self.assertIn("Fr", self.build["tiles"])
        self.assertIn("L4fr", self.build["tiles"])
        self.assertEqual(
            self.build["tiles"]["UD4r"],
            {"W": "unit1_r", "S": "q-t-done",
             "E": "r-t", "N": "r-t-done"})
        placed = {name for asm in self.seen for _pos, name in asm}
        self.assertNotIn("UD4r", placed)

    def test_v01_builds_byte_stable(self):
        # Registered receipt counts (tick 46/48; PC4 at tick 50),
        # hardcoded: stage 3 moves ONLY terminal-false-head programs
        # (PC4 12->13 = +UD3r); every other verified build is
        # unmoved and regeneration of run.out cannot make the
        # stability pin vacuous.
        registered = {"PC1": (8, 15), "PC2": (14, 45), "PC3": (14, 35),
                      "PC4": (13, 35), "PC5": (16, 70), "PC6": (18, 85),
                      "PC7": (20, 100), "PC8": (18, 85), "PC9": (12, 35)}
        for name, (prog, model, _note) in sorted(CORPUS.items()):
            rep = check_program(name, prog, model)
            self.assertTrue(rep["ok"], name)
            self.assertEqual((rep["tiles"], rep["assemblies"]),
                             registered[name], name)


if __name__ == "__main__":
    unittest.main()
