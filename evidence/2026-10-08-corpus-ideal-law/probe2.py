"""Tick 66 probe v2 — the corpus-wide law at the well-founded
level (SON-4861).

v1 (probe.py, same directory) FALSIFIED its own P2/P3 by
measurement: local or-support is the NORM, not the exception
(PC12-N4: 13 of 16 sites carry >= 2 minimal support sets — the
north-bond cooperative alternatives), so "presence sets == ideals
of a derived DAG" is false as stated for every corpus program,
and tick-65's table survives only because the extra local options
are pruned by reachability, not by strength.  This v2 restates the
law at the level where that pruning is native, with predictions
frozen BEFORE this v2 run (v1's receipt probe.out is kept
untouched as the falsification evidence):

  P1' (the law): for every compiling corpus program, the BFS
  presence sets equal the WELL-FOUNDED sets of the derived
  attach grammar (both directions, exact set equality).  The
  grammar is derived from the face tables alone (all four
  directions, contended neighbours pooled), never from the BFS
  result it is compared against — except the occupant map (which
  names can appear where), which is BFS-measured by construction.

  P2' (classes): every program's grammar contains or-support
  sites (v1 finding, now predicted to persist); PC7's terminal
  row carries 3-way name contention ("contended-split"), the
  other contention sites are "contended-shared".

  P3' (tick-65 specialization): for the PC12 family and
  PR13-dead, the well-founded sets equal the ideals of the
  4-column nested-height poset, so the counts are binomial:
  PC12-N4 == 70 == C(8,4), PC12-DOC == 126 == C(9,4),
  PR13-dead == 210 == C(10,4) (tick-62/65 anchors reproduce),
  PR13-dead's two dead tiles BFS-absent and all 24 box sites
  occupied somewhere.

  P4' (PC11): non-box poset, two terminals, 147 assemblies
  (tick-62 anchor); law P1' still holds; its well-founded count
  is NOT a binomial C(n+k,k) value (checked).

  Falsifier: any program where presence != well-founded in
  either direction — the face-table grammar derivation then
  misses a real BFS channel (or admits a phantom one), and the
  corpus-wide law fails; report which, never widen to pass.

Run at HEAD 1915589 + this tick's molasp/poset.py rewrite.
Output JSON-lines on stdout, saved verbatim as probe2.out.
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
    "PC10": "p. q :- z. r :- q.",
    "PC11": "p. q. s. q2 :- p. r :- q2, s. r :- q2.",
    "PC12-N4": "p. q. q2 :- p. r :- q2, q.",
    "PC12-DOC": "p. s. q. q2 :- p. r :- q2, q.",
    "PR13-dead": "p. s. q. q2 :- z. r :- q2, q.",
}


def box_ideals(n, k=4):
    """Tick-65 poset ideals: nested height vectors in a k x n box."""
    def rec(hi, remaining):
        if len(hi) == k:
            return 1
        return sum(rec(hi + [h], h)
                   for h in range(min(hi[-1] if hi else n,
                                      remaining), -1, -1))
    return rec([], n)


def probe_one(name, text):
    t0 = time.perf_counter()
    build = compile_program(text, name=name)
    seen, terminals = producible(build)
    presence = poset.presence_sets(seen)
    supports, classes, occ = poset.grammar(build, seen)
    wf = poset.well_founded_sets(supports)
    l1 = len(presence) == len(wf)
    l2a = presence <= wf      # every BFS set is well-founded
    l2b = wf <= presence      # every well-founded set is reached
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
        "well_founded": len(wf),
        "terminals": len(terminals),
        "classes": {c: sum(1 for v in classes.values() if v == c)
                    for c in sorted(set(classes.values()))},
        "contended_sites": contended,
        "L1_counts_equal": l1,
        "L2a_bfs_sets_well_founded": l2a,
        "L2b_well_founded_sets_reached": l2b,
        "law_holds": l1 and l2a and l2b,
        "dead_tiles_bfs_absent": dead_tiles,
    }
    # tick-65 specialization: box poset equality where it applies
    box_programs = {"PC12-N4": 4, "PC12-DOC": 5, "PR13-dead": 6}
    if name in box_programs:
        n = box_programs[name]
        bi = box_ideals(n)
        rec["box_ideals"] = bi
        rec["binomial_C"] = comb(n + 4, 4)
        rec["well_founded_equals_box"] = len(wf) == bi
    if name == "PC11":
        rec["is_binomial_C104"] = len(wf) == comb(10, 4)
    rec["seconds"] = round(time.perf_counter() - t0, 3)
    return rec


def main():
    records = []
    for name, (text, _model, _note) in sorted(CORPUS.items()):
        records.append(probe_one(name, text))
    for name, text in EXTRAS.items():
        records.append(probe_one(name, text))
    for rec in records:
        print(json.dumps(rec, sort_keys=True))
    summary = {
        "summary": {
            "programs": len(records),
            "law_holds_count": sum(r["law_holds"] for r in records),
            "or_support_everywhere": all(
                r["classes"].get("or-support", 0) > 0 for r in records),
            "anchors": {r["name"]: [r["assemblies"],
                                    r.get("binomial_C"),
                                    r.get("well_founded_equals_box")]
                        for r in records if r["name"] in
                        ("PC12-N4", "PC12-DOC", "PR13-dead", "PC11")},
            "not_probed": "PR9 (compiles, no pinned text in molasp/tests)",
        }
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
