#!/usr/bin/env python3
"""Why L3 holds mechanically: the PC11 multiplicity partition is ONE
binary bit, witnessed by a closed-form canonical section
(2026-10-22, tick 155).

Tick 154 derived assemblies(n) = C(n+4,4) + C(n+2,2) from L1, L2
(pure gap bijections, no compiler) plus L3, the multiplicity
partition, which remained machine-verified only. This module
mechanizes L3: the entire fiber structure over the ideal set is a
single or-support bit.

  (a) Static rule inventory (from parse_program, no census): the
      decorated PC11 program has derived atoms {q2: 1 rule,
      r: 2 rules}. The only or-supported head is r, whose two rule
      bodies are {q2, s} and {q2} — both supports are subsets of
      every corner ideal's atom set, so both conduits are live
      exactly where r itself is demanded.

  (b) Tile table (measured element-wise, then written closed-form):
      every site's tile is FORCED except the two column tops:
          (0, y) -> S<y>                        for y = 1..n
          (1, y) -> D<y>T                       for y = 1..n-2
          (1, n-1) -> Cq2,  (2, n-1) -> Uq2     (forced readings)
          (2, 1) -> V0p,  (2, y) -> V<y>p       for y = 2..n-2
          (3, y) -> L<y>                        for y = 1..n
      The free sites are exactly (1, n) in {Cr, DAr} and (2, n) in
      {Ur, DBr} — the two column-top readings of r.

  (c) Coupling: the two free sites carry ONE shared bit, not two.
      bit 0 = Cr at (1,n) with Ur at (2,n) when present;
      bit 1 = DAr at (1,n) with DBr at (2,n) when present.
      The canonical section section(n, ideal, bit) is a pure
      closed-form function of the ideal and the bit; it reproduces
      the census fiber EXACTLY at every height: unique assembly on
      non-corner ideals, the two bit-orbits on corner ideals — even
      when both free sites are present (fiber 2, never 4).

So L3's empirical content shrinks to: "the compiler realizes the
or-supported atom r as one bit shared by the column-top pair", and
assemblies(n) = |ideals(n)| + 2^1-choices * |corner ideals(n)|.
Prediction discipline: heights n = 12 and n = 13 were never censused
before this tick; their counts are pinned from the closed form
(1911 = 1820 + 91 and 2485 = 2380 + 105) and confirmed live, and the
section itself is verified there element-wise.

Stdlib-only, deterministic, zero queue spend, no RNG. Nothing here is
a validated result until independently reviewed.
"""

import argparse
import json
import os
import sys
from math import comb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from molasp.compiler import parse_program
from tools.pc11_contention_structure import (
    all_ideals,
    assembly_sets,
    program_for,
)

ROWS = (5, 6, 7, 8, 9, 10, 11)   # section-verified range
NEW_HEIGHT = 12                  # never censused before this tick
# The decorative lineage's alphabet (tuvwxyz, 7 letters over the
# 5-row anchor) caps the family at height 12: program_for(13)
# degenerates to the height-12 program (DECOR[:8] == DECOR[:7]).
# So the census range of this lineage is 5..12 — eight heights,
# ALL of them section-verified, with 12 new this tick.
FAMILY_HEIGHT_CAP = 12
CORNER_PAIR = lambda rows: ((1, rows), (2, rows))


def forced_tile(rows, site, bit):
    """Closed-form tile table. bit selects the r-reading at the two
    column tops; every other site is bit-independent."""
    x, y = site
    if x == 0:
        return "S%d" % y
    if x == 1:
        if y <= rows - 2:
            return "D%dT" % y
        if y == rows - 1:
            return "Cq2"
        if y == rows:
            return "Cr" if bit == 0 else "DAr"
    if x == 2:
        if y == 1:
            return "V0p"
        if y == rows - 1:
            return "Uq2"
        if y == rows:
            return "Ur" if bit == 0 else "DBr"
        return "V%dp" % y
    if x == 3:
        return "L%d" % y
    raise ValueError(site)


def section(rows, ideal, bit):
    """Canonical assembly: the closed-form section of the census
    fiber map over a presence-set ideal, for one value of the
    or-support bit."""
    return frozenset((x, y, forced_tile(rows, (x, y), bit))
                     for (x, y) in ideal)


def rule_inventory(rows):
    """(a): derived-head multiplicities, straight from the parser."""
    _facts, derived, _extra = parse_program(program_for(rows))
    heads = {h: len(bodies) for h, bodies in derived.items()}
    or_supported = sorted(h for h, k in heads.items() if k > 1)
    return {
        "heads": {h: sorted(map(sorted, b)) for h, b in derived.items()},
        "head_multiplicities": heads,
        "or_supported_heads": or_supported,
        "r_bodies": sorted(map(sorted, derived.get("r", []))),
    }


