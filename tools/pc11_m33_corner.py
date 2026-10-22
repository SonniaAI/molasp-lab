#!/usr/bin/env python3
"""Tick 161: the LAST corner — k_r=3 x k_w=3 (2026-10-22,
designs/012 northward truth-OR relay).

Ticks 158-160 confirmed the inclusion-exclusion total law at three
of the four {k_r, k_w} corners.  This tick closes the square,
predicting BEFORE censusing:

  PC11-M33   p. q. s. q2 :- p. r :- q2. r :- q2. r :- q2.
             w :- r. w :- r. w :- r.

r is the RELAYED or-head at row n-1 with THREE duplicate unit
bodies (k_r = 3), w the terminal or-head at row n with THREE
(k_w = 3).  Family-local decor alphabet tuvxyz.

The total law predicts, with the SAME geometric corner sets
C_w = ideals containing (1, n)  [= C(n+2,2) <= C_r] and
C_r = ideals containing (1, n-1)  [= (n+1)(3n+2)/2]:

  assemblies(n) = |I| + (k_r-1)|C_r| + (k_w-1)|C_w|
                      + (k_r-1)(k_w-1)|C_r ^ C_w|
               = |I| + 2|C_r| + 6|C_w|
               = C(n+4,4) + (n+1)(3n+2) + 6*C(n+2,2)

predicting 518/730/999/1335/1749/2253/2860 at heights 6..12, with
fibers {1: rest, 3: C_r\\C_w, 9: C_w} — BOTH head signatures
present (fiber 3 returns, M23's mirror fiber 2 vanishes) and the
overlap fiber now k_r*k_w = 9, never 2^anything.

Falsified alternatives, computed and checked element-wise:
  collapsed  |I| + 2|C_r|                  (one shared bit per
                                   head: fiber 3 everywhere on C_r,
                                   fiber 9 never)
  additive   |I| + 2|C_r| + 2|C_w| (fiber k_r+k_w-1 = 5 on C_w)
  power      |I| + 2|C_r| + 15|C_w| (fiber 2^(k_r+k_w-2) = 16)

Checks, live at every height 6..12:

  P1  presence == the full four-column ideal set, |I| = C(n+4,4)
  M1  |assemblies| == |I| + 2|C_r| + 6|C_w| at every height;
      collapsed, additive and power totals falsified element-wise
  F1  fiber histogram exactly {1: rest, 3: |C_r|-|C_w|, 9: |C_w|};
      fibers 2, 4, 6 and 8 NEVER occur anywhere
  X1  mixed product structure ELEMENT-WISE: every 9-fiber realizes
      all nine combinations tile@(1,n-1) in {Cr, Cr2, Cr3} x
      tile@(1,n) in {Cw, Cw2, Cw3} — the two heads choose
      independently
  X2  readings differ only at the two site pairs (1,n-1)/(2,n-1),
      (1,n)/(2,n)
  R1  the relay stays value-typed: all three of r's conduits
      expose N = {r}-t-done (never a body glue north)
  B1  body-identity handshake intact at BOTH rows with SIX body
      glues: unit1_r/unit2_r/unit3_r and unit1_w/unit2_w/unit3_w
      each occur exactly twice in the whole inventory
  S1  the completed square: the unified law
      assemblies(n) = C(n+4,4) + (k_r-1)(n+1)(3n+2)/2
                      + k_r*(k_w-1)*C(n+2,2)
      holds at ALL FOUR corners (2,2)/(3,2)/(2,3)/(3,3), 28/28
      scalars, from the four ticks' receipts.

Stdlib-only, deterministic, zero queue spend, no RNG. The receipt is
a pure function of the censuses and the three prior (byte-stable)
receipts. Nothing here is a validated result until independently
reviewed.
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

ANCHOR = ("p. q. s. q2 :- p. r :- q2. r :- q2. r :- q2. "
          "w :- r. w :- r. w :- r.")
ROWS = tuple(range(6, 13))          # anchor 6, decor to 12
# Family-local decor alphabet (skips w, this family's terminal head
# atom — the collision lesson of tick 158).
DECOR_M33 = "tuvxyz"

K_R = 3
K_W = 3

# The square: (k_r, k_w) -> receipt of record (ticks 158/159/160/161)
SQUARE_RECEIPTS = {
    (2, 2): os.path.join("evidence", "2026-10-22-pc11-two-or",
                         "two_or.json"),
    (3, 2): os.path.join("evidence", "2026-10-22-pc11-mixed-heads",
                         "mixed_heads.json"),
    (2, 3): os.path.join("evidence", "2026-10-22-pc11-mixed-mirror",
                         "mixed_mirror.json"),
    (3, 3): None,                   # this tick, measured live
}


def program_for(rows):
    if rows == 6:
        return ANCHOR
    decor = " ".join(a + "." for a in DECOR_M33[:rows - 6])
    if not decor:
        return ANCHOR
    head, tail = ANCHOR.split("q. ", 1)
    return head + "q. " + decor + " " + tail


def corner_counts(rows):
    ideals = all_ideals(rows)
    c_w = ideals_containing((1, rows), rows)
    c_r = ideals_containing((1, rows - 1), rows)
    return ideals, c_r, c_w


def unified_law(rows, k_r, k_w):
    """assemblies(n) from the inclusion-exclusion form with
    C_w <= C_r, i.e. C(n+4,4) + (k_r-1)|C_r| + k_r*(k_w-1)|C_w|."""
    return (comb(rows + 4, 4)
            + (k_r - 1) * (rows + 1) * (3 * rows + 2) // 2
            + k_r * (k_w - 1) * comb(rows + 2, 2))


def relay_static(rows):
    """R1/B1 straight from the emitted inventory (three conduits)."""
    prog = program_for(rows)
    build = compile_program(prog, name="PC11_M33_stat%d" % rows)
    tiles = build["tiles"]
    n = rows
    r_conduits = sorted(t for t in tiles
                        if t.startswith("Cr")
                        and build["row_of"].get(t) == n - 1)
    w_conduits = sorted(t for t in tiles
                        if t.startswith("Cw")
                        and build["row_of"].get(t) == n)
    north_faces = {t: tiles[t].get("N", "") for t in r_conduits}
    reads_r = {t: tiles[t].get("S", "")
               for t in tiles if build["row_of"].get(t) == n
               and tiles[t].get("S")}
    body_glues = ["unit%d_r" % i for i in range(1, K_R + 1)] + \
                 ["unit%d_w" % i for i in range(1, K_W + 1)]
    counts = Counter(g for faces in tiles.values()
                     for g in faces.values() if g)
    return {
        "rows": rows,
        "r_conduits": r_conduits,
        "r_conduit_count_is_k": len(r_conduits) == K_R,
        "w_conduits": w_conduits,
        "w_conduit_count_is_k": len(w_conduits) == K_W,
        "relay_conduit_north_faces": north_faces,
        "relay_value_typed_north":
            bool(north_faces)
            and set(north_faces.values()) == {"r-t-done"},
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
    build = compile_program(prog, name="PC11_M33_N%d" % rows)
    tiles = build["tiles"]
    assemblies, _terminals = assembly_sets(prog, "PC11_M33_N%d" % rows)
    by_shape = {}
    for asm in assemblies:
        shape = frozenset((x, y) for x, y, _t in asm)
        by_shape.setdefault(shape, set()).add(asm)
    ideals, c_r, c_w = corner_counts(rows)
    contended = {s: v for s, v in by_shape.items() if len(v) > 1}
    mult = Counter(len(v) for v in by_shape.values())
    fib3 = {s for s, v in by_shape.items() if len(v) == 3}
    fib9 = {s for s, v in by_shape.items() if len(v) == 9}
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
    # X1: element-wise mixed product structure on every 9-fiber —
    # k_r distinct conduit choices at (1,n-1) x k_w at (1,n), all
    # nine combinations realized.
    product_structure = True
    r_choices, w_choices = set(), set()
    for shape, fiber in contended.items():
        if len(fiber) != K_R * K_W:
            continue
        combos = set()
        for asm in fiber:
            at = {(x, y): t for x, y, t in asm}
            combos.add((at.get((1, n - 1)), at.get((1, n))))
            r_choices.add(at.get((1, n - 1)))
            w_choices.add(at.get((1, n)))
        if len(combos) != K_R * K_W:
            product_structure = False
    tot_mix = (len(ideals) + (K_R - 1) * len(c_r)
               + (K_W - 1) * len(c_w)
               + (K_R - 1) * (K_W - 1) * len(c_w))
    tot_collapse = len(ideals) + (K_R - 1) * len(c_r)
    tot_add = len(ideals) + (K_R - 1) * len(c_r) + (K_W - 1) * len(c_w)
    tot_pow = (len(ideals) + (K_R - 1) * len(c_r)
               + (2 ** (K_R + K_W - 2) - 1) * len(c_w))
    return {
        "rows": rows,
        "program": prog,
        "k_r": K_R,
        "k_w": K_W,
        "presence": len(by_shape),
        "presence_equals_ideals": set(by_shape) == ideals,
        "box_law": comb(rows + 4, 4),
        "assemblies": len(assemblies),
        "mixed_law": tot_mix,
        "collapsed_law": tot_collapse,
        "additive_law": tot_add,
        "power_law": tot_pow,
        "mixed_law_holds": len(assemblies) == tot_mix,
        "collapsed_falsified": len(assemblies) != tot_collapse,
        "additive_falsified": len(assemblies) != tot_add,
        "power_falsified": len(assemblies) != tot_pow,
        "c_r": len(c_r),
        "c_r_formula": (rows + 1) * (3 * rows + 2) // 2,
        "c_w": len(c_w),
        "c_w_formula": comb(rows + 2, 2),
        "fiber_hist": dict(sorted(mult.items())),
        "fiber2_never": 2 not in mult,
        "fiber4_never": 4 not in mult,
        "fiber6_never": 6 not in mult,
        "fiber8_never": 8 not in mult,
        "fiber3_shapes_are_Cr_minus_Cw": fib3 == (c_r - c_w),
        "fiber9_shapes_are_Cw": fib9 == c_w,
        "elementwise_product_structure": product_structure,
        "conduit_choices_at_free_sites": {
            "row_n_minus_1": sorted(r_choices),
            "row_n": sorted(w_choices),
        },
        "readings_differ_only_at_site_pairs": diff_restricted,
    }


def corner_square(m33_censuses):
    """S1: the unified law over all four corners, from the four
    ticks' receipts of record (the first three byte-stable in
    evidence/, M33 measured live this tick)."""
    table = {}
    for (k_r, k_w), rel in SQUARE_RECEIPTS.items():
        heights = {}
        if rel is None:
            for r in ROWS:
                if str(r) in m33_censuses:
                    heights[str(r)] = m33_censuses[str(r)]["assemblies"]
        else:
            with open(os.path.join(ROOT, rel)) as fh:
                prior = json.load(fh)
            for r in prior["rows_measured"]:
                heights[str(r)] = prior["censuses"][str(r)]["assemblies"]
        table["%dx%d" % (k_r, k_w)] = {
            "k_r": k_r, "k_w": k_w,
            "assemblies_by_height": heights,
            "unified_law_holds_everywhere": all(
                heights[str(r)] == unified_law(r, k_r, k_w)
                for r in ROWS if str(r) in heights),
        }
    return {
        "corners": table,
        "all_four_corners_hold": all(
            v["unified_law_holds_everywhere"] for v in table.values()),
        "scalars_checked": sum(
            len(v["assemblies_by_height"]) for v in table.values()),
    }


def build_receipt():
    censuses = {str(r): census(r) for r in ROWS}
    static = {str(r): relay_static(r) for r in ROWS}
    square = corner_square(censuses)
    summary = {
        "mixed_total_law_all_heights": all(
            c["mixed_law_holds"] and c["collapsed_falsified"]
            and c["additive_falsified"] and c["power_falsified"]
            for c in censuses.values()),
        "presence_box_law_all_heights": all(
            c["presence_equals_ideals"]
            and c["presence"] == c["box_law"]
            for c in censuses.values()),
        "fiber_structure_all_heights": all(
            c["fiber2_never"] and c["fiber4_never"]
            and c["fiber6_never"] and c["fiber8_never"]
            and c["fiber3_shapes_are_Cr_minus_Cw"]
            and c["fiber9_shapes_are_Cw"]
            and c["elementwise_product_structure"]
            and c["readings_differ_only_at_site_pairs"]
            for c in censuses.values()),
        "relay_static_all_heights": all(
            s["r_conduit_count_is_k"] and s["w_conduit_count_is_k"]
            and s["relay_value_typed_north"]
            and s["above_reads_only_value"]
            and s["body_glues_each_exactly_twice"]
            for s in static.values()),
        "corner_formulas_all_heights": all(
            c["c_r"] == c["c_r_formula"]
            and c["c_w"] == c["c_w_formula"]
            for c in censuses.values()),
        "four_corner_square_complete": square["all_four_corners_hold"],
    }
    return {
        "family": "PC11-M33 last corner of the {k_r,k_w} square "
                  "(relayed k_r=3 duplicate-unit OR x terminal k_w=3 "
                  "duplicate-unit OR)",
        "design": "designs/012 northward truth-OR relay",
        "result": "square complete: assemblies(n) = |I| + "
                  "(k_r-1)|C_r| + (k_w-1)|C_w| + (k_r-1)(k_w-1)"
                  "|C_r^C_w| = C(n+4,4) + (n+1)(3n+2) + 6*C(n+2,2); "
                  "fibers {1: rest, 3: C_r\\C_w, 9: C_w}, fibers "
                  "2/4/6/8 never; element-wise 3x3 product structure "
                  "on every 9-fiber; the unified law "
                  "C(n+4,4) + (k_r-1)(n+1)(3n+2)/2 + "
                  "k_r*(k_w-1)*C(n+2,2) holds at ALL FOUR corners",
        "rows_measured": list(ROWS),
        "summary": summary,
        "corner_square": square,
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
        print("n=%-2d presence=%d/%d assemblies=%d mix=%d col=%d "
              "add=%d pow=%d hist=%s prod=%s" % (
                  r, c["presence"], c["box_law"], c["assemblies"],
                  c["mixed_law"], c["collapsed_law"], c["additive_law"],
                  c["power_law"], c["fiber_hist"],
                  c["elementwise_product_structure"]))
    sq = receipt["corner_square"]
    print("square:", {k: v["unified_law_holds_everywhere"]
                      for k, v in sq["corners"].items()},
          "scalars=%d" % sq["scalars_checked"])
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
