#!/usr/bin/env python3
"""Tick-65 probe (SON-4859): derive the C(n+4,4) assembly count
for the decorative-fact family — or find where it breaks.

Tick 64 measured assemblies == C(n+4,4) at n=4..9 and called it an
"empirical closed form (observation, not a theorem)".  Static
analysis of the face tables (this tick, before any BFS run) says
the family's attach grammar is a four-column poset:

  (0,i) spine S_i      : S=SPi vs below N (seed SP1 at i=1) -> 2
                         alone; attaches on the tile below ONLY.
  (1,i) D_iT/Cq2/DAr   : below (1) + west go_i from spine (1).
  (2,i) V0p/V*/Uq2/DBr : below (1) + west (1); east (1) also
                         exists locally but east requires (3,i),
                         which requires (2,i) — pruned by
                         reachability, not by local strength.
  (3,i) L_i            : below base-chain (1) + west (1).

with glue_strength = {SPi/SPi: 2, other matched: 1, mismatched: 0}
(compiler.py:81, class closure designs/010 §10.3) and TAU = 2.
Ideals of that poset are column heights n >= h0 >= h1 >= h2 >= h3
>= 0 — partitions inside a 4 x n box — classically counted by
C(n+4,4) (stars-and-bars / lattice paths on the box border).

Pre-registered predictions (frozen before running anything):
  D1  len(seen) == C(n+4,4) at n=4..12 (extends tick 64 by 10-12).
  D2  assemblies biject with shapes: across ALL seen assemblies,
      every site is occupied by exactly ONE tile name (no variant
      or cross-site fill).
  D3  every reachable shape IS an ideal: columns contiguous from
      row 1 and h0 >= h1 >= h2 >= h3.
  D4  every ideal is realized: the set of reached shapes EQUALS
      the set of all 4-tuples n >= h0 >= ... >= h3 >= 0.
  D5  no empty moves at non-terminal shapes is assumed; the BFS
      itself is the oracle (any non-ideal locally-attachable shape
      would surface as a D3/D4 violation — the set equality is
      the complete check, in both directions).
Falsifier: any D1-D4 failure at any n in 4..12.  A failure of D3
with D1 intact would mean the binomial fit is a coincidence at the
measured points; a failure of D4 means ideals overcount; a D2
failure means tile identity, not shape, carries the count.

Receipt: stdout saved verbatim as probe.out; one JSON record per
line; first line carries git HEAD.  n=4..9 re-measured first as
self-calibration against tick 64's pinned values (must reproduce
70/126/210/330/495/715 exactly or the probe is broken and nothing
below it counts).

Run from the repo root:
  python3 evidence/2026-10-08-binomial-derivation/probe.py
"""
import json
import math
import os
import subprocess
import sys
import time

sys.path.insert(0, os.getcwd())
from molasp.compiler import compile_program, least_model, parse_program  # noqa: E402
from molasp.parity import producible  # noqa: E402

TICK64 = {4: 70, 5: 126, 6: 210, 7: 330, 8: 495, 9: 715}
ANCHOR_N4 = "p. q. q2 :- p. r :- q2, q."  # PC12-N4, ticks 55/62
DECOR = "tuvwxyz"  # n>=5: first n-5 letters go between s and q


def program_for(n):
    if n == 4:
        return ANCHOR_N4
    decor = " ".join(a + "." for a in DECOR[:n - 5])
    if decor:
        decor += " "
    return "p. s. %sq. q2 :- p. r :- q2, q." % decor


def _sites(h):
    return frozenset((x, y) for x in range(4) for y in range(1, h[x] + 1))


head = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
print(json.dumps({"probe": "binomial-derivation", "tick": 65, "head": head}))

for n in range(4, 13):
    prog = program_for(n)
    facts, derived, _ = parse_program(prog)
    model = set(least_model(facts, derived))
    t0 = time.time()
    build = compile_program(prog, name="PC12docN%d" % n, predicted=model)
    seen, terminals = producible(build)
    rec = {"n": n, "program": prog, "tiles": len(build["tiles"]),
           "assemblies": len(seen), "terminals": len(terminals),
           "binom_C(n+4,4)": math.comb(n + 4, 4),
           "D1_binomial": len(seen) == math.comb(n + 4, 4)}
    if n in TICK64:
        rec["tick64_anchor"] = TICK64[n]
        rec["anchor_reproduced"] = len(seen) == TICK64[n]
        if n == 4:
            rec["anchor_program"] = "PC12-N4"
    # D2: bijectivity of tile identity per site (frozen assemblies
    # are frozensets of ((x, y), tile) pairs)
    site_tiles = {}
    for asm in seen:
        for (x, y), tile in asm:
            if y >= 1:
                site_tiles.setdefault((x, y), set()).add(tile)
    rec["D2_site_tile_bijective"] = all(
        len(v) == 1 for v in site_tiles.values())
    rec["D2_sites_filled"] = len(site_tiles)
    # D3/D4: shapes vs ideals
    shapes = {frozenset((x, y) for (x, y), _t in asm if y >= 1)
              for asm in seen}
    ideal_set = {frozenset(_sites((h0, h1, h2, h3)))
                 for h0 in range(n + 1) for h1 in range(h0 + 1)
                 for h2 in range(h1 + 1) for h3 in range(h2 + 1)}
    rec["D3_all_shapes_ideals"] = shapes <= ideal_set
    rec["D4_all_ideals_reached"] = ideal_set <= shapes
    rec["shape_count"] = len(shapes)
    rec["ideal_count"] = len(ideal_set)
    rec["seconds"] = round(time.time() - t0, 3)
    print(json.dumps(rec, sort_keys=True))
