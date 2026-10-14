# Pre-datum OC of the CAL exact-match VOID gate (tick 141, SON-5152)

The frozen tick-120 arbitration map reads, in order: `CAL_FAIL → VOID`;
`min pair-n < 3400 → NO_EVENTS`; `p ≤ 0.05 → SUPPORTED`;
`p > 0.05 → NOT_DETECTED`. Ticks 139–140 measured the last two branches
and the floor branch pre-datum. The FIRST branch had never been
measured: the queued instrument replays the 500-seed CAL window
(`260261107+[0,500)`) and VOIDs unless the mid-window pair census
returns **EXACTLY D2T 367 : L2 131** (implicitly other = 2) — the "10th
consecutive identity run" gate. This note measures, before the queued
request (`dd5a8300…`, still behind the board-operator maintenance lease)
can produce a datum, what that exact-match gate is worth as an anomaly
detector and what corruption level silently passes the whole gate set.

## Model (stated before any arithmetic)

Each seed's terminal reading is independently perturbed with
probability ε. Two kernels bracket destructive vs benign corruption:

- **DROPOUT** — a perturbed seed reads 'other':
  `P_pass = (1−ε)^498` (the 2 committed others cannot become pairs).
- **MARGINAL RESHUFFLE** — a perturbed seed re-draws iid from the
  committed census marginal (367/500, 131/500, 2/500); lucky
  compensation allowed; `P_pass` is the exact K-conditioned convolution
  (all-positive lgamma float evaluation, no complements).

## Measured (receipt `evidence/2026-10-14-w8-blockpower-cal-oc/cal-oc.json`,
## sha256 `fc214df7…510f3`)

1. **The CAL is a 1e-4-scale detector.** Pass probability hits 5%
   mismatch at ε = **1.030e-4** (dropout; analytic closed form
   `1 − 0.95^(1/498)` agrees with bisection to 13 digits) and
   **2.646e-4** (reshuffle); 50% at 1.391e-3 / 4.406e-3.
2. **~385× more sensitive than the census floor.** The NO_EVENTS floor
   reaches 5% risk only at the tick-140 other-rate 3.96e-2; the CAL
   gate at 1.03e-4 — on the same per-seed dropout scale. At the
   tick-140 collapse yield the CAL pass probability is **1.8e-9**:
   corruption large enough to threaten the census floor VOIDs at the
   CAL near-certainly (joint silent-pass 1.6e-9).
3. **Verdict-safe bracket.** The largest corruption that still escapes
   the CAL with ≥95% probability displaces each group's expected pair
   census by **0.367 seeds** (dropout) / **0.942** (reshuffle) —
   0.46%/1.19% of the smallest pre-registered effect (Δ0.0223 = 79.4
   seeds). Corruption big enough to distort the verdict trips the CAL;
   corruption that escapes the CAL is too small to matter.
4. **Honest framing — the gate measures substrate drift, not sampling.**
   The committed 0.5% 'other' rate is ACROSS seeds; the CAL replay is a
   deterministic re-execution of FIXED seeds (9 consecutive committed
   identity runs), so the historical other-rate cannot fire this gate
   by statistical chance. Correspondingly, IF a per-run 0.5% random
   dropout existed, the CAL would VOID ~92% of clean runs
   (P_pass(0.005) = 0.0824) — the gate's power IS its determinism
   premise, empirically supported and now quantified.

## Verification (receipt `verification` block, all pinned in tests)

- ε = 1: the convolution collapses to the single-term iid multinomial
  pmf; float vs exact Fraction agreement **1.83e-12**.
- First-order slope: hand-derived exact `49073/250 = 196.292`
  (reshuffle) and `498` (dropout); numeric finite difference at ε=1e-7
  agrees to 1.4e-5 / 2.5e-5 relative — pure O(ε) second-order bias,
  recorded as such.
- Mid anchor ε = 1/1024: exact Fraction sum truncated at K ≤ 10 with a
  recorded Chernoff tail bound `(eμ/11)^11 = 7.89e-11`; float full sum
  differs from the exact partial by **9.61e-13**, well inside the bound.
- Cross-tick consistency: the silent-pass table's NO_EVENTS arm reuses
  the tick-140 float walk unchanged — the q = 0.995 row is
  byte-identical (3.0968e-95) to the tick-140 receipt.

## Boundaries

Zero kTAM trajectories; none of the probe's virgin seed windows
consumed; no gate executed; no branch of the frozen map touched or
re-derived; the ladder stays PAUSED. No RNG anywhere (closed forms,
exact sums, bisection). Stdlib-only, byte-reproducible, hosted-CI-safe.
No blog (branch-calibration evidence, not a milestone); no wet-lab, no
external contact, no paper/preprint activity.
