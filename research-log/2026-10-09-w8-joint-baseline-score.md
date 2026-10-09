# W8 baseline-aware profile-score limit for the registered two-hot shape

Date: 2026-10-09 · SON-4949. This is a secondary, post-result analysis of
the six-window tick-103 counts. It adds no trajectories and does not change
the registered `HETEROGENEITY_NOT_DETECTED` primary result.

## Question and model

Tick 104's 4-baseline/2-hot noncentral-chi-square map held historical
`p0=1110/1499` fixed; tick 105 varied that plug-in value over a Wilson
interval but did not propagate baseline uncertainty. Here I profile the
baseline jointly with the hot-window contrast under the specified model:
the historical pool and four candidate cold windows share probability
`p`, and the other two windows share `p+delta`.

For each of the 15 possible hot-window pairs, aggregate the 1,499 historical
trials with the four cold windows, then compare that binomial count with the
two hot windows' aggregated count. For a fixed `delta`, maximize the joint
two-binomial likelihood over `p` subject to `0 <= p <= 1-delta`. Invert the
one-sided efficient-score test at z=1.64485362695. Report the maximum upper
endpoint over all 15 pair assignments, so the pair is not selected to
produce a narrower limit. This is a nuisance-profile binomial analysis, not
the earlier noncentral-chi-square mapping.

## Measured output

- Candidate assignments: 15.
- Narrowest assignment-specific nominal upper endpoint: `delta=0.0008329193`
  for blocks 8 and 11.
- Selection-conservative envelope: `delta=0.0136728784` (1.3673 percentage
  points) for blocks 9 and 13. This is the headline limit for the specified
  four-cold/two-hot model when the hot pair is unknown.
- The profile-score equation at the envelope endpoint returns
  `z=-1.64485362695`, confirming the numerical inversion.

Implementation: `tools/w8_joint_baseline_bound.py`; four new unittest pins
in `tests/test_w8_joint_baseline_bound.py`. The exact repo CI command
`python3 -m unittest discover -s tests -v` passed: `Ran 727 tests in
10.636s / OK (skipped=1)`.

## Scope and interpretation

This endpoint profiles the shared base rate instead of treating the
historical 1110/1499 estimate as known. Taking the maximum across candidate
pairs makes the reported endpoint selection-conservative under the stated
two-hot model: it is no smaller than the endpoint for the actual pair.
However, the one-sided score calibration is asymptotic, so this is a
**nominal model-conditional limit, not an exact finite-sample 95% guarantee**.
It covers neither arbitrary six-window heterogeneity nor a common shift of
all windows, and the historical/cold pooling assumption may fail if their
rates differ. It does not prove identical seed windows or say anything
about physical molecular replicates. Keep the registered omnibus verdict
unchanged; no blog, external claim, paper/preprint, or wet-lab step is
warranted from this exploratory bound alone.
