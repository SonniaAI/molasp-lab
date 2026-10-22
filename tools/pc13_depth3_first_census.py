#!/usr/bin/env python3
"""Tick 164: the FIRST true depth-3 census — the designs/013 §1
fragment implemented, tested against predictions pinned BEFORE any
census (designs/013 §3, tick 163).

The compiler carve-out (MAX_RELAY_STAGES = 3, molasp/compiler.py)
admits a relay CHAIN on the designs/012 per-body discipline: up to
three stacked relays, each stage's duplicate unit bodies reading the
adjacent-below derived row (the previous stage's head, or the spine
for the first relay).  The family censused here (terminal-first
multiplicities ks = [k_w, k_r, k_u]):

  PC13-D3   p. <decor>.  q2 :- p.  u :- q2. (x k_u)
                          r :- u.  (x k_r)  w :- r. (x k_w)

with the family-local decor alphabet t y z k m b a (never a head
atom — the tick-158 collision lesson).

Tick 163 pinned, before this family could compile:

  [2,2,2]  577 / 813 / 1110 / 1478 / 1928 / 2472 / 3123  (n=6..12)
  [3,2,2]  689 / 957 / 1290 / 1698 / 2192 / 2784 / 3487
  [2,2,3]  818 / 1132 / 1518 / 1986 / 2547 / 3213 / 3997
  [2,2,2,2] (depth 4) 1099/1511/2010/2606/3310/4134/5091

under the nested-shell product law
assemblies(n) = C(n+4,4) + sum_d (prod_{i>=d} k_i - 1)(d+1)C(n-d+2,2)
(suffix product per shell), with shell_d ideals censusing at fiber
exactly prod_{i>=d} k_i — never additive (fiber sum_{i>=d} k_i -
(m-d)), never a power of two unless the product itself is one.

Checks, live at every censused height:

  P1  presence == the full four-column ideal set C(n+4,4)
  M1  |assemblies| == the pinned scalar (product law) exactly
  F1  fiber histogram exactly {1: rest, prod-shell fibers only};
      for [2,2,2]: {1,2,4,8} and nothing else
  F2  element-wise expected fiber: every shape's realized fiber ==
      prod of k_i over the corners (1, n-i) it contains
  N1  corner nesting C^(0) <= C^(1) <= C^(2) element-wise
  X1  product structure element-wise: every full fiber realizes all
      conduit combinations at the column-1 corner sites
  X2  readings differ only at the corner site pairs (1,n-d)/(2,n-d)
  R1  every relay stage stays value-typed: all its conduits expose
      N = {head}-t-done, k conduits per relay stage
  B1  per-body conduit-glue handshake: every unit{j}_{a} glue occurs
      exactly twice in the whole inventory, at every head
  G1  the new fence: depth-5 chains refuse verbatim; AND and mixed
      bodies at a relay row still refuse verbatim; a second
      terminal consumer of a relayed head still refuses (now by the
      non-adjacency arm); BOTH tick-163 depth-3 axes now compile.

Stdlib-only, deterministic, zero queue spend, no RNG.  Not a
validated result until independently reviewed.
"""
import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from math import comb, prod

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from molasp.compiler import MAX_RELAY_STAGES, compile_program
from tools.pc11_contention_structure import (
    all_ideals,
    assembly_sets,
    ideals_containing,
)

# ------------------------------------------------------------ family

DECOR = "tyzkmba"                     # 7 letters: n = 6..12 for depth 3
RELAYS_D3 = ["u", "r"]                # bottom-up (u on spine, r below w)
RELAYS_D4 = ["u", "v", "r"]
PINNED_222 = {6: 577, 7: 813, 8: 1110, 9: 1478,
              10: 1928, 11: 2472, 12: 3123}
PINNED_322 = {6: 689, 7: 957, 8: 1290, 9: 1698,
              10: 2192, 11: 2784, 12: 3487}
PINNED_223 = {6: 818, 7: 1132, 8: 1518, 9: 1986,
              10: 2547, 11: 3213, 12: 3997}
PINNED_2222 = {6: 1099, 7: 1511, 8: 2010, 9: 2606,
               10: 3310, 11: 4134, 12: 5091}


