# Per-row kTAM grid — 3-row systems under the v3 protocol (tick 15)

**Date:** 2026-10-06 · **Evidence:** `evidence/2026-10-06-multirow-ktam-grid/`
(`ktam_mc_multirow.py`, `run.out`; tile systems imported unchanged from
ticks 13–14) · **Status:** measured this tick, unreviewed promotion.

## Question

Designs/002 established, at aTAM (τ=2, zero temperature), that the
3-row 2-cycle system and the three anchored-cycle builds terminate in
exactly their predicted decodes. Tick 14's criterion 4: no wrong build
decodes the stable model `{a,p,q}` — stage order and cut discipline
are load-bearing. This tick runs the same systems under the v3 kTAM
protocol (Gse=9, Gmc ∈ {9.5, 11, 13, 16}, T_read = 400·e^Gmc,
n=500/point, no-mismatch, identical rates to the C2 grids), with
pre-registered predictions P1–P4 in the harness header.

## Results (all from `run.out`, strict decode = spine + all decision
sites + all lock sites filled)

| system | dG=0.5 | dG=2 | dG=4 | dG=7 |
|---|---|---|---|---|
| 2cycle (exp `{a}`) | 433 a / 13 apq / 54 partl | 466 a / 1 apq / 33 partl | 496 a / 0 / 4 | 425 a / 0 / 75 |
| anchored CORRECT (exp `{a,p,q}`) | 500 apq | 499 apq / 1 partl | 495 apq / 5 partl | 433 apq / 67 partl |
| WRONG_CUT (aTAM: `{a,p}`) | **500 apq** | **496 apq** / 1 ap | **363 apq** / 137 partl | 3 apq / 497 partl |
| WRONG_ROWS (aTAM: `{a}`) | 500 partl (loose: 479 a) | 500 partl (loose: 495 a) | 500 partl (loose: 494 a) | 500 partl (loose: 494 a) |

## Findings

**F1 — suppression carries across rows (P1, P2 hold).** 2-cycle
strict wrong total 14/2000 (13 at dG=0.5, 1 at dG=2, 0 elsewhere),
every point at or below the e^{-2dG} envelope (dG=2: 0.002 vs 0.018).
Anchored CORRECT: 0/2000 wrong complete decodes at every point. The
per-row value typing of v3 extends to depth 3 without a new error
channel. First non-zero strict wrong counts in the v3 family
(previously 0/2000 on C2): the extra rows add an `{a,p,q}` channel at
fast kinetics (loose — unlocked transients at read — runs 67/32/0/0
per 500, so locks+detach filter ~30x of transients before read).

**F2 — the cut is not kinetically load-bearing (P3 fires, benign
direction).** WRONG_CUT strict-decodes the true stable model
`{a,p,q}` at 100% / 99.2% / 72.6% for dG ≤ 4. Mechanism (pinned
structurally in `tests/test_multirow_ktam.py`): the cut kills only the
south glue of q's true tile (`u-cut`, inert); its value outputs stay
intact and the lock chain below is value-complete — L3 bonds `rq-t`
(west) and `base3` (south, L2's north). The aTAM-dead tile rides a
b=1 transient into a b=2 locked terminal. The wrong compile
**self-corrects** to the stable model: same family as tick 14's
growth-dead variants (value-equivalent, lock-compatible), now with a
measured kinetic payoff. Honest boundary, untested: this build's L3
bonds the fixpoint-true value `rq-t`; a compiler that re-predicted
q=false after cutting would emit lock-on-`rq-f` and would presumably
capture `{a,p}` instead — the cut's kinetic fate is decided by the
lock's value typing, not by the cut. That variant is the natural next
build.

**F3 — the row order is kinetically load-bearing.** WRONG_ROWS:
0/2000 strict decodes of any kind; loose decode reads `{a}` (empty
upper rows) in ~99% at every dG. The swapped lock rows mismatch every
south face above row 1 (L3.S=`base2` vs L2.N=`cap3`; L2.S=`base3` vs
L1.N=`base2`), so no lock above row 1 can reach b=2 — the kTAM value
channel exists (D3TQ bonds row 2's transient `rq-t-done`) but
dead-ends without lockable south faces. Geometry kills what value
typing cannot.

**F4 — depth's read-time cost is mild (P4, measurement).** At dG=7
the partial (growth-incomplete at read) fraction is 0.150 (2cycle) /
0.134 (CORRECT) vs the 2-row C2 baseline 0.128: a 1.05–1.17x growth,
not a blow-up — the 400·e^Gmc rule mostly absorbs the third row. The
2cycle partial curve is U-shaped (0.108 → 0.066 → 0.008 → 0.150):
dead-row churn dominates at fast kinetics, growth starvation at slow.

## Taxonomy after this tick

| error family | aTAM | kTAM | mechanism |
|---|---|---|---|
| wrong VALUE (v3 falsifier) | dead | dead (0/2000, tick 5) | un-lockable: b=1 everywhere |
| wrong CUT (support severed) | dead | **captured → stable model** | value outputs intact + lock chain value-complete |
| wrong ROW ORDER (geometry severed) | dead | dead (0/2000 strict) | lock south faces mismatched, no b=2 |

## Limits

Unreviewed promotion; single n=500/point grid; no mismatch errors
modelled (protocol constant since the v2.1 grid); the WRONG_CUT
lock-on-false variant (F2 boundary) not yet built; per-row kTAM on
the 2cycle's own rows (not just grid-level) not decomposed.
