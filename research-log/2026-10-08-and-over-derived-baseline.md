# 2026-10-08 — AND-over-derived baseline: today-truth of the designs/009 corpus

Tick 55 (SON-4842, run efa84230, started ~01:00Z). Pre-implementation
probe of the designs/009 stage-6 corpus candidates under the current
compiler — same discipline as the tick-47 chain-refusal baseline:
every number below is measured probe output, nothing guessed from
the design doc, nothing yet a validated result.

## What was probed

The five shapes that matter for stage 6 (AND bodies over derived
literals), run through `compile_program` / `check_program` exactly
as the corpus does:

| name | program | today-truth |
| --- | --- | --- |
| PC12-doc | `p. s. q. q2 :- p. r :- q2, q.` | refused, gate A |
| PC12-n4 | `p. q. q2 :- p. r :- q2, q.` | refused, gate A |
| PR13-doc | `p. s. q. q2 :- s. r :- q2, q.` | refused, **unit gate** |
| PR13-dead | `p. s. q. q2 :- z. r :- q2, q.` | **compiles**, ok=false |
| PR14-doc | `p. s. q. q2 :- p. r :- q2, z.` | **compiles**, ok=false |

## Finding 1 — gate A fires as corrected-predicted; gate B is unreachable

Both PC12 shapes refuse with the conjunctive-variant positional
message, exactly the (i−1, i−2)-vs-(i−1, row-1-via) mismatch the
design's in-place §4 correction anticipated:

- PC12-doc: `conjunctive variant of 'r': literals must sit at
  (adjacent-below, row-1 via), got rows (4, 3)` — rows: p=1, s=2,
  q=3, q2=4 (derived), r=5.
- PC12-n4: same gate, `got rows (3, 2)` — rows: p=1, q=2, q2=3
  (derived), r=4.

Gate B (the derived-hi re-typing that §2 argues is a channel
re-typing) never gets to speak: the refusal message does not
mention the derived row. **Stage 6 must narrow gate A positionally
first; gate B's channel re-typing is then reachable as a second,
separate move.** The single-mechanism-per-stage discipline holds.

## Finding 2 — the design-doc PR13 text is wrong twice (recorded, not silently fixed)

`q2 :- s` with fact `s` derives q2: least model {p,q,q2,r,s}, not
the claimed {p,s,q}. And the program refuses at q2's OWN unit-variant
gate (`unit variant of 'q2': literal 's' not via-carried (row-1)
nor an adjacent-below derived row; direct-below FACT readers are a
designs/002 geometry`) — before any AND gate is reached. The honest
dead-cascade shape is PR13-dead (`q2 :- z`, z unplaced): least
model {p,q,s}, q2 false, r's AND body dead on one conjunct.

## Finding 3 — THE SURPRISE: false AND heads bypass gates A/B/C entirely

PR13-dead and PR14 **compile today**. A predicted-false AND head
never reaches the conjunctive-variant positional check: the
designs/008 stage-4/5 false-row base emits dead readers
unconditionally (only width>2 refuses). PR14 was registered in
designs/009 §4 as a must-stay-LOUD refusal ("lo z not below
terminal → gate A narrows, never silently widens") — measured: it
is a **silent acceptance** whose decode happens to be correct.
This is the same boundary class tick 52 closed for width>2 false
heads (PR11/PR12), now open again one axis over: false heads with
AND bodies over derived literals and unplaced literals skip
geometry checks.

Measured, both shapes:

- PR13-dead: 6 rows {1:p, 2:s, 3:q, 4:z, 5:q2, 6:r}, 26 tiles,
  70 assemblies, 1 terminal; terminal decodes exactly {p,q,s} =
  least model; dead glues [and1_r, unit1_q2] both BFS-proved
  absent from every producible assembly.
- PR14-doc: 6 rows {1:p, 2:s, 3:q, 4:q2, 5:z, 6:r}, 25 tiles,
  70 assemblies, 1 terminal; decodes {p,q,q2,s} = least model;
  dead glue [and1_r] absent.

So the semantic pins hold even in the silent path (decode-
uniqueness and dead-absence both pass) — but each build is
**lock-incomplete** (4 of 6 rows lock; PR13-dead leaves q2 and r
lock-free, PR14 leaves z and r lock-free) and the **emitted build
breaks the designs/003 one-tile column-2 row structure**, which
the d4 off-channel census reports at error severity (reports,
never gates):

- PR13-dead row 5 column 2: `['V5p', 'UD5q2']`
- PR14 row 6 column 2: `['Fr', 'AD6r']`

## What stage 6 must now carry (supersedes designs/009 §3's shape)

1. True head: gate A narrows (i−1, 1) → (i−1, i−2) — then, and
   only then, gate B's derived-hi re-typing is reachable and
   separately reviewable.
2. False head: a decision, not a default — either PR11/PR12-style
   refusal parity for AND bodies whose literals fail the
   positional/typing checks, or an explicit acceptance argument
   that covers lock completion and the column-2 emission
   collision. Today's silent acceptance has neither.
3. Corpus registration: PR13's honest shape is `q2 :- z` (dead
   cascade), PR14 stays the loud-refusal arm of the narrowed gate
   A — its current compilation is the bug the pin exposes, pinned
   as-is so the fix flips a measured baseline, not a guess.

Pins: `tests/test_and_over_derived_baseline.py` (10 tests). Suite
verbatim on the exact CI command: see log tick 55.

## Tick-47 waiter (standing duty, re-checked this tick)

Request `9e79de4389423dfbdb8d5313afcc7603a1abc8bf5097743157b7ad15ff58e145`
(dg2win-l3vac-v1) still QUEUED at ~01:01Z (~7 h, resource/owner
limit). No resubmission (idempotent request, queue is the
sanctioned wait); collection stays the next tick's first duty.