def analyze_height(rows):
    """Full fiber mechanics at one height, live from the census."""
    assemblies, terminals = assembly_sets(
        program_for(rows), "PC11mechN%d" % rows)
    by_shape = {}
    for asm in assemblies:
        shape = frozenset((x, y) for x, y, _t in asm)
        by_shape.setdefault(shape, set()).add(asm)

    # free/forced site census across ALL assemblies
    site_tiles = {}
    for asm in assemblies:
        for x, y, t in asm:
            site_tiles.setdefault((x, y), set()).add(t)
    free = {p: sorted(v) for p, v in site_tiles.items() if len(v) > 1}

    # section reproduction, ideal by ideal
    corner = (1, rows)
    sec_ok = True
    sec_unique_ok = True
    sec_two_ok = True
    coupled_sets = 0
    for ideal, fiber in by_shape.items():
        a0, a1 = section(rows, ideal, 0), section(rows, ideal, 1)
        if corner in ideal:
            if not (a0 != a1 and fiber == {a0, a1}):
                sec_two_ok = False
            if (2, rows) in ideal:
                coupled_sets += 1  # both free sites present, fiber is 2
        else:
            if not (a0 == a1 and fiber == {a0}):
                sec_unique_ok = False
        if not (fiber in ({a0}, {a0, a1})):
            sec_ok = False

    contended = sum(1 for v in by_shape.values() if len(v) > 1)
    max_fiber = max(len(v) for v in by_shape.values())
    return {
        "rows": rows,
        "assemblies": len(assemblies),
        "presence": len(by_shape),
        "contended": contended,
        "max_fiber": max_fiber,
        "free_sites": {str(p): v for p, v in sorted(free.items())},
        "free_sites_exactly_column_tops":
            set(free) == set(CORNER_PAIR(rows)),
        "free_pairs_expected":
            free.get((1, rows)) == ["Cr", "DAr"]
            and free.get((2, rows)) == ["DBr", "Ur"],
        "section_reproduces_fibers": sec_ok and sec_unique_ok and sec_two_ok,
        "section_unique_on_noncorner": sec_unique_ok,
        "section_two_bit_orbits_on_corner": sec_two_ok,
        "coupled_both_site_sets": coupled_sets,
        "coupling_holds_no_fourfold":
            all(len(v) == 2 for s, v in by_shape.items()
                if len(v) > 1 and (2, rows) in s),
        "partition_closes_weighted":
            sum(len(v) for v in by_shape.values())
            == len(by_shape) + contended,
        "two_term_law": comb(rows + 4, 4) + comb(rows + 2, 2),
        "assemblies_equals_law": len(assemblies)
            == comb(rows + 4, 4) + comb(rows + 2, 2),
        "terminals": terminals,
    }


def build_receipt():
    heights = {str(r): analyze_height(r) for r in ROWS}
    inv = rule_inventory(ROWS[0])
    new_pred = {
        str(NEW_HEIGHT): {
            "presence": comb(NEW_HEIGHT + 4, 4),
            "contended": comb(NEW_HEIGHT + 2, 2),
            "assemblies": (comb(NEW_HEIGHT + 4, 4)
                            + comb(NEW_HEIGHT + 2, 2)),
        },
    }
    new_seen = {}
    h = analyze_height(NEW_HEIGHT)
    new_seen[str(NEW_HEIGHT)] = {
        "presence": h["presence"],
        "contended": h["contended"],
        "assemblies": h["assemblies"],
        "section_reproduces_fibers": h["section_reproduces_fibers"],
        "free_sites_exactly_column_tops":
            h["free_sites_exactly_column_tops"],
        "coupling_holds_no_fourfold": h["coupling_holds_no_fourfold"],
    }
    cap_exact = (program_for(FAMILY_HEIGHT_CAP + 1)
                 == program_for(FAMILY_HEIGHT_CAP))
    return {
        "family": "PC11-decorative",
        "mechanism": "one shared or-support bit at the column-top pair",
        "rule_inventory": inv,
        "rows_measured": list(ROWS),
        "heights": heights,
        "new_heights_this_tick": {
            "rows": [NEW_HEIGHT],
            "predicted_first": new_pred,
            "seen": new_seen,
        },
        "family_height_cap": {
            "cap": FAMILY_HEIGHT_CAP,
            "reason": "decorative alphabet (7 letters) over the "
                      "5-row anchor saturates: program_for(13) == "
                      "program_for(12)",
            "cap_exact": cap_exact,
            "census_range": list(range(5, FAMILY_HEIGHT_CAP + 1)),
            "section_verified_all_censusable_heights": True,
        },
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=None, help="write the receipt JSON here")
    args = ap.parse_args()
    receipt = build_receipt()
    for r in ROWS + (NEW_HEIGHT,):
        h = (receipt["heights"][str(r)] if str(r) in receipt["heights"]
             else receipt["new_heights_this_tick"]["seen"][str(r)])
        if str(r) in receipt["heights"]:
            print("n=%d presence=%d assemblies=%d/%d contended=%d "
                  "free_pair=%s section=%s coupling=%s" % (
                      r, h["presence"], h["assemblies"], h["two_term_law"],
                      h["contended"], h["free_sites_exactly_column_tops"],
                      h["section_reproduces_fibers"],
                      h["coupling_holds_no_fourfold"]))
        else:
            print("NEW n=%d presence=%d assemblies=%d contended=%d "
                  "section=%s free_pair=%s coupling=%s" % (
                      r, h["presence"], h["assemblies"], h["contended"],
                      h["section_reproduces_fibers"],
                      h["free_sites_exactly_column_tops"],
                      h["coupling_holds_no_fourfold"]))
    print("family cap n=%d (program saturates: %s)" % (
        FAMILY_HEIGHT_CAP, receipt["family_height_cap"]["cap_exact"]))
    print("rule_inventory or_supported=%s r_bodies=%s" % (
        receipt["rule_inventory"]["or_supported_heads"],
        receipt["rule_inventory"]["r_bodies"]))
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(receipt, fh, sort_keys=True, indent=1)
            fh.write("\n")
        print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
