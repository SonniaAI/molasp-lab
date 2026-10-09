# W8 profile-score sensitivity to historical/current exchangeability

Date: 2026-10-09 · SON-4949. This post-result sensitivity analysis reuses tick-103 counts; it adds no trajectories and leaves `HETEROGENEITY_NOT_DETECTED` unchanged. The analysis was pre-registered in `research-log/2026-10-09-w8-history-baseline-prereg.md` before computing the endpoints.

## Model and method

Tick 106 pools historical 1110/1499 with the four current candidate cold windows. Here the historical baseline is allowed a separate, unrestricted rate. Under that model its likelihood factorizes from the current-window contrast, so the historical count contributes no information to the hot-minus-cold difference. For each of 15 candidate hot pairs, the calculation therefore aggregates only the four current cold windows and two hot windows, then inverts the same constrained-binomial efficient-score test at z=1.6448536269514722.

This still assumes a common current cold rate and a common rate for the selected hot pair. The one-sided score calibration is nominal/asymptotic, not an exact finite-sample confidence guarantee.

## Measured output

- The 15 current-only upper endpoints range from `0.0009771071` (blocks 8,11) to `0.0141265773` (blocks 9,13).
- The maximum current-only endpoint is `0.0004536989` (0.0454 percentage points) above tick 106's historical-pooled envelope `0.0136728784`. Relaxing historical/current exchangeability therefore modestly widens this particular model-conditional upper endpoint; it does not erase or establish a general bound.
- All 15 inverted endpoints return the registered lower-tail score `z=-1.644853626951` within numerical tolerance. The independent-history implementation does not include the historical count in either current group.

Implementation: `tools/w8_independent_history_bound.py`; four unittest pins in `tests/test_w8_independent_history_bound.py`. Exact repo CI command `python3 -m unittest discover -s tests -v` passed: `Ran 731 tests in 10.877s / OK (skipped=1)`. All four new test methods appear in verbose discovery.

## Interpretation boundary

This is a sensitivity analysis for historical/current baseline pooling under the specified two-hot model, not a test that the historical and current baseline rates are equal. It still relies on pooling four current windows into one cold group, does not cover arbitrary six-window heterogeneity or common shifts of all six windows, and says nothing about physical molecular replicates. Keep the registered omnibus verdict unchanged. No blog, external claim, paper/preprint, wet-lab work, or external contact follows from this result alone.