def chain_program(rows, ks, relays):
    """Program of the relay-chain family at `rows` rows, terminal-
    first multiplicities ks (ks[0] = terminal, ks[-1] = bottom relay
    on the spine)."""
    n_chain = 2 + len(relays)          # q2 + relays + terminal w
    n_decor = rows - 1 - n_chain
    assert n_decor >= 0 and n_decor <= len(DECOR), (rows, ks)
    facts = "p. " + " ".join(a + "." for a in DECOR[:n_decor])
    rules = ["q2 :- p."]
    for j, atom in enumerate(relays):          # bottom-up
        k = ks[len(ks) - 1 - j]
        below = "q2" if j == 0 else relays[j - 1]
        rules += ["%s :- %s." % (atom, below)] * k
    rules += ["w :- %s." % relays[-1]] * ks[0]
    return facts + " " + " ".join(rules)


def shell_law(rows, ks):
    """designs/013 §2: suffix-product law, recomputed live."""
    total = comb(rows + 4, 4)
    m = len(ks) - 1
    for d in range(m + 1):
        suffix = 1
        for i in range(d, m + 1):
            suffix *= ks[i]
        total += (suffix - 1) * (d + 1) * comb(rows - d + 2, 2)
    return total


def additive_falsifier(rows, ks):
    """Additive alternative: fiber on shell_d = sum_{i>=d} k_i -
    (m - d), i.e. head multiplicities added, never multiplied."""
    total = comb(rows + 4, 4)
    m = len(ks) - 1
    for d in range(m + 1):
        s = sum(ks[d:]) - (m - d)
        total += (s - 1) * (d + 1) * comb(rows - d + 2, 2)
    return total


# ------------------------------------------------------------- checks

def census_height(rows, ks, relays, pinned):
    prog = chain_program(rows, ks, relays)
    assemblies, terminals = assembly_sets(prog, "PC13_N%d" % rows)
    by_shape = {}
    for asm in assemblies:
        shape = frozenset((x, y) for x, y, _t in asm)
        by_shape.setdefault(shape, set()).add(asm)
    ideals = all_ideals(rows)
    m = len(ks) - 1
    corners = [ideals_containing((1, rows - d), rows) for d in range(m + 1)]

    # P1 presence
    presence_ok = set(by_shape) == ideals
    # N1 nesting, element-wise over ALL ideals
    nesting_ok = all(corners[d] <= corners[d + 1] for d in range(m))
    # F2 element-wise expected fiber + F1 histogram
    expected = {}
    elem_ok = True
    for shape in by_shape:
        exp = 1
        for i in range(m + 1):
            if shape in corners[i]:
                exp *= ks[i]
        expected[shape] = exp
        if len(by_shape[shape]) != exp:
            elem_ok = False
    hist = Counter(len(v) for v in by_shape.values())
    shells = Counter(expected.values())
    hist_ok = hist == shells
    never_ok = all(f in set(shell_law_fibers(ks)) for f in hist)
    # X2 readings differ only at the corner site pairs
    pairs = set()
    for d in range(m + 1):
        pairs |= {(1, rows - d), (2, rows - d)}
    diff_ok = True
    for shape, fiber in by_shape.items():
        if len(fiber) < 2:
            continue
        for a1 in fiber:
            for a2 in fiber:
                if a1 is a2:
                    continue
                if not {(x, y) for x, y, _t in (a1 ^ a2)} <= pairs:
                    diff_ok = False
    # X1 product structure element-wise: every fiber realizes all
    # conduit combinations at the column-1 corner sites it carries
    sites = [(1, rows - d) for d in range(m + 1)]
    combos_ok = True
    for shape, fiber in by_shape.items():
        carried = [i for i in range(m + 1) if shape in corners[i]]
        want = 1
        for i in carried:
            want *= ks[i]
        if len(fiber) != want:
            combos_ok = False
            continue
        seen = set()
        for asm in fiber:
            tiles_at = {(x, y): t for x, y, t in asm if (x, y) in sites}
            seen.add(tuple(tiles_at.get(s) for s in sites))
        if len(seen) != want:
            combos_ok = False
    measured = len(assemblies)
    return {
        "rows": rows,
        "ks": ks,
        "program": prog,
        "assemblies": measured,
        "pinned": pinned,
        "matches_pinned": measured == pinned,
        "law_total": shell_law(rows, ks),
        "law_holds": measured == shell_law(rows, ks),
        "additive_total": additive_falsifier(rows, ks),
        "additive_falsified": measured != additive_falsifier(rows, ks),
        "presence": len(by_shape),
        "presence_equals_ideals": presence_ok,
        "nesting_elementwise": nesting_ok,
        "fiber_histogram": {str(k): v for k, v in sorted(hist.items())},
        "shell_sizes": {str(k): v for k, v in sorted(shells.items())},
        "fiber_hist_is_shell_hist": hist_ok,
        "expected_fiber_elementwise": elem_ok,
        "fibers_all_legal": never_ok,
        "readings_differ_only_at_corner_pairs": diff_ok,
        "conduit_combos_realized": combos_ok,
        "terminals": terminals,
    }


