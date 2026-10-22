#!/usr/bin/env python3
"""The coupling rule itself, derived from conduit geometry
(2026-10-22, tick 156).

Tick 155 mechanized L3 as "one shared or-support bit" and left the
coupling unexplained: WHY do the two column tops (1,n) in {Cr, DAr}
and (2,n) in {Ur, DBr} never realize all four combinations? This
module derives the rule from the emitted inventory alone (static
glue arithmetic under cooperative attachment at TAU = 2, honoring
growth order), with the census used only as a cross-check.

THE RULE, in three lemmas (all machine-checked per height):

  L-east (body-identity glue).  The emitter names one conduit glue
  per rule BODY of the or-supported head: the conduit's east face
  is v_b = unit1_r (unit body {q2}) resp. and1_r (AND body {q2,s}),
  and the same glue occurs NOWHERE else in the inventory except the
  west face of that body's own reader (exactly two occurrences:
  conduit-E and reader-W of the same body).  The east-west
  handshake across row n is therefore a BODY-IDENTITY match.

  L-west (the bit is free only at (1,n)).  Against the forced
  context (S{n} east face go_n west; the passthrough re-type puts
  {lo}-t-done = s-t-done on Cq2's north face south), EVERY conduit
  reaches exactly TAU = 2 by west+south bonds (1+1), so the number
  of admissible (1,n) tiles equals the number of LIVE bodies of r
  — here 2, both live under the least model (q2, s true).  The
  south bond is the semantic read by value typing: a false lo
  emits {lo}-t-done nowhere, so its conduit would die at 1 < 2.

  L-coupling ((2,n) is a FUNCTION of the bit).  At (2,n) the only
  available providers at attach time are south (Uq2's north
  q2-t-done, strength exactly 1 for both readers — the hi chain
  link, again value-typed) and west (the chosen conduit's v_b).
  No single face reaches 2 (v_b is not a spine glue), so a west
  match is NECESSARY; by L-east the only tile whose west face
  matches v_b is body b's own reader.  Growth order closes the
  last escape: L{n} east of (2,n) needs ITS west bond (south alone
  is 1 < 2), so it can never arrive first to supply an east bond.
  Hence admissible(2,n | bit = b) = {reader_b}, a singleton: the
  two sites carry ONE choice, not two.

COROLLARY (derived, not just measured): the census fiber over a
presence set is the number of live bodies k of the or-head on
corner ideals (k = 2 here), so
    assemblies(n) = |ideals(n)| + (k - 1) * |corner ideals(n)|,
whose (k-1) multiplier is now the per-body glue handshake of
L-east/L-coupling.  Falsifiable prediction for the natural
follow-up family: a 3-body or-head censuses at fiber k = 3 on its
corner ideals (never 2^3).  Not yet measured; recorded open.

Stdlib-only, deterministic, zero queue spend, no RNG. Nothing here
is a validated result until independently reviewed.
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

from molasp.compiler import TAU, compile_program, glue_strength
from tools.pc11_contention_structure import (
    all_ideals,
    assembly_sets,
    program_for,
)
from tools.pc11_fiber_mechanics import FAMILY_HEIGHT_CAP, section

ROWS = tuple(range(5, FAMILY_HEIGHT_CAP + 1))   # the whole census range
OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}


# ---------- static glue arithmetic --------------------------------------

def build_for(rows):
    return compile_program(program_for(rows), name="PC11ruleN%d" % rows)


def body_map(build):
    """{body-key: {conduit, reader, glue}} for the or-head r, straight
    from the emitted tile faces (names are the emitter's own minting)."""
    heads = [t for t, row in build["row_of"].items() if row == max(build["rows"])]
    out = {}
    for tname in sorted(build["tiles"]):
        faces = build["tiles"][tname]
        w = faces.get("W", "")
        if w in ("unit1_r", "and1_r"):
            kind = "unit" if w.startswith("unit") else "and"
            out.setdefault(kind, {})["reader"] = tname
            out[kind]["glue"] = w
        e = faces.get("E", "")
        if e in ("unit1_r", "and1_r"):
            kind = "unit" if e.startswith("unit") else "and"
            out.setdefault(kind, {})["conduit"] = tname
    return out


def bond_sum(build, tname, placed):
    """Total bond strength of tile `tname` against placed neighbor
    glues {DIR: neighbor's opposing face glue}."""
    return sum(
        glue_strength(build["tiles"][tname].get(d, ""), g)
        for d, g in placed.items())


def admissible(build, placed):
    """Every inventory tile (any row) reaching TAU against `placed` —
    the exhaustive static scan; no BFS, no census."""
    return sorted(t for t in build["tiles"]
                  if bond_sum(build, t, placed) >= TAU)


def face_census(build):
    c = Counter()
    for faces in build["tiles"].values():
        for d, g in faces.items():
            if g:
                c[g] += 1
    return c


# ---------- the three lemmas + corollary, per height ---------------------

def analyze_height(rows):
    build = build_for(rows)
    tiles = build["tiles"]
    n = rows
    ctx = {
        "S_col_east": tiles["S%d" % n].get("E"),      # west of (1,n)
        "D_below_north": tiles["Cq2"].get("N"),       # south of (1,n)
        "V_below_north": tiles["Uq2"].get("N"),       # south of (2,n)
        "L_below_north": tiles["L%d" % (n - 1)].get("N"),  # south of (3,n)
    }
    bmap = body_map(build)

    # L-west: admissible conduits at (1,n) given {W: go_n, S: s-t-done}
    placed_D = {"W": ctx["S_col_east"], "S": ctx["D_below_north"]}
    adm_D = admissible(build, placed_D)
    d_sums = {t: bond_sum(build, t, placed_D) for t in adm_D}

    # L-coupling: admissible readers at (2,n) per bit, given south only
    # 1 and west = that body's conduit glue
    placed_V = {"S": ctx["V_below_north"]}
    south_only = admissible(build, placed_V)
    per_bit = {}
    for kind, info in bmap.items():
        placed = {"S": ctx["V_below_north"], "W": info["glue"]}
        per_bit[kind] = {
            "glue": info["glue"],
            "conduit": info["conduit"],
            "reader": info["reader"],
            "admissible_at_2n": admissible(build, placed),
            "cross_bond_sum": bond_sum(
                build, info["reader"],
                {"S": ctx["V_below_north"],
                 "W": bmap["and" if kind == "unit" else "unit"]["glue"]}),
        }

    # growth-order lemma: nothing attaches at (3,n) from south alone
    adm_L_south_only = admissible(
        build, {"S": ctx["L_below_north"]})
    l_tile = "L%d" % n
    l_south_sum = bond_sum(build, l_tile, {"S": ctx["L_below_north"]})
    l_with_west = bond_sum(
        build, l_tile,
        {"S": ctx["L_below_north"],
         "W": tiles[bmap["unit"]["reader"]].get("E")})

    # L-east: each body glue occurs exactly twice (conduit E, reader W)
    counts = face_census(build)
    glue_uniqueness = {
        info["glue"]: counts[info["glue"]] for info in bmap.values()}

    # semantic south: conduit S faces are the value-typed lo read
    lo_faces = {kind: tiles[info["conduit"]].get("S")
                for kind, info in bmap.items()}
    hi_faces = {kind: tiles[info["reader"]].get("S")
                for kind, info in bmap.items()}

    return {
        "rows": rows,
        "context": ctx,
        "bodies": bmap,
        "L_east": {
            "body_glue_occurrences": glue_uniqueness,
            "each_glue_exactly_twice":
                all(v == 2 for v in glue_uniqueness.values()),
        },
        "L_west": {
            "admissible_at_1n": adm_D,
            "bond_sums": d_sums,
            "free_bit_exactly_two_conduits":
                sorted(adm_D) == sorted(
                    info["conduit"] for info in bmap.values()),
            "south_is_value_typed_lo_read":
                len(set(lo_faces.values())) == 1
                and next(iter(lo_faces.values())).endswith("-t-done"),
        },
        "L_coupling": {
            "south_only_admissible_at_2n": south_only,
            "south_only_is_empty": not south_only,
            "per_bit": per_bit,
            "reader_is_function_of_bit": all(
                v["admissible_at_2n"] == [v["reader"]]
                for v in per_bit.values()),
            "cross_pair_fails_tau": all(
                v["cross_bond_sum"] < TAU for v in per_bit.values()),
            "growth_order": {
                "tile": l_tile,
                "south_only_admissible": adm_L_south_only,
                "south_only_sum": l_south_sum,
                "with_west_sum": l_with_west,
                "cannot_arrive_first":
                    not adm_L_south_only and l_south_sum < TAU
                    and l_with_west >= TAU,
            },
        },
        "reader_south_is_hi_chain_link":
            len(set(hi_faces.values())) == 1
            and next(iter(hi_faces.values())) == "q2-t-done",
    }


def census_cross_check(rows):
    """Measured fiber == static prediction on corner ideals (the only
    place a fiber exists at all)."""
    assemblies, _terminals = assembly_sets(
        program_for(rows), "PC11ruleX%d" % rows)
    by_shape = {}
    for asm in assemblies:
        shape = frozenset((x, y) for x, y, _t in asm)
        by_shape.setdefault(shape, set()).add(asm)
    corner = (1, rows)
    both = (2, rows)
    n_corner = n_both = agree = 0
    max_fiber_both = 0
    for ideal, fiber in by_shape.items():
        if corner in ideal:
            n_corner += 1
            predicted = {section(rows, ideal, 0), section(rows, ideal, 1)}
            if fiber != predicted:
                agree = -10 ** 9
            if both in ideal:
                n_both += 1
                max_fiber_both = max(max_fiber_both, len(fiber))
    k = 2
    ideals = all_ideals(rows)
    return {
        "rows": rows,
        "corner_ideals": n_corner,
        "corner_ideals_with_both_sites": n_both,
        "max_fiber_on_both_site_sets": max_fiber_both,
        "fiber_equals_k_never_4": max_fiber_both == k,
        "section_prediction_agrees": agree >= 0,
        "assemblies": len(assemblies),
        "law_k_form":
            comb(rows + 4, 4) + (k - 1) * comb(rows + 2, 2),
        "law_holds": len(assemblies)
            == comb(rows + 4, 4) + (k - 1) * comb(rows + 2, 2),
        "ideals_count": len(ideals),
    }


def build_receipt():
    heights = {str(r): analyze_height(r) for r in ROWS}
    checks = {str(r): census_cross_check(r) for r in ROWS}
    lemmas = {
        "L_east_all_heights": all(
            h["L_east"]["each_glue_exactly_twice"]
            for h in heights.values()),
        "L_west_all_heights": all(
            h["L_west"]["free_bit_exactly_two_conduits"]
            and h["L_west"]["south_is_value_typed_lo_read"]
            for h in heights.values()),
        "L_coupling_all_heights": all(
            h["L_coupling"]["south_only_is_empty"]
            and h["L_coupling"]["reader_is_function_of_bit"]
            and h["L_coupling"]["cross_pair_fails_tau"]
            and h["L_coupling"]["growth_order"]["cannot_arrive_first"]
            for h in heights.values()),
        "census_agrees_all_heights": all(
            c["section_prediction_agrees"]
            and c["fiber_equals_k_never_4"] and c["law_holds"]
            for c in checks.values()),
    }
    return {
        "family": "PC11-decorative",
        "result": "coupling rule derived from conduit geometry",
        "lemmas": lemmas,
        "rule": "the or-bit is carried east by exactly one named "
                "conduit glue per rule body; the (2,n) reader is a "
                "function of that glue, so k bodies give fiber k",
        "corollary": "assemblies(n) = |ideals| + (k-1)*|corner ideals| "
                     "with k = live body count of the or-head (k = 2 "
                     "here); the (k-1) multiplier is derived",
        "open_prediction": {
            "claim": "a 3-body or-head censuses at fiber 3 on corner "
                     "ideals, never 2^3",
            "status": "derived-level prediction, not yet censused",
        },
        "rows_measured": list(ROWS),
        "heights": heights,
        "census_cross_checks": checks,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=None, help="write the receipt JSON here")
    args = ap.parse_args()
    receipt = build_receipt()
    for r in ROWS:
        h = receipt["heights"][str(r)]
        c = receipt["census_cross_checks"][str(r)]
        print("n=%-2d adm1n=%s per-bit readers=%s cross<tau=%s "
              "growth-order=%s fiber==k=%s law=%s" % (
                  r, h["L_west"]["admissible_at_1n"],
                  {k: v["admissible_at_2n"]
                   for k, v in h["L_coupling"]["per_bit"].items()},
                  h["L_coupling"]["cross_pair_fails_tau"],
                  h["L_coupling"]["growth_order"]["cannot_arrive_first"],
                  c["fiber_equals_k_never_4"], c["law_holds"]))
    print("lemmas:", json.dumps(receipt["lemmas"], sort_keys=True))
    if args.out:
        data = json.dumps(receipt, indent=2, sort_keys=True,
                          default=sorted) + "\n"
        with open(args.out, "w") as fh:
            fh.write(data)
        print("sha256(%s) = %s" % (
            args.out,
            hashlib.sha256(data.encode()).hexdigest()))


if __name__ == "__main__":
    main()
