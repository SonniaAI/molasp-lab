# w8 fit-parameter sensitivity — pre-registered before the datum

Date: 2026-10-09 (tick 87, SON-4885). Registered BEFORE the w8
falsifier datum exists: instrument request `ed50c7ba…4daa85` still
queued (ci admission floor, probed 01:48Z this tick). Tool:
`tools/w8_param_sensitivity.py`, 12 pins in
`tests/test_w8_param_sensitivity.py`; suite verbatim `Ran 542 tests /
OK (skipped=1)` = 530 + 12.

## What this adds over tick 86

Tick 86 (`2026-10-09-w8-extrapolation-sensitivity.md`) priced the
EXTRAPOLATION-FORM axis — how hazards evolve beyond w4 — and found the
form spread (0.20609) dominates the frozen band. This note prices the
other axis it named but did not number: FIT-PARAMETER sensitivity —
what happens to w8 when the committed `VH_BASIS` parameters themselves
move, (i) within the one quotable measured-receipt uncertainty (the w1
census split) and (ii) at labelled arithmetic probe deltas/scales that
are NOT asserted confidence bounds (no receipt → no claim). The frozen
W8 gate and the five-step collection chain are untouched.

## Measured results

Baseline identity anchors: local chain reproduces `_vh_share(8)` and
0.83376 (≤5e-6), asserted in-tool.

| axis | probe | w8 | dev from 0.83376 |
| --- | --- | --- | --- |
| v0 census (Wilson-95, 232:229, n=461) | split lo 0.45777 | 0.82807 | −0.00569 |
| | split hi 0.54868 | 0.85288 | +0.01912 |
| attach odds (pair-sum fixed) | −0.04 | 0.81664 | −0.01712 |
| | −0.01 | 0.82963 | −0.00414 |
| | +0.01 | 0.83780 | +0.00404 |
| | +0.04 | 0.84939 | +0.01563 |
| haz_l2[4] scale | ×0.5 | 0.77699 | **−0.05677 — below frozen floor 0.78376** |
| | ×0.75 | 0.80753 | −0.02623 |
| | ×1.25 | 0.85628 | +0.02252 |
| | ×1.5 | 0.87563 | +0.04187 |
| | ×2.0 | 0.90655 | **+0.07279 — above frozen ceiling 0.88376** |
| haz_d2t[4] scale | ×2 | 0.82614 | −0.00762 |
| haz_l2 grid (2–4) | ×2 | 0.94351 | +0.10975 |

Elasticities d ln s8 / d ln param (central difference, eps 1e-3):
**odds +0.255 > haz_l2[4] +0.116 ≫ haz_d2t[4] −0.009 ≈ lam 0.000**.

## Findings (pre-registered reading content)

1. **The one quotable fit uncertainty is subdominant.** The w1 census
   Wilson-95 bracket induces w8 width 0.02481 ≈ 0.50 band halfwidths,
   and the whole bracket stays inside the HELD region. Initial-condition
   uncertainty can neither create nor rescue a verdict.
2. **No odds miss at ±0.04 reaches refutation** (min probe 0.81664 >
   floor 0.78376). A REFUTED-low datum is therefore NOT explainable by
   initial conditions or a plausible attach-odds miss alone — it
   indicts the L2 leak rate itself (form or fit).
3. **haz_l2[4] is the dangerous parameter**: ×0.5→×2 spans 0.12956
   (2.6 halfwidths), crossing the floor between ×0.5 and ×0.75 and the
   ceiling above ×1.5; a coherent grid-wide ×2 fit miss reaches
   0.94351. Second only to the form spread (0.20609).
4. **lam cancels in the share by mechanism, not by dead code** (the
   tick-86 zero-sensitivity rule): lam scales every attach flux
   equally and the share is a ratio — stationary
   π_D2T:π_L2 = (p_D2T/d_d2t):(p_L2/d_l2) is lam-free. Guard: under
   lam ×2 the E-state mass at w8 halves (1.2190e-4 → 6.0930e-5,
   ratio 2.0007) while the share residual is 4.2e-5 (elasticity ~7e-5,
   four orders below odds). The perturbation provably reaches the
   computation; the output ratio does not move.
5. **Collection-day lookup**: for a REFUTED-low datum s, the tables
   above give which single-parameter moves can reach it (l2-scale
   ≲×0.6; nothing else quotable); for s inside the band, parameter
   space is not the discriminator — form is (tick 86 reading map).
   The region-3 follow-up design gains a second job: a DIRECT
   late-L2 hazard measurement disambiguates form-vs-fit
   simultaneously (it pins both).

## Method notes (two near-misses caught pre-landing)

- The lam cancellation first appeared as an exact 0.0 elasticity —
  treated as a bug smell per the tick-86 rule until the E-mass guard
  proved otherwise; the honest statement is "cancels to ~7e-5", not
  "exactly zero".
- Test bugs caught locally: parsing `%.4e` strings by splitting off
  the exponent dropped a factor of 10; a `places=3` tolerance was
  tighter than the measured 2.0007 ratio. Measure-then-claim applies
  to test tolerances and test parsing, not just science bands.
