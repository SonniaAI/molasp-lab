"""Tick-65 pins: the C(n+4,4) assembly count is DERIVED for the
decorative-fact family — reached-assembly shapes equal the ideals
of the four-column poset (partitions in a 4xn box), both directions
(SON-4859; receipt evidence/2026-10-08-binomial-derivation/
probe.out, run at HEAD b651e40).

D2 (assemblies <-> shapes bijective), D3 (every reached shape is
an ideal), D4 (every ideal is reached) are re-derived LIVE at
n=4..8 by rerunning the BFS; n=9..12 are pinned as EMPIRICAL
constants (arithmetic on measured values from the receipt —
labeled, not silent). A compiler or strength-table change that
alters the attach grammar fails D2/D3/D4 at n<=8 loudly.

All numbers are measured probe output (2026-10-08 tick 65), not
design predictions; nothing here is a validated result until
independently reviewed.
"""

import unittest
from math import comb

from molasp.compiler import compile_program, least_model, parse_program
from molasp.parity import producible

ANCHOR_N4 = "p. q. q2 :- p. r :- q2, q."  # PC12-N4, ticks 55/62
DECOR = "tuvwxyz"


def program_for(n):
    if n == 4:
        return ANCHOR_N4
    decor = " ".join(a + "." for a in DECOR[:n - 5])
    if decor:
        decor += " "
    return "p. s. %sq. q2 :- p. r :- q2, q." % decor


def ideal_sites(h):
    return frozenset((x, y) for x in range(4) for y in range(1, h[x] + 1))


def ideals(n):
    return {frozenset(ideal_sites((h0, h1, h2, h3)))
            for h0 in range(n + 1) for h1 in range(h0 + 1)
            for h2 in range(h1 + 1) for h3 in range(h2 + 1)}


class BinomialIdealEquality(unittest.TestCase):
    """D2+D3+D4 live at n=4..8: the BFS 'seen' set maps bijectively
    onto the full ideal set of the 4-column poset, and |seen| ==
    C(n+4,4) (D1)."""

    def test_shapes_equal_ideals_and_bijective(self):
        for n in range(4, 9):
            with self.subTest(n=n):
                prog = program_for(n)
                facts, derived, _ = parse_program(prog)
                model = set(least_model(facts, derived))
                build = compile_program(
                    prog, name="PC12docN%d" % n, predicted=model)
                seen, _terminals = producible(build)
                site_tiles = {}
                shapes = set()
                for asm in seen:
                    shapes.add(frozenset(
                        (x, y) for (x, y), _t in asm if y >= 1))
                    for (x, y), tile in asm:
                        if y >= 1:
                            site_tiles.setdefault((x, y), set()).add(tile)
                # D2: one tile name per site across all assemblies
                self.assertTrue(all(len(v) == 1
                                    for v in site_tiles.values()))
                # D3 + D4: exact set equality with the box ideals
                self.assertEqual(shapes, ideals(n))
                # D1: the classical count
                self.assertEqual(len(seen), comb(n + 4, 4))


class BinomialEmpiricalTail(unittest.TestCase):
    """n=9..12 from the tick-65 receipt (EMPIRICAL constants,
    labeled per the tick-64 convention; the live pins above already
    guard the grammar at n<=8)."""

    TAIL = {9: 715, 10: 1001, 11: 1365, 12: 1820}

    def test_tail_matches_binomial(self):
        for n, measured in sorted(self.TAIL.items()):
            with self.subTest(n=n):
                self.assertEqual(measured, comb(n + 4, 4))
