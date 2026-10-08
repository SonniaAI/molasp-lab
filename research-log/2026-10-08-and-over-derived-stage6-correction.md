# Designs/009 stage-6 sequencing correction — tick 56

Date: 2026-10-08 ~02:25Z · SON-4846 · run 7e0ddb54 · compiler pristine
at 4b71903 (edits attempted, measured, reverted; suite `Ran 421 tests`
/ `OK (skipped=1)` before and after).

## What was attempted

The tick-55-gated stage-6 landing: gate A narrowed from
`(i−1, row-1 via)` to `(i−1, i−2)` positional; gate B (derived-hi
refusal) removed — a channel re-typing, since DA.S = `{hi}-t-done`
already names the D-column chain link; gate C re-typed from
`below_v != via` to `below_v != {lo}-done` (value-typed). An initial
V-tile re-typing on fact rows (N := d_north[i−1]) was also tried and
reverted first — it mutates fact-row V relays for nothing.

## Measured dead end 1 — gate A as replacement breaks the corpus

Suite after the gate edits: 4 failures + 2 errors. The errors are the
load-bearing ones:

- `test_census_generality.TestCensusGeneralityReceipt.
  test_live_recompute_matches_receipt` — census arm AND terminal now
  refuses: `conjunctive variant of 'r': literals must sit at
  (adjacent-below, adjacent-below-2) — … got rows (3, 1)`.
- `test_chain_refusal_corpus.TestDeadReaderEmissionStage2.
  test_v01_builds_byte_stable` — same class, chain corpus.

The arms' ANDs read lo = the row-1 atom through the V-column via relay
— the only lo channel v0.1 ever had at n>3. Narrowed gate A refuses
every one: receipt-breaking, not a relaxation. **Stage 6 gate A must be
a union: (i−1, 1) via-channel OR (i−1, i−2) positional.**

## Measured dead end 2 — the positional channel has no V-column slot

Derived from the emit structure, then confirmed by the value-typed
gate C firing:

- DA (col 1) reads `{hi}-t-done` from the D-column N face at row i−1 —
  for a derived hi that is exactly the stage-1 chain link; gate B
  relaxation is sound name-wise with zero emission change.
- DB (col 2) reads `{lo}-t-done` from the V-column N face at row i−1 —
  but an intermediate derived row's V tile carries the chain link
  (`{hi}-t-done`), which PC9/PC10's unit readers pin as load-bearing.
  The lo row's own `{lo}-t-done` N face is two rows down at column 1,
  unreachable.

Measured: PC12-N4 (`p. q. q2 :- p. r :- q2, q.`) under A-narrow +
B-relax + value-typed C refuses at gate C: `the V column at row 3
carries 'q2-t-done', not the lo value 'q-t-done'` — the honest sound
of the missing channel. Without value-typed C the same build would
compile with a dead DB.S glue and BFS would show `r` absent from
terminal decodes: a silent dead build, the class tick 52 closed.

## Consequence for stage 6

Redirected to Option II (designs/009 §3, now §8): a second N-face
channel on the intermediate derived row re-emitting the row below's
`{lo}-t-done`, with the false-link over-production guard §3 names
(dead links must stay dead by value, BFS-proved); gate A as union.
PC12 stays the corpus candidate; it is unreachable by gate moves
alone — the tick-54 design and tick-55 sequencing both missed the
V-column occupancy conflict.

## Unchanged from tick 55

False-head decision open: PR13-dead/PR14 silently accept (correct
decode, 4/6 locks, d4 column-2 collisions); refusal-parity vs an
acceptance argument covering lock completion still to be decided
before any stage-6 acceptance claim.

## Waiter

Tick-47 request `9e79de43…e145` (nonce dg2win-l3vac-v1, job
`hxq-9e79de4389423dfb`) STILL QUEUED at the ~02:03Z re-check (~9 h,
"resource/owner limit; gateway and engine margin preserved"); no
resubmission per queue discipline; collection stays the next tick's
first duty.
