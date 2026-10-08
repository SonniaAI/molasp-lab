"""Tick 66 probe — the corpus-wide ideal law (SON-4861).

Run at HEAD 1915589 (tick 65).  Predictions frozen in this
docstring BEFORE any execution; output is JSON-lines on stdout,
saved verbatim as probe.out in this directory.

Programs: every compiling corpus program at HEAD — CORPUS PC1..PC9
plus the five compiling shapes outside CORPUS with standing pins
(PC10, PC11, PC12-N4, PC12-DOC n=5, PR13-dead).  PR9 also compiles
(stage-6 pins) but has no pinned program text in molasp/tests; it
is the one compiling shape NOT probed here (noted, not hidden).

  P1 (occupancy): every occupied site carries exactly one tile
  name, except PC7's designed terminal-row V-slot contention; its
  contended names share ONE minimal support set
  ("contended-shared", never "contended-split").

  P2 (grammar): every occupied site in every program has exactly
  one minimal support set (class "and"; contended sites
  "contended-shared").  Any "or-support" or "support-varies" or
  "contended-split" site is a named finding, and P3 is NOT claimed
  for that program.

  P3 (the law): for every program with all sites "and"/
  "contended-shared", BFS presence sets == ideals of the
  requirement DAG, both directions: D3 every presence set is
  downward-closed, D4 every ideal is reached, D1 counts equal.
  This extends tick-65's decorative-family derivation to the whole
  compiling corpus.

  P4 (anchors reproduce): PC12-N4 assemblies == 70 == C(8,4);
  PC12-DOC == 126 == C(9,4); PR13-dead == 210 == C(10,4), with its
  dead tiles BFS-absent and all 24 sites of the 4x6 box occupied.

  P5 (PC11, not a box): two terminals, non-box poset; its ideal
  count is whatever the DAG gives — tick-62 anchor 147 assemblies —
  and the law P3 still holds for it.

Falsifier: any "and"-class program whose presence sets differ from
its ideals in either direction (D3 or D4 or D1 fails) — then the
poset argument does NOT extend corpus-wide and tick-65's law stays
family-local.  A finding either way; nothing is widened to pass.
"""
import json
import sys
import time
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from molasp.compiler import compile_program          # noqa: E402
from molasp.parity import CORPUS, producible         # noqa: E402
from molasp import poset                             # noqa: E402

EXTRAS = {
    "PC10": ("p. q :- z. r :- q.", {"p"}),
    "PC11": ("p. q. s. q2 :- p. r :- q2, s. r :- q2.",
             {"p", "q", "s", "q2", "r"}),
    "PC12-N4": ("p. q. q2 :- p. r :- q2, q.", {"p", "q", "q2", "r"}),
    "PC12-DOC": ("p. s. q. q2 :- p. r :- q2, q.",
                 {"p", "q", "s", "q2", "r"}),
    "PR13-dead": ("p. s. q. q2 :- z. r :- q2, q.", {"p", "q", "s"}),
}

LAW_CLASSES = {"and", "contended-shared"}


def probe_one(name, text):
    t0 = time.perf_counter()
    build = compile_program(text, name=name)
    seen, terminals = producible(build)
    presence = poset.presence_sets(seen)
    dag, classes, occ = poset.requirement_dag(build, seen)
    ideals = poset.ideals_of(dag)
    d3, d3_site = poset.downward_closed(presence, dag)
    d4 = ideals <= presence
    d1 = len(presence) == len(ideals)
    law_scope = set(classes.values()) <= LAW_CLASSES
    placed = {n for asm in seen for _p, n in asm if _p[1] >= 1}
    dead_tiles = sorted(set(build["tiles"]) - placed)
    contended = {f"{x},{y}": sorted(occ[s])
                 for s, names in occ.items() if len(names) > 1
                 for x, y in [s]}
    rec = {
        "name": name,
        "rows": len(build["rows"]),
        "tiles": len(build["tiles"]),
        "occupied_sites": len(occ),
        "assemblies": len(seen),
        "presence_sets": len(presence),
        "ideals": len(ideals),
        "terminals": len(terminals),
        "classes": {c: sum(1 for v in classes.values() if v == c)
                    for c in sorted(set(classes.values()))},
        "contended_sites": contended,
        "D1_count_equal": d1,
        "D3_downward_closed": d3,
        "D3_violation_site": (f"{d3_site[0]},{d3_site[1]}"
                              if d3_site else None),
        "D4_all_ideals_reached": d4,
        "law_in_scope": law_scope,
        "law_holds": law_scope and d1 and d3 and d4,
        "dead_tiles_bfs_absent": dead_tiles,
    }
    rec["seconds"] = round(time.perf_counter() - t0, 3)
    return rec


def main():
    records = []
    for name, (text, _model, _note) in sorted(CORPUS.items()):
        records.append(probe_one(name, text))
    for name, (text, _model) in EXTRAS.items():
        records.append(probe_one(name, text))
    for rec in records:
        print(json.dumps(rec, sort_keys=True))
    summary = {
        "summary": {
            "programs": len(records),
            "law_holds_count": sum(r["law_holds"] for r in records),
            "law_in_scope_count": sum(r["law_in_scope"] for r in records),
            "findings_classes": sorted(
                {c for r in records for c in r["classes"]
                 if c not in LAW_CLASSES}),
            "anchor_PC12N4_C84": [next(r["assemblies"] for r in records
                                       if r["name"] == "PC12-N4"), comb(8, 4)],
            "anchor_PC12DOC_C94": [next(r["assemblies"] for r in records
                                        if r["name"] == "PC12-DOC"), comb(9, 4)],
            "anchor_PR13dead_C104": [next(r["assemblies"] for r in records
                                          if r["name"] == "PR13-dead"),
                                     comb(10, 4)],
            "not_probed": "PR9 (compiles, no pinned text in molasp/tests)",
        }
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
