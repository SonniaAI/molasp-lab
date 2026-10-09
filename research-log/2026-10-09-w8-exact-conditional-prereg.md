# W8 finite-sample conditional audit — analysis plan

Date: 2026-10-09 · SON-4949. This is a post-result secondary analysis plan, frozen before calculating any conditional tail probabilities. The six-window data are already public in the repository; this is not a preregistration that predates data collection and does not replace the original Pearson test.

## Question and scope

For the registered six current windows, how does a finite-sample test of the pre-existing two-hot-versus-four-cold contrast compare with the nominal asymptotic score sensitivity? The candidate hot pair is selected from all 15 pairs, so selection must be included in the test calibration.

This is a conditional test of the global common-rate null against the *family* of directional two-hot partitions. It is not an interval for the rate difference, not an omnibus test against every possible six-window pattern, and not evidence about physical molecular replicates.

## Frozen inputs

Use only the six pair-terminal D2T counts and denominators in the tick-103 collection:

- block 8: 3644 / 4999
- block 9: 3707 / 4998
- block 10: 3692 / 4999
- block 11: 3675 / 4999
- block 12: 3696 / 4998
- block 13: 3697 / 4996

No historical arms, other-terminal states, or later-selected subset enter this audit. The tick-103 primary `HETEROGENEITY_NOT_DETECTED` result and all prior records remain unchanged.

## Exact conditional procedure

For each of the 15 choices S of two candidate hot blocks, let `X_S` and `N_S` be their combined D2T successes and pair-terminal trials; let `K` and `N` be the corresponding totals across all six blocks. Under the global common-probability null, conditional on K, `X_S` has the hypergeometric distribution `Hypergeom(N, K, N_S)`. Compute the one-sided tail `p_S = Pr(X >= X_S | N, K, N_S)` using the complete finite support of that distribution.

Control selection by the frozen Bonferroni rule `p_FWER = min(1, 15 * min_S(p_S))`; compare with alpha 0.05. Report the minimum unadjusted tail and its pair, the adjusted value, and all 15 tails. The resulting test has finite-sample conditional familywise error control under the common-rate null. The numerical implementation may use floating-point log probabilities, but tests must cross-check it against direct combinatorial probabilities on small supports.

Interpretation is restricted to this test family: adjusted p below 0.05 would reject the common-rate null in favor of at least one two-hot partition; otherwise report no detection by this test, not evidence of equality. It is a secondary finite-sample hypothesis test, not an exact confidence bound for delta and not a substitute for the preregistered Pearson omnibus result.

## Implementation and reporting gates

Implement a standard-library-only helper, validate inputs and support boundaries, and pin the small-support distribution plus the fixed six-window input. Then run it once on the frozen counts and independently check the returned 15-pair family adjustment. Record every result and caveat in a separate dated research log. Run the exact CI command `python3 -m unittest discover -s tests -v` and verify the new test names appear. No new trajectories or cluster job are needed. Do not publish a blog, contact collaborators, perform wet-lab work, or submit a paper/preprint on the strength of this secondary audit alone.
