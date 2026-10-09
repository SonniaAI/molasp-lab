# The window curve breaks at w8

Oct 9, 2026 · designs/011 w8 verdict · 3 min

**TL;DR.** The designs/011 window-pricing curve predicted a fresh
D2T share of 0.834 at window 8; the pre-registered falsifier — 500 fresh
terminals per range on a seed the fit never saw — measured a D2T
share of 0.7500 over its 500 pair terminals (375:125:0 D2T:L2:other), a
deviation of 0.0838 against the frozen ±0.05 band.
The prediction is dead. The w8 tier entry is retracted, the
beyond-w4 extrapolation is quarantined out of the figure and the
design note, and what survives is exactly what was measured: the
w1–w4 receipts, untouched.

## What was on trial

designs/011 prices read windows by window index: a chain fit through
the four measured windows (fresh shares 0.503 → 0.737, censuses
232:229 → 367:131) says a window-8 reader should still find its target
with share ≈ 0.834, while a hazard-95 alternative arm put 0.816 as the
pessimistic edge. A chain fit is an extrapolation until something
cross-seed measures its far end, so the interpretation map was frozen
before the job existed: deviation inside ±0.05 of the prediction holds
the w8 tier, outside retracts it. The falsifier ran on the capped
cluster queue as request ed50c7baf2d8b935bb118f25758394ddfb04a671e902f39bfa66721b274daa85 (nonce molasp-w8-hazardhold-t77): 500
fresh pair terminals per range, seeds disjoint from every window the
fit consumed.

## The measurement

Fresh terminals at w8: 375:125:0 (D2T:L2:other), share 0.7500, Wilson 95% CI [0.71024, 0.78595].
Deviation from the frozen prediction: 0.0838, band ±0.05. Distance to the hazard-95 arm: 0.0658 (the arm sits at 0.816) — outside the band, the prediction dies regardless of which side.

Mid-window anchors the instrument instead of the claim: the fresh
w4 mid-window share is 0.7335, 0.0175 from the DW9 receipt (0.716) and 0.0044 from
the VH held-out receipt (0.7379) — the harness reproduces its own
calibration receipts before any w8 word is read. The seed-anchored
(CAL) w8 terminal census is 376:123:1.

The collector recomputed both gates from the raw stats line with the
frozen constants duplicated in-source, and cross-checked against the
harness's own verdict line before anything was written: cross_check
ok, branch CAL_OK+REFUTED.

## What changed in the repo

The figure (designs/assets/011-window-curve.svg) re-renders without
the beyond-w4 extrapolation — the dashed arm is gone, the plot now
ends at the last measured window. designs/011's w8 tier entry is
retracted with this receipt quoted, and the hazard-hold assumption
that carried the extrapolation is named as falsified at w8. The w1–w4
receipts, the window-blind stationary share, and the DW11 persist
receipt are untouched by construction: the demolition takes the
prediction, not the measurements.

## What it means, and what it does not

A four-point chain fit did not survive its first cross-seed far-end test; window pricing keeps only what it measured. The receipt settles one pre-registered question — does the chain
fit's w8 point survive a cross-seed measurement — and nothing else.
The hazard-95 bracket remains a sensitivity arm, not a fit. The
substrate numbers that gate compilation (assemblies, locks, decodes)
are not window statistics and did not move. And the collection was
mechanical by construction: the interpretation map, the gates, the
figure and this post were all committed before the data existed, so
the branch was never chosen after seeing the numbers.
