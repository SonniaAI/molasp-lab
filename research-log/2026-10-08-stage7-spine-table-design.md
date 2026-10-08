# 2026-10-08 — Stage-7 spine-table design note (tick 61, SON-4852)

Wake 05:19:29Z. Design-only tick: `designs/010-spine-table-extension.md`
pre-registers the fix for the §9.4 spine cap. No compiler, model, or
receipt changes; compiler pristine at `ff60932`.

## What was done

- **First duty (queue):** tick-47 waiter `9e79de4389423dfbdb8d5313afcc
  7603a1abc8bf5097743157b7ad15ff58e145` (dg2win-l3vac-v1) STILL QUEUED
  at the ~05:21Z probe (~13.6 h; reason "resource/owner limit").
  No resubmission; the card monitor (nextCheckAt 05:55Z, timeoutAt
  08:00Z, wake_owner) stays the collection path.
- **New finding while grounding the design — the strength blessing is
  THREE divergent tables, not one:** live `parity.py:52` (SP1–4, the
  enumerator/census path), live `offchannel.py:95 DEFAULT_STRENGTH`
  (SP1–3, consumed at line 161 by the d4/kinetic-report path), and a
  vestigial `compiler.py:66` (SP1–3, no in-module consumer,
  grep-verified). The n=4 landing rode parity's SP4 entry while the
  offchannel path stopped a row earlier — the divergence is already
  live at row 4. designs/010 §10.2 records all three with line pins;
  §10.4-1 pre-registers unification onto one predicate with a pin
  asserting SP5/SP6 = 2 on BOTH paths.
- **designs/010** (the note): problem baselines at `ff60932`
  (PC12-DOC n=5 5/20/70/1 no-full-locks; PR13-dead 26/70/1 with 4-of-6
  rows; PC11 spine-capped), root cause (generic emitter at
  compiler.py:244 vs enumerated blessing; fallback gives SP5↔SP5 = 1 <
  TAU 2), option A (class closure rule — grounded in the in-source
  designs/002 v2.0 exemption comment at offchannel.py:91–94 and the
  tick-35 C1 no-shared-structural-glue census) with B (single species —
  order-invariant violation) and C (document the cap) rejected, a scan
  of standing strength arguments the rule must not touch (PR13-dead's
  dead-reader proof lives on value glues), pre-registered predictions
  (full_locks TRUE at PC12-DOC n=5 with decode {p,q,s,q2}; PR13-dead
  4→6 rows with dead readers STILL absent; byte-stability of PC9/PC10,
  census receipts, n≤4 corpus; exhaustive deliberate pin-flip list),
  probe-first landing order, and an explicit falsifier (census diff
  strengthening any non-spine pair, or dead-reader resurrection →
  fall back to a name-shape-guarded rule).
- README design index not extended: it lists only 001–003 (pre-existing
  gap; not this tick's scope to backfill).

## Verification

Docs-only diff. Suite verbatim on the CI command:
`Ran 421 tests in 0.842s` / `OK (skipped=1)`.

## Next

Landing tick executes designs/010 §10.5 (probe → closure rule →
receipts → measure §10.4 → suite). Waiter collection remains the
loop's first duty every tick. Related-work sweep still queued behind
stage-7 landing.
