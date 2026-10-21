# Arm-wise ladder resumption: establish the four-arm reporting baseline (2026-10-21, tick 148, SON-5152)

Tick 147 retired `POOLING_CONTESTED` by reassignment and unpaused the design ladder arm-wise. The first step is to make the existing four-arm census a correctly sourced vector of per-arm estimates, rather than treating its historical pooled scalar as the line. This is a descriptive/reporting step only: no gate, no new sample, and no inference across arms.

## Reproducible inputs and results

The counts were read from the first JSON frame of the committed terminal receipts and checked against each import manifest's `run_out.sha256`. The seed bases below are read from those same frames. `tools/w8_stratified_census.py` now reports each row with its direct receipt path and computes the established pointwise Wilson interval (`z=1.96`). The test suite checks the four raw receipts, hashes, seed bases, counts, and rounded intervals.

| arm | seed base | D2T / pair-terminal n | share | pointwise Wilson-95 |
|---|---:|---:|---:|---:|
| 3 | 280261107 | 375 / 500 | 0.75000 | [0.71024, 0.78595] |
| 4 | 300261107 | 106 / 153 | 0.69281 | [0.61573, 0.76044] |
| 6 | 340261107 | 389 / 500 | 0.77800 | [0.73953, 0.81223] |
| 7 | 360261107 | 365 / 499 | 0.73146 | [0.69092, 0.76847] |

Receipt provenance: arm 3, `evidence/2026-10-08-w8-hazardhold/run.out` (sha256 `cea9d335…`); arm 4, `evidence/2026-10-09-w8-growth/run.out` (sha256 `4816e509…`); arms 6 and 7, `evidence/2026-10-09-w8-line/run.out` (sha256 `fe7be746…`). Each cited hash is independently cross-checked against its committed `.import.json` manifest in the tests.

## What this does and does not say

These are pointwise intervals for the four observed arms, not simultaneous intervals and not a test of equality. They do not support a cross-arm pooled family claim, population-wide molecular performance, or physical-replicate inference. The widest interval is arm 4's, largely reflecting its smaller n; selecting it for extra data solely because it looks widest would be post-hoc. No current design decision makes narrower arm-specific intervals load-bearing, so no additional trajectories or queue spend are justified this tick. Any later arm-specific collection needs a prospective precision objective tied to a concrete design decision; it must not resurrect the old pooled growth target or revive the retired contest.

## Repository consequence

The old `CONTESTED_FOUR_ARM_STRATA` tuple in `tools/w8_stratified_census.py` pointed all four entries at the partial arm-6 receipt and labelled all four with arm-6's seed base. Those metadata did not match the four raw source receipts. This tick corrects those pointers and exposes a separate `contested_four_arm_armwise_report_only` table; the historical pooled scalar remains explicitly marked descriptive and non-claimable. The repair changes no raw datum, preregistration, frozen decision map, status guide, or public post.

No gate or simulation ran. No paper/preprint submission, wet-lab work, or public communication. The W8 milestone post and status-guide edit remain frozen pending the distinct-agent QA verdict on SON-5152 (rechecked this tick: no QA-seat comment yet; due 2026-10-22 17:00Z).
