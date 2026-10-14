# 2026-10-14 — Consolidated pre-datum dashboard of the frozen W8 arbitration map (tick 142)

**Status: pre-datum evidence, aggregation only. No datum exists; request
`dd5a8300` (nonce `molasp-w8-blockpower-t138-b`) is still queued behind the
board-operator maintenance lease. The ladder stays PAUSED. No branch of the
frozen map is touched or re-derived.**

## What and why

Ticks 139–141 measured the operating characteristics of every branch of the
frozen arbitration map — but in three separate receipts. The collection tick
(whenever the queue releases) will need the whole calibration at hand in one
place, with every number traceable to its source. This tick builds that
artifact: `tools/w8_arbitration_dashboard.py` reads the three committed
receipts and emits `evidence/2026-10-14-w8-arbitration-dashboard/dashboard.json`
(sha256 `a4d9e647cc637ad1be8f7cba0e2a79d2b0861cf58f7ce208f08b59108f8bf51d`),
a pure function of its inputs — byte-stable, stdlib-only, no RNG, no
trajectories, no gate executed, no seed window consumed.

Inputs (hashes recorded live in the receipt and re-verified by tests):

| receipt | tick | covers |
|---|---|---|
| `evidence/2026-10-14-w8-blockpower-cal-oc/cal-oc.json` | 141 | CAL exact-match VOID gate (branch 1) |
| `evidence/2026-10-14-w8-blockpower-floor-oc/floor-oc.json` | 140 | NO_EVENTS floor (branch 2) |
| `evidence/2026-10-14-w8-blockpower-oc/oc.json` | 139 | Fisher branch pair (branches 3–4) |

## The map at a glance (all numbers traced, pre-datum)

| # | branch | fires when | verdict | operating characteristic |
|---|---|---|---|---|
| 1 | `CAL_FAIL` | 500-seed CAL replay ≠ D2T 367 : L2 131 exactly | VOID | substrate-drift detector: 5% per-seed-corruption mismatch at ε = 1.030e-4 (dropout) / 2.646e-4 (reshuffle); passes at the floor's collapse yield w.p. 1.8e-9 |
| 2 | `min pair-n < 3400` | pooled pair census < 3400 either group | NO_EVENTS | catastrophic-collapse backstop: 6.19e-95 two-group risk at historical q ≥ 0.995; 5% only at other-rate 3.96% (≈8× collapse); floor-edge n = 3400 still delivers size 0.04325 / power 0.89225 |
| 3 | `p ≤ 0.05` | exact one-sided Fisher rejects | BLOCK_MECHANISM_SUPPORTED | realized size 0.04825 ≤ α; power 0.89775 @ Δ0.030, 0.979 @ Δ0.038; every prereg normal-approx power claim inside the exact MC Wilson-95 |
| 4 | `p > 0.05` | Fisher fails to reject | BLOCK_MECHANISM_NOT_DETECTED | calibrated reading: at a hotrepro-sized effect (Δ0.0223) power is only 0.69425 — NOT_DETECTED then carries ~0.31 probability of missing a real effect |

## Cross-receipt relations (the only new content, all computed from receipts)

- **Sensitivity ordering**: CAL detects per-seed corruption **384.83×** finer
  than the floor tolerates collapse (both 5%-firing points on the same
  per-seed scale). The map reads CAL → floor → p-value in strictly
  increasing tolerance.
- **Size chain**: 0.04325 (floor edge) < 0.04825 (nominal) ≤ α = 0.05 — the
  floor does not erode the arbitration and the instrument is conservative.
- **Clean-run VOID risk**: 6.19e-95 at historical yield (floor) and 0 by
  construction under the determinism premise (CAL) — a clean run cannot be
  VOIDed by statistical chance.
- **Coverage chain**: per-seed corruption escaping the CAL with ≥ 95%
  probability displaces each group census by ≤ 1.19% of the smallest
  pre-registered effect (79.388 seeds at Δ0.0223); verdict-scale corruption
  VOIDs at the CAL near-certainly.

## Verifications

11 pins in `tests/test_w8_arbitration_dashboard.py`: live re-hash of all
three input receipts; branch order/verdicts/provenance-path walk into the
source receipts; independent recomputation of the sensitivity ratio, size
chain, power monotonicity, Wilson containment of prereg approximations,
clean-run risk, and displacement fractions; byte-stability of the committed
artifact under regeneration (build-to-string and main()-to-file).

Suite: Ran 1097 tests / OK (skipped = 1) = 1086 + 11.

## Framing (honest limits)

Pre-datum calibration of a frozen instrument. The dashboard aggregates; it
derives no new science, and its numbers carry no claim about the pending
datum. The CAL row measures substrate drift on fixed replayed seeds under
the determinism premise — not sampling variation. Power numbers describe the
instrument, not the world.
