# W8 exact conditional test: power calibration plan

Date: 2026-10-10 · SON-4957. The six-window observations are already known; this is a prospective design-calibration simulation, not a new simulator result or an independent confirmation of the observed data.

## Question and estimand

At the registered design size of 5,000 pair-terminal Bernoulli trials in each of six windows, what is the rejection probability of the tick-108 finite-sample two-hot test under four baseline windows and two windows elevated by δ? Compare that operating characteristic with the earlier Pearson-χ² design calculation. The target is power for this specified simulator/protocol model only; it is not power for physical molecular replicates or arbitrary heterogeneity.

## Frozen inputs and analysis

- Six equal groups, `n=5,000` pair-terminal outcomes per group. This conditions on pair-terminal observations; it is not a claim that every trajectory reaches a pair terminal.
- Baseline `p0=1110/1499`. The fixed true hot pair is blocks 8 and 9, each at `p0+δ`; blocks 10–13 remain at `p0`. Equal group sizes make the choice of true pair exchangeable; the test still scans all 15 pairs.
- Effect sizes: `δ ∈ {0.01, 0.02, 0.03}`.
- For each effect, simulate 200,000 independent six-count datasets from the stated binomial model using NumPy PCG64 seeds 20261010, 20261011, and 20261012, respectively. No outcome-dependent stopping or replacement draws.
- On every dataset, apply the exact conditional procedure from `tools/w8_conditional_exact.py`: for each candidate pair, compute the one-sided `Hypergeom(6n, K, 2n)` upper tail, where `K` is the six-group success total; apply Bonferroni over all 15 pairs; reject iff adjusted `p < 0.05`. With equal denominators, the smallest pair tail is attained by the two largest group counts, but the implementation must verify this equivalence against enumeration on fixed synthetic inputs.
- Estimate power as the rejection fraction; report its 95% Wilson interval. The interval quantifies Monte Carlo error only, not uncertainty in `p0`, model choice, simulator fidelity, or physical replication.
- Validate SciPy's survival-function value against the repository's exact integer-combinatorial helper for deterministic sample inputs before simulation. Record NumPy/SciPy versions, RNG, seeds, counts, and the exact test command.

## Interpretation and limits

Compare δ=.02 and .03 against the earlier registered Pearson design powers (0.842 and 0.997 at n=5,000). Any difference is a calibration result for these two specified tests and alternatives, not evidence that the observed windows differ or match. The test's conditional null remains the common-rate null; the alternatives assume independent binomial outcomes, fixed baseline `p0`, equal denominators, exactly two elevated windows, and no extra block-level dispersion. Do not revise the observed `HETEROGENEITY_NOT_DETECTED` verdict, calculate a post-hoc physical-replicate claim, or publish a blog from this analysis alone. No new kinetic trajectories, cluster job, wet-lab work, collaborator contact, or paper/preprint submission is planned.
