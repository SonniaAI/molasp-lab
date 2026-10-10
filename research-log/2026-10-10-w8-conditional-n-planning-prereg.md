# W8 exact conditional test: sample-size planning preregistration

Date: 2026-10-10 · SON-4959. This is a prospective binomial design calibration that follows the exact-test power run on SON-4957. It does not re-analyze the observed six-window result or generate kinetic trajectories.

## Question and estimand

For the six-window, two-hot alternative used in the previous calibration, what tested sample sizes per window put the exact conditional Bonferroni procedure's Monte Carlo power above 80%, 90%, and 95% for δ=.01 and δ=.02? The estimand is rejection probability under the specified independent-binomial model, conditional on six equal window denominators. It is not power for physical molecular replicates or arbitrary between-window variation.

## Frozen design and decision rule

- Baseline `p0=1110/1499`; blocks 8 and 9 have rate `p0+δ`, blocks 10–13 have rate `p0`. The true pair is fixed before simulation; the test scans all 15 pairs.
- Effects: `δ ∈ {0.01, 0.02}`. Equal per-window sample-size grid: `n ∈ {2500, 4000, 5000, 7500, 10000, 15000, 20000, 25000, 30000}` pair-terminal Bernoulli outcomes.
- Run 100,000 independent six-count datasets per (δ,n) cell. Use NumPy `Generator(PCG64)`, with seeds 20261020–20261037 assigned in δ-major then n-major order. No outcome-dependent stopping, replacement, or seed changes.
- On each dataset use the frozen `tools/w8_conditional_power.py` procedure: conditional one-sided hypergeometric upper-tail for the most extreme two-window sum, Bonferroni over all 15 candidate pairs, and reject only when adjusted p < .05. For equal denominators the largest two counts attain the minimum tail; the existing enumeration-equivalence tests remain part of CI.
- Record each rejection fraction and its pointwise 95% Wilson interval. For each δ and target power (.80, .90, .95), the primary summary is the **smallest tested n whose Wilson lower endpoint is at least the target**; if no grid point qualifies, report none. Report the neighboring tested grid point and the full cell results. Do not interpolate or call this the exact minimum n; pointwise intervals are not a simultaneous guarantee across the grid.
- Include the n=5,000 cells as a fresh-seed calibration against SON-4957, and retain the fixed-tail SciPy-vs-integer cross-check. Record library versions and receipt hash.

## Interpretation limits

This is a fixed-baseline, equal-denominator, independent-binomial, exactly-two-hot design calculation. Wilson intervals cover Monte Carlo error only; `p0` is treated as known, and neither nuisance-rate estimation nor overdispersion is included. The tested-n summary is grid-limited, and no physical-replicate or observed-window inference follows from it. The primary observed-data `HETEROGENEITY_NOT_DETECTED` verdict remains unchanged. No new kinetic trajectories, queue job, wet-lab activity, blog, external contact, or paper/preprint submission is planned.
