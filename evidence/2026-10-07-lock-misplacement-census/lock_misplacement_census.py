#!/usr/bin/env python3
"""designs/006 lock-tile off-channel placement census — gates M1-M4.

Views: BUILD1 (tiles_and, family scope) and UNIT_ONLY
(compile_program v0.1) at family arithmetic and under the s2 bond
rule (tick-38 matched_s2, imported verbatim from the strength2
evidence script: any L* W read counts 2, any tile's E bond into a
placed L* counts 2).  MINIMAL ("p.") is an emit-path control.

Gates registered in designs/006-lock-misplacement-census.md BEFORE
this script's census output was produced (registration commit
precedes the receipt; instrument import-check only, no hazard data
inspected, 2026-10-07 tick 39):

  M1  fam views: >=1 L*-placement channel AND all channels bond == 1
      [falsified: any fam view empty OR any fam channel bond >= 2]
  M2  s2 views: L2@(3,3) and L3@(3,2) present with bond >= 2, AND
      every non-L squatter at the lock sites stays bond <= 1 under
      the same s2 arithmetic
      [falsified: either named channel missing/<2, OR any non-L
      lock-site squatter >= 2]
  M3  all views: every layer channel appears in that view's bond
      table (off_channel at fam; matched_s2 table at s2) with the
      identical total — classification, not channels
      [falsified: any mismatch]
  M4  compile arms UNIT_ONLY + MINIMAL: auto-attached build["d4"]
      carries lock_misplacements equal to check_d4's
      [falsified: missing or differing on any arm]

Output: one JSON line per view + one VERDICTS line. Exit 0 always —
the census reports; gates are recorded, not gating (d4 semantics).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SIB_AND = os.path.join(os.path.dirname(HERE),
                       "2026-10-06-body-conjunction-builds")
SIB_S2 = os.path.join(os.path.dirname(HERE), "2026-10-07-strength2-lock")
for p in (HERE, REPO, SIB_AND, SIB_S2):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_and import BUILD1                          # noqa: E402
from ktam_strength2 import matched_s2                 # noqa: E402
from molasp.compiler import compile_program           # noqa: E402
from molasp.offchannel import (canonical_assembly,    # noqa: E402
                               check_d4,
                               infer_lock_sites,
                               lock_misplacements,
                               matched_strength,
                               skey)

UNIT_ONLY = "p. q. r :- p."
MINIMAL = "p."


def s2_off_channel(build, canon):
    """The who-can-squat-where table under the tick-38 s2 bond rule."""
    table = {}
    for site in sorted(canon):
        squatters = {}
        for tile in sorted(build["tiles"]):
            if tile == canon[site]:
                continue
            b = matched_s2(build, canon, site, tile)
            if b >= 1:
                squatters[tile] = b
        if squatters:
            table[skey(site)] = squatters
    return table


def view(build, name, s2=False):
    canon = canonical_assembly(build)
    locks = {skey(s) for s in infer_lock_sites(canon)}
    rep = check_d4(build)
    fam_layer = rep["lock_misplacements"]
    if s2:
        layer = lock_misplacements(build, canon, bond_fn=matched_s2)
        bond_table = s2_off_channel(build, canon)
    else:
        layer = fam_layer
        bond_table = rep["off_channel"]
    named = {}
    for site, tile in (("3,3", "L2"), ("3,2", "L3")):
        ch = layer.get(site, {}).get(tile)
        named[f"{tile}@{site}"] = ch["bond"] if ch else None
    nonl_lock_max = 0
    for site in locks:
        for tile in sorted(build["tiles"]):
            if tile == canon[tuple(int(v) for v in site.split(","))] \
                    or tile.startswith("L"):
                continue
            b = (matched_s2(build, canon,
                            tuple(int(v) for v in site.split(",")), tile)
                 if s2 else
                 matched_strength(build, canon,
                                 tuple(int(v) for v in site.split(",")),
                                 tile))
            nonl_lock_max = max(nonl_lock_max, b)
    rec = {
        "view": name,
        "s2": s2,
        "n_channels": sum(len(v) for v in layer.values()),
        "max_bond": max((ch["bond"] for v in layer.values()
                         for ch in v.values()), default=0),
        "all_bond_1": all(ch["bond"] == 1 for v in layer.values()
                          for ch in v.values()),
        "named": named,
        "w_read_channels": sorted(
            f"{t}@{s}" for s, v in layer.items()
            for t, ch in v.items() if ch["w_read"]),
        "nonl_lock_site_max_bond": nonl_lock_max,
        "lock_misplacements": layer,
        "m3_mismatches": [
            f"{t}@{s}: layer {ch['bond']} vs table "
            f"{bond_table.get(s, {}).get(t)}"
            for s, v in layer.items() for t, ch in v.items()
            if bond_table.get(s, {}).get(t) != ch["bond"]],
    }
    return rec, rep


def main():
    lines, per_view = [], {}

    unit = compile_program(UNIT_ONLY, name="UNIT_ONLY")
    mini = compile_program(MINIMAL, name="MINIMAL")

    # M4 emit-path: the auto-attached d4 carries the layer and
    # equals check_d4's (instrument invariant; loud on failure).
    for arm, b in (("UNIT_ONLY", unit), ("MINIMAL", mini)):
        assert "lock_misplacements" in b["d4"], \
            f"{arm}: auto-attached d4 lacks lock_misplacements"
        assert json.dumps(b["d4"], sort_keys=True) == \
            json.dumps(check_d4(b), sort_keys=True), arm

    for build, name in ((BUILD1, "BUILD1"), (unit, "UNIT_ONLY")):
        for s2 in (False, True):
            rec, _ = view(build, f"{name}_{'s2' if s2 else 'fam'}", s2=s2)
            per_view[rec["view"]] = rec
            lines.append(json.dumps(rec, sort_keys=True))
            print(json.dumps(rec, sort_keys=True))

    m1 = (per_view["BUILD1_fam"]["n_channels"] >= 1
          and per_view["UNIT_ONLY_fam"]["n_channels"] >= 1
          and per_view["BUILD1_fam"]["all_bond_1"]
          and per_view["UNIT_ONLY_fam"]["all_bond_1"])
    m2 = all(
        (per_view[f"{a}_s2"]["named"]["L2@3,3"] or 0) >= 2
        and (per_view[f"{a}_s2"]["named"]["L3@3,2"] or 0) >= 2
        and per_view[f"{a}_s2"]["nonl_lock_site_max_bond"] <= 1
        for a in ("BUILD1", "UNIT_ONLY"))
    m3 = all(v["m3_mismatches"] == [] for v in per_view.values())
    m4 = ("lock_misplacements" in unit["d4"]
          and "lock_misplacements" in mini["d4"])
    verdicts = {"M1": m1, "M2": m2, "M3": m3, "M4": m4}
    vline = "VERDICTS " + json.dumps(verdicts, sort_keys=True)
    print(vline)
    lines.append(vline)

    out_path = os.path.join(HERE, "lock_misplacement_census.out")
    with open(out_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
