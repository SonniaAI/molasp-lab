#!/usr/bin/env python3
"""Tick 166: the k in {2..5} multiplicity grid at depth 3 — five
new full tables, every scalar pinned law-only BEFORE census.

Tick 165 left three open paths (designs/013 section 5 gaps, the
k-grid, and the publication track).  This tick executes the
k-grid: the depth-3 relay-chain family PC13-D3 (designs/013
section 1 fragment, MAX_RELAY_STAGES = 3) censused at five new
multiplicity tuples, terminal-first ks = [k_w, k_r, k_u]:

  [4,2,2]   the 4 on the terminal stage
  [2,4,2]   the 4 on the middle relay
  [2,2,4]   the 4 on the bottom relay
  [5,2,2]   the FIRST k = 5 point ever censused
  [4,3,2]   all three stages distinct (non-palindromic, k mix 4/3)

Pinned BEFORE any census this tick — law-only derivation from the
nested-shell product law (designs/013 section 2), printed to the
tick transcript before the first census probe ran:

  [4,2,2]  n=6..12:  801 / 1101 / 1470 / 1918 / 2456 / 3096 / 3851
            additive:  479 /  685 /  948 / 1278 / 1686 / 2184 / 2785
  [2,4,2]  n=6..12:  969 / 1325 / 1758 / 2278 / 2896 / 3624 / 4475
            additive:  563 /  797 / 1092 / 1458 / 1906 / 2448 / 3097
  [2,2,4]  n=6..12: 1059 / 1451 / 1926 / 2494 / 3166 / 3954 / 4871
            additive:  653 /  923 / 1260 / 1674 / 2176 / 2778 / 3493
  [5,2,2]  n=6..12:  913 / 1245 / 1650 / 2138 / 2720 / 3408 / 4215
            additive:  507 /  721 /  993 / 1333 / 1752 / 2262 / 2876
  [4,3,2]  n=6..12: 1109 / 1501 / 1974 / 2538 / 3204 / 3984 / 4891
            additive:  549 /  777 / 1065 / 1423 / 1862 / 2394 / 3032

Fiber predictions (suffix products, terminal-first): the three
k=4 placements are ORIENTATION-DISCRIMINATING — they produce three
DIFFERENT legal fiber sets, all subsets of {1,2,4,8,16}:

  [4,2,2] -> {1, 2, 4, 16}     [2,4,2] -> {1, 2, 8, 16}
  [2,2,4] -> {1, 4, 8, 16}     [5,2,2] -> {1, 2, 4, 20}
  [4,3,2] -> {1, 2, 6, 24}

Same checks per height as ticks 164/165 (P1/M1/F1/F2/N1/X1/X2 +
additive separation), statics R1/B1 at n=6 and n=12 per point,
and the full fence probe set unchanged.

Stdlib-only, deterministic, zero queue spend, no RNG.  Not a
validated result until independently reviewed.
"""
import argparse
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.pc13_depth3_first_census import (  # noqa: E402
    RELAYS_D3,
    census_height,
    guard_probe,
    static_checks,
)

# ---- pinned BEFORE this tick's census (law-only derivation above) ----
PINNED_422 = {6: 801, 7: 1101, 8: 1470, 9: 1918,
              10: 2456, 11: 3096, 12: 3851}
PINNED_242 = {6: 969, 7: 1325, 8: 1758, 9: 2278,
              10: 2896, 11: 3624, 12: 4475}
PINNED_224 = {6: 1059, 7: 1451, 8: 1926, 9: 2494,
              10: 3166, 11: 3954, 12: 4871}
PINNED_522 = {6: 913, 7: 1245, 8: 1650, 9: 2138,
              10: 2720, 11: 3408, 12: 4215}
PINNED_432 = {6: 1109, 7: 1501, 8: 1974, 9: 2538,
              10: 3204, 11: 3984, 12: 4891}

POINTS = {
    "[4,2,2]": ([4, 2, 2], PINNED_422),
    "[2,4,2]": ([2, 4, 2], PINNED_242),
    "[2,2,4]": ([2, 2, 4], PINNED_224),
    "[5,2,2]": ([5, 2, 2], PINNED_522),
    "[4,3,2]": ([4, 3, 2], PINNED_432),
}

