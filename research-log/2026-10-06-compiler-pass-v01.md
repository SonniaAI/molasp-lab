# Compiler pass v0.1 — program text to tile inventory (tick 21, 2026-10-06)

Card: SON-4765. Code: `molasp/compiler.py`. Tests:
`../tests/test_compiler_v01.py` (15 new; suite 148/148 under
`python3 -m unittest discover -s tests`).

## Question

Tick 20 closed with: "with d2 + d3 + the tick-14 order acceptance
test, the compiler-pass prototype now has all its acceptance tests —
the pass itself is unbuilt." This tick builds it.

## What was built

`molasp/compiler.py` compiles a ground positive ASP program in the
machine-checked fragment (facts + rules, bodies of width ≤ 2) to a
build dict in the exact `tiles_orand` BUILDS shape — the existing
aTAM BFS checkers consume compiler output unchanged. The pass:

1. parses `a.` / `h :- l1, l2.` and computes the least model (the
   stable model of a positive program) as the predicted-true set,
   with an override parameter for wrong-compile arms;
2. lays out rows topologically (every body literal strictly below
   its head, first-appearance tie-break) — the tick-14 order
   falsifier discipline as an emit-time gate;
3. emits the pinned tick-20 policy mechanically: rule-local reader
   variants (dead variants EMITTED with true-typed reads, killed by
   value typing), conduit + V-column reader for unit variants,
   slot-A/slot-B readers for conjunctive variants, false rows typed
   by the row-below predicted value, via relay of the row-1 witness,
   spine/lock/seed chains;
4. enforces d2 (emitted variant reads == rule body) and d3
   (compile-model closure/support) as fatal static emit-time checks.

## Acceptance results

- **Structural parity, P1–P3**: compiled P_OA / P_OA−q / P_OA−p are
  structurally identical to the BFS-machine-checked BUILD1/2/3 of
  tick 20 (same rows, seed, per-row face-glue multisets; 14/14/12
  tile types). Assembly behaviour depends only on those fields, so
  parity with a verified build is parity of verdicts — G1–G3 and
  d1–d3 carry over to compiler output.
- **d3 fires on the tick-20 wrong compile**: feeding W2's solver
  model {p} for P_OA−q is refused at emit time (rule `r :- p` live
  under the model's own prediction). Two more refusal arms: d3
  support (underivable predicted-true atom), d3 completeness
  (omitted fact).
- **Row order**: P_OA−p compiles rows q < p < r — topological,
  first-appearance tie-break.
- **Untested geometry is refused, not guessed**: b ≥ 3 bodies,
  non-via-carried unit literals, rule atoms at non-terminal rows
  (multi-derived-row chains) raise `UnsupportedGeometry`.

## What it establishes

The first automated program→tile-set emission in the lab. For the
covered fragment, the hand constructions of designs/002–003 and the
tick-20 composition are now the OUTPUT of a pass whose emit-time
checks subsume the wrong-compile certificates — the compiler cannot
emit W2-class errors without d3 firing first.

## Honest limits

- Parity is with the OR-AND corpus (3 rows, ≤ 2 rule variants, one
  derived atom). designs/001–002 geometries (direct-below unit
  readers, 2-cycle/anchored-cycle shapes) are not yet parity
  targets; wider bodies and multi-derived-row chains are refused,
  not supported.
- Structural parity transfers BFS verdicts; no fresh kTAM evidence
  was produced this tick (the kTAM grid on these builds remains
  queued behind the structural-death reassertion build).
- The pass emits tile inventories only — no seed-surgery arms, no
  BFS run inside the compiler (callers use the existing checkers).

## Tooling notes

The parity tests caught two real emission bugs before landing:
variant glue numbering must be per-kind (`and1_r` / `unit1_r`), not
per-rule-index; and the via-relay tile name needed a row prefix
once 4-row programs stopped colliding with the corpus shape. Zero
science bugs — the emission rules transcribed from tick 20 held.
