# Vp-residual dissection — the residual is real, and it is delay (tick 27, SON-4778)

Card: SON-4778. Receipts: `../evidence/2026-10-07-vp-residual/`
(`ktam_mc_vp_residual.py` pre-registered at 295fbf8 BEFORE the job;
landed receipt `vp_residual.out` + `queue-receipt.json`).
Tests: `../tests/test_vp_residual.py`.

## Question

Tick 24/25 confirmed R2 with a residual attached to the Vp arm:
conditioned on read-time-clean lock columns, strict "pqr" at dG 0.5
is 0.927 in Vp-missing vs 0.7813 in build1 — gap 0.146, inside the
0.15 falsifier but outside the 0.10 "pure trap relief" target. Two
explanations survived: a real second-order Vp effect, or read-time
conditioning selecting at n=500 (a trajectory can squat, lose time,
and still read clean). designs/004 picked the compiler-guidance
route and queued this dissection in parallel.

## Design (pre-registered at 295fbf8, before submission)

n=2000 per arm, build1 + Vp-missing, dG 0.5 only, fresh seed base
40261107 (disjoint from the v2 grid's block), full-history tracking:
per-trajectory ever-visited flags and cumulative off-channel dwell,
reported for read-clean pqr / read-clean non-pqr / all cohorts.

- P1 the clean-conditional gap is >= 0.10 [real]; < 0.08 [the n=500
  residual was selection noise — falsified]; 0.08–0.10 inconclusive.
- P2 build1 read-clean non-pqr mean lock dwell >= 2x read-clean pqr
  [delay signature]; ratio <= 1.0 falsified.
- P3 calibration within 0.05 of 0.7813 / 0.927; >= 0.08 drift.

## Verdicts (job hxq-12ce8d979f6f5070, all three CONFIRMED)

- **P1 REAL** — gap 0.1235 (build1 0.8011, Vp-missing 0.9246). The
  residual is not n=500 noise: it narrows from 0.146 but clears the
  0.10 target at quadrupled power.
- **P2 DELAY** — ratio 4.5059: read-clean non-pqr trajectories dwelt
  1.146e6 time units in lock squats vs 2.543e5 for read-clean pqr.
  The residual's signature is time, not death.
- **P3 CALIBRATED** — deviations 0.0198 / 0.0024. The n=500
  references reproduce; no protocol drift.

## What the history tracking adds

- build1 lock squats at n=2000 reproduce the census order:
  Vp@(3,2)=429, V0p@(3,1)=259 — the only two lock squatters the
  static census names, now trajectory-counted at 4x power.
- D2T fills Vp's vacancy in 1554/1729 = 89.9% of Vp-missing strict
  pqr — R3b_Vp's 90.1% at n=500 reproduces.
- The structural misread appears inside build1's strict-pqr
  terminals: L2@(3,3)=42 of 1186 (3.5%; tick-24: 23/500 = 4.6%); in
  the Vp-missing arm, strict-pqr terminals carry ZERO lock squats —
  no Vp, no west enabler, no misread.
- blocked_frac collapses 0.286 -> 0.065 when Vp is removed — the
  dominant squatter is the dominant block source.

## Interpretation (closes the tick-23 residual question)

The residual is real and it is a dwell cost. The same value-glue
sharing that makes substitution repair possible (R3b) puts Vp/V0p on
lock sites (census, R3a), where they rarely kill the read — they
consume read-time (P2), and removing the biggest squatter returns
~0.12 of clean yield (P1). Both channels close with dG (R4). This
directly feeds designs/004 d4: the emit-time squat census should
weight severity by dwell exposure, and it already names the
offenders (Vp@(3,2), V0p@(3,1)). d4 implementation per A1–A4 is
next tick's head.
