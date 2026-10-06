"""Exhaustive aTAM (tau=2) check for the structural-death build —
tick 22 (SON-4773). S1 arm of the pre-registration in
ktam_mc_death.py; BFS machinery verbatim from
evidence/2026-10-06-body-conjunction-builds/atam_check_and.py.

S1 (aTAM death, deterministic):
  - exactly one terminal;
  - its lock-column decode is ("pq", 2) — rows p,q locked true, row
    3 vacant (aTAM strict decode of record: "partial");
  - DBr and L3 appear in 0 producible assemblies;
  - site (1,3) is occupied in 0 producible assemblies;
  - glues and1_r / r-t are exposed by 0 producible assemblies;
  - clingo anchors: P_AND stable {p,q,r}; `p. q.` stable {p,q}.

Falsifier: any of the above failing (a second terminal, any
producible DBr/L3, any (1,3) occupation).

Writes the JSON receipt to atam_death.out next to this file.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIBLING = os.path.join(os.path.dirname(HERE),
                       "2026-10-06-body-conjunction-builds")
for p in (HERE, SIBLING):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_death import BUILD_DEAD, PROGRAMS  # noqa: E402
from atam_check_and import (  # noqa: E402
    producible, decode, exposes_glue, clingo_models)


def main():
    report = {"build": BUILD_DEAD["name"], "checks": {}}
    ck = report["checks"]

    ck["clingo"] = {name: clingo_models(prog)
                    for name, prog in PROGRAMS.items()}

    seen, terms = producible(BUILD_DEAD)
    names_seen = set()
    site13 = 0
    for asm in seen:
        for pos, name in asm:
            names_seen.add(name)
            if pos == (1, 3):
                site13 += 1
    ck["S1"] = {
        "assemblies": len(seen),
        "terminals": len(terms),
        "terminal_decodes": [decode(BUILD_DEAD, t) for t in terms],
        "dbr_producible": "DBr" in names_seen,
        "l3_producible": "L3" in names_seen,
        "site_1_3_occupied_assemblies": site13,
        "and1_r_exposed": exposes_glue(BUILD_DEAD, seen, "and1_r"),
        "r_t_exposed": exposes_glue(BUILD_DEAD, seen, "r-t"),
        "inventory": sorted(BUILD_DEAD["tiles"]),
    }

    out = os.path.join(HERE, "atam_death.out")
    with open(out, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    print(json.dumps(report, indent=1, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
