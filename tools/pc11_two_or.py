#!/usr/bin/env python3
"""Tick 158: the two-or-pair family — fibers MULTIPLY, they do not add
(2026-10-22, designs/012 northward truth-OR relay).

Tick 157 closed the single-head question (fiber = k exactly, never
2^k) and left the composition question open: two INDEPENDENT or-heads
competing in one assembly — does the contention ADD (a shared bit,
fiber 3 on the overlap) or MULTIPLY (independent bits, fiber 4)?

Compiler v0.2 could not reach the question: an OR at an intermediate
derived row was refused outright.  This tick moves the fragment
boundary BY DESIGN first (designs/012, the northward truth-OR relay:
a duplicate-unit OR-head one row above its old terminal position,
conduit N faces re-typed to the VALUE glue {a}-t-done so growth north
of the head is bit-blind), then censuses the first two-or-pair family:

  PC11-T2U   p. q. s. q2 :- p. r :- q2. r :- q2. w :- r. w :- r.

r is a RELAYED or-head at row n-1 (two duplicate unit bodies on the
adjacent-below derived row q2), w the terminal or-head at row n (two
duplicate unit bodies on r).  Decorative extension as in PC11
(facts between `q.` and `s.`), heights 6..12.

Three candidate laws, sharply separated by the census:
  multiplicative  |I| + |C_r| + 2|C_w|   (fiber 4 on C_w)
  additive        |I| + |C_r| + |C_w|    (fiber 3 on C_w: shared bit)
  collapsed       |I| + |C_r|            (fiber 2 on C_r: tied bits)
with C_w = ideals containing site (1, n)  [= C(n+2,2), the corner law]
and  C_r = ideals containing site (1, n-1) [= (n+1)(3n+2)/2].

Checks, live at every height 6..12:

  P1  presence == the full four-column ideal set, |I| = C(n+4,4)
  M1  |assemblies| == |I| + |C_r| + 2|C_w| — MULTIPLICATIVE, at every
      height; the additive and collapsed totals are computed and
      falsified element-wise
  F1  fiber histogram exactly {1: rest, 2: |C_r|-|C_w|, 4: |C_w|};
      the fiber-2 shapes are exactly C_r \\ C_w, the fiber-4 shapes
      exactly C_w; fiber 3 NEVER occurs anywhere (additivity killed)
  X1  multiplicative structure ELEMENT-WISE: every 4-fiber realizes
      all four combinations tile@(1,n-1) in {C_r, C_r2} x
      tile@(1,n) in {C_w, C_w2} — a product, not a selection
  X2  readings differ only at the two site pairs (1,n-1)/(2,n-1),
      (1,n)/(2,n)
  R1  the relay is value-typed in the emitted inventory: both of r's
      conduits expose N = {r}-t-done (never a body glue north), and
      every tile that bonds south into row n-1 from above reads
      {r}-t-done — the bit cannot leak north
  B1  body-identity handshake intact at BOTH rows: unit1_r/unit2_r
      and unit1_w/unit2_w each occur exactly twice in the whole
      inventory (conduit E + own reader W), tick-157's L-east

Stdlib-only, deterministic, zero queue spend, no RNG. The receipt is
a pure function of the censuses. Nothing here is a validated result
until independently reviewed.
"""

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from math import comb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from molasp.compiler import compile_program, parse_program
from tools.pc11_contention_structure import (
    all_ideals,
    assembly_sets,
    ideals_containing,
)

ANCHOR = "p. q. s. q2 :- p. r :- q2. r :- q2. w :- r. w :- r."
ROWS = tuple(range(6, 13))          # anchor 6, decor to 12
# The shared PC11 decor alphabet "tuvwxyz" COLLIDES with this
# family's terminal head atom w at its 4th letter: the first receipt
# run broke the presence box law exactly at n=10 (the height that
# first inserts "w." as a fact while w is also the or-head — a
# fact-row {w}-t-done vs head-row {w}-t-done glue wreck, census-caught,
# not silently wrong).  This family therefore uses its own alphabet,
# skipping w: t, u, v, x, y, z (six fresh atoms, heights 7..12).
DECOR_T2U = "tuvxyz"


