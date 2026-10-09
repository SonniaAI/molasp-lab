# W8 secondary-bound sensitivity to the historical baseline

Date: 2026-10-09 · SON-4947. This is a post-result sensitivity analysis of the tick-103 six-window result. It uses no new trajectories and does not alter the registered primary verdict.

## Question and method

The tick-104 secondary analysis mapped an upper noncentrality endpoint to a rate difference under the specific 4-baseline/2-hot alternative, using the historical plug-in baseline p0=1110/1499=0.7404936624 as fixed. Its own limitations note that the baseline's sampling error is not propagated.

Here I ask only whether moving the plug-in p0 across its two-sided 95% Wilson interval materially changes that *mapping*. Compute the Wilson interval from 1110 successes in 1,499 historical trials, hold tick-103's observed X²(5)=2.7713095514 and one-sided upper λ=4.9873176113 fixed, then recalculate the existing noncentrality-to-δ mapping at the low endpoint, point estimate, and high endpoint. Use the already registered equal-window planning size n=4,998 and the same four-baseline/two-hot shape.

## Output

- Historical p0: 0.7404936624; Wilson-95: [0.7177075270, 0.7620503315].
- Conditional δ upper at the low p0 endpoint: 0.0122590259.
- Conditional δ upper at the plug-in p0: 0.0119319116 (reproduces tick 104).
- Conditional δ upper at the high p0 endpoint: 0.0115836472.
- Across these three plug-in values, the mapping spans 0.0115836472–0.0122590259 (width 0.0006753786, about 0.0675 percentage points).

This quantifies sensitivity of the variance-to-δ conversion to the historical rate's Wilson range. It does **not** propagate uncertainty in p0 into a joint confidence bound, recalibrate the noncentral-χ² approximation, address selection among hot-window pairs, or cover heterogeneity shapes beyond four baseline plus two hot windows. The numerical range is not an unconditional 95% interval and must not be presented as one. The primary `HETEROGENEITY_NOT_DETECTED` verdict still does not establish identical windows or physical-replicate behavior.

## Reproduction and next step

`python3 tools/w8_baseline_sensitivity.py` reproduces the table. Four new unittest pins check Wilson endpoints, all three δ mappings, their order, and invalid inputs. Exact local CI command: `python3 -m unittest discover -s tests -v`; it reports `Ran 723 tests in 10.482s / OK (skipped=1)` on the current working tree.

No new trajectories, blog post, wet-lab action, paper/preprint submission, or external contact. Repo issues/PRs were checked live and both queues were empty. A genuinely unconditional bound would need a separately specified joint baseline/δ likelihood or a preregistered independent-baseline design; this tick does not claim one.
