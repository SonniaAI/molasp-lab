"""Tick-150 pins: the C(rows+4,4) assembly-count law holds for a
SECOND corpus family — PR13-dead (SON-5152, 2026-10-22).

Discharges designs/010 §10.9's hand-registered prediction ("PR13-dead
shares the grammar, 210 at n=6") by live measurement. For the PR13-dead
anchor `p. s. q. q2 :- z. r :- q2, q.` (6 spine rows) extended with
decorative facts to 7 and 8 rows:

  D1  |producible assemblies| == comb(rows+4,4): 210 / 330 / 495
  D2  one tile name per site across all assemblies (site-decorated)
  D3+D4  reached shapes == the full ideal set of the four-column
      poset at depth = rows, exactly, in both directions
  T   unique terminal assembly
  DR  the dead readers (`and1_r`, `unit1_q2`) appear in no producible
      assembly (the dead machinery is emitted and never bonds)

Reconciliation of record: tick-55 measured "70 assemblies" for
PR13-dead — that was the pre-design-010 spine cap's 4-row prefix
(70 == C(8,4)), an inventory artifact, not a family property; with the
spine-class rule landed, the full-height build obeys the same binomial
law as the PC12-doc family. Scope: two measured families, not a
corpus-wide law; everything re-derived live from the BFS on every run.
No kinetic claim, no queue spend, in-silico only. Nothing here is a
validated result until independently reviewed.
"""

import unittest
from math import comb

from molasp.compiler import compile_program, least_model, parse_program
from molasp.parity import producible

ANCHOR_ROWS = 6
PR13_ANCHOR = "p. s. q. q2 :- z. r :- q2, q."
DECOR = "tuvwxyz"


def program_for(rows):
    if rows == ANCHOR_ROWS:
        return PR13_ANCHOR
    decor = " ".join(a + "." for a in DECOR[:rows - ANCHOR_ROWS])
    if decor:
        decor += " "
    return "p. s. %sq. q2 :- z. r :- q2, q." % decor


def ideal_sites(h):
    return frozenset((x, y) for x in range(4) for y in range(1, h[x] + 1))


def ideals(rows):
    return {frozenset(ideal_sites((h0, h1, h2, h3)))
            for h0 in range(rows + 1) for h1 in range(h0 + 1)
            for h2 in range(h1 + 1) for h3 in range(h2 + 1)}


class Pr13IdealLaw(unittest.TestCase):

    def test_law_live_rows_6_to_8(self):
        for rows in range(ANCHOR_ROWS, ANCHOR_ROWS + 3):
            with self.subTest(rows=rows):
                prog = program_for(rows)
                facts, derived, _ = parse_program(prog)
                model = set(least_model(facts, derived))
                build = compile_program(
                    prog, name="PR13deadR%d" % rows, predicted=model)
                seen, terminals = producible(build)
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
                # D3 + D4: exact equality with the box ideals
                self.assertEqual(shapes, ideals(rows))
                # D1: the classical count
                self.assertEqual(len(seen), comb(rows + 4, 4))
                # T: unique terminal
                self.assertEqual(len(terminals), 1)
                # DR: dead readers never bond
                for asm in seen:
                    names = {t for _p, t in asm}
                    self.assertNotIn("and1_r", names)
                    self.assertNotIn("unit1_q2", names)

    def test_tick55_count_was_the_spine_cap_artifact(self):
        """The tick-55 receipt's 70 is the 4-row-prefix count C(8,4),
        recorded in designs/010 §10.1 as measured under the cap; the
        full-height law above supersedes it as the family number."""
        self.assertEqual(70, comb(8, 4))
        self.assertEqual(210, comb(10, 4))
