# Preregistered design: exact conditional w8 test under unequal denominators

Date: 2026-10-10 · SON-4961. This is a simulation design-calibration, not a new kinetic result and not a reanalysis of the observed six-window outcome.

## Question

At a fixed total of 30,000 pair-terminal Bernoulli outcomes across six windows, how does reallocating observations away from or toward the two prespecified elevated windows change the power of the existing conditional exact two-hot-family test? Does the test remain calibrated under unequal denominators, and does the equal-n “two largest counts” shortcut remain valid?

## Frozen method and design

- Under the global null, all six window probabilities are equal. Conditional on total successes `K`, the combined successes in a *fixed* two-window subset with `m` trials are Hypergeometric(`N=sum(n_i)`, `K`, `m`). Compute the one-sided upper tail for each of the 15 fixed two-window subsets, and reject only if `15 * min(p_pair) < .05`. Bonferroni gives family-wise control without requiring independence among the 15 tests.
- Under each alternative, windows 8 and 9 (indices 0 and 1) have probability `p0+δ`; windows 10–13 have probability `p0`, with `p0=1110/1499` and `δ ∈ {.01,.02}`. The three denominator allocations all total 30,000: balanced `[5000,5000,5000,5000,5000,5000]`; hot-small `[2500,2500,6250,6250,6250,6250]`; hot-large `[6500,6500,4250,4250,4250,4250]`.
- Also run a global-null calibration at `p_i=p0` under each of those three denominator vectors.
- Generate 100,000 independent six-count datasets per cell with NumPy `Generator(PCG64)`, using seeds 20261040–20261048 mapped in order to balanced-null, hot-small-null, hot-large-null, then balanced δ=.01/.02, hot-small δ=.01/.02, and hot-large δ=.01/.02. No outcome-dependent stopping, replacement, or seed changes.
- Enumerate all 15 subsets for every dataset; do not use the balanced-design top-two-count shortcut. Report rejections, power/false-positive fraction, pointwise Wilson-95 Monte Carlo interval, and fraction whose minimum p-value is the true pair (alternative cells only). For each imbalanced-vs-balanced power difference, report an independent-run normal 95% Monte Carlo interval using the two binomial standard errors. These intervals describe simulation error only.
- Validate the exact-integer hypergeometric helper against SciPy on a fixed unequal-n count vector; test a counterexample where maximizing the raw pair-count sum does not minimize the unequal-n conditional tail. Verify the three n vectors sum to 30,000.

## Interpretation limits

The test concerns a common-probability global null and the specified independent-binomial alternatives only. Bonferroni validity is an analytic conditional argument, while simulated null rejection rates are finite Monte Carlo checks, not a proof. Power is a function of where the fixed total exposure is allocated; the two-hot alternative and `p0` are fixed rather than estimated. Wilson/contrast intervals quantify Monte Carlo error only. Nothing changes the observed `HETEROGENEITY_NOT_DETECTED` verdict or supports claims about physical replicates. No kinetic trajectories, wet-lab work, blog, external contact, paper/preprint, or cluster job is planned; the vectorized simulation is bounded local design analysis.