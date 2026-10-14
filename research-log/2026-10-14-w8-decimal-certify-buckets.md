# Exact-Decimal certification of the complement decade-bucket maxima (tick 137)

**Date:** 2026-10-14 (tick 137, SON-5152)
**Status:** measured + pinned; CI-gated
**Artifacts:** `tools/w8_decimal_certify_buckets.py`;
receipt `evidence/2026-10-14-w8-decimal-certify-buckets/buckets.json`
(sha256 `b4e95510ad690e79775dd287c1577b833be193fece0594a1d3ed282e3e4fe10d`);
pins `tests/test_w8_decimal_certify_buckets.py` (11 tests).
**Zero kTAM trajectories, no gate, ladder stays PAUSED.**

## Context

Tick 136 closed the envelope's oracle-noise honesty limit *at the
extrema*: the six branch-class argmax points of the pinned tick-134
envelope receipt were certified against exact-integer-factorial
Decimal ground truth (prec 80, truth at the module's actual float
`p`, defining-side sums only). Its honesty box disclosed the
remaining limit: *"certifies the six argmax extrema (the class-maxima
claim), not all 537 grid points."*

This note closes the next ring inward for the branch that actually
carries the 1e-8 bar and the figure-013 curves: **every per-decade
bucket maximum of both complement classes** — `binom_cdf` decades
0, −1…−5 (six buckets) and `binom_sf_ge` decades 0, −1, −2, −5 (four
buckets) — is re-located on the identical deterministic sweep grid
and certified against the same exact truth. After this, every point
the figure-013 complement curves *plot* (each bucket's worst measured
deviation) is exact-certified, not just the two global extrema.

## Method

Identical to tick 136 (`w8_decimal_certify.certify_point`, reused):
`Decimal(p)` converts the module's actual float argument to its exact
binary value; binomial coefficients are exact integers by recurrence;
powers incremental (per-term relative error ≤ ~2n ulp₈₀ ≈ 1e-76 at
n = 4999); `cdf` sums j = 0..k and `sf_ge` sums j = k..n — the
defining side, never a 1−x complement, independent of branch routing.

The bucket argmax *points* are not stored in the envelope receipt
(only bucket values), so the tool replays
`w8_exactness_envelope.sweep`'s iteration exactly (same
`FULL_NS`/`FULL_PS`, same `k_grid`, same rel rule, same
first-strictly-greater tie behaviour) and locates them. **Determinism
guards, all asserted before any certification is emitted:** the
replay must reproduce the receipt's stored `decade_buckets` values
EXACTLY (float `==`, per point), the complement class argmax points
and `max_rel` EXACTLY, and the 537 compared / 37 below-floor counts.
`certify_point` re-derives the branch class live and refuses on guard
drift, so a future re-routing of any certified point cannot be
silently re-certified.

## Measured (all vs exact Decimal truth)

`binom_cdf` complement buckets — decade 0 @ (1475, 2500, 0.5):
**7.52e-20**; −1 @ (2500, 4999, 0.5): 6.644e-11; −2 @ (4719, 4999,
0.95): 1.0403e-9; −3 @ (496, 500, 0.999): 3.793e-11; −4 @
(4984, 4999, 0.999): **4.0861e-9**; −5 @ (494, 500, 0.999): 4.7502e-9.

`binom_sf_ge` complement buckets — decade 0 @ (0, 2500, 0.5):
**exactly 0.0** (sf_ge(0) = 1, module exact); −1 @ (1250, 4999,
0.25): 2.734e-11; −2 @ (1311, 4999, 0.25): **1.2707e-9**; −5 @
(16, 100, 0.05): 2.3396e-9.

All ten ≤ the 1e-8 complement bar. Two of the worst points were
**beyond tick 136's extrema set** and are now certified: the n = 4999
pair cdf(4984, 4999, 0.999) at 4.0861e-9 and sf_ge(1311, 4999, 0.25)
at 1.2707e-9.

**Oracle-noise share bounded across the whole bucket set:**
max |oracle − truth|/truth = 5.9622e-12 (tick 136: 4.943e-12 at the
six argmax points). The decade-0 bucket maxima turn out to be
~entirely oracle noise — the recorded two-method maxima there
(3.8369e-13) are the oracle's own error; the module is at 7.5e-20 /
exactly 0.

## Honesty box

- Certifies the ten complement bucket maxima — the worst point per
  (helper × decade), i.e. every point figure 013 plots on the
  complement curves — not all 537 grid points, and not the direct
  classes beyond their (already-certified) argmax points.
- Bucket-point *location* is a deterministic function of the current
  code state; the value-equality guard proves the located point
  carries exactly the receipt's recorded maximum at certification
  time, but a code change that re-locates a tie would require a fresh
  certification run (the refusal guards force this rather than let it
  pass silently).
- Ground-truth arithmetic error ≤ ~1e-76 relative (six orders below
  every compared deviation).
- Ladder/census state unchanged: blockpower request
  `d3aa0acaa37ff4c9…` still queued (board-operator maintenance
  lease); no resubmit, nonce idempotent.

## Consequences

The 1e-8 complement bar now holds against exact ground truth at
every decade bucket of both helpers, not only at the global extrema;
figure 013's complement curves are exact-certified at every plotted
point. No consumer-facing claim changes — every certified value was
already within its bar; this strengthens the evidence class of the
claim (two-float-method → exact) without moving any number that a
consumer reads.