def shell_law_fibers(ks):
    """The only fiber values the product law permits."""
    m = len(ks) - 1
    return {1} | {prod(ks[d:]) for d in range(m + 1)}


def static_checks(rows, ks, relays):
    """R1/B1 straight from the emitted inventory."""
    prog = chain_program(rows, ks, relays)
    build = compile_program(prog, name="PC13_stat%d" % rows)
    tiles = build["tiles"]
    row_of = build["row_of"]
    n = rows
    heads_bottom_up = relays + ["w"]
    out = {"rows": rows, "stages": {}}
    ok = True
    counts = Counter(g for faces in tiles.values()
                     for g in faces.values() if g)
    for j, atom in enumerate(heads_bottom_up):
        k = ks[len(ks) - 1 - j]
        row = n - len(heads_bottom_up) + j + 1
        names = {"C%s" % atom} | {"C%s%d" % (atom, i)
                                for i in range(2, k + 1)}
        conduits = sorted(t for t in names
                          if t in tiles and row_of.get(t) == row)
        north = {tiles[t].get("N", "") for t in conduits}
        terminal = (atom == "w")
        if terminal:
            # the terminal or-head keeps PER-BODY value glues north
            # (designs/012 §2 re-types only relay conduits)
            want_north = {"unit%d_%s-done" % (i, atom)
                          for i in range(1, k + 1)}
        else:
            want_north = {"%s-t-done" % atom}
        value_typed = north == want_north
        glues = ["unit%d_%s" % (i, atom) for i in range(1, k + 1)]
        handshake = all(counts[g] == 2 for g in glues)
        stage = {"row": row, "conduits": len(conduits), "k": k,
                 "conduit_count_is_k": len(conduits) == k,
                 "north_faces": sorted(north),
                 "north_faces_exactly_expected": value_typed,
                 "body_glues_each_exactly_twice": handshake}
        out["stages"][atom] = stage
        ok = ok and len(conduits) == k and value_typed and handshake
    out["all_stages_ok"] = ok
    return out


# -------------------------------------------------------------- fence

GUARD_PROBES = {
    "depth5_chain": (
        "p. t. q2 :- p. u :- q2. u :- q2. v :- u. v :- u. "
        "r :- v. r :- v. x :- r. x :- r. w :- x. w :- x."),
    "and_body_at_relay": (
        "p. t. q2 :- p. u :- q2. u :- q2, p. "
        "r :- u. r :- u. w :- r. w :- r."),
    "mixed_bodies_at_relay": (
        "p. t. q2 :- p. u :- q2. u :- q2. u :- t. "
        "r :- u. r :- u. w :- r. w :- r."),
    "second_terminal_consumer": (
        "p. q. s. q2 :- p. r :- q2. r :- q2. w :- r. w :- r. "
        "v :- r. v :- r."),
    "tick163_axis_stacked_spine_relay": (
        "p. q. s. q2 :- p. u :- q2. u :- q2. r :- u. r :- u. "
        "w :- r. w :- r."),
    "tick163_axis_head_chained_relay": (
        "p. q. s. q2 :- p. r :- q2. r :- q2. u :- r. u :- r. "
        "w :- u. w :- u."),
}


def guard_probe():
    results = {}
    for label, prog in sorted(GUARD_PROBES.items()):
        entry = {"program": prog}
        try:
            build = compile_program(prog, name="probe_%s" % label)
            entry["compiled"] = True
            entry["tiles"] = len(build["tiles"])
        except Exception as exc:                # noqa: BLE001 - pinned
            entry["compiled"] = False
            entry["refusal"] = "%s: %s" % (type(exc).__name__, exc)
        results[label] = entry
    return results


# ------------------------------------------------------------ receipt

