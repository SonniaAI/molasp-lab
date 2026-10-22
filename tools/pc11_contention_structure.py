#!/usr/bin/env python3
"""Height extension of the PC11 name-contention law: n = 9, 10 (2026-10-22, tick 153).

Tick 152 measured the first height-resolved name-contention law on the
one corpus family with contention above the poset level (PC11,
decorative extension): assemblies(n) = C(n+4,4) + C(n+2,2), with the
contended presence sets exactly the ideals containing site (1, n),
multiplicity exactly 2, at n = 5..8. A closed form is only worth its
predictions, so this module extends the same census to two NEW heights
the law had never seen — n = 9 and n = 10 — and verifies every
structural claim element-wise at EVERY height 5..10, live, from
molasp.parity.producible on every run:

  P1  presence sets == the full four-column ideal set, and
      |presence| == C(rows+4,4)  (box law, presence level)
  A1  |assemblies| == C(rows+4,4) + C(rows+2,2)  (two-term law)
  C1  contended presence sets == exactly the ideals containing (1, n)
      (h0 = h1 = n), count C(n+2,2)
  C2  multiplicity exactly 2 on contended sets, exactly 1 elsewhere;
      the two readings of each contended set differ only at sites
      (1, n) / (2, n)
  D1  placement independence at the new top height: the two valid
      decorative insertions (after `q.` and after `p.`) produce the
      SAME assembly set at n = 10
  F1  fourth finite difference of the assembly counts == 1 at every
      interior offset (degree-4 consistency of the two-term law:
      C(n+4,4) contributes 1, C(n+2,2) contributes 0)

Stdlib-only, deterministic, zero queue spend, no RNG. The receipt is a
pure function of the census. Nothing here is a validated result until
independently reviewed.
"""

import argparse
import json
import os
import sys
from math import comb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from molasp.compiler import compile_program, least_model, parse_program
from molasp.parity import producible

ANCHOR_ROWS = 5
PC11_ANCHOR = "p. q. s. q2 :- p. r :- q2, s. r :- q2."
DECOR = "tuvwxyz"
ROWS = (5, 6, 7, 8, 9, 10)


def program_for(rows, placement="after_q"):
    """Decorative extension of the PC11 anchor.

    placement "after_q" inserts the decorative facts between `q.` and
    `s.` (used for the census); "after_p" inserts them after the first
    fact (the second geometrically valid placement, used only for the
    D1 agreement check). Both were probed valid at n = 6 in tick 152.
    """
    if rows == ANCHOR_ROWS:
        return PC11_ANCHOR
    decor = " ".join(a + "." for a in DECOR[:rows - ANCHOR_ROWS])
    if not decor:
        return PC11_ANCHOR
    decor += " "
    if placement == "after_q":
        return "p. q. %ss. q2 :- p. r :- q2, s. r :- q2." % decor
    if placement == "after_p":
        return "p. %sq. s. q2 :- p. r :- q2, s. r :- q2." % decor
    raise ValueError(placement)


def ideal_sites(h):
    return frozenset((x, y) for x in range(4) for y in range(1, h[x] + 1))


def all_ideals(rows):
    return {frozenset(ideal_sites((h0, h1, h2, h3)))
            for h0 in range(rows + 1)
            for h1 in range(h0 + 1)
            for h2 in range(h1 + 1)
            for h3 in range(h2 + 1)}


def ideals_containing(site, rows):
    return {s for s in all_ideals(rows) if site in s}


def assembly_sets(prog, name):
    """Census of name-level assemblies, each as a frozenset of
    (column, row, tile) presence triples (row >= 1)."""
    facts, derived, _ = parse_program(prog)
    model = set(least_model(facts, derived))
    build = compile_program(prog, name=name, predicted=model)
    seen, terminals = producible(build)
    assemblies = {frozenset((x, y, t) for (x, y), t in asm if y >= 1)
                  for asm in seen}
    return assemblies, len(terminals)


def census_height(rows):
    """Full element-wise structural census at one height."""
    prog = program_for(rows)
    assemblies, terminals = assembly_sets(prog, "PC11docN%d" % rows)
    by_shape = {}
    for asm in assemblies:
        shape = frozenset((x, y) for x, y, _t in asm)
        by_shape.setdefault(shape, set()).add(asm)
    contended = {s: v for s, v in by_shape.items() if len(v) > 1}
    corner = ideals_containing((1, rows), rows)
    diff_restricted = True
    for v in contended.values():
        a1, a2 = sorted(v)
        d = {(x, y) for x, y, _t in (a1 ^ a2)}
        if not d <= {(1, rows), (2, rows)}:
            diff_restricted = False
    mult1 = sum(1 for s, v in by_shape.items() if len(v) == 1)
    mult2 = sum(1 for s, v in by_shape.items() if len(v) == 2)
    return {
        "program": prog,
        "presence": len(by_shape),
        "box_law": comb(rows + 4, 4),
        "presence_equals_ideals": set(by_shape) == all_ideals(rows),
        "assemblies": len(assemblies),
        "two_term_law": comb(rows + 4, 4) + comb(rows + 2, 2),
        "contended": len(contended),
        "corner_law": comb(rows + 2, 2),
        "contended_equals_corner_ideals": set(contended) == corner,
        "multiplicity_1_sets": mult1,
        "multiplicity_2_sets": mult2,
        "no_other_multiplicity": all(len(v) in (1, 2) for v in by_shape.values()),
        "readings_differ_only_at_corner_pair": diff_restricted,
        "terminals": terminals,
    }


def placement_agreement(rows):
    a, _ = assembly_sets(program_for(rows, "after_q"), "PC11docN%dA" % rows)
    b, _ = assembly_sets(program_for(rows, "after_p"), "PC11docN%dB" % rows)
    return a == b


def finite_differences(seq, order):
    cur = list(seq)
    for _ in range(order):
        cur = [cur[i + 1] - cur[i] for i in range(len(cur) - 1)]
    return cur


def build_receipt():
    heights = {}
    for rows in ROWS:
        row = census_height(rows)
        row.pop("program")  # anchor + placement recorded at receipt level
        heights[str(rows)] = row
    agreement_rows = max(ROWS)
    receipt = {
        "family": "PC11-decorative",
        "anchor": PC11_ANCHOR,
        "decorative_placement": "after_q (between q. and s.); D1 checks after_p",
        "rows_measured": list(ROWS),
        "new_heights_this_tick": [9, 10],
        "heights": heights,
        "placement_agreement_top": {
            "rows": agreement_rows,
            "agree": placement_agreement(agreement_rows),
        },
        "fourth_difference_assemblies": finite_differences(
            [heights[str(r)]["assemblies"] for r in ROWS], 4),
    }
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=None, help="write the receipt JSON here")
    args = ap.parse_args()
    receipt = build_receipt()
    for rows in ROWS:
        h = receipt["heights"][str(rows)]
        print("n=%d presence=%d/%d assemblies=%d/%d contended=%d/%d "
              "structure_ok=%s" % (
                  rows, h["presence"], h["box_law"], h["assemblies"],
                  h["two_term_law"], h["contended"], h["corner_law"],
                  h["presence_equals_ideals"]
                  and h["contended_equals_corner_ideals"]
                  and h["no_other_multiplicity"]
                  and h["readings_differ_only_at_corner_pair"]))
    print("placement_agreement@n=%d: %s" % (
        receipt["placement_agreement_top"]["rows"],
        receipt["placement_agreement_top"]["agree"]))
    print("fourth_difference_assemblies: %s" % receipt["fourth_difference_assemblies"])
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(receipt, fh, sort_keys=True, indent=1)
            fh.write("\n")
        print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
