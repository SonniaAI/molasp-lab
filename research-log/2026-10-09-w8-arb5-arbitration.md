# W8 arm-5 pairwise arbitration (tick 98)

Date: 2026-10-09 · SON-4919 · run 577d12ff · pre-registered before
submission (commit hash in the receipt below; wake 10:00:46Z).

## What this is

The tick-97 stage-1 growth census produced the first
POOLING_CONTESTED receipt of the programme: exact two-sided
p = 5.6667e-3 between arm-3 (seeds 280261107+[0,500), w8 terminal
census 375/500 = 0.750) and arm-4 (seeds 300261107+[0,153), w8
terminal census 106/153 = 0.6928) under one CAL-verified
instrument. Two candidate explanations were named:

- **(S) ARM4_SMALLN** — arm-4's low share is a small-n artifact of
  n=153; arm-level shares are iid draws from one w8 rate and the
  pooling premise behind the census ladder stands.
- **(B) BLOCK_STRUCTURE** — the difference is real across reserved
  stride blocks (220261107 + m·2e7); pooling stays contested and
  the DW9/VH cross-seed stability statements need a re-read at the
  w8 level.

Tick 97 recommended pairwise arbitration with a fresh n=500 arm
over a beta-binomial refit (the pairwise test answers the question
actually asked; the refit estimates a parameter nobody needs yet).
This note pre-registers that arbitration.

## Instrument

VERBATIM `evidence/2026-10-09-w8-growth/ktam_w8_growth.py` (which
is verbatim `ktam_w8_hazardhold.py`): same BUILD1 Vp-missing
protocol, same s2 lock-read arithmetic, same `run_traj` (DW9's
function verbatim, no RNG-order change), same WIN_MULT=8 read
window, same CAL identity gate (mid-window pair census over
seeds 260261107+[0,500) must be EXACTLY D2T 367 : L2 131).

- **CAL arm**: seeds 260261107+[0,500) — UNCHANGED (arm 2).
- **ARM5**: seeds 320261107+[0,500) — arm 5 of the reserved stride
  block (BASE_SEED + 5·2e7), never run before this job. n=500
  matches the arm-3 datum's precision.

Only additions: `logpmf`/`exact_two_sided_p` copied VERBATIM from
`tools/w8_dispersion_receipt.py` (duplication on purpose; the test
suite identity-pins the two copies against each other) and the
module-level `arbitrate()` branch function.

## Pre-registered reading (frozen before submission)

x5 = arm-5 terminal pair census D2T count, denominator n5 =
D2T+L2. alpha = 0.05, fixed now.

- P3 = exact_two_sided_p(n5, 375/500, x5) — vs arm-3 rate
- P4 = exact_two_sided_p(n5, 106/153, x5) — vs arm-4 rate

Branch map (mechanical, exhaustive, no default arm):

| condition | branch | consequence |
| --- | --- | --- |
| CAL_FAIL | VOID | instrument, not science |
| n5 < 50 | NO_EVENTS | no reading |
| P3 ≥ α, P4 < α | ARM4_SMALLN | pooling premise restored at arm level; pooled line datum 481/653 becomes claimable; ladder may resume mechanically |
| P3 < α, P4 ≥ α | BLOCK_STRUCTURE | pooling stays contested; arm-level reporting only; next step = block-mechanism probe, never blind growth |
| P3 ≥ α, P4 ≥ α | AMBIGUOUS_MIDDLE | record; arm-5 distinguishable from neither reference at n=500 |
| P3 < α, P4 < α | OUTSIDE_BOTH | neither reference rate describes w8; mechanism search reopens |

Measured branch windows at n=500 (formula output, pre-registered
as descriptive context): ARM4_SMALLN for x5 ≈ 368–396;
BLOCK_STRUCTURE for x5 ≈ 334–357; AMBIGUOUS_MIDDLE ≈ 358–367;
OUTSIDE_BOTH below ≈ 333 or above ≈ 397. Reference rates: arm-3
0.750, arm-4 0.69281; expected x5 under arm-3 rate 375.0, under
arm-4 rate 346.4.

Descriptive at collection (no gates): arm-5 Wilson-95 alone; the
3-arm leave-one-out dispersion receipt recomputed with the
committed tool on [(375,500),(106,153),(x5,500)].

## Boundaries

- The arbitration tests ARM-LEVEL iid, the exact premise the
  tick-97 receipt contested. It does not re-run the w8 falsifier
  verdict (tick-96 REFUTED stands regardless of branch).
- Pairwise tests at one alpha, no multiplicity correction
  (two pre-registered tests, planning convention per tick 93).
- If AMBIGUOUS_MIDDLE lands, no account wins this tick; the named
  next step is arm-6 (seeds 340261107+[0,500)) or a
  block-mechanism probe, decided from the dispersion receipt.

## Submission record

(filled at submission)

## Collection (same tick)

(filled after collection)
