"""Tick-64 pins: n>=6 build survey after the stage-7 spine class
closure (SON-4856; receipt evidence/2026-10-08-n6-build-survey/
probe.out, run at HEAD 7714eac, records verbatim).

The tick-62 closure claim ("no second hidden cap") was measured at
n=5 only.  This survey extends the PC12-DOC family with decorative
facts to n=6..9 under pre-registered predictions P1-P6 (frozen in
the probe docstring in the same commit as the receipt): every one
holds.  The n=5 anchor re-measured (5, 20, 126, 1) before any new
row was trusted — probe self-calibration, not a new claim.

All numbers are measured probe output (2026-10-08 tick 64), not
design predictions; nothing here is a validated result until
independently reviewed.
"""

import unittest
from math import comb

from molasp.parity import check_program

# n -> (program, expected least model in decode order)
PROGRAMS = {
    5: ("p. s. q. q2 :- p. r :- q2, q.",
        ["p", "q", "q2", "r", "s"]),
    6: ("p. s. t. q. q2 :- p. r :- q2, q.",
        ["p", "q", "q2", "r", "s", "t"]),
    7: ("p. s. t. u. q. q2 :- p. r :- q2, q.",
        ["p", "q", "q2", "r", "s", "t", "u"]),
    8: ("p. s. t. u. v. q. q2 :- p. r :- q2, q.",
        ["p", "q", "q2", "r", "s", "t", "u", "v"]),
    9: ("p. s. t. u. v. w. q. q2 :- p. r :- q2, q.",
        ["p", "q", "q2", "r", "s", "t", "u", "v", "w"]),
}

# n -> (n_rows, tiles, assemblies, terminals), measured tick 64
# (n=4's (4, 16, 70, 1) was measured ticks 55/62 and anchors the
# series from below).
SHAPES = {
    5: (5, 20, 126, 1),
    6: (6, 24, 210, 1),
    7: (7, 28, 330, 1),
    8: (8, 32, 495, 1),
    9: (9, 36, 715, 1),
}


class N6BuildSurveyShapes(unittest.TestCase):
    """P1-P5 at n=5..9: rows == n, tiles == 4n, assemblies strictly
    monotone, unique terminal, full locks, decode == full least
    model.  P6 (no refusal at via distance up to 8) is implicit:
    every build compiled."""

    def test_shapes_full_locks_and_decode_n5_to_n9(self):
        for n, (prog, model) in sorted(PROGRAMS.items()):
            with self.subTest(n=n):
                v = check_program("PC12docN%d" % n, prog, set(model))
                self.assertEqual(
                    (v["n_rows"], v["tiles"], v["assemblies"],
                     v["terminals"]), SHAPES[n])
                self.assertTrue(v["full_locks"])   # P4: no table edge
                self.assertTrue(v["ok"])
                self.assertEqual(v["terminal_decodes"], [model])  # P5


class N6BuildSurveyClosedForm(unittest.TestCase):
    """EMPIRICAL closed form, not a theorem: measured assemblies
    equal C(n+4, 4) at every measured point n=4..9 (n=4: 70 from
    ticks 55/62).  Pinned as arithmetic on measured values so any
    future build change that breaks the fit fails loudly here; the
    combinatorial proof from the BFS enumerator is open (tick-65
    candidate)."""

    def test_assemblies_equal_binomial_n_plus_4_choose_4(self):
        for n, (_rows, _tiles, assemblies, _terms) in sorted(
                SHAPES.items()):
            with self.subTest(n=n):
                self.assertEqual(assemblies, comb(n + 4, 4))
        self.assertEqual(70, comb(8, 4))   # n=4 anchor of the series


if __name__ == "__main__":
    unittest.main()
