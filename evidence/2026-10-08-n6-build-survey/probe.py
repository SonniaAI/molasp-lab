#!/usr/bin/env python3
"""Tick-64 probe (SON-4856): n>=6 build survey after the stage-7
spine class closure (designs/010, tick 62).

Question: tick 62 removed the SP-table cap and measured full locks
at n=5 (PC12-DOC (5, 20, 126, 1), decode == the FULL least model
{p,q,q2,r,s} — first n=5 build with full locks, "no second hidden
cap" claimed at n=5 only).  Does that claim survive n=6..9, or is
there a second hidden cap (spine or otherwise) past row 5?

Family: PC12-DOC extended with decorative facts between s and q.
Each decorative fact adds one row; no rule reads them, so the
AND-over-derived geometry (r reads q2 at i-1, q at i-2) and the
unit via read (q2 reads p at row 1) both keep their shape while the
via distance grows with n:

    n=5: p. s. q. q2 :- p. r :- q2, q.        (tick-62 measured)
    n=6: p. s. t. q. q2 :- p. r :- q2, q.
    n=7: p. s. t. u. q. q2 :- p. r :- q2, q.
    n=8: p. s. t. u. v. q. q2 :- p. r :- q2, q.
    n=9: p. s. t. u. v. w. q. q2 :- p. r :- q2, q.

Pre-registered predictions (written before running anything, tick 64):
  P1 rows == n and tiles == 4n (measured: 4->16, 5->20).
  P2 assemblies strictly monotone in n (70, 126, then growth); no
     collapse back to an (n-1)-shaped count.
  P3 terminals == 1 (unique terminal) for every n.
  P4 full_locks TRUE for every n: the class closure (same-name spine
     self-bond = 2 for every SPi >= 1) leaves no table edge behind.
  P5 terminal decode == the full least model (all facts + q2 + r).
  P6 no refusal: the unit via read of p (row 1 -> row n-1)
     generalizes with distance.  If a distance cap fires instead,
     the loud refusal is a FINDING (an ordering-based second cap),
     not a probe failure — record it, do not widen the compiler.
Falsifier for the tick-62 closure claim: any n>=6 build with
full_locks FALSE, a prefix decode, or an assembly count equal to
the n-1 build's.

Receipt: stdout saved verbatim as probe.out; one JSON record per
line; the first line carries the git HEAD for provenance.  n=5 is
re-measured first as a self-calibration anchor: it must reproduce
(5, 20, 126, 1) or the probe itself is broken and nothing below it
counts.

Run from the repo root: python3 evidence/2026-10-08-n6-build-survey/probe.py
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.getcwd())
from molasp.compiler import least_model, parse_program  # noqa: E402
from molasp.parity import check_program  # noqa: E402

PROGRAMS = [
    (5, "p. s. q. q2 :- p. r :- q2, q."),
    (6, "p. s. t. q. q2 :- p. r :- q2, q."),
    (7, "p. s. t. u. q. q2 :- p. r :- q2, q."),
    (8, "p. s. t. u. v. q. q2 :- p. r :- q2, q."),
    (9, "p. s. t. u. v. w. q. q2 :- p. r :- q2, q."),
]

head = subprocess.check_output(
    ["git", "rev-parse", "HEAD"]).decode().strip()
print(json.dumps({"probe": "n6-build-survey", "tick": 64, "head": head}))

for n, prog in PROGRAMS:
    facts, derived, _order = parse_program(prog)
    model = sorted(least_model(facts, derived))
    rec = {"n": n, "program": prog, "least_model": model}
    t0 = time.time()
    try:
        v = check_program("PC12docN%d" % n, prog, set(model))
        rec.update({"n_rows": v["n_rows"], "tiles": v["tiles"],
                    "assemblies": v["assemblies"],
                    "terminals": v["terminals"],
                    "full_locks": v["full_locks"], "ok": v["ok"],
                    "terminal_decodes": v["terminal_decodes"]})
    except Exception as exc:  # loud refusal is a finding (P6)
        rec.update({"refused": str(exc),
                    "refusal_type": type(exc).__name__})
    rec["seconds"] = round(time.time() - t0, 3)
    print(json.dumps(rec, sort_keys=True))
