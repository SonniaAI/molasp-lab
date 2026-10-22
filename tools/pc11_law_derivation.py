#!/usr/bin/env python3
"""Why the PC11 contention law holds: a gap-bijection derivation (2026-10-22, tick 154).

Ticks 152-153 measured, at n = 5..10, that the PC11 decorative
family's name-level assemblies follow

    assemblies(n) = C(n+4,4) + C(n+2,2)

with contended presence sets exactly the ideals containing site
(1, n), multiplicity exactly 2 there and 1 elsewhere. This module
DERIVES that law instead of curve-fitting it, from three lemmas:

  L1 (box law, pure counting). Ideals of the four-column region are
      exactly the column-height sets with weakly decreasing heights
      (h0, h1, h2, h3) bounded by n. The gap map
      (h0,h1,h2,h3) -> (h0-h1, h1-h2, h2-h3, h3, n-h0)
      is a bijection onto the compositions of n into 5 nonnegative
      parts, so |ideals(n)| = C(n+4,4).

  L2 (corner law, pure counting). An ideal contains site (1, n)
      iff h1 = n, iff (h0, h1) = (n, n); the free tail (h2, h3)
      runs over weakly decreasing pairs in [0, n], and the gap map
      (h2, h3) -> (h2-h3, h3, n-h2) is a bijection onto the
      compositions of n into 3 parts, so
      |corner ideals(n)| = C(n+2,2).

  L3 (multiplicity partition, machine-verified at every measured
      height, live re-derivation from molasp.parity.producible).
      Every ideal carries exactly one name-level assembly except the
      corner ideals, which carry exactly two, whose readings differ
      only at the or-support conduit pair (1, n) / (2, n).

  Theorem. assemblies(n) = |ideals(n)| + |corner ideals(n)|
                        = C(n+4,4) + C(n+2,2).

The law's empirical content is thereby reduced to L3 alone: L1 and L2
are bijection-counting with no compiler in the loop. To keep the
prediction discipline, this tick also writes down the law's numbers
for one further height the census had never visited (n = 11:
1365 / 78 / 1443) and confirms them live, extending the measured
range to seven consecutive heights, and stress-checks the gap
bijection itself at n = 20 (10626 ideals), far past the census range
of the anchor family.

Stdlib-only, deterministic, zero queue spend, no RNG. The receipt is
a pure function of the census and the bijections. Nothing here is a
validated result until independently reviewed.
"""

import argparse
import json
import os
import sys
from math import comb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.pc11_contention_structure import (
    all_ideals,
    census_height,
    ideals_containing,
)

ROWS = (5, 6, 7, 8, 9, 10)
NEW_HEIGHT = 11            # predicted from the closed form, then censused
BIJECTION_STRESS = 20      # gap bijection only, no compiler
CORNER_SITE = (1, 11)      # site (1, n) of the census heights


def compositions(total, parts):
    """All tuples of `parts` nonnegative integers summing to `total`,
    in lexicographic order of the reversed gap vector (deterministic)."""
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def gaps_to_heights(g):
    """Inverse gap map for L1: composition of n into 5 parts ->
    weakly decreasing column heights (h0, h1, h2, h3) bounded by n.

    g = (h0-h1, h1-h2, h2-h3, h3, n-h0): each h is recovered as a
    suffix sum of the first four gaps, and n as the total.
    """
    g0, g1, g2, g3, _gn = g
    h3 = g3
    h2 = h3 + g2
    h1 = h2 + g1
    h0 = h1 + g0
    return (h0, h1, h2, h3)


def heights_to_gaps(h, rows):
    """Gap map for L1: heights -> composition of `rows` into 5 parts."""
    h0, h1, h2, h3 = h
    return (h0 - h1, h1 - h2, h2 - h3, h3, rows - h0)


def corner_gaps_to_heights(g):
    """Inverse gap map for L2: composition of n into 3 parts ->
    corner-heights (n, n, h2, h3) with (h2, h3) weakly decreasing.

    g = (h2-h3, h3, n-h2).
    """
    g2, g3, _gn = g
    h3 = g3
    h2 = h3 + g2
    return (h2, h3)


def heights_of_ideal(ideal):
    """Column heights of an enumerated ideal (well-definedness check)."""
    hs = {}
    for x, y in ideal:
        hs[x] = max(hs.get(x, 0), y)
    return tuple(hs.get(x, 0) for x in range(4))


def derive_height(rows):
    """L1 + L2 at one height: bijections, counts, set equalities."""
    ideals = all_ideals(rows)
    from_gaps = {frozenset(
        (x, y) for x in range(4) for y in range(1, h[x] + 1))
        for h in (gaps_to_heights(g) for g in compositions(rows, 5))}
    encodings = sorted(heights_to_gaps(heights_of_ideal(i), rows)
                       for i in ideals)
    gap_pool = sorted(compositions(rows, 5))
    corner = ideals_containing((1, rows), rows)
    corner_from_gaps = {frozenset(
        (x, y) for x in range(4) for y in range(1, h[x] + 1))
        for h in ((rows, rows) + corner_gaps_to_heights(g)
                  for g in compositions(rows, 3))}
    return {
        "rows": rows,
        "ideals": len(ideals),
        "ideals_from_gaps": len(from_gaps),
        "gap_bijection_exact": from_gaps == ideals,
        "encoding_bijection_exact": encodings == gap_pool,
        "box_law": comb(rows + 4, 4),
        "composition_count_5": len(gap_pool),
        "corner_ideals": len(corner),
        "corner_from_gaps": len(corner_from_gaps),
        "corner_gap_bijection_exact": corner_from_gaps == corner,
        "corner_law": comb(rows + 2, 2),
        "composition_count_3": len(list(compositions(rows, 3))),
    }