def build_receipt():
    primary = {str(n): census_height(n, [2, 2, 2], RELAYS_D3,
                                     PINNED_222[n]) for n in range(6, 13)}
    mixed_u = {str(n): census_height(n, [2, 2, 3], RELAYS_D3,
                                     PINNED_223[n]) for n in range(6, 13)}
    mixed_w = {str(n): census_height(n, [3, 2, 2], RELAYS_D3,
                                     PINNED_322[n]) for n in (6, 12)}
    depth4 = {str(n): census_height(n, [2, 2, 2, 2], RELAYS_D4,
                                    PINNED_2222[n]) for n in (8, 9, 10)}
    static = {str(n): static_checks(n, [2, 2, 2], RELAYS_D3)
              for n in range(6, 13)}
    probes = guard_probe()
    receipt = {
        "kind": "pc13-depth3-first-census",
        "date": "2026-10-22",
        "card": "SON-5152 tick 164",
        "family": "PC13-D3 (designs/013 section 1 fragment, now real)",
        "compiler": {
            "max_relay_stages": MAX_RELAY_STAGES,
            "carve_out": "designs/013 section 1: relay chains, same "
                         "per-body discipline; everything else refused",
        },
        "pinned_before_census": "designs/013 section 3 (tick 163)",
        "primary_222": primary,
        "mixed_bottom_relay_223": mixed_u,
        "mixed_terminal_322": mixed_w,
        "depth4_2222": depth4,
        "static": static,
        "guard_probes": probes,
        "summary": {
            "all_pinned_scalars_land": all(
                v["matches_pinned"] for leg in
                (primary, mixed_u, mixed_w, depth4)
                for v in leg.values()),
            "law_holds_everywhere": all(
                v["law_holds"] for leg in
                (primary, mixed_u, mixed_w, depth4)
                for v in leg.values()),
            "additive_falsified_everywhere": all(
                v["additive_falsified"] for leg in
                (primary, mixed_u, mixed_w, depth4)
                for v in leg.values()),
            "presence_equals_ideals_everywhere": all(
                v["presence_equals_ideals"] for leg in
                (primary, mixed_u, mixed_w, depth4)
                for v in leg.values()),
            "nesting_elementwise_everywhere": all(
                v["nesting_elementwise"] for leg in
                (primary, mixed_u, mixed_w, depth4)
                for v in leg.values()),
            "expected_fiber_elementwise_everywhere": all(
                v["expected_fiber_elementwise"] for leg in
                (primary, mixed_u, mixed_w, depth4)
                for v in leg.values()),
            "conduit_combos_everywhere": all(
                v["conduit_combos_realized"] for leg in
                (primary, mixed_u, mixed_w, depth4)
                for v in leg.values()),
            "readings_restricted_everywhere": all(
                v["readings_differ_only_at_corner_pairs"] for leg in
                (primary, mixed_u, mixed_w, depth4)
                for v in leg.values()),
            "static_handshake_every_height": all(
                v["all_stages_ok"] for v in static.values()),
            "fence_new_depth_refused": not
                probes["depth5_chain"]["compiled"],
            "fence_and_still_refused": not
                probes["and_body_at_relay"]["compiled"],
            "fence_mixed_still_refused": not
                probes["mixed_bodies_at_relay"]["compiled"],
            "fence_second_consumer_still_refused": not
                probes["second_terminal_consumer"]["compiled"],
            "tick163_axes_now_compile": all(
                probes[k]["compiled"] for k in
                ("tick163_axis_stacked_spine_relay",
                 "tick163_axis_head_chained_relay")),
        },
    }
    return receipt


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit-receipt", action="store_true")
    args = ap.parse_args(argv)
    receipt = build_receipt()
    print(json.dumps(receipt["summary"], indent=2, sort_keys=True))
    for n, v in receipt["primary_222"].items():
        print("n=%s assemblies=%d pinned=%d law=%d fibers=%s" % (
            n, v["assemblies"], v["pinned"], v["law_total"],
            v["fiber_histogram"]))
    if args.emit_receipt:
        out_dir = os.path.join(ROOT, "evidence",
                               "2026-10-22-pc13-depth3-first-census")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "depth3.json")
        with open(path, "w") as fh:
            json.dump(receipt, fh, indent=2, sort_keys=True)
            fh.write("\n")
        with open(path, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        print("receipt:", path)
        print("sha256:", digest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
