# 2026-10-06 — Cage kTAM: the ratio falsifier fires (tick 12)

**Question.** Tick 11's lemma amendment predicts for the maximally-blind
cage: correct completion ~e^{−2·dG}, wrong completion ~e^{−3·dG},
wrong/correct ~e^{−dG} ("the SAME ratio as v2.1"). Falsifier: wrong
completions at or above e^{−2·dG} with correct completion within
e^{−dG} of v3's rate refutes the lemma.

**Prediction bug found before running.** In `tiles_v3p.py`, D2F and D2T
are bond-arithmetic identical: each bonds only W=go2 into S2.E (b=1),
and after L2's arrival each sits at b=2 the same way; cap3/no-p (S
faces) and topF/topT (N faces) are unique-name inert. The e^{−3·dG}
arithmetic modeled only the D1F (row-1) channel and assumed row-2 wrong
paid an extra coincidence window. It does not: the unfounded completion
`ap` is the correct completion with the other coin face — whichever of
D2F/D2T is resident when L2's b=2 catch locks the overlap is a fair
race at equal attach rates.

**Method.** Identical protocol to the v2.1/v3 grids (`ktam_mc_v3p.py`:
Gse=9, Gmc ∈ {9.5, 11, 13, 16}, T_read = 400·e^{Gmc}, n=500/point,
no-mismatch kTAM, seeds printed, raw `run.out`). Reference curves
e^{−dG}/e^{−2·dG} and the co-residency budget guide
1−exp(−400·p_L1·p_row2), p_L1 = 1/(1+e^{dG}), p_row2 = 2/(2+e^{dG}),
printed per point.

**Measured (`run.out`).**

- dG=0.5: a 229, ap 232, p 20, empty 18, partial 1 — wrong/correct
  1.18, ap/a 1.01. The wrong row-1 channels survive only here.
- dG=2: a 255, ap 230, partial 15 — wrong/correct 0.90. Falsifier
  fires: wrong 0.46 ≥ e^{−4} = 0.018 (25x) while correct 0.51 ≥
  v3 0.996 × e^{−2} = 0.135.
- dG=4: a 27, ap 25, partial 448 — wrong/correct 0.93. Falsifier
  fires: wrong 0.05 ≥ 3.35e-4 (149x) while correct 0.054 ≥ 0.018.
  Completion 0.104 vs budget guide 0.22: the independence approximation
  overestimates ~2x — the L2 catch needs simultaneity, and occupancies
  anti-correlate through the shared window.
- dG=7: 0/500 complete, all partial — budget 7e-4; ratio unmeasurable.
- Totals over 2000: a 511, ap 487 — the fair-coin symmetry, 1.05:1.

**Verdict.** Refuted as arithmetic, confirmed and sharpened as lemma.
The wrong ~e^{−3·dG} prediction misses by orders of magnitude (measured
wrong 0.46 at dG=2 vs 2.5e-3 predicted; 0.05 at dG=4 vs 6.1e-6), and
wrong/correct is ≈1 at every measurable point, not e^{−dG}. The D1F
channels the old arithmetic modeled are near-dead at scaled read (empty
18/2000, p 20/2000, all at dG=0.5): D1T's τ-residency lands the founded
row-1 value ~surely within T_read, so wrong row-1 loses by arrival
race, not by locking. The lemma's core survives strengthened: value-
agnostic locking cannot push the error/throughput ratio below O(1) —
partial blindness gives v2.1's e^{−dG}; full blindness collapses the
ratio to unity because wrong and correct become the same process with
different labels. Value-typing (v3: 0/2000 wrong, no growth penalty,
aTAM intact) is the only separation mechanism. And correct completion
itself pays the trade (0.458 / 0.510 / 0.054 / 0 across the grid) —
e^{−2·dG} as a rate paid equally by both channels, now measured rather
than argued. This is the kinetic mirror of foundedness demonstrated at
both limits: geometry moves error ratios, kinetics cannot.

**Status.** Unreviewed notebook promotion per lab convention. No
C-claim advanced; C2 unchanged. CI pins the structural identity
(D2F/D2T bond-identical), the budget-curve arithmetic, a small
fixed-seed symmetry run, and the run.out verdict rows
(`tests/test_cage_ktam_ratio.py`).