def census_partition(rows):
    """L3 + theorem check at one height, from the live census."""
    c = census_height(rows)
    return {
        "presence": c["presence"],
        "assemblies": c["assemblies"],
        "contended": c["contended"],
        "multiplicity_1_sets": c["multiplicity_1_sets"],
        "multiplicity_2_sets": c["multiplicity_2_sets"],
        "partition_closes_sets": (c["multiplicity_1_sets"]
                                  + c["multiplicity_2_sets"]
                                  == c["presence"]),
        "partition_closes_weighted": (c["multiplicity_1_sets"]
                                      + 2 * c["multiplicity_2_sets"]
                                      == c["assemblies"]),
        "assemblies_equals_presence_plus_contended":
            c["assemblies"] == c["presence"] + c["contended"],
        "structure_ok": (c["presence_equals_ideals"]
                         and c["contended_equals_corner_ideals"]
                         and c["no_other_multiplicity"]
                         and c["readings_differ_only_at_corner_pair"]),
        "theorem_pred": comb(rows + 4, 4) + comb(rows + 2, 2),
    }


def build_receipt():
    derivation = {str(r): derive_height(r) for r in ROWS}
    census = {str(r): census_partition(r) for r in ROWS}
    new_pred = {
        "presence": comb(NEW_HEIGHT + 4, 4),
        "contended": comb(NEW_HEIGHT + 2, 2),
        "assemblies": (comb(NEW_HEIGHT + 4, 4)
                       + comb(NEW_HEIGHT + 2, 2)),
    }
    new_seen = census_height(NEW_HEIGHT)
    stress = derive_height(BIJECTION_STRESS)
    return {
        "family": "PC11-decorative",
        "lemmas": {
            "L1": "ideals <-> weakly-decreasing heights <-> "
                  "compositions of n into 5 parts -> C(n+4,4)",
            "L2": "corner ideals (containing (1,n)) <-> compositions "
                  "of n into 3 parts -> C(n+2,2)",
            "L3": "multiplicity 1 on non-corner ideals, exactly 2 on "
                  "corner ideals, readings differ only at (1,n)/(2,n) "
                  "(machine-verified, live, every measured height)",
        },
        "theorem": "assemblies(n) = C(n+4,4) + C(n+2,2)",
        "rows_measured": list(ROWS),
        "derivation": derivation,
        "census_partition": census,
        "new_height_this_tick": {
            "rows": NEW_HEIGHT,
            "predicted_first": new_pred,
            "seen": {
                "presence": new_seen["presence"],
                "contended": new_seen["contended"],
                "assemblies": new_seen["assemblies"],
            },
            "structure_ok": (new_seen["presence_equals_ideals"]
                             and new_seen["contended_equals_corner_ideals"]
                             and new_seen["no_other_multiplicity"]
                             and new_seen["readings_differ_only_at_corner_pair"]),
        },
        "bijection_stress": {
            "rows": BIJECTION_STRESS,
            "ideals": stress["ideals"],
            "box_law": stress["box_law"],
            "gap_bijection_exact": stress["gap_bijection_exact"],
            "corner_gap_bijection_exact": stress["corner_gap_bijection_exact"],
        },
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=None, help="write the receipt JSON here")
    args = ap.parse_args()
    receipt = build_receipt()
    for r in ROWS:
        d, c = receipt["derivation"][str(r)], receipt["census_partition"][str(r)]
        print("n=%d ideals=%d/%d gap_ok=%s corner=%d/%d corner_ok=%s "
              "partition=%s/%s theorem=%d/%d" % (
                  r, d["ideals"], d["box_law"], d["gap_bijection_exact"],
                  d["corner_ideals"], d["corner_law"],
                  d["corner_gap_bijection_exact"],
                  c["partition_closes_sets"],
                  c["partition_closes_weighted"],
                  c["assemblies"], c["theorem_pred"]))
    n = receipt["new_height_this_tick"]
    print("new height n=%d predicted=%s seen=%s structure_ok=%s" % (
        n["rows"], n["predicted_first"], n["seen"], n["structure_ok"]))
    s = receipt["bijection_stress"]
    print("bijection stress n=%d ideals=%d/%d exact=%s/%s" % (
        s["rows"], s["ideals"], s["box_law"], s["gap_bijection_exact"],
        s["corner_gap_bijection_exact"]))
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(receipt, fh, sort_keys=True, indent=1)
            fh.write("\n")
        print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
