# 2026-10-07 — Designs/008 stage 2: dead-reader emission for false derived heads

Tick 49 (SON-4825, run dd5ad99d). Scope: the deferred piece named in
the stage-1 honesty boundary (research-log 2026-10-07-chain-stage1-v02.md):
"explicit dead-reader emission for predicted-false derived heads".

## What changed

**molasp/compiler.py** — a non-terminal predicted-false derived row
now emits its dead reader(s) explicitly, per unit body, alongside
the plain false row (which stays the false-cap relay, stage 1
untouched). For PC10 (`p. q :- z. r :- q.`; rows p, z, q, r) the
tile is `UD3q` with faces W=`unit1_q`, S=`z-t-done`, E=`q-t`,
N=`q-t-done`. AND-bodied false heads and terminal false rows keep
the plain basis (terminal F-cap is pinned by PC4; both deferred).

**molasp/parity.py** — `dead_variant_glues` now scans every derived
row, not just the terminal head: an intermediate false head's dead
link is machinery once emitted, so it is reported and then checked,
not silently assumed. Output is unchanged for every program whose
rule atoms sit only at the terminal row (the whole v0.1 corpus).

## Why the dead reader provably never realizes

Every body of a predicted-false head is dead (least-model support).
So the reader's S face reads `{lit}-t-done` for a false literal —
emitted nowhere — and its W face is the vj conduit glue, which the
false basis emits nowhere. Match strength is 1 per matching face and
TAU is 2, so a tile needs two matches; the dead reader has zero.
Stacked dead readers (a dead reader for `b :- a` sitting above one
for `a :- z`) mutually expose exactly one match each — still below
TAU. The tile is in the set and provably in no assembly.

## Measured (probed live this tick, then pinned)

| program | before (tick 47/48 pin) | after (this tick) |
| --- | --- | --- |
| PC10 | 16 tiles / 70 asm / 1 term / full locks / dead `[unit1_r]` (vacuous) | 17 tiles / 70 asm / 1 term / full locks / dead `[unit1_q, unit1_r]`, both absent — `unit1_q` now **emitted + BFS-proved absent** |
| PC1–PC9 | registered receipt counts | byte-identical (pinned hardcoded in tests/test_chain_refusal_corpus.py so receipt regeneration cannot make the pin vacuous) |

No producible assembly contains `UD3q` (exhaustive BFS, 70
assemblies unchanged — the dead reader adds no growth path).

## Honesty boundaries

- Terminal false heads keep the v0.1 F-cap basis; their dead-reader
  emission is deferred (moving PC4's basis is its own tick).
- AND-bodied false non-terminal heads keep the plain basis
  (unexercised in the corpus).
- Refusal set unchanged (CYC, non-adjacent, OR/AND at intermediate,
  depth > 2, derived-hi conduit all still refuse).
- Time-box overran slightly (science ~35 min vs 30); recorded here
  rather than hidden.

## Receipts

- Suite: `python3 -m unittest discover -s tests` → `Ran 407
  tests in 0.803s` / `OK (skipped=1)` = 402 + 5 new pins (count
  measured before claiming).
- Corpus receipt `evidence/2026-10-07-parity-corpus/run.out`
  regenerated: only timing lines moved; all verdict lines identical.

## Tick-47 waiter (unchanged)

Request `9e79de4389423dfbdb8d5313afcc7603a1abc8bf5097743157b7ad15ff58e145`
(nonce dg2win-l3vac-v1, dG-2 window + L3-at-vacancy, gates DW8-DW11/
LV1-LV2 frozen at df958f2) STILL QUEUED at the 20:02Z re-check —
collection remains the next tick's first duty.