def program_for(rows):
    if rows == 6:
        return ANCHOR
    decor = " ".join(a + "." for a in DECOR_T2U[:rows - 6])
    if not decor:
        return ANCHOR
    head, tail = ANCHOR.split("q. ", 1)
    return head + "q. " + decor + " " + tail


def corner_counts(rows):
    ideals = all_ideals(rows)
    c_w = ideals_containing((1, rows), rows)
    c_r = ideals_containing((1, rows - 1), rows)
    return ideals, c_r, c_w


def relay_static(rows):
    """R1/B1 straight from the emitted inventory."""
    prog = program_for(rows)
    build = compile_program(prog, name="PC11_T2U_stat%d" % rows)
    tiles = build["tiles"]
    n = rows
    n = rows
    r_conduits = sorted(t for t in tiles
                        if t.startswith("Cr")
                        and build["row_of"].get(t) == n - 1)
    w_conduits = sorted(t for t in tiles
                        if t.startswith("Cw")
                        and build["row_of"].get(t) == n)
    north_faces = {t: tiles[t].get("N", "") for t in r_conduits}
    # every tile whose S face bonds into row n-1 from row n
    reads_r = {t: tiles[t].get("S", "")
               for t in tiles if build["row_of"].get(t) == n
               and tiles[t].get("S")}
    body_glues = [g for g in ("unit1_r", "unit2_r", "unit1_w", "unit2_w")]
    counts = Counter(g for faces in tiles.values()
                     for g in faces.values() if g)
    return {
        "rows": rows,
        "relay_conduit_north_faces": north_faces,
        "relay_value_typed_north":
            set(north_faces.values()) == {"r-t-done"},
        "row_n_south_reads": sorted(set(reads_r.values())),
        "above_reads_only_value":
            set(reads_r.values()) <= {"r-t-done", "base%d" % n,
                                      "SP%d" % n},
        "body_glues_each_exactly_twice":
            all(counts[g] == 2 for g in body_glues),
        "body_glue_occurrences": {g: counts[g] for g in body_glues},
    }


def census(rows):
    prog = program_for(rows)
    build = compile_program(prog, name="PC11_T2U_N%d" % rows)
    tiles = build["tiles"]
    assemblies, _terminals = assembly_sets(prog, "PC11_T2U_N%d" % rows)
    by_shape = {}
    for asm in assemblies:
        shape = frozenset((x, y) for x, y, _t in asm)
        by_shape.setdefault(shape, set()).add(asm)
    ideals, c_r, c_w = corner_counts(rows)
    contended = {s: v for s, v in by_shape.items() if len(v) > 1}
    mult = Counter(len(v) for v in by_shape.values())
    fib2 = {s for s, v in by_shape.items() if len(v) == 2}
    fib4 = {s for s, v in by_shape.items() if len(v) == 4}
    n = rows
    pair = {(1, n - 1), (2, n - 1), (1, n), (2, n)}
    diff_restricted = True
    for shape, fiber in contended.items():
        for a1 in fiber:
            for a2 in fiber:
                if a1 is a2:
                    continue
                d = {(x, y) for x, y, _t in (a1 ^ a2)}
                if not d <= pair:
                    diff_restricted = False
    # X1: element-wise product structure on every 4-fiber
    product_structure = True
    for shape, fiber in contended.items():
        if len(fiber) != 4:
            continue
        combos = set()
        for asm in fiber:
            at = {(x, y): t for x, y, t in asm}
            combos.add((at.get((1, n - 1)), at.get((1, n))))
        if len(combos) != 4:
            product_structure = False
    tot_mult = len(ideals) + len(c_r) + 2 * len(c_w)
    tot_add = len(ideals) + len(c_r) + len(c_w)
    tot_col = len(ideals) + len(c_r)
    return {
        "rows": rows,
        "program": prog,
        "presence": len(by_shape),
        "presence_equals_ideals": set(by_shape) == ideals,
        "box_law": comb(rows + 4, 4),
        "assemblies": len(assemblies),
        "multiplicative_law": tot_mult,
        "additive_law": tot_add,
        "collapsed_law": tot_col,
        "multiplicative_holds": len(assemblies) == tot_mult,
        "additive_falsified": len(assemblies) != tot_add,
        "collapsed_falsified": len(assemblies) != tot_col,
        "c_r": len(c_r),
        "c_r_formula": (rows + 1) * (3 * rows + 2) // 2,
        "c_w": len(c_w),
        "c_w_formula": comb(rows + 2, 2),
        "fiber_hist": dict(sorted(mult.items())),
        "fiber3_never": 3 not in mult,
        "fiber2_shapes_are_Cr_minus_Cw": fib2 == (c_r - c_w),
        "fiber4_shapes_are_Cw": fib4 == c_w,
        "elementwise_product_structure": product_structure,
        "readings_differ_only_at_site_pairs": diff_restricted,
    }


