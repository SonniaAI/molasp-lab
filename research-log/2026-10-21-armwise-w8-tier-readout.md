# Arm-wise w8 tier readout: the 0.75 label is not interval-stable (2026-10-21, tick 149, SON-5152)

The tick-148 restart made the four w8 terminal counts reportable per arm, with receipt provenance and pointwise Wilson-95 intervals. This tick asks the next bounded design question: do design 011's existing descriptive window-tier labels assign a stable tier to any individual w8 arm?

`tools/w8_armwise_tier_readout.py` applies the existing `window_tier` boundaries from `designs/011-window-indexed-marginal-pricing.md` to each arm's point estimate and Wilson interval. It reads the frozen, receipt-pinned summary in `tools/w8_stratified_census.py`; it runs no trajectories.

| arm | D2T / pair-terminal n | share | point label | pointwise Wilson-95 | labels intersected by interval |
|---|---:|---:|---|---:|---|
| 3 | 375 / 500 | 0.75000 | ratchet-tilted | [0.71024, 0.78595] | ratchet-tilting; ratchet-tilted |
| 4 | 106 / 153 | 0.69281 | ratchet-tilting | [0.61573, 0.76044] | ratchet-tilting; ratchet-tilted |
| 6 | 389 / 500 | 0.77800 | ratchet-tilted | [0.73953, 0.81223] | ratchet-tilting; ratchet-tilted |
| 7 | 365 / 499 | 0.73146 | ratchet-tilting | [0.69092, 0.76847] | ratchet-tilting; ratchet-tilted |

## Interpretation and boundary

All four point estimates exceed design 011's 0.55 lower boundary, but every pointwise interval crosses the 0.75 boundary. Thus the point labels differ by arm, yet none is stable across its own pointwise interval; the evidence does not support assigning one tier robustly to an arm. This is a descriptive threshold-sensitivity result, not a test of tier equality or a simultaneous family statement. The intervals remain pointwise, not simultaneous, and no pooled family claim is revived.

This does not restore design 011's retracted w8 extrapolation gate or change the W8 verdict. The w8 tier cutoffs are labelled choices, not inferential thresholds. Since no current design decision requires narrower arm estimates, no new sampling or queue spend is justified. Any future arm-specific collection needs a prospective precision target tied to a concrete decision before data are collected.

The four counts and Wilson endpoints are pinned by `tests/test_w8_armwise_tier_readout.py`; the full input provenance remains checked by `tests/test_w8_stratified_census.py`.
