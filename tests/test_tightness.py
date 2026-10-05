"""Tightness verdicts on the canonical cases from the founding analysis."""

import unittest

from molasp import tightness as T


class TestParse(unittest.TestCase):
    def test_fact_rule_constraint(self):
        program = T.parse("a.\n p :- a, not q. \n:- p. % comment\n")
        self.assertEqual(len(program), 3)
        self.assertEqual(program[0], T.Rule("a", [], []))
        self.assertEqual(program[1], T.Rule("p", ["a"], ["q"]))
        self.assertEqual(program[2], T.Rule(None, ["p"], []))

    def test_rejects_bad_atom(self):
        with self.assertRaises(ValueError):
            T.parse("BadAtom.")

    def test_rejects_missing_period(self):
        with self.assertRaises(ValueError):
            T.parse("a :- b")


class TestTightness(unittest.TestCase):
    def test_self_loop_is_not_tight(self):
        # Comp(P) of `p :- p.` admits {p} and {}; only {} is stable.
        # The positive dependency graph has the cycle p -> p.
        tight, cycles = T.tightness(T.parse("p :- p."))
        self.assertFalse(tight)
        self.assertEqual(cycles, [["p"]])

    def test_mutual_recursion_is_not_tight(self):
        tight, cycles = T.tightness(T.parse("p :- q.\nq :- p.\na."))
        self.assertFalse(tight)
        self.assertEqual(len(cycles), 1)
        self.assertEqual(set(cycles[0]), {"p", "q"})

    def test_positive_cycle_with_negation_elsewhere_is_not_tight(self):
        # `a :- b, not z. b :- a.` has positive edges a<->b: no level
        # mapping exists, so not tight regardless of the `not z`.
        tight, _ = T.tightness(T.parse("a :- b, not z.\nb :- a."))
        self.assertFalse(tight)

    def test_simple_chain_is_tight(self):
        tight, cycles = T.tightness(T.parse("a.\np :- a.\nq :- p."))
        self.assertTrue(tight)
        self.assertEqual(cycles, [])

    def test_choice_between_atoms_is_tight(self):
        # `a :- not b. b :- not a.` has no positive dependency edges at
        # all, hence trivially tight — and its stable models {a}, {b}
        # are exactly its supported models. The gap between this case
        # and the self-support case is the whole foundedness question.
        tight, cycles = T.tightness(T.parse("a :- not b.\nb :- not a."))
        self.assertTrue(tight)
        self.assertEqual(cycles, [])

    def test_constraints_do_not_create_dependencies(self):
        tight, _ = T.tightness(T.parse(":- p, q.\np."))
        self.assertTrue(tight)


if __name__ == "__main__":
    unittest.main()
