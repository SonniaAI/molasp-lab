# Structural-death reassertion — a missing species is kinetically
# repaired except in the slow-growth window (tick 22, SON-4773)

Card: SON-4773. Build and receipts:
`../evidence/2026-10-06-structural-death/` (atam_death.out, run.out,
submit.out, result blob). Tests: `../tests/test_structural_death.py`
(suite 155 + 1 unskipped grid-receipt pin).

## Question

Tick 19 refuted K4's reassertion detector as a measurement: in an
always-completable positive program, growth-incompletion reads as a
subset of the true model by construction, so "kinetic reassertion of
the true model" is unmeasurable at a fixed read time. The named
honest successor: a structural-death build — remove one tile species
(no recompilation, so the d2/d3 emit-time checks are silent by
construction: this models a synthesis-time missing strand) and ask
whether the kinetics rebuilds the true-model readout anyway.

## Build

`tiles_death.py`: BUILD1 (P_AND `p. q. r :- p, q.`, errata E1/E2
applied) minus the single species DAr (r's slot-A reader). Glue
arithmetic, machine-verified by exhaustive tau=2 BFS (S1 receipt):
site (1,3) is permanently vacant (only DAr ever read q-t-done/go3
there); DBr and L3 can never attach (each retains one strength-1
south bond, tau=2 unreachable); the unique terminal is rows 1-2
complete + spine S3, lock decode ("pq", 2). Semantic anchor: {p,q}
is the stable model of `p. q.` — species-death reaches the
dropped-rule MODEL without re-layout.

kTAM is where the two separate: DBr and L3 each keep a b=1 south
bond and can attach transiently; once both sit in row 3 they
mutually stabilize (DBr.E=r-t bonds L3.W=r-t, each reaches b=2).
The pre-registration (ktam_mc_death.py header, written before the
run) asks: does that pair rebuild the full true-model strict decode
(S2), at what mechanism class and rate (S3), with build1 as
calibration (S4)?

## Measured (queue job hxq-eb04748e, paperclip-test, ~1 min wall)

Strict "pqr" fraction per 500 (protocol of record: Gse=9,
T=400·e^Gmc, n=500/point, seeds BASE 20261022):

| dG | dead pqr | build1 pqr | dead/build1 | dead trap split (dbr_l3 / l3_only) |
| --- | --- | --- | --- | --- |
| 0.5 | 0.442 | 0.542 | 0.82 | 158 / 63 |
| 2 | 0.658 | 0.790 | 0.83 | 307 / 22 |
| 4 | 0.726 | 0.984 | 0.74 | 359 / 4 |
| 7 | 0.006 | 0.872 | 0.007 | 3 / 0 |

Dead build at dG=7: loose decode "pq" in 496/500 (99.2%) — exactly
the dropped-rule stable model.

## Verdicts against the pre-registration

- **S2 PASSES (channel exists)**: dead strict "pqr" total 916/2000
  — nowhere near the 0-count falsifier. A structurally dead species
  IS kinetically bypassed: the substrate rebuilds the true-model
  readout through b=1 transients. This is completion-independent by
  construction (a strict decode needs spine + all three locks
  simultaneously; unfinished assemblies read "partial") — the
  confound that killed K4 does not exist here.
- **S3(i) PASSES (trapping class)**: dead "pqr" = 0.726 at dG=4 vs
  10·e^{-2dG} = 0.0034 — 213× above the value-typing error floor.
  Mechanism confirmed by the joint split: mutual-stabilization trap
  (dbr_l3) dominates everywhere except the fastest point (63/221
  transient-share at dG=0.5, 22/329 at dG=2, ≤1% from dG=4 up).
- **S3(ii) PASSES (kinetic invisibility)**: dead/build1 ratio
  0.82/0.83/0.74 at dG ≤ 4 — a missing species costs at most ~26%
  completion across the fast regime. The readout largely repairs
  the synthesis error.
- **S3(iii) (the lever)**: the repair is NOT flat in dG — it
  collapses at dG=7 (0.006), where the substrate instead reads the
  dropped-rule stable model {p,q} at 99.2%. The read window selects
  between kinetic repair and faithful absence; detecting a missing
  species requires the slow-growth window, echoing the tick-10
  readwindow invariant (escalate Gse, don't extend the wait).
- **S4 PASSES (calibration)**: build1 strict "pqr"
  0.542/0.790/0.984/0.872 vs tick-19's 0.540/0.790/0.984/0.870 —
  the protocol reproduces.

## What it establishes

K4's honest successor, answered: kinetic reassertion of a
true-model readout EXISTS as a completion-independent channel, it is
near-miss-trapping class (b=1 bridging with mutual stabilization),
and it is read-window-controlled. Species-death and rule-drop
recompiles are different substrates for the same solver answer
({p,q}) — but only the species-death substrate can flip between
"repaired true model" and "faithful dropped-rule model" by window
choice. Missing-species detection is therefore a WINDOW problem,
not a rate problem.

## Honest limits

- One geometry (4-column AND), one species (a slot-A reader), one
  read rule (T=400·e^Gmc). The dG=7 collapse point and the repair
  ceiling are properties of this build's glue arithmetic
  (L3.S=base3 strength 1, DBr.S=p-t-done strength 1), not yet a
  general law.
- The trap is the same near-miss family designs/001 measured at
  O(1) whenever Gmc ≥ Gse; what is new here is that the trap
  RECONSTRUCTS the true decode rather than corrupting it, and that
  it dies at large dG where the b=1 attach rate starves.
- No C-claim advanced; unreviewed promotion; clingo anchored the
  program semantics only.

## Tooling notes

Zero science bugs, zero harness bugs this tick: the aTAM arm
verified S1 first-run, the queue job ran clean on first submission
(~1 min wall), and the smoke run (single trajectory per system
before submission) correctly previewed the trap. The
internal-consistency grid pin in the test suite checksums pqr
totals against the per-point rows.
