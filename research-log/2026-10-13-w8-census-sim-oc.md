# W8 census estimator operating characteristics — fixed-seed simulation (tick 123)

Date: 2026-10-13 · SON-5152 · run 562a708f. Simulation addendum to the
tick-122 pre-registered design (`2026-10-13-w8-stratified-census-design.md`),
landed while the blockpower arbitration datum (`d3aa0acaa37ff4c9…`, queued
since 21:30:03Z) is still outstanding. **Zero kTAM trajectories were run.**
All draws are synthetic binomial counts calibrated to committed receipts;
fixed stdlib Mersenne Twister seeds (20261013 / 20261014), 4000 replicates
per world; every number is byte-reproducible and pinned in
`tests/test_w8_census_sim.py` (the module is stdlib-only — see the repair
note at the end).
No gate is executed; the ladder stays PAUSED; the pooled contested line
stays REPORTED-NOT-CLAIMABLE. Automated pre-registration; independent QA
review pending. In-silico only.

## What was measured

Operating characteristics of the frozen estimator menu over the two branch
worlds of the pending blockpower map (module `tools/w8_census_sim.py`):

| metric | A: homogeneous six-window (n≈5000×6) | B: contested four-arm (500/153/500/499) |
| --- | ---: | ---: |
| per-stratum Wilson-95 coverage (min) | 0.94675 | 0.9445 |
| pooled Wilson coverage of size-weighted truth | 0.94375 | 0.94375 |
| inv-var θ̂ ± 1.96·SE coverage of θ* | 0.94375 | 0.93875 |
| conservative band coverage of θ* | 1.0 | 0.99975 |
| conservative band covers ALL stratum shares | 1.0 | **0.0** |
| mean band width vs pooled Wilson width | 0.024392 vs 0.009962 (2.448×) | 0.080668 vs 0.041843 (1.928×) |

Truth conventions (stated in the module): pooled truth q* = Σnᵢpᵢ/Σnᵢ;
inv-var truth θ* = plim θ̂ = [Σ nᵢ/(1−pᵢ)]/[Σ nᵢ/(pᵢ(1−pᵢ))] — under
heterogeneity θ* ≠ q* (world B: 0.749190 vs 0.747579), which is itself
pinned.

## Findings

1. **Design caveat discovered before the datum (the point of the tick).**
   The conservative band θ̂ ± Σ(wᵢ/Σw)·hᵢ is a **θ-interval, not a
   stratum-simultaneous band**. In the contested world it covers θ* at
   0.99975 but covers all four stratum shares simultaneously in **0 of
   4000** replicates: the shares span 0.6928–0.778 while the band
   half-width averages ≈0.0403. Under heterogeneity at these n's,
   per-stratum Wilson intervals remain the ONLY per-stratum uncertainty
   authority; the band is the honesty-first summary for the weighted
   estimand alone. The tick-122 design's "conservative simultaneous band"
   phrasing is hereby scoped to the θ estimand. Branch-conditional use is
   unchanged: SUPPORTED → per-stratum Wilson primary + band as the θ
   summary only.
2. **Honest negative.** Pooled Wilson does NOT collapse at the contested
   n's (coverage 0.94375 of q*, within MC error of nominal at 4000 reps,
   ±0.0068): Σnᵢpᵢ(1−pᵢ) ≈ Nq*(1−q*) for this
   dispersion pattern, so the stratification case there rests on
   interpretability and per-stratum authority, not pooled coverage
   collapse. The pooling dispute (POOLING_CONTESTED) is about the exact
   gate and estimand legitimacy, not interval coverage at this n.
3. **Per-stratum Wilson is robust in both worlds** (all coverages
   0.9445–0.9578, within MC noise of nominal 0.95). The inv-var
   delta-method interval shows mild under-coverage in the heterogeneous
   world (0.93875) — consistent with delta-method optimism under
   estimated weights; recorded honestly, not promoted.
4. **Honesty premium quantified**: the band costs 2.45× pooled width in
   the six-window world, 1.93× in the contested world.

## Standing consequences

- Nothing here unfreezes the ladder, executes a gate, or makes the pooled
  contested line claimable.
- When blockpower lands, the frozen branch map (VOID / NO_EVENTS /
  SUPPORTED / NOT_DETECTED) and the tick-122 branch table apply verbatim;
  this addendum only scopes the band's claim and quantifies the trade.
- MC error at 4000 replicates ≈ ±0.0034 at the 95% level; pins are exact
  under the frozen seeds, so every rerun reproduces the table.

## Repair note (same tick, disclosed)

The first version of this note and module (commit `d051ca5`) drew its
replicates with numpy PCG64 and pinned those numbers. Hosted unittest
CI failed on `d051ca5`: the `checks` workflow runs `python3 -m unittest
discover -s tests` with **no dependency install** — `import numpy`
inside `simulate_world` is a ModuleNotFoundError in the hosted
environment (green locally only because the sandbox has numpy). The
module was rewritten stdlib-only in the same tick: cached log-CDF table
(`ln C(n,k) = ln n! − ln k! − ln (n−n)!` — note the first sampler draft
used `ln k!` there, producing degenerate x=n draws caught by a sanity
check BEFORE any number was pinned or committed; never landed) +
bisection inversion of `random.Random(seed).random()`, same seeds, same
estimator loop. All numbers above were re-measured under the stdlib
sampler; every qualitative finding (band is a θ-interval vs 0/4000
all-stratum coverage, per-stratum nominal coverage, no pooled collapse,
the two honesty premiums) is unchanged; the numpy-based values in
`d051ca5`'s message are superseded by this note.
