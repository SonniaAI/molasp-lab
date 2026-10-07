# 2026-10-07 — Designs/008 stage 4: AND-body dead-reader emission (the last deferred basis)

Tick 51 (SON-4830, run df160bcb). Scope: the boundary deferred by
stages 2-3 (research-log 2026-10-07-chain-dead-reader-emission.md
and 2026-10-07-terminal-dead-reader-emission.md): "AND-bodied
false heads keep the plain false basis — still unexercised in the
corpus, still deferred." This tick exercises it: PC4's `and1_r`
was the last vacuously non-emitted dead glue in the corpus.

## What changed

**molasp/compiler.py** — a predicted-false derived row with rule
support now emits the READER half of each AND body (the DB-shaped
tile), in both the terminal (stage-3) and non-terminal (stage-2)
false-row bases:

`AD{i}{a}` = W `and{j}_{a}` (the vj conduit glue), S `{lo}-t-done`
(the row-1 via conjunct's truth-typed done), E `{a}-t`,
N `{a}-t-done`.

The CONDUIT half (the DA-shaped tile) deliberately stays
unemitted, and that asymmetry is load-bearing: the conduit's S
face reads `{hi}-t-done`, and a false head's AND body only needs
ONE dead conjunct — hi may be true, giving the conduit a live S
bond (plus its W column bond) and risking a producible dead
conduit that would change the assembly set. The unit-body
conduits of stages 2-3 are unemitted for the same reason (their S
face reads `below_d`, always exposed by the real row below).

## Why the reader can never realize (glue arithmetic, not row geometry)

The true-block geometry gates (hi adjacent-below, lo row-1 via,
hi not derived) never run for a false head — the reader's
never-realizes proof must therefore be bond arithmetic alone, and
it is:

- **W** is the vj conduit glue `and{j}_{a}`, unique to this body.
  The only tile that could expose it eastward is the conduit half
  of the same variant — unemitted — and no true variant of a
  false head exists. W never bonds, at any site.
- **S** reads `{lo}-t-done`. If lo is false it is emitted nowhere
  (stacked dead readers mutually expose one match each); if lo is
  TRUE it bonds the true basis at strength 1. Either way S
  contributes at most 1.
- **E/N** are outputs (`{a}-t`, `{a}-t-done`); nothing reads them
  at strength 2 (false-row locks read `{a}-f`; readers of `{a}`
  are dead machinery).

Max match strength 1 < TAU 2 at every site: the tile is emitted
machinery whose absence from every producible assembly BFS-proves
— non-vacuous **even when the other conjunct is true**, which is
exactly PC4's shape (`r :- p, q.` with q true, p false).

## Measured (probed live this tick, then pinned)

| program | before (tick 50 pin) | after (this tick) |
| --- | --- | --- |
| PC4 (`q. r :- p, q. r :- p.`) | 13 tiles / 35 asm / 1 term / dead `[and1_r, unit1_r]` — and1_r vacuous | **14 tiles** (+`AD3r` @ row 3: W and1_r, S q-t-done, E r-t, N r-t-done) / 35 asm / 1 term / full locks / model `{q}` unmoved / dead `[and1_r, unit1_r]` — **both now emitted + BFS-proved absent** |
| PC1–PC3, PC5–PC9 | registered counts | byte-identical (PC3's and1_r is a TRUE head's dead variant — emitted since tick 20, untouched) |
| PC10 (`p. q :- z. r :- q.`) | 18 tiles / 70 asm | byte-identical (unit bodies only — no AND body to emit) |

Corpus receipt `evidence/2026-10-07-parity-corpus/run.out`
regenerated: all 9 programs + 10 refusals verify (all_ok true);
only PC4's tile count and timing lines moved. Hand-build parity P3
(test_compiler_v01) now asserts compiled-minus-{UD3r,AD3r} ==
BUILD3 exactly, with both readers' exact faces/row pinned; b4
(test_parity_corpus) pins AD3r's faces and its absence from every
producible assembly (the live-S-bond case is the point of the
pin).

## Honesty boundaries

- Body width > 2 on a false head: skipped, unchanged — a
  pre-existing silent-acceptance boundary of false heads (the
  width gate lives in the true block and never runs for them);
  recorded here, not widened.
- The AND-body geometry gates (adjacent-below hi, row-1 lo, hi
  not derived) remain true-block-only; the dead reader's proof
  does not depend on them, but a compile of a false head with an
  out-of-fragment AND body still does not refuse. Whether false
  heads should run the same geometry refusals is a follow-up
  question, not silently decided here.
- Refusal set unchanged (CYC, non-adjacent, OR/AND at
  intermediate, depth > 2, derived-hi conduit all still refuse —
  corpus refusals all_ok).

## Receipts

- Suite (exact CI command): `python3 -m unittest discover -s
  tests -v` → `Ran 408 tests in 0.778s` / `OK (skipped=1)` =
  407 + 1 net new (test_b4_pc4_and_body_dead_reader_emitted; name
  verified in verbose discovery; count measured before claiming).
- Queue: no cluster job — static BFS work, tick-37 standing rule
  (corpus wall < 0.1 s).

## Tick-47 waiter (unchanged)

Request `9e79de4389423dfbdb8d5313afcc7603a1abc8bf5097743157b7ad15ff58e145`
(nonce dg2win-l3vac-v1, dG-2 window + L3-at-vacancy, gates
DW8-DW11/LV1-LV2 frozen at df958f2) STILL QUEUED at the 22:04Z
re-check (~4 h; resource/owner limit — waiting is legitimate, no
resubmission). Collection remains the next tick's first duty;
monitor re-armed this tick.
