"""Regression tests for the OR-AND composition builds (tick 20,
SON-4763; designs/003 honest-limit item 3).  Stdlib-only BFS; clingo
enforced when present.

Pins:
  G1  P_OA (`p. q. r :- p, q. r :- p.`): two terminals — one per
      variant path (conjunctive DAr&DBr, unit Cr&Ur) — both decoding
      {p,q,r} with 3 locked rows; NO assembly mixes variants; the
      shared value output r-t-done appears in exactly 2 tile types
      (inventory) and at most once per assembly (site competition).
  G1-cut  seed surgery on p's fact over-collapses to the empty
      decode and r-t is never producible (fact deletion is not
      modular — tick 18 finding 3 carries into the OR geometry).
  G2  OR rescue: P_OA-q (`p. r :- p, q. r :- p.`) terminates
      uniquely at {p,r} — the SAME deletion that killed r in
      designs/003 build 2 (pure AND, terminal {p}).  The conjunctive
      variant is emitted but value-dead: q-t, q-t-done, and1_r
      producible in 0, DBr in no assembly.
  G3  foundedness: P_OA-p terminates uniquely at {q}; p-t and r-t
      producible in 0 (both of r's rules die with p).
  G4  certificate: the W2 dropped-unit-rule wrong compile terminates
      uniquely at {p} != clingo stable {p,r}; the static d3 closure
      check fires independently (rule r :- p live under the solver's
      own model).
  d1/d2/d3  via discipline holds on all builds; AND discipline holds
      where in scope (r predicted true); closure/support holds on
      builds 1-3 and fires on build 4.
  inertness  unique-name rule for SP4 / cap3 / and1_r-done /
      unit1_r-done / rf-relay / u-cutp.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "evidence", "2026-10-06-or-and-composition")
sys.path.insert(0, D)

from tiles_orand import BUILDS, PROGRAMS, FACTS, RULES, PREDICTED  # noqa: E402
from atam_check_orand import (producible, decode, exposes_glue,  # noqa: E402
                              tile_in_any, glue_counts, via_discipline,
                              and_discipline, closure_support,
                              clingo_models)

try:
    import clingo  # noqa: F401
    HAS_CLINGO = True
except ImportError:
    HAS_CLINGO = False


class TestG1Composition(unittest.TestCase):
    def setUp(self):
        self.b = BUILDS["build1"]
        self.seen, self.terms = producible(self.b)

    def test_two_terminals_both_decode_pqr_locked(self):
        self.assertEqual(len(self.terms), 2)
        for t in self.terms:
            self.assertEqual(decode(self.b, t), ("pqr", 3))

    def test_both_variant_paths_realize(self):
        conj = [t for t in self.terms if "DAr" in t.values()]
        unit = [t for t in self.terms if "Cr" in t.values()]
        self.assertEqual(len(conj), 1)
        self.assertEqual(len(unit), 1)

    def test_no_assembly_mixes_variants(self):
        for asm in self.seen:
            names = {n for _p, n in asm}
            self.assertFalse(names & {"DAr", "DBr"} and
                             names & {"Cr", "Ur"})

    def test_shared_value_output_fingerprint(self):
        # inventory: exactly the two reader tiles expose r-t-done
        self.assertEqual(glue_counts(self.b).get("r-t-done"), 2)
        # per assembly: site competition caps exposure at 1
        for asm in self.seen:
            count = sum(1 for _p, n in asm
                        if n in ("DBr", "Ur"))
            self.assertLessEqual(count, 1)

    def test_r_true_tiles_producible(self):
        self.assertTrue(exposes_glue(self.b, self.seen, "r-t"))


class TestG1Cut(unittest.TestCase):
    def test_cut_p_fact_overcollapses(self):
        b = BUILDS["build1_cutp"]
        seen, terms = producible(b)
        self.assertFalse(exposes_glue(b, seen, "r-t"))
        for t in terms:
            self.assertNotIn("r", decode(b, t)[0])


class TestG2OrRescue(unittest.TestCase):
    def test_unique_terminal_pr(self):
        b = BUILDS["build2"]
        seen, terms = producible(b)
        self.assertEqual(len(terms), 1)
        self.assertEqual(decode(b, terms[0]), ("pr", 3))

    def test_conjunctive_variant_value_dead(self):
        b = BUILDS["build2"]
        seen, terms = producible(b)
        self.assertFalse(exposes_glue(b, seen, "q-t"))
        self.assertFalse(exposes_glue(b, seen, "q-t-done"))
        self.assertFalse(exposes_glue(b, seen, "and1_r"))
        self.assertFalse(tile_in_any(b, seen, "DBr"))
        self.assertFalse(tile_in_any(b, seen, "DAr"))


class TestG3Foundedness(unittest.TestCase):
    def test_unique_terminal_q(self):
        b = BUILDS["build3"]
        seen, terms = producible(b)
        self.assertEqual(len(terms), 1)
        self.assertEqual(decode(b, terms[0]), ("q", 3))
        self.assertFalse(exposes_glue(b, seen, "p-t"))
        self.assertFalse(exposes_glue(b, seen, "r-t"))


class TestG4Certificate(unittest.TestCase):
    def test_unique_terminal_p(self):
        b = BUILDS["build4"]
        seen, terms = producible(b)
        self.assertEqual(len(terms), 1)
        self.assertEqual(decode(b, terms[0]), ("p", 3))

    def test_d3_closure_fires_statically(self):
        v = closure_support(set(PREDICTED["build4"]), FACTS, RULES)
        self.assertIn(["closure", "r", ["p"]],
                      [list(x) for x in v])

    @unittest.skipUnless(HAS_CLINGO, "clingo module not available")
    def test_certificate_fires_vs_clingo(self):
        b = BUILDS["build4"]
        _seen, terms = producible(b)
        dec = sorted({decode(b, t)[0] for t in terms})
        stable = clingo_models(PROGRAMS["P_OA_minus_q"])[0]
        stable_str = "".join(sorted(a.rstrip(".") for a in stable))
        self.assertEqual(dec, ["p"])
        self.assertNotEqual(dec, [stable_str])


class TestDisciplines(unittest.TestCase):
    def test_d1_via_discipline_all_builds(self):
        for name, b in BUILDS.items():
            self.assertEqual(via_discipline(b), [], name)

    def test_d2_and_discipline_in_scope(self):
        for name in ("build1", "build2"):
            self.assertEqual(
                and_discipline(BUILDS[name], {"r": ["p", "q"]}), [], name)

    def test_d3_closure_support(self):
        for name in ("build1", "build2", "build3"):
            self.assertEqual(
                closure_support(set(PREDICTED[name]), FACTS, RULES), [], name)
        self.assertNotEqual(
            closure_support(set(PREDICTED["build4"]), FACTS, RULES), [])

    @unittest.skipUnless(HAS_CLINGO, "clingo module not available")
    def test_predicted_sets_match_clingo_stable_models(self):
        expected = {"P_OA": "pqr", "P_OA_minus_q": "pr",
                    "P_OA_minus_p": "q"}
        pred = {"P_OA": "build1", "P_OA_minus_q": "build2",
                "P_OA_minus_p": "build3"}
        for prog, key in pred.items():
            stable = clingo_models(PROGRAMS[prog])[0]
            stable_str = "".join(sorted(a.rstrip(".") for a in stable))
            self.assertEqual(stable_str, expected[prog])
            self.assertEqual("".join(sorted(PREDICTED[key])), expected[prog])


class TestInertness(unittest.TestCase):
    def test_unique_names_occur_exactly_once_where_used(self):
        names = ["SP4", "cap3", "and1_r-done", "unit1_r-done",
                 "rf-relay", "u-cutp"]
        for bname, b in BUILDS.items():
            occ = glue_counts(b)
            for g in names:
                self.assertIn(occ.get(g, 0), (0, 1), (bname, g))


if __name__ == "__main__":
    unittest.main()
