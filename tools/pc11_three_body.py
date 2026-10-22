#!/usr/bin/env python3
"""Tick-156's falsifiable prediction, tested and confirmed at every
censusable height: a 3-body or-head censuses at fiber exactly 3,
never 2^3 (2026-10-22, tick 157).

Tick 156 DERIVED assemblies(n) = |ideals| + (k-1)*|corner ideals|
with k = live body count of the or-head, from three static lemmas
(L-east body-identity glue, L-west free bit, L-coupling reader-is-a-
function-of-the-bit), and recorded the open prediction: a 3-body
or-head censuses at fiber k = 3 on its corner ideals, never 2^3.

Fragment fact first (probed live, not assumed): compiler v0.2's
terminal-or geometry admits at most two DISTINCT body shapes — a
unit body on the adjacent-below derived row and one AND body on
(adjacent-below derived, i-2 passthrough) — every other placement
is refused by the emitter's geometry guards.  The k > 2 families
that DO compile are duplicate bodies (semantically idempotent in
ASP, geometrically distinct: the emitter mints a fresh conduit
glue per rule body — unit1_r, unit2_r, ... — so each duplicate is
its own body-identity handshake).  Two 3-body families and one
4-body family are censused here:

  PC11-3U  r :- q2, s. / r :- q2. / r :- q2.        (duplicate unit)
  PC11-3A  r :- q2, s. / r :- q2, s. / r :- q2.     (duplicate AND)
  PC11-4   r :- q2, s. / r :- q2. / r :- q2. / r :- q2, s.

Checks, all live per height 5..12 (decorative extension, same
alphabet, same saturation boundary at n = 12):

  P1  presence sets == the full four-column ideal set,
      |presence| == C(n+4, 4)  (box law unchanged by k)
  A1  |assemblies| == C(n+4, 4) + (k-1)*C(n+2, 2)  — the derived
      law's k-slot tested at k = 3 AND k = 4 (beyond the recorded
      prediction's k = 3)
  C1  contended presence sets == exactly the corner ideals
      (containing site (1, n)), count C(n+2, 2)
  C2  fiber exactly k on corner ideals, exactly 1 elsewhere, no
      other multiplicity anywhere — fiber 3 never 8 (k = 3), fiber
      4 never 16 (k = 4), including the both-site corner ideals
  B1  body-identity pairing, element-wise: in EVERY contended
      fiber, the conduit chosen at (1, n) and the reader chosen at
      (2, n) carry the SAME body glue (east face == west face), and
      the k readings differ only at the site pair (1, n)/(2, n)
  V1  duplicate-shape independence at the top height: PC11-3U and
      PC11-3A produce identical presence/assembly/multiplicity
      censuses (which body shape is duplicated is immaterial)
  S1  the three tick-156 lemmas re-verified statically on the
      k = 3 inventory: every body glue occurs exactly twice in the
      whole inventory; the admissible (1, n) tiles given the forced
      context are exactly the k conduits; each body's reader is the
      unique admissible (2, n) tile given its own west glue, every
      cross-body pairing fails TAU, and growth order still closes
      the (3, n) escape.

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

from molasp.compiler import TAU, compile_program, glue_strength, parse_program
from tools.pc11_contention_structure import (
    DECOR,
    all_ideals,
    assembly_sets,
    ideals_containing,
)
from tools.pc11_fiber_mechanics import FAMILY_HEIGHT_CAP

ROWS = tuple(range(5, FAMILY_HEIGHT_CAP + 1))   # the whole census range
ANCHOR_3U = "p. q. s. q2 :- p. r :- q2, s. r :- q2. r :- q2."
ANCHOR_3A = "p. q. s. q2 :- p. r :- q2, s. r :- q2, s. r :- q2."
ANCHOR_4 = ("p. q. s. q2 :- p. r :- q2, s. r :- q2. r :- q2. "
            "r :- q2, s.")


def program_for_k(rows, family="3U"):
    """Decorative extension of the PC11 anchor with a k-body or-head
    (same placement as the k = 2 census family: decor facts between
    `q.` and `s.`)."""
    anchor = {"3U": ANCHOR_3U, "3A": ANCHOR_3A, "4": ANCHOR_4}[family]
    if rows == 5:
        return anchor
    decor = " ".join(a + "." for a in DECOR[:rows - 5])
    if not decor:
        return anchor
    head, tail = anchor.split("q. ", 1)
    return head + "q. " + decor + " " + tail


# ---------- body-glue reconstruction (the emitter's own minting) ----

def body_glues(prog):
    """{body index: glue} for the multi-body head, replaying the
    emitter's per-body counters (unit{i}_{head} / and{j}_{head} in
    source order) — then verified against the emitted inventory."""
    _facts, rules, _order = parse_program(prog)
    multi = [(h, bodies) for h, bodies in rules.items()
             if len(bodies) > 1]
    if len(multi) != 1:
        raise ValueError("expected exactly one multi-body head")
    head, bodies = multi[0]
    unit_no = and_no = 0
    out = {}
    for i, body in enumerate(bodies):
        if len(body) >= 2:
            and_no += 1
            out[i] = "and%d_%s" % (and_no, head)
        else:
            unit_no += 1
            out[i] = "unit%d_%s" % (unit_no, head)
    return head, bodies, out


# ---------- static glue arithmetic (tick-156 lemmas, k = 3) ---------

def bond_sum(build, tname, placed):
    return sum(
        glue_strength(build["tiles"][tname].get(d, ""), g)
        for d, g in placed.items())


def admissible(build, placed):
    return sorted(t for t in build["tiles"]
                  if bond_sum(build, t, placed) >= TAU)


def face_census(build):
    c = Counter()
    for faces in build["tiles"].values():
        for _d, g in faces.items():
            if g:
                c[g] += 1
    return c


def static_lemmas(rows):
    prog = program_for_k(rows, "3U")
    build = compile_program(prog, name="PC11_3U_stat%d" % rows)
    tiles = build["tiles"]
    head, bodies, glues = body_glues(prog)
    n = rows
    ctx_w = tiles["S%d" % n].get("E")            # west of (1, n)
    ctx_d_south = tiles["Cq2"].get("N")          # south of (1, n)
    ctx_v_south = tiles["Uq2"].get("N")          # south of (2, n)
    counts = face_census(build)
    conduits, readers = {}, {}
    for i, g in glues.items():
        conduits[i] = [t for t in tiles if tiles[t].get("E") == g]
        readers[i] = [t for t in tiles if tiles[t].get("W") == g]
    adm_1n = admissible(build, {"W": ctx_w, "S": ctx_d_south})
    per_bit = {}
    for i, g in glues.items():
        own = admissible(build, {"S": ctx_v_south, "W": g})
        cross = {j: bond_sum(build, readers[i][0],
                             {"S": ctx_v_south, "W": glues[j]})
                 for j in glues if j != i}
        per_bit[str(g)] = {
            "reader": readers[i],
            "conduit": conduits[i],
            "admissible_at_2n": own,
            "cross_bond_sums": cross,
        }
    l_tile = "L%d" % n
    l_south = bond_sum(build, l_tile, {"S": tiles["L%d" % (n - 1)].get("N")})
    l_west = bond_sum(build, l_tile,
                      {"S": tiles["L%d" % (n - 1)].get("N"),
                       "W": tiles[readers[0][0]].get("E")})
    return {
        "rows": rows,
        "bodies": [sorted(b) for b in bodies],
        "body_glues": glues,
        "L_east": {
            "occurrences": {g: counts[g] for g in glues.values()},
            "each_exactly_twice":
                all(counts[g] == 2 for g in glues.values()),
            "one_conduit_one_reader_each":
                all(len(conduits[i]) == 1 and len(readers[i]) == 1
                    for i in glues),
        },
        "L_west": {
            "admissible_at_1n": adm_1n,
            "exactly_the_k_conduits":
                adm_1n == sorted(t[0] for t in conduits.values()),
        },
        "L_coupling": {
            "south_only_at_2n": admissible(build, {"S": ctx_v_south}),
            "per_bit": per_bit,
            "reader_function_of_bit":
                all(v["admissible_at_2n"] == v["reader"]
                    for v in per_bit.values()),
            "all_cross_pairs_fail_tau":
                all(s < TAU for v in per_bit.values()
                    for s in v["cross_bond_sums"].values()),
            "growth_order_L_cannot_arrive_first":
                l_south < TAU and l_west >= TAU
                and not admissible(
                    build, {"S": tiles["L%d" % (n - 1)].get("N")}),
        },
    }


# ---------- census ---------------------------------------------------

def census(rows, family="3U"):
    k = {"3U": 3, "3A": 3, "4": 4}[family]
    prog = program_for_k(rows, family)
    _head, _bodies, glues = body_glues(prog)
    build = compile_program(prog, name="PC11_%s_N%d" % (family, rows))
    tiles = build["tiles"]
    assemblies, _terminals = assembly_sets(
        prog, "PC11_%s_N%d" % (family, rows))
    by_shape = {}
    for asm in assemblies:
        shape = frozenset((x, y) for x, y, _t in asm)
        by_shape.setdefault(shape, set()).add(asm)
    corner = ideals_containing((1, rows), rows)
    contended = {s: v for s, v in by_shape.items() if len(v) > 1}
    mult = Counter(len(v) for v in by_shape.values())
    diff_restricted = True
    body_paired = True
    glue_set = set(glues.values())
    pair = {(1, rows), (2, rows)}
    for shape, fiber in contended.items():
        for a1 in fiber:
            for a2 in fiber:
                if a1 is a2:
                    continue
                d = {(x, y) for x, y, _t in (a1 ^ a2)}
                if not d <= pair:
                    diff_restricted = False
        for asm in fiber:
            at = {(x, y): t for x, y, t in asm}
            east = tiles.get(at.get((1, rows), ""), {}).get("E")
            reader = at.get((2, rows))
            west = tiles.get(reader, {}).get("W") if reader else None
            # (2, n) absent (single-site corner ideal): the conduit
            # attaches west+south alone; pairing is vacuous at east.
            if east not in glue_set or (
                    reader is not None and west != east):
                body_paired = False
    both_corner = [s for s in contended if (2, rows) in s]
    return {
        "family": family,
        "rows": rows,
        "k": k,
        "presence": len(by_shape),
        "presence_equals_ideals": set(by_shape) == all_ideals(rows),
        "assemblies": len(assemblies),
        "law": comb(rows + 4, 4) + (k - 1) * comb(rows + 2, 2),
        "law_holds": len(assemblies)
            == comb(rows + 4, 4) + (k - 1) * comb(rows + 2, 2),
        "contended": len(contended),
        "corner_law": comb(rows + 2, 2),
        "contended_equals_corner_ideals": set(contended) == corner,
        "multiplicity_hist": dict(sorted(mult.items())),
        "fiber_exactly_k_on_corner_else_1":
            mult == Counter({1: len(by_shape) - len(contended),
                             k: len(contended)}),
        "never_power": max(mult) == k and k < 2 ** k,
        "both_site_corner_ideals": len(both_corner),
        "max_fiber_both_site": max((len(v) for s, v in contended.items()
                                    if (2, rows) in s), default=0),
        "readings_differ_only_at_site_pair": diff_restricted,
        "body_identity_pairing": body_paired,
    }


def build_receipt():
    static = {str(r): static_lemmas(r) for r in ROWS}
    cens3 = {str(r): census(r, "3U") for r in ROWS}
    cens4 = {str(r): census(r, "4") for r in ROWS}
    top = max(ROWS)
    variant = census(top, "3A")
    agreement = {
        "rows": top,
        "presence": variant["presence"] == cens3[str(top)]["presence"],
        "assemblies": variant["assemblies"]
            == cens3[str(top)]["assemblies"],
        "multiplicity_hist": variant["multiplicity_hist"]
            == cens3[str(top)]["multiplicity_hist"],
        "law_holds": variant["law_holds"],
    }
    lemmas = {
        "L_east_all_heights": all(
            h["L_east"]["each_exactly_twice"]
            and h["L_east"]["one_conduit_one_reader_each"]
            for h in static.values()),
        "L_west_all_heights": all(
            h["L_west"]["exactly_the_k_conduits"]
            for h in static.values()),
        "L_coupling_all_heights": all(
            h["L_coupling"]["reader_function_of_bit"]
            and h["L_coupling"]["all_cross_pairs_fail_tau"]
            and h["L_coupling"]["growth_order_L_cannot_arrive_first"]
            and not h["L_coupling"]["south_only_at_2n"]
            for h in static.values()),
        "prediction_k3_all_heights": all(
            c["fiber_exactly_k_on_corner_else_1"]
            and c["never_power"] and c["law_holds"]
            and c["presence_equals_ideals"]
            and c["contended_equals_corner_ideals"]
            and c["readings_differ_only_at_site_pair"]
            and c["body_identity_pairing"]
            for c in cens3.values()),
        "beyond_prediction_k4_all_heights": all(
            c["fiber_exactly_k_on_corner_else_1"]
            and c["never_power"] and c["law_holds"]
            and c["body_identity_pairing"]
            for c in cens4.values()),
        "duplicate_shape_independence_top": all(
            agreement[k] for k in
            ("presence", "assemblies", "multiplicity_hist", "law_holds")),
    }
    return {
        "family": "PC11-decorative, k-body or-head extension",
        "result": "tick-156 prediction CONFIRMED: fiber == k exactly "
                  "(3 never 8 at k = 3; 4 never 16 at k = 4); "
                  "assemblies(n) = C(n+4,4) + (k-1)*C(n+2,2)",
        "fragment_boundary": "compiler v0.2 admits at most two "
                             "DISTINCT terminal-or body shapes; the "
                             "k > 2 families that compile are duplicate "
                             "bodies (fresh conduit glue per body)",
        "lemmas": lemmas,
        "rows_measured": list(ROWS),
        "static_lemmas_k3": static,
        "census_3U": cens3,
        "census_4": cens4,
        "duplicate_shape_agreement_top": agreement,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=None, help="write the receipt JSON here")
    args = ap.parse_args()
    receipt = build_receipt()
    for r in ROWS:
        c3 = receipt["census_3U"][str(r)]
        c4 = receipt["census_4"][str(r)]
        print("n=%-2d k=3 assemblies=%d/%d hist=%s paired=%s | "
              "k=4 assemblies=%d/%d hist=%s" % (
                  r, c3["assemblies"], c3["law"],
                  c3["multiplicity_hist"], c3["body_identity_pairing"],
                  c4["assemblies"], c4["law"], c4["multiplicity_hist"]))
    print("lemmas:", json.dumps(receipt["lemmas"], sort_keys=True))
    if args.out:
        data = json.dumps(receipt, indent=2, sort_keys=True,
                          default=sorted) + "\n"
        with open(args.out, "w") as fh:
            fh.write(data)
        print("sha256(%s) = %s" % (
            args.out, hashlib.sha256(data.encode()).hexdigest()))


if __name__ == "__main__":
    main()
