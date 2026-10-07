# 2026-10-07 — OR-AND parity corpus for compiler v0.1

Tick 46 · SON-4819 · static compute-only work (tick-37 rule: no
cluster job; the whole corpus runs in 0.03 s).

## What this tick did

Turned compiler v0.1's verification from "parity with the three
hand-built tick-20 builds" (P1–P3) into a systematic corpus:
`molasp/parity.py` compiles **8 program shapes** spanning every
admitted fragment axis and BFS-verifies each on the full 4×n grid,
plus **6 refusal shapes** that must refuse loudly.

The parity claim, per corpus program: *every terminal assembly of
the compiled tile system decodes exactly the program's least
model*, all rows fully locked, and every dead variant's reader
glue is absent from every producible assembly.

## Corpus results (all pinned, receipt `run.out`)

| name | shape | n | tiles | assemblies | terminals | decode |
| --- | --- | --- | --- | --- | --- | --- |
| PC1 | unit-only OR, smallest shape | 2 | 8 | 15 | 1 | {p,r} |
| PC2 | AND+unit (BUILD1 program, corpus path) | 3 | 14 | 45 | 2 | {p,q,r} |
| PC3 | dead AND over false q (BUILD2 program) | 3 | 14 | 35 | 1 | {p,r} |
| PC4 | both rules dead, false terminal (BUILD3 program) | 3 | 12 | 35 | 1 | {q} |
| PC5 | AND over (row-3 fact, row-1 via) | 4 | 16 | 70 | 1 | {p,q,s,r} |
| PC6 | duplicate-AND OR pair | 4 | 18 | 85 | 2 | {p,q,s,r} |
| PC7 | three-way terminal contention (2 unit + 1 AND) | 4 | 20 | 100 | 3 | {p,q,s,r} |
| PC8 | AND+unit at n=4 | 4 | 18 | 85 | 2 | {p,q,s,r} |

PC5–PC8 are the **first exhaustive 4-row BFS** in the programme —
the BUILD1 shape generalizes past n=3 with middle facts, and PC7's
three-way V-column contention still resolves semantically (three
terminals, one decode).

Dead-channel pins: PC3 `and1_r` absent from all 35 assemblies;
PC4 `and1_r` + `unit1_r` both absent (both rules dead, r's false
terminal caps with `rf-relay`).

Refusals (PR1–PR6): non-adjacent AND hi, fact-true terminal row,
rule atom below the terminal row, non-via-carried unit literal,
body width 3, and the wrong-compile d3-support arm (needs the
caller override — the least model alone is correctly smaller; the
refusal fires on the *wrong-compile prediction*, which is the
semantically meaningful place).

## Honest boundaries

1. The corpus covers single-derived-atom programs only — the
   fragment v0.1 admits (U3 still refuses multi-derived chains).
2. n caps at 4 (PC5–PC8); no 5-row geometry has been BFS-checked.
3. Exhaustive BFS cost grows with tiles×sites; at 20 tiles/16
   sites it is still 0.00 s, but the scaling claim is only
   measured, not analyzed, through n=4.
4. PC2–PC4 re-verify the tick-20 programs through the corpus path
   (independent machinery), not new shapes.

## Receipt

| Claim | Evidence |
| --- | --- |
| corpus verdicts | `evidence/2026-10-07-parity-corpus/run.out` (JSON block, `all_ok: true`) |
| receipt pins | `tests/test_parity_corpus.py::TestReceiptPins` (R0–R5) |
| BFS recomputation | `TestBFSRecompute` (B1–B3: PC1/PC3/PC4 from scratch) |
| suite | verbatim `Ran 374 tests in 0.747s` / `OK (skipped=1)` = 365 + 9 |

## Next

Queue from tick 44 stands: (1) dG-2 window arm + L3-at-vacancy
follow-up (kinetic, needs cluster queue) if promoted from boundary
note; (2) founder-gated collaborator/venue shortlist (no founder
yes yet); (4-done) parity corpus — candidate successor: widen the
corpus to two derived atoms once a multi-row-chain design exists
(designs/003 honest limit), or n=5 geometry if a 5-row build is
ever hand-pinned.
