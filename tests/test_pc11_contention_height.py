"""Tick-152 pins: the first height-resolved name-contention law (SON-5152).

For the PC11 decorative family (anchor `p. q. s. q2 :- p. r :- q2, s.
r :- q2.`, extended to n = 6..8 spine rows with decorative facts
inserted among the leading facts), live BFS re-derivation on every run:

  P1  presence sets == the full ideal set of the four-column poset at
      depth = rows, both directions, and |presence| == C(rows+4,4) —
      the box law now measured at new heights on a THIRD family
  A1  |assemblies| == C(rows+4,4) + C(rows+2,2) exactly, n = 5..8
  C1  contended presence sets == exactly those containing site (1, n)
      (equivalently: order ideals with column heights h0 = h1 = n;
      their count is the partitions h2 >= h3 in [0, n], i.e. C(n+2,2))
  C2  every contended presence set has multiplicity exactly 2, and the
      two name-level readings differ only at sites (1, n) / (2, n) —
      the or-support row's top conduit choice
  T1  exactly 2 terminal assemblies at every measured height
      (descriptive, carried from the n=5 anchor)

Anchor reconciliation: n = 5 reproduces the tick-66 corpus constants
for PC11 — 147 assemblies over 126 presence sets, 21 contended.
Decoration validity was probed at n = 6: the two geometrically valid
placements (after `q.` and after `p.`) agree exactly; insertion between
`s.` and the `q2 :- p.` rule and appending after the last rule are both
rejected by the compiler's geometry guard. Zero queue spend, in-silico
BFS only; nothing here is a validated result until independently
reviewed.
"""

import unittest
from math import comb

from molasp.compiler import compile_program, least_model, parse_program
from molasp.parity import producible

ANCHOR_ROWS = 5
PC11_ANCHOR = "p. q. s. q2 :- p. r :- q2, s. r :- q2."
DECOR = "tuvwxyz"

# tick-66 corpus constants for the n=5 anchor (probe2.out, 2026-10-08)
ANCHOR_ASSEMBLIES = 147
ANCHOR_PRESENCE = 126
ANCHOR_CONTENDED = 21


def program_for(rows):
    if rows == ANCHOR_ROWS:
        return PC11_ANCHOR
    decor = " ".join(a + "." for a in DECOR[:rows - ANCHOR_ROWS])
    if decor:
        decor += " "
    return "p. q. %ss. q2 :- p. r :- q2, s. r :- q2." % decor


def ideal_sites(h):
    return frozenset((x, y) for x in range(4) for y in range(1, h[x] + 1))


def ideals(rows):
    return {frozenset(ideal_sites((h0, h1, h2, h3)))
            for h0 in range(rows + 1) for h1 in range(h0 + 1)
            for h2 in range(h1 + 1) for h3 in range(h2 + 1)}


def census(rows):
    prog = program_for(rows)
    facts, derived, _ = parse_program(prog)
    model = set(least_model(facts, derived))
    build = compile_program(prog, name="PC11docN%d" % rows, predicted=model)
    seen, terminals = producible(build)
    name_map = {}
    for asm in seen:
        sites = frozenset((x, y) for (x, y), _t in asm if y >= 1)
        name_map.setdefault(sites, set()).add(asm)
    return seen, terminals, name_map


class Pc11ContentionHeight(unittest.TestCase):

    def test_presence_level_box_law_and_assembly_closed_form(self):
        for rows in range(5, 9):
            with self.subTest(rows=rows):
                seen, terminals, name_map = census(rows)
                # P1: presence == ideals, both directions; count == C(rows+4,4)
                self.assertEqual(set(name_map), ideals(rows))
                self.assertEqual(len(name_map), comb(rows + 4, 4))
                # A1: assemblies == C(rows+4,4) + C(rows+2,2)
                self.assertEqual(len(seen),
                                 comb(rows + 4, 4) + comb(rows + 2, 2))
                # T1: descriptive terminal count, carried from the anchor
                self.assertEqual(len(terminals), 2)

    def test_contention_is_exactly_top_row_site_one(self):
        for rows in range(5, 9):
            with self.subTest(rows=rows):
                seen, _terminals, name_map = census(rows)
                contended = {s for s, v in name_map.items() if len(v) > 1}
                contains_1n = {s for s in name_map if (1, rows) in s}
                # C1: contended == presence sets containing (1, rows);
                # count == C(rows+2,2) (ideals with h0 = h1 = rows)
                self.assertEqual(contended, contains_1n)
                self.assertEqual(len(contended), comb(rows + 2, 2))
                # C2: multiplicity exactly 2; readings differ only at
                # (1, rows) / (2, rows)
                for sites, readings in name_map.items():
                    if sites in contended:
                        self.assertEqual(len(readings), 2)
                        pair = list(readings)
                        diff = ({p for p in pair[0] if p not in pair[1]} |
                                {p for p in pair[1] if p not in pair[0]})
                        self.assertTrue(all(
                            site in {(1, rows), (2, rows)}
                            for site, _tile in diff), diff)
                    else:
                        self.assertEqual(len(readings), 1)

    def test_anchor_reproduces_tick66_constants(self):
        seen, _terminals, name_map = census(ANCHOR_ROWS)
        self.assertEqual(len(seen), ANCHOR_ASSEMBLIES)
        self.assertEqual(len(name_map), ANCHOR_PRESENCE)
        contended = sum(1 for v in name_map.values() if len(v) > 1)
        self.assertEqual(contended, ANCHOR_CONTENDED)


if __name__ == "__main__":
    unittest.main()
