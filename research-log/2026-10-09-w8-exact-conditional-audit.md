# W8 two-hot family: exact conditional finite-sample audit

Date: 2026-10-09 · SON-4949. This is a post-result secondary test of the existing six-window data, not a pre-registration predating data collection. Its analysis plan was committed first in `research-log/2026-10-09-w8-exact-conditional-prereg.md` (commit `56c8d4d`), before calculating the conditional tails.

## Result

The six current windows contain 22,111 D2T outcomes among 29,989 pair-terminal trials. For each of the 15 possible two-hot/two-window groups, the one-sided conditional tail was computed from the exact hypergeometric law under the common-rate null, conditional on the total success count. The smallest raw tail is **0.165759251604651**, for blocks **9 and 13** (7,404 / 9,994). The frozen Bonferroni adjustment across 15 candidate pairs is **1.0** after capping at one; at alpha 0.05 the test does not reject the common-rate null.

| Candidate hot blocks | Hot D2T / trials | Exact conditional upper tail |
|---|---:|---:|
| 9, 13 | 7404 / 9994 | 0.165759251605 |
| 9, 12 | 7403 / 9996 | 0.183518685687 |
| 9, 10 | 7399 / 9997 | 0.220651371575 |
| 12, 13 | 7393 / 9994 | 0.253185987697 |
| 10, 13 | 7389 / 9995 | 0.297189041582 |
| 10, 12 | 7388 / 9997 | 0.321485570368 |
| 9, 11 | 7382 / 9997 | 0.383441291423 |
| 11, 13 | 7372 / 9995 | 0.476433956331 |
| 11, 12 | 7371 / 9997 | 0.503899983030 |
| 10, 11 | 7367 / 9998 | 0.556306951367 |
| 8, 9 | 7351 / 9997 | 0.714373928085 |
| 8, 13 | 7341 / 9995 | 0.789100146335 |
| 8, 12 | 7340 / 9997 | 0.808410995286 |
| 8, 10 | 7336 / 9998 | 0.842240036718 |
| 8, 11 | 7319 / 9998 | 0.930030590858 |

## Verification and limits

`tools/w8_conditional_exact.py` evaluates the finite hypergeometric support with integer combinatorial weights, and `tests/test_w8_conditional_exact.py` pins the frozen six inputs, all 15 pairs, support boundaries, Bonferroni rule, and numerical results. The minimum tail was independently recomputed by direct integer-combinatorial summation (`Fraction(sum(C(K,x) C(N-K,m-x)), C(N,m))`), matching 0.165759251604651. The exact CI command `python3 -m unittest discover -s tests -v` passed: `Ran 737 tests in 20.657s / OK (skipped=1)`; all six new test methods appeared in verbose discovery.

This finite-sample test only addresses the directional two-hot family under the common-rate null. It is not an exact confidence interval for delta and does not cover arbitrary six-window heterogeneity. It does not change the original preregistered Pearson result `HETEROGENEITY_NOT_DETECTED`, the nominal/asymptotic interpretation of the score endpoints, or any claim about physical molecular replicates. No new trajectories or cluster job, blog, wet-lab work, paper/preprint, or external contact.