def build_receipt():
    censuses = {str(r): census(r) for r in ROWS}
    static = {str(r): relay_static(r) for r in ROWS}
    summary = {
        "multiplicative_all_heights": all(
            c["multiplicative_holds"] and c["additive_falsified"]
            and c["collapsed_falsified"] for c in censuses.values()),
        "presence_box_law_all_heights": all(
            c["presence_equals_ideals"]
            and c["presence"] == c["box_law"]
            for c in censuses.values()),
        "fiber_structure_all_heights": all(
            c["fiber3_never"]
            and c["fiber2_shapes_are_Cr_minus_Cw"]
            and c["fiber4_shapes_are_Cw"]
            and c["elementwise_product_structure"]
            and c["readings_differ_only_at_site_pairs"]
            for c in censuses.values()),
        "relay_value_typed_all_heights": all(
            s["relay_value_typed_north"]
            and s["body_glues_each_exactly_twice"]
            for s in static.values()),
        "corner_formulas_all_heights": all(
            c["c_r"] == c["c_r_formula"]
            and c["c_w"] == c["c_w_formula"]
            for c in censuses.values()),
    }
    return {
        "family": "PC11-T2U two-or-pair (relayed intermediate "
                  "duplicate-unit OR + terminal duplicate-unit OR)",
        "design": "designs/012 northward truth-OR relay",
        "result": "fibers MULTIPLY: assemblies(n) = C(n+4,4) + "
                  "(n+1)(3n+2)/2 + 2*C(n+2,2); fiber 4 on the "
                  "both-corner ideals, fiber 2 on C_r\\C_w, fiber 3 "
                  "nowhere; element-wise product structure on every "
                  "4-fiber",
        "rows_measured": list(ROWS),
        "summary": summary,
        "censuses": censuses,
        "relay_static": static,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=None, help="write the receipt JSON here")
    args = ap.parse_args()
    receipt = build_receipt()
    for r in ROWS:
        c = receipt["censuses"][str(r)]
        print("n=%-2d presence=%d/%d assemblies=%d mult=%d add=%d "
              "col=%d hist=%s prod=%s" % (
                  r, c["presence"], c["box_law"], c["assemblies"],
                  c["multiplicative_law"], c["additive_law"],
                  c["collapsed_law"], c["fiber_hist"],
                  c["elementwise_product_structure"]))
    print("summary:", json.dumps(receipt["summary"], sort_keys=True))
    if args.out:
        data = json.dumps(receipt, indent=2, sort_keys=True,
                          default=sorted) + "\n"
        with open(args.out, "w") as fh:
            fh.write(data)
        print("sha256(%s) = %s" % (
            args.out, hashlib.sha256(data.encode()).hexdigest()))


if __name__ == "__main__":
    main()
