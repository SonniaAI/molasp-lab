"""Designs/008 chain-refusal baseline: today-truth pins for the
twice-derived-chain corpus programs under compiler v0.1.

Every pin in this file records the *probed* behavior of the current
compiler (probe run 2026-10-07 ~18:44Z, tick 47 wait-work) — none of it
is guessed from the design doc. These are the acceptance boundary for
the v0.2 relaxation (designs/008, PR3): the G1 refusals pinned here
must FLIP to verified corpus entries (PC9, PC11) when the
intermediate-derived-row machinery lands, the cycle refusal must
SURVIVE it, and PC10 must re-verify on the derived-row basis (its
fact-false-row baseline numbers below are expected to move).

The PC10 surprise (research-log 2026-10-07-chain-refusal-baseline.md):
designs/008 §1 lists PC10 as blocked by G1+G2, but the probe shows it
already compiles and BFS-verifies today — rule atoms outside
`predicted` take fact-false rows, so the G1 gate (armed only for
predicted atoms) never fires. The relaxation is needed for the
false-cap relay *machinery*, not for PC10's least model.
"""

import unittest

from molasp.compiler import CompileError, UnsupportedGeometry
from molasp.parity import check_program, compile_program


class TestChainRefusalsV01(unittest.TestCase):
    """Programs designs/008 §4 proposes as PC9/PC10/PC11, probed as-is
    against v0.1. PC9 and PC11 hit G1 (rule atom below the terminal
    row); the cycle program hits the tick-14 order falsifier."""

    def test_pc9_live_two_link_chain_refused_g1(self):
        # p. q :- p. r :- q.  — least model {p,q,r}; q is a derived
        # row at y=2, r terminal. v0.1 refuses at G1 before any G2
        # check on r's unit reader.
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program("p. q :- p. r :- q.", name="PC9",
                            predicted={"p", "q", "r"})
        msg = str(cm.exception)
        self.assertIn("rule atom 'q' at non-terminal row 2", msg)
        self.assertIn("multi-derived-row chains", msg)

    def test_pc11_chain_plus_and_terminal_refused_g1(self):
        # p. q. s. q2 :- p. r :- q2, s. r :- q2.  — q2 derived at
        # row 4 below the terminal r.
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program(
                "p. q. s. q2 :- p. r :- q2, s. r :- q2.",
                name="PC11", predicted={"p", "q", "s", "q2", "r"})
        self.assertIn("rule atom 'q2' at non-terminal row 4",
                      str(cm.exception))

    def test_g1_fires_before_g2_in_a_chain(self):
        # p. q :- p. s. r :- q. — r's unit reader would be a G2
        # (direct-below unit) refusal, but q's non-terminal rule atom
        # is rejected first: G1 (compiler.py G1 region) precedes G2 in
        # evaluation order. Pins the gate ordering the relaxation must
        # respect when it lifts both.
        with self.assertRaises(UnsupportedGeometry) as cm:
            compile_program("p. q :- p. s. r :- q.", name="G2inchain",
                            predicted={"p", "q", "s", "r"})
        self.assertIn("non-terminal row 2", str(cm.exception))
        self.assertNotIn("via-carried", str(cm.exception))

    def test_cycle_refused_by_order_falsifier(self):
        # q :- r. r :- q. — no fact row, no founded order. This
        # refusal is geometry-independent (tick-14 order falsifier)
        # and must SURVIVE the v0.2 relaxation untouched.
        with self.assertRaises(CompileError) as cm:
            compile_program("q :- r. r :- q.", name="CYC")
        self.assertIn("dependency cycle", str(cm.exception))


class TestPC10BaselineV01(unittest.TestCase):
    """PC10 (p. q :- z. r :- q., least model {p}) compiles and
    BFS-verifies under v0.1 today: q and r fall outside `predicted`,
    so both take fact-false rows and the dead reader `unit1_r` is a
    plain dead-variant glue. Numbers below freeze the v0.1 basis; the
    v0.2 tick must re-verify on the intermediate-derived-row basis
    (false-cap relay at q) with these numbers free to move."""

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

    def test_baseline_scale(self):
        # 4 rows (p, z, q, r all get rows), 16 tiles, 70 assemblies,
        # 1 terminal — the v0.1 fact-false-row basis for a dead chain.
        self.assertEqual(self.rep["n_rows"], 4)
        self.assertEqual(self.rep["tiles"], 16)
        self.assertEqual(self.rep["assemblies"], 70)
        self.assertEqual(self.rep["terminals"], 1)


if __name__ == "__main__":
    unittest.main()
