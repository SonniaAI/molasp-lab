# 2026-10-13 — w8: exact-Šidák calibration of the simultaneous bands (tick 125)

**Status while writing:** blockpower arbitration request `d3aa0acaa37ff4c9…`
(job hxq-d3aa0acaa37ff4c9, nonce molasp-w8-blockpower-t120-a) still
`queued: resource/owner limit` — probed once this tick at 22:5xZ; no
resubmit, no ceiling-raise. This is a never-idle planning increment on
the PAUSED ladder: zero kTAM trajectories, no gate executed, pooled
contested line stays REPORTED-NOT-CLAIMABLE.

## Question

Tick 124 (548234b) priced Bonferroni-Wilson simultaneous per-stratum
bands: family-0.95 simultaneity costs **1.3458× (m=6) / 1.2700× (m=4)**
per-stratum width over nominal Wilson-95. How much of that price is
*correction slack* that a smarter correction could reclaim?

## Method

The strata are **independent by design** (disjoint seed bases / disjoint
blocks feed each stratum — true in both frozen worlds and in the real
readout). For independent strata the *exact* simultaneous calibration is
Šidák: per-stratum two-sided level 1−α′ with α′ = 1−(1−α)^(1/m), giving
family miscoverage exactly α in expectation, strictly tighter than
Bonferroni's α/m. Module `tools/w8_sidak_band.py` (stdlib-only, tick-123
CI rule):

- `sidak_z(m)`: z_Šidák = Φ⁻¹(1−α′/2). z₆ = 2.6310382845 vs z_Bonf₆ =
  2.638257273; z₄ = 2.4909151310 vs 2.497705474.
- **Paired MC** on the tick-123/124 datasets (seeds 20261013/20261014,
  4000 reps, identical `_BinomialCDF` draw rows; `first_draw_row`
  fingerprints pinned equal to tick 124's tests).
- **Real-data readout**: per-stratum Wilson at nominal/Bonferroni/Šidák
  on the frozen six-window (m=6) and contested four-arm (m=4) counts —
  the concrete simultaneous-band table the branch map reports once
  blockpower adjudicates.

## Numbers (all pinned in `tests/test_w8_sidak_band.py`, 20 pins)

Paired MC, same 4000 datasets as tick 124 (tick-124 values recompute
exactly on the shared data — nominal 0.73675/0.81625, Bonferroni
0.94975/0.95275, width ratios 1.345752…/1.270049…):

| quantity | world A (m=6) | world B (m=4) |
|---|---|---|
| all-strata coverage, Wilson-at-z_Šidák | 0.949 | 0.95275 |
| min per-stratum coverage (Šidák) | 0.9895 | 0.9865 |
| mean width ratio Šidák/nominal | 1.34207 | 1.26666 |
| mean width ratio Bonferroni/Šidák | **1.002741** | **1.002678** |
| z ratio Bonferroni/Šidák (exact) | 1.0027438 | 1.0027260 |

Real-data readout (family 0.95, per-stratum Šidák-Wilson):

- six-window: block8 [0.7120966, 0.7451618], block9 [0.7250807,
  0.7576440], block10 [0.7218738, 0.7545619], block11 [0.7184099,
  0.7512338], block12 [0.7228380, 0.7554911], block13 [0.7233402,
  0.7559796].
- contested four-arm (descriptive only): arm3 [0.6988980, 0.7949734],
  arm4 [0.5939132, 0.7766789], arm6 [0.7284554, 0.8207295], arm7
  [0.6794220, 0.7778185].

## Findings

1. **The Bonferroni price is essentially irreducible.** At m=6/m=4 the
   independence-exact Šidák calibration reclaims only **0.27%** of
   per-stratum width. Tick 124's 1.3458×/1.2700× simultaneity price is
   not correction slack; the width lever is per-stratum n, not the
   choice of correction. Bonferroni remains the sensible default since
   it needs no independence assumption and costs ≤0.3% extra.
2. **Realized family level of Wilson-at-z_Šidák is approximate**, as
   pre-stated: world A realizes 0.949 (inside ±0.0068 MC error; same
   flavor as tick 124's honest Bonferroni catch at 0.94975). Šidák's
   exactness assumes *exact* per-stratum intervals; Wilson's O(n⁻¹)
   discreteness deviations and MC realization both move the fixed-seed
   value. Claim kept in-expectation, realization pinned.
3. **Branch-map consequence:** when blockpower adjudicates, the
   simultaneous readout is the table above; Bonferroni-Wilson (not
   Šidák) stays the house authority — the ≤0.3% saving does not justify
   an independence premise in a report that must survive contested
   provenance. Šidák is recorded as the optimality certificate bounding
   what any correction could reclaim.

## Guardrails

Šidák must not be reused for overlapping/reused-seed strata. Zero
trajectories; no gate; ladder stays PAUSED; nothing here is a
physical-replicate claim.
