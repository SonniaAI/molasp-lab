# W8 anchored re-seed: the seed-underflow hazard repaired (tick 129)

**Scope:** repair of the tick-128 fenced hazard in `tools/w8_exact_bands.py`
(recorded there as follow-up work). Zero kTAM trajectories, no gate, ladder
stays PAUSED, no blog (repair, not a milestone), stdlib only, no RNG.

## The hazard, now with measured numbers

`_pmf_terms` seeds one exact log-factorial pmf at `j_start` and walks with an
O(1) multiply recurrence. When the seed is not a normal double the walk is
corrupt from its first step:

- **Class 1 (seed = 0.0).** `log_seed(2500, 4999, 0.753304) = -745.2543`
  (measured), so `exp` rounds to 0.0 and the recurrence stays 0 forever:
  `binom_sf_ge(2500, 4999, 0.753304)` returned **0.0**. True value **1 -
  ~4e-12** (i.e. exactly 1.0 to double precision) — measured two ways below.
  The original tick-128 note's prose "true value is 0.9958" was itself wrong;
  withdrawn here.
- **Class 2 (deep-tail seed, normal or subnormal).** `log_seed(2601) =
  -636.6287`: a *normal* seed whose lgamma-cancellation-scale (~1e-11)
  relative error is inherited by every later term of the walk. The branches
  then exposed impossible values: `cdf(2601, 4999, 0.753304) = -6.3309e-11`
  (negative probability) and `sf_ge(2601) = 1.0000000000639078` (> 1).
  Subnormal seeds (measured band: `log_seed` in (-744.4, -708.4), i.e. j =
  2501..2533 for this (n, p)) are the same class, worse.

## The repair

1. **Anchored re-seed** inside `_pmf_terms`: when `log_seed` is below the
   min-normal double (`-708.3964185322641`), the walk seeds at the mode
   (or the interval endpoint nearest the mode) and walks *outward*, so the
   recurrence only ever starts at a healthy term and terms only decay toward
   the deep tail where they are negligible relative to the accumulated mass.
2. **[0, 1] clamp** in `binom_cdf`/`binom_sf_ge`: deep-tail *normal* seeds
   keep the original walk (bit-identical) and can no longer surface
   impossible values. Documented clamp, not a defect: the shorter-side
   `1 - x` branch cannot resolve a true CDF below ~1e-13 (e.g.
   `cdf(2601)` true 5.08e-277 -> 0.0); no consumer compares at that scale
   (CP targets are alpha/2 ~ 4e-3).

**Bit-conservatism:** healthy-seed calls take the original path
byte-for-byte, so every pinned tick-127/128 number is unchanged — the full
suite (which pins them) passes green, and `sf_ge(3766, 4999, 0.753304) =
0.50459576964362` is byte-identical pre/post repair.

## Cross-check (independent algorithm: per-term lgamma + running logsumexp)

| call | pre-repair | repaired | independent |
|---|---|---|---|
| sf_ge(2500, 4999, 0.7533) | 0.0 | 1.0 | 0.9999999999962389 |
| sf_ge(2500, 4999, 0.753304) | 0.0 | 1.0 | 0.9999999999960009 |
| sf_ge(2601, 4999, 0.753304) | 1.0000000000639078 | 1.0 | 0.9999999999934998 |
| sf_ge(3766, 4999, 0.753304) | 0.50459576964362 | unchanged | 0.5045957696284772 |
| sf_ge(4500, 4999, 0.753304) | 2.613964657949628e-154 | unchanged | 2.613964657825656e-154 |
| sf_ge(2500, 4999, 0.5) | (healthy) | unchanged | 0.49999999999785766 |

Two-method bar: <= 1e-10 absolute on O(1) values (both methods carry ~1e-11
on 2500-step walks; observed max 6.5e-12 on the corrupted class, 3.6e-11 on
the healthy p=0.5 symmetry case whose truth is exactly 0.5). The naive
CDF-quantile search from k = n/2 that produced the withdrawn tick-128
"CP collapse under drift" first draft now returns a sane window at the same
entry point: `clopper_pearson(2500, 4999, 0.05) = (0.48614293075084325,
0.5140569923589355)`, defining equations residual < 1e-9 — the collapse was
pure artifact.

## In-tick catches (measure-then-pin streak, #6 and #7)

- **#6:** the first draft of the anchored concatenation dropped the anchored
  seed term `pmf(anchor)` — the mode's ~0.0131 mass — returning 0.9869 where
  the truth is ~1.0. Caught by the pre-pin battery vs the independent
  implementation, never landed. Pinned now by length/sum/max-term invariants.
- **#7:** the first-draft *mechanism attribution* for the 2601 exposure
  ("subnormal seed quantization") was wrong — `log_seed(2601) = -636.63` is
  a normal double; that case is cured by the clamp, not the anchored path.
  Measured boundary: anchored fires for j <= 2530 (-712.1369), original path
  from j = 2534 (-707.7757). The test battery pins the measured boundary.

## Tests

`tests/test_w8_anchored_pmf.py`: 12 tests — battery vs independent,
documented-corruption repair, healthy spot pins, p=0.5 symmetry, boundary
identities, clamped-short-side documentation, anchored-walk invariants,
repair-threshold boundary (measured), bit-conservatism vs an inline copy of
the pre-repair recurrence, naive-search recovery + CP defining equations.
`tests/test_w8_dependence_stress.py`: the hazard pin updated to the repaired
truth (fence stays as defense in depth). Full suite: **Ran 985 tests / OK
(skipped=1)** = 973 + 12. Hosted CI on this head to verify next tick.

Waiter unchanged: blockpower arbitration probe `d3aa0acaa37ff4c9...` still
queued (one frozen-rule probe this tick, no resubmit, nonce idempotent).
