#!/usr/bin/env python3
"""Tick 165: depth-4 FULL pinned table + the first ALL-stages-unequal
depth-3 point, extending the designs/013 nested-shell census.

Tick 164 left three open paths (designs/013 section 4): complete the
depth-4 table, census unequal multiplicities at ALL three stages, and
promote the per-body handshake to a proof sketch for general m.  This
tick executes the first two (the sketch lands as designs/013 section 5
in the same commit).

Predictions pinned BEFORE any census run this tick — computed from the
nested-shell product law (designs/013 section 2, suffix products per
shell) alone, then written here as literals:

  depth-4 [2,2,2,2] (tick-163 pins, law re-derives): the FULL table
      n=6..12:  1099/1511/2010/2606/3310/4134/5091
      (tick 164 censused only n=8..10; this tick adds 6, 7, 11, 12
      and re-runs 8..10 for one coherent receipt)

  [3,2,3] — unequal multiplicities at ALL THREE stages simultaneously
      n=6..12:  986/1348/1788/2316/2943/3681/4543
      additive falsifier: 566/804/1104/1476/1931/2481/3139
      (separated everywhere, margin >= 420 at n=6)

  depth-4 unequal singles (which stage carries the 3):
      [3,2,2,2] n=6: terminal k_w=3  -> 1323   (additive 606)
      [2,2,2,3] n=6: bottom relay k_u=3 -> 1621 (additive 733)

Fiber predictions: shell_d censuses at exactly prod_{i>=d} k_i
(suffix products); for [3,2,3] the only legal fibers are
{1, 3, 6, 18}; for [2,2,2,3] {1, 3, 6, 12, 24}; never additive sums,
never powers of two unless the product itself is one.

Same checks per height as tick 164 (P1/M1/F1/F2/N1/X1/X2 + additive
separation), statics R1/B1 at depth-4 stages, and the full fence
probe set unchanged.

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
    PINNED_2222,
    RELAYS_D3,
    RELAYS_D4,
    census_height,
    guard_probe,
    static_checks,
)

# ---- pinned BEFORE this tick's census (law-only derivation above) ----
PINNED_323 = {6: 986, 7: 1348, 8: 1788, 9: 2316,
              10: 2943, 11: 3681, 12: 4543}
PINNED_3222_6 = 1323
PINNED_2223_6 = 1621
FIBERS_323 = [1, 3, 6, 18]
FIBERS_2223 = [1, 3, 6, 12, 24]


def build_receipt():
    depth4_full = {str(n): census_height(n, [2, 2, 2, 2], RELAYS_D4,
                                         PINNED_2222[n])
                   for n in range(6, 13)}
    unequal_323 = {str(n): census_height(n, [3, 2, 3], RELAYS_D3,
                                         PINNED_323[n])
                   for n in range(6, 13)}
    d4_terminal3 = {"6": census_height(6, [3, 2, 2, 2], RELAYS_D4,
                                       PINNED_3222_6)}
    d4_bottom3 = {"6": census_height(6, [2, 2, 2, 3], RELAYS_D4,
                                     PINNED_2223_6)}
    static_d4 = {str(n): static_checks(n, [2, 2, 2, 2], RELAYS_D4)
                 for n in range(6, 13)}
    static_323 = {str(n): static_checks(n, [3, 2, 3], RELAYS_D3)
                  for n in range(6, 13)}
    probes = guard_probe()
    legs = (depth4_full, unequal_323, d4_terminal3, d4_bottom3)
    all_ = [v for leg in legs for v in leg.values()]
    receipt = {
        "kind": "pc13-depth4-full-and-unequal",
        "date": "2026-10-22",
        "card": "SON-5152 tick 165",
        "family": "PC13-D3/D4 (designs/013 section 1 fragment)",
        "pinned_before_census": "this file's module docstring "
                                "(law-only derivation, tick 165)",
        "depth4_2222_full_table": depth4_full,
        "unequal_all_stages_323": unequal_323,
        "depth4_terminal3_3222": d4_terminal3,
        "depth4_bottom3_2223": d4_bottom3,
        "static_depth4": static_d4,
        "static_323": static_323,
        "guard_probes": probes,
        "summary": {
            "depth4_full_table_all_pinned_scalars_land": all(
                v["matches_pinned"] for v in depth4_full.values()),
            "depth4_new_heights_land": all(
                depth4_full[str(n)]["matches_pinned"]
                for n in (6, 7, 11, 12)),
            "unequal_323_all_pinned_scalars_land": all(
                v["matches_pinned"] for v in unequal_323.values()),
            "depth4_unequal_singles_land": (
                d4_terminal3["6"]["matches_pinned"]
                and d4_bottom3["6"]["matches_pinned"]),
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
            "fibers_323_exactly_suffix_products": sorted(
                map(int, unequal_323["6"]["fiber_histogram"]))
            == sorted(FIBERS_323),
            "fibers_2223_exactly_suffix_products": sorted(
                map(int, d4_bottom3["6"]["fiber_histogram"]))
            == sorted(FIBERS_2223),
            "static_handshake_depth4_every_height": all(
                v["all_stages_ok"] for v in static_d4.values()),
            "static_handshake_323_every_height": all(
                v["all_stages_ok"] for v in static_323.values()),
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
    for n, v in receipt["depth4_2222_full_table"].items():
        print("D4 n=%s assemblies=%d pinned=%d" % (
            n, v["assemblies"], v["pinned"]))
    for n, v in receipt["unequal_all_stages_323"].items():
        print("[3,2,3] n=%s assemblies=%d pinned=%d fibers=%s" % (
            n, v["assemblies"], v["pinned"], v["fiber_histogram"]))
    if args.emit_receipt:
        out_dir = os.path.join(
            ROOT, "evidence", "2026-10-22-pc13-depth4-full-unequal")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "depth4_unequal.json")
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