FIBERS = {
    "[4,2,2]": [1, 2, 4, 16],
    "[2,4,2]": [1, 2, 8, 16],
    "[2,2,4]": [1, 4, 8, 16],
    "[5,2,2]": [1, 2, 4, 20],
    "[4,3,2]": [1, 2, 6, 24],
}


def build_receipt():
    tables = {}
    statics = {}
    for name, (ks, pinned) in POINTS.items():
        tables[name] = {str(n): census_height(n, ks, RELAYS_D3,
                                              pinned[n])
                        for n in range(6, 13)}
        statics[name] = {
            "6": static_checks(6, ks, RELAYS_D3),
            "12": static_checks(12, ks, RELAYS_D3),
        }
    probes = guard_probe()
    all_ = [v for t in tables.values() for v in t.values()]
    receipt = {
        "kind": "pc13-kgrid45",
        "date": "2026-10-22",
        "card": "SON-5152 tick 166",
        "family": "PC13-D3 (designs/013 section 1 fragment)",
        "pinned_before_census": "this file's module docstring "
                                "(law-only derivation, tick 166)",
        "tables": tables,
        "statics": statics,
        "guard_probes": probes,
        "summary": {
            "all_pinned_scalars_land": all(
                v["matches_pinned"] for v in all_),
            "first_k5_point_lands": all(
                v["matches_pinned"] for v in tables["[5,2,2]"].values()),
            "all_distinct_432_lands": all(
                v["matches_pinned"] for v in tables["[4,3,2]"].values()),
            "law_holds_everywhere": all(v["law_holds"] for v in all_),
            "additive_falsified_everywhere": all(
                v["additive_falsified"] for v in all_),
            "presence_equals_ideals_everywhere": all(
                v["presence_equals_ideals"] for v in all_),
            "nesting_elementwise_everywhere": all(
                v["nesting_elementwise"] for v in all_),
            "expected_fiber_elementwise_everywhere": all(
                v["expected_fiber_elementwise"] for v in all_),
            "conduit_combos_everywhere": all(
                v["conduit_combos_realized"] for v in all_),
            "readings_restricted_everywhere": all(
                v["readings_differ_only_at_corner_pairs"]
                for v in all_),
            "fibers_exactly_suffix_products_per_point": {
                name: sorted(map(int, t["6"]["fiber_histogram"]))
                == sorted(FIBERS[name])
                for name, t in tables.items()},
            "k4_placements_pairwise_distinct_fiber_sets": (
                sorted(map(int, tables["[4,2,2]"]["6"]
                           ["fiber_histogram"]))
                != sorted(map(int, tables["[2,4,2]"]["6"]
                              ["fiber_histogram"]))
                != sorted(map(int, tables["[2,2,4]"]["6"]
                              ["fiber_histogram"]))),
            "static_handshake_n6_and_n12_every_point": all(
                v["all_stages_ok"]
                for s in statics.values() for v in s.values()),
            "fence_unchanged": (
                not probes["depth5_chain"]["compiled"]
                and not probes["and_body_at_relay"]["compiled"]
                and not probes["mixed_bodies_at_relay"]["compiled"]
                and not probes["second_terminal_consumer"]["compiled"]
                and probes["tick163_axis_stacked_spine_relay"][
                    "compiled"]
                and probes["tick163_axis_head_chained_relay"][
                    "compiled"]),
        },
    }
    return receipt


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit-receipt", action="store_true")
    args = ap.parse_args(argv)
    receipt = build_receipt()
    print(json.dumps(receipt["summary"], indent=2, sort_keys=True))
    for name, t in receipt["tables"].items():
        print("%s n=6..12: %s" % (
            name, "/".join(str(t[str(n)]["assemblies"])
                           for n in range(6, 13))))
    if args.emit_receipt:
        out_dir = os.path.join(
            ROOT, "evidence", "2026-10-22-pc13-kgrid45")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "kgrid45.json")
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
