# 2026-10-07 — Designs/008 stage 3: terminal dead-reader emission (PC4 basis move)

Tick 50 (SON-4828, run 16011e56). Scope: the boundary deferred by
stage 2 (research-log 2026-10-07-chain-dead-reader-emission.md):
"terminal false heads keep the v0.1 F-cap basis; their dead-reader
emission is deferred (moving PC4's basis is its own tick)" — this is
that tick.

## What changed

**molasp/compiler.py** — a terminal predicted-false derived row with
rule support now emits its dead reader(s) per unit body, alongside
the plain false row (which stays the false-cap relay, stages 1-2
untouched). Same tile shape as stage 2:
`UD{i}{a}` = W `unit{j}_{a}` (the vj conduit glue the false basis
never emits), S `{lit}-t-done` (truth-typed done of the body
literal), E `{a}-t`, N `{a}-t-done`. AND bodies stay deferred
(stage-2 boundary, unexercised in the corpus).

## Why the argument is the same at the terminal row

Least-model support kills every body of a predicted-false head (if
any unit body's literal were true, the head would be predicted
true). So the reader's S glue is emitted nowhere (false literals
carry `-f` glues only), its W glue is emitted nowhere (the conduit
is a true-basis tile), and match strength 1 per face < TAU 2 means
zero matchable faces — stacked dead readers mutually expose one
match each, still under TAU. The top-row unmatched N face is
already the existing basis (the inert cap `F{a}` carries
`rf-relay`).

## Measured (probed live this tick, then pinned)

| program | before (tick 49 pin) | after (this tick) |
| --- | --- | --- |
| PC4 (`q. r :- p, q. r :- p.`) | 12 tiles / 35 asm / 1 term / full locks / dead `[and1_r, unit1_r]` vacuously absent | **13 tiles** (+`UD3r` @ row 3: W unit1_r, S p-t-done, E r-t, N r-t-done) / 35 asm / 1 term / full locks / dead `[and1_r, unit1_r]` — `unit1_r` now **emitted + BFS-proved absent** |
| PC10 (`p. q :- z. r :- q.`) | 17 tiles / 70 asm | **18 tiles** (+`UD4r` @ row 4: W unit1_r, S q-t-done, E r-t, N r-t-done) / 70 asm / 1 term — `UD4r` in no producible assembly (pinned) |
| PC1–PC3, PC5–PC9 | registered counts | byte-identical (hardcoded pin updated only for PC4) |

Corpus receipt `evidence/2026-10-07-parity-corpus/run.out`
regenerated: all 9 programs + 10 refusals still verify (all_ok
true); only PC4's tile count and timing lines moved. Hand-build
parity P3 (test_compiler_v01) now asserts compiled-minus-UD3r ==
BUILD3 exactly, plus UD3r's exact faces/row.

## Honesty boundaries

- AND-bodied false heads (terminal or not) keep the plain basis —
  still unexercised in the corpus, still deferred.
- PC4's `and1_r` remains vacuously non-emitted (AND body); the
  non-vacuous claim covers unit bodies only.
- Refusal set unchanged (CYC, non-adjacent, OR/AND at
  intermediate, depth > 2, derived-hi conduit all still refuse —
  corpus refusals all_ok).
- Time-box: science landed inside ~30 min; landing/ops overran the
  overall tick slightly (~35 min) — recorded, not hidden.

## Receipts

- Suite: `python3 -m unittest discover -s tests` → `Ran 407
  tests in 0.776s` / `OK (skipped=1)` (no net new test methods:
  stage-2's terminal-boundary test became the stage-3 emission
  test; r4 gained non-vacuous-absence assertions; count measured
  before claiming).
- Queue: no cluster job — static BFS work, tick-37 standing rule
  (total corpus wall 0.03 s).

## Tick-47 waiter (unchanged)

Request `9e79de4389423dfbdb8d5313afcc7603a1abc8bf5097743157b7ad15ff58e145`
(nonce dg2win-l3vac-v1, dG-2 window + L3-at-vacancy, gates
DW8-DW11/LV1-LV2 frozen at df958f2) STILL QUEUED at the 21:04Z
re-check. Collection remains the next tick's first duty; monitor
re-armed this tick.
