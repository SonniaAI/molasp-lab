"""Regression tests for the designs/003 body-conjunction builds F1-F3
(tick 18, SON-4758).  Stdlib-only BFS; clingo enforced when present.

Pins:
  F1  the corrected P_AND build has a unique terminal decoding {p,q,r};
      cutting EITHER witness channel (p's seed fact / q's fact tile)
      makes r's true-value glue producible in zero assemblies.
  F2  P_AND-q terminates uniquely at {p} with all three rows locked,
      and no true-value glue for q or r is ever producible.
  F3  the W1 dropped-literal wrong compile terminates uniquely at
      {q,r} — a NON-model (clingo: stable model {q}) — so the
      BFS-vs-clingo certificate fires; static AND-discipline (d2)
      flags the missing p-read independently.
  E1/E2  the as-written design tables stall: build1_raw at {p}
      (D2T.S=f-q matches nothing), build3_raw at {q} — which IS the
      stable model, i.e. a wrong compile that escapes the semantic
      certificate by stalling (the reason d2 is a compiler invariant).
  d1  via discipline: no violations in any build.
  d2  AND discipline holds on the correct build.
  inertness  unique-name rule for SP4/cap3/rf-relay/pf-cap.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "evidence", "2026-10-06-body-conjunction-builds")
sys.path.insert(0, D)

from tiles_and import BUILDS, PROGRAMS  # noqa: E402
from atam_check_and import (producible, decode, exposes_glue,  # noqa: E402
                            via_discipline, and_discipline, clingo_models)

try:
    import clingo  # noqa: F401
    HAS_CLINGO = True
except ImportError:
    HAS_CLINGO = False


class TestF1Foundedness(unittest.TestCase):
    def test_build1_unique_terminal_decodes_stable_model(self):
        seen, terms = producible(BUILDS["build1"])
        self.assertEqual(len(terms), 1)
        self.assertEqual(decode(BUILDS["build1"], terms[0]), ("pqr", 3))

    def test_cut_p_fact_kills_r_true_tiles(self):
        b = BUILDS["build1_cutp"]
        seen, terms = producible(b)
        self.assertFalse(exposes_glue(b, seen, "r-t"))
        self.assertFalse(exposes_glue(b, seen, "and1_r"))
        for t in terms:
            self.assertNotIn("r", decode(b, t)[0])

    def test_cut_q_fact_kills_r_true_tiles(self):
        b = BUILDS["build1_cutq"]
        seen, terms = producible(b)
        self.assertFalse(exposes_glue(b, seen, "r-t"))
        self.assertFalse(exposes_glue(b, seen, "and1_r"))
        for t in terms:
            self.assertNotIn("r", decode(b, t)[0])

    def test_cut_p_fact_overcollapses_the_chain(self):
        # Honest recorded behaviour, stronger than the design narrative:
        # with chain-discipline facts, deleting p's fact kills q's fact
        # tile too — the cut re-run terminates at the empty decode.
        b = BUILDS["build1_cutp"]
        _, terms = producible(b)
        self.assertEqual(sorted({decode(b, t)[0] for t in terms}), [""])


class TestF2SlotADeath(unittest.TestCase):
    def test_build2_unique_terminal_p_all_rows_locked(self):
        b = BUILDS["build2"]
        seen, terms = producible(b)
        self.assertEqual(len(terms), 1)
        self.assertEqual(decode(b, terms[0]), ("p", 3))

    def test_no_true_value_glue_for_q_or_r_ever_producible(self):
        b = BUILDS["build2"]
        seen, _ = producible(b)
        for glue in ("q-t", "r-t", "and1_r"):
            self.assertFalse(exposes_glue(b, seen, glue), glue)


class TestF3CertificateArm(unittest.TestCase):
    def test_build3_unique_terminal_is_a_non_model(self):
        b = BUILDS["build3"]
        _, terms = producible(b)
        self.assertEqual(len(terms), 1)
        self.assertEqual(decode(b, terms[0])[0], "qr")

    @unittest.skipUnless(HAS_CLINGO, "clingo module not available")
    def test_certificate_fires_against_clingo(self):
        b = BUILDS["build3"]
        _, terms = producible(b)
        decodes = sorted({decode(b, t)[0] for t in terms})
        stable = clingo_models(PROGRAMS["P_AND_minus_p"])
        stable_str = "".join(sorted(a.rstrip(".") for a in stable[0]))
        self.assertEqual(stable_str, "q")
        self.assertNotEqual(decodes, [stable_str])

    def test_d2_static_flags_missing_body_literal(self):
        b = BUILDS["build3"]
        v = and_discipline(b, {"r": ["p", "q"]})
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0][0], "r")
        self.assertEqual(v[0][1], "p")

    def test_d2_holds_on_the_correct_build(self):
        self.assertEqual(and_discipline(BUILDS["build1"], {"r": ["p", "q"]}), [])


class TestErrataDemolitions(unittest.TestCase):
    """The as-written tick-17 tables fail their own predictions; these
    pins keep the demolitions machine-checked."""

    def test_E1_as_written_build1_stalls_at_p(self):
        b = BUILDS["build1_raw"]
        _, terms = producible(b)
        self.assertEqual(sorted({decode(b, t)[0] for t in terms}), ["p"])

    def test_E2_as_written_build3_stalls_and_masquerades_as_correct(self):
        b = BUILDS["build3_raw"]
        _, terms = producible(b)
        # stalls at {q} — the stable model of P_AND-p: the wrong
        # compile escapes the semantic certificate by stalling.
        self.assertEqual(sorted({decode(b, t)[0] for t in terms}), ["q"])
        # ...but d2 still flags the dropped literal:
        self.assertEqual(len(and_discipline(b, {"r": ["p", "q"]})), 1)


class TestStructuralInvariants(unittest.TestCase):
    def test_d1_via_discipline_no_violations_anywhere(self):
        for name, b in BUILDS.items():
            self.assertEqual(via_discipline(b), [], name)

    def test_unique_name_inertness(self):
        inert = {"SP4", "cap3", "rf-relay", "pf-cap", "u-cutp"}
        for name, b in BUILDS.items():
            occ = {}
            for faces in b["tiles"].values():
                for g in faces.values():
                    occ[g] = occ.get(g, 0) + 1
            for g in b["seed"].values():
                occ[g] = occ.get(g, 0) + 1
            for n in inert:
                self.assertIn(occ.get(n, 0), (0, 1), (name, n))

    @unittest.skipUnless(HAS_CLINGO, "clingo module not available")
    def test_clingo_semantic_anchors(self):
        self.assertEqual(clingo_models(PROGRAMS["P_AND"]),
                         [["p.", "q.", "r."]])
        self.assertEqual(clingo_models(PROGRAMS["P_AND_minus_q"]), [["p."]])
        self.assertEqual(clingo_models(PROGRAMS["P_AND_minus_p"]), [["q."]])


if __name__ == "__main__":
    unittest.main()
