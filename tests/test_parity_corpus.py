"""Parity-corpus pins (tick 46, SON-4819).

Two layers, matching house style (receipts first, machinery
exercised directly where cheap):

  R*  receipt pins — every verdict line in evidence/.../run.out is
      recomputed-against: all 8 compiling programs ok, decodes ==
      registered least models, full locks, dead glues absent, all 6
      refusals raising the registered flavor (parsed from the JSON
      block of the receipt).
  B*  BFS pins — the three smallest arms (PC1/PC3/PC4) recomputed
      from scratch through molasp.parity (compile + exhaustive
      producibility), so the machinery itself is exercised by the
      suite, not just its saved output.

Suite arithmetic: 365 existing + these pins; the verbatim count is
quoted in the tick-46 log entry after running the exact CI command.
"""
import json
import os
import unittest

from molasp.parity import (
    CORPUS,
    REFUSALS,
    compile_program,
    dead_variant_glues,
    decode,
    producible,
)
from molasp.compiler import CompileError, UnsupportedGeometry

HERE = os.path.dirname(os.path.abspath(__file__))
RECEIPT = os.path.join(HERE, "..", "evidence", "2026-10-07-parity-corpus",
                       "run.out")


def _receipt_json():
    text = open(RECEIPT, encoding="utf-8").read()
    block = text.split("--- json ---", 1)[1]
    return json.loads(block)


class TestReceiptPins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rep = _receipt_json()

    def test_r0_all_ok(self):
        self.assertTrue(self.rep["all_ok"], "receipt must be all_ok")

    def test_r1_corpus_programs_all_ok(self):
        by = {r["name"]: r for r in self.rep["corpus"]}
        self.assertEqual(set(by), set(CORPUS))
        for name, r in by.items():
            self.assertTrue(r["ok"], name)
            self.assertEqual(r["predicted"], r["expected"], name)
            self.assertEqual(r["terminal_decodes"], [r["expected"]], name)
            self.assertTrue(r["full_locks"], name)
            self.assertTrue(all(r["dead_glues_absent"].values()), name)

    def test_r2_four_row_bfs_firsts(self):
        by = {r["name"]: r for r in self.rep["corpus"]}
        four = [r for r in by.values() if r["n_rows"] == 4]
        self.assertEqual({r["name"] for r in four},
                         {"PC5", "PC6", "PC7", "PC8"})
        for r in four:
            self.assertGreater(r["assemblies"], 0, r["name"])
            self.assertEqual(r["terminal_decodes"],
                             [["p", "q", "r", "s"]], r["name"])

    def test_r3_contention_three_terminals_one_decode(self):
        pc7 = next(r for r in self.rep["corpus"] if r["name"] == "PC7")
        self.assertEqual(pc7["terminals"], 3)
        self.assertEqual(len(pc7["terminal_decodes"]), 1)

    def test_r4_dead_variant_absence(self):
        by = {r["name"]: r for r in self.rep["corpus"]}
        self.assertEqual(by["PC3"]["dead_variant_glues"], ["and1_r"])
        self.assertEqual(by["PC4"]["dead_variant_glues"],
                         ["and1_r", "unit1_r"])

    def test_r5_refusal_flavors(self):
        got = {r["name"]: r for r in self.rep["refusals"]}
        self.assertEqual(set(got), set(REFUSALS))
        for name, spec in REFUSALS.items():
            r = got[name]
            self.assertTrue(r["ok"], (name, r))
            self.assertEqual(r["raised"], spec[1], name)


class TestBFSRecompute(unittest.TestCase):
    def _recompute(self, name):
        program, expected, _axis = CORPUS[name]
        build = compile_program(program, name=name)
        seen, terminals = producible(build)
        decodes = {frozenset(atoms) for atoms, _locked in
                   (decode(build, a) for a in terminals)}
        return build, seen, terminals, decodes, frozenset(expected)

    def test_b1_pc1_smallest_shape(self):
        build, seen, terminals, decodes, exp = self._recompute("PC1")
        self.assertEqual(len(build["tiles"]), 8)
        self.assertEqual(decodes, {exp})
        self.assertEqual(len(terminals), 1)

    def test_b2_pc3_dead_and_never_realizes(self):
        build, seen, terminals, decodes, exp = self._recompute("PC3")
        self.assertEqual(decodes, {exp})
        dead = dead_variant_glues(build)
        self.assertEqual(dead, {"and1_r"})
        for asm in seen:
            for _pos, tile in asm:
                if tile.startswith("seed"):
                    continue
                faces = set(build["tiles"][tile].values())
                self.assertFalse(dead & faces,
                                 f"dead glue realized by {tile}")

    def test_b3_pc4_false_terminal_row(self):
        build, seen, terminals, decodes, exp = self._recompute("PC4")
        self.assertEqual(decodes, {exp})
        self.assertEqual(exp, {"q"})
        for a in terminals:  # both variant channels dead
            names = {t for _p, t in a}
            self.assertNotIn("DBr", names)
            self.assertNotIn("Ur", names)


if __name__ == "__main__":
    unittest.main()
