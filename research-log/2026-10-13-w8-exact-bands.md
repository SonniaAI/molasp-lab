# Exact per-stratum bands: pricing the exactness premium (tick 127)

**Status: measured planning math, pre-datum. Zero kTAM trajectories, no gate
executed, ladder stays PAUSED. Descriptive only — the pooled contested line
stays REPORTED-NOT-CLAIMABLE (POOLING_CONTESTED, tick 119).**

While the blockpower arbitration probe (`d3aa0acaa37ff4c9…`, nonce
`molasp-w8-blockpower-t120-a`) remains queued on the admission floor, this
tick closes the third leg of the simultaneous-band calibration triangle:

- tick 124 (`548234b`): the **simultaneity premium** — Bonferroni-Wilson at
  family 0.95 costs 1.3458×/1.2700× per-stratum width vs nominal Wilson,
  with an *in-expectation* guarantee only (realized 3799/4000, one replicate
  short, honestly disclosed).
- tick 125 (`8611b8c`): the **correction-choice floor** — exact Šidák
  reclaims ≤0.27%; Bonferroni stays house authority, Šidák the optimality
  certificate.
- tick 126 (`fe0439b`): the **width lever** — per-stratum n, at measured
  exact halving multiples 4.0032×/4.1046× (the 1/√n rule is slightly
  adverse at all frozen rates).
- **this tick: the exactness premium** — Bonferroni-**Clopper-Pearson** at
  the same family level, whose per-stratum coverage is ≥ 1−α/m *by
  construction*, so family coverage under independence is ≥ 0.95 exactly
  (product of per-stratum coverages; Bernoulli inequality). What does
  removing the in-expectation caveat cost in width?

Module: `tools/w8_exact_bands.py`; pins: `tests/test_w8_exact_bands.py`.
Stdlib-only, and — new for this module — **no RNG at all**: every number is
an exact binomial sum or a bisection root.

## Method note (stated upgrade)

For any count-based interval, per-stratum coverage at a fixed true rate is
an exact sum over the count support, and all-strata coverage under
independent strata is the exact product of per-stratum coverages. No Monte
Carlo is needed for those two quantities: this module computes them by
bound-crossing search + exact CDF sums (one exact log-pmf seed, O(1)
recurrence per term). The tick-123/124/125 fixed-seed MC datasets remain
the authority for quantities that genuinely need the joint draw (pooled and
inverse-variance estimator coverage, the conservative θ-band).

## Solver validation (measure-then-pin earned its keep again)

- Analytic edges: k=0 upper = 1−0.025^(1/n), k=n lower = 0.025^(1/n), for
  n ∈ {1,2,7,153,4999} — all to 1e-12; n=1 literals [0,0.975]/[0.025,1].
- Textbook reference: CP95 for 5/10 = [0.187086, 0.812914] ✓.
- Defining equations P(X≥k|lo)=α/2, P(X≤k|hi)=α/2 and k-reflection
  symmetry: max residual **8.6e-14** over the frozen (k,n,α) spread.
- **First-draft bug caught pre-pin:** the upper-bound bisection passed the
  target α/2 to the increasing form 1−CDF (correct target 1−α/2), solving
  the wrong tail — exposed instantly by the k=0 analytic check (0.000165 vs
  0.023822) and the 5/10 reference, never landed. The analytic-identity and
  defining-equation pins are the permanent guard.

## The exactness premium at the frozen strata (observed counts)

Six-window family (m=6, α/6): premium = CP width / Wilson width is
**1.00619–1.00627** across all six strata (block8: CP ±0.016681 vs Wilson
±0.016578). Contested four-arm family (m=4, α/4): **1.02154–1.02208** at
the n≈500 arms, and **1.04048 at arm4 (n=153)** — CP ±0.095333 vs Wilson
±0.091624. Exactness is cheap at n≈5000, real at n≈500, and 4% at n=153.

## Exact coverage: the certificate and the cross-check (both worlds)

Exact closed-form products, both frozen tick-123 worlds:

| world | family Wilson (exact) | tick-124 MC | MC − exact | family CP |
|---|---|---|---|---|
| A homogeneous six-window | 0.951428 | 0.94975 | −0.001678 | **0.953621** |
| B contested four-arm | 0.954065 | 0.95275 | −0.001315 | **0.961294** |

- **Cross-check:** the tick-124 4000-rep MC realizations sit 0.0017/0.0013
  below the exact products — well inside the ±0.0068 (2σ) MC bar. Two
  independent computations of the same number agree.
- **The guarantee, verified:** every CP per-stratum coverage ≥ 1−α/m
  (mins 0.991984 / 0.988518 vs nominals 0.991667 / 0.9875); both CP
  families ≥ 0.95 structurally.
- **The honest content of the tick-124 caveat is real:** the *worst* Wilson
  stratum lands below nominal in both worlds (0.991602 < 0.991667;
  0.986750 < 0.9875). Family level still cleared 0.95 in both worlds — but
  via over-coverage elsewhere, which is a measurement of these two worlds,
  not a guarantee.
- Family-level width ratio CP/Wilson: 1.00231 (A) / 1.00758 (B).

## Expected-width premium trend (bounded-n study, E[width] under exact enumeration)

Premium decays monotonically in n at all three design rates (worst-case
0.5; pooled 22111/29989; arm4 106/153): **1.0397/1.0391/1.0405 at n=153 →
1.0082/1.0089/1.0090 at n=2500**. The measured six-window strata (n≈5000,
premium 1.0062) sit on the same trend. Bounded to n≤2500 (per-k CP solves);
trend measured, not extrapolated to the tick-126 n-menu points.

## Reading for the branch map

- **Either branch:** Bonferroni-Wilson **stays house authority** for
  reported per-stratum widths (tick 125's ruling unchanged). CP is recorded
  as the **exactness certificate**: at the SUPPORTED-branch census n's
  (thousands per stratum) it costs ≲0.6–0.9% width and buys a per-stratum
  finite-sample guarantee — affordable where the report is
  contested-provenance; at small-n strata (arm4) the 4% premium is the
  price of a guarantee the descriptive line does not need.
- No new data, no gate, no trajectory; the blockpower waiter stays queued
  (one frozen-rule status probe this tick, no resubmit, no monitor).

## Honesty box

- Exact products assume independent strata — the same assumption the
  tick-124 MC made; provenance heterogeneity is exactly what the queued
  arbitration probe adjudicates.
- CP conservatism is a discreteness bonus: realized per-stratum levels sit
  above nominal (e.g. 0.9920–0.9924 vs 0.9917), i.e. the premium slightly
  overpays at large n — measured, not corrected for (no mid-p here).
- Premiums at observed counts are deterministic width ratios; the trend
  study is expectation-based at n≤2500 only.
