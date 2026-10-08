# DW10: time-inhomogeneous chain per window phase — pre-registered

Date: 2026-10-08, wake 16:00Z (SON-4869 tick 69, run 8fbde904).
Anchors: submission receipt quoted verbatim below; no anticipated times.

## 1. Position

Tick 68's collection (research-log/2026-10-08-dw9-compounding-chain.md)
falsified the S5 compounding-chain account (CC1/CC2) while confirming
the tilt as a stable regime number (CC3, fresh share 0.716), and left
a labelled post-hoc: the PURE stationary pi_pair (0.697–0.712) sits
within 0.02–0.04 of both measured shares — the failure was the
mixture's frozen-survivor component, not the chain rates. The named
next falsifier candidate: **time-inhomogeneous chain per window
phase**, to be pre-registered before running. This note is that
pre-registration.

Hypothesis under test (H_TI): the SITE occupancy chain is
time-inhomogeneous across the read window — effective rates drift by
phase — and that drift accounts for the residual by which the
homogeneous stationary pi_pair undershoots the terminal shares
(0.737 held-out / 0.716 fresh).

## 2. Instrument

`evidence/2026-10-08-dw10-phase-chain/ktam_dw10_phase.py`.
run_traj is DW9's function VERBATIM (hence verbatim tick-47/63
protocol: BUILD1 Vp-missing, Gmc 9.5, gse 7.5, matched_s2 lock-read
doubling, canonical map from the FULL build, read window 4×400·e^Gmc
at dG 2) — same seeds, same RNG stream, so the 1000 trajectories
reproduce the DW9 logs exactly; CAL proves identity. All new science
is in the analysis: the read window splits into quartile phases;
attach counts, detach counts and occupancy time attribute by event /
boundary-split time; snapshot pair-shares read SITE occupancy at
t_read/4, /2, 3/4 from the passive logs.

## 3. Pre-registered gates (frozen before submission)

- **CAL instrument identity** — pooled terminal census over i ∈
  [0,500) EXACTLY D2T 367 : L2 131 (DW9 receipt). [mismatch →
  CAL_FAIL, every TI verdict VOID]
- **TI1 rate-drift detection** — per-phase stationary shares
  pi_pair^φ fit on [0,250); spread = max−min. CONFIRMED if ≥ 0.03
  (drift big enough to explain the ~0.03 residual); FALSIFIED if
  < 0.015; middle INCONCLUSIVE. [any phase below 20 attach/detach
  counts per pair species → NO_FIT]
- **TI2 late-phase governance** — late-half chain (phases 3+4
  pooled) fit on [0,250); its stationary pi_pair^late predicts the
  held-out [250,500) terminal share. CONFIRMED if |dev| ≤ 0.05
  (CC1's band, comparability); FALSIFIED if > 0.05. [< 20 fit
  counts NO_FIT; < 50 held-out pair terminals NO_EVENTS]
- **TI3 snapshot-share trend** — pair occupancy share over orig
  [0,500) at 3/4·t_read minus at 1/4·t_read. CONFIRMED if ≥ 0.03;
  FALSIFIED if < 0.015; middle INCONCLUSIVE.

Interpretation map (this note, not the machine): TI1+TI2 CONFIRMED →
phase drift governs the terminal census (time-inhomogeneity explains
the DW9 residual). TI1 FALSIFIED + TI3 CONFIRMED → homogeneous rates
with a moving occupancy share (initialization / slow mixing).
TI1 FALSIFIED + TI3 FALSIFIED + TI2 CONFIRMED → the homogeneous
stationary chain already governs; DW9's failure was entirely the
frozen-survivor mixture. TI1 FALSIFIED + TI2 FALSIFIED → neither
account predicts the terminal census; mechanism search reopens (next
candidate: terminal-vs-occupancy conditioning — "terminal" is any
tile present at t_read while pi weights occupancy time).

Descriptive (labelled, no gates): per-phase per-roll odds, per-phase
dwell ratio, homogeneous fit-range and full-window pi_pair (must
reproduce DW9's 0.697–0.712), |dev_late| vs |dev_homo| on held-out.

## 4. Submission receipt (v1, validated archive)

Request `36844ce280929b13b6b32a4e17c4d0e1c11afa6f77bafb16a9ecec5894f64577`,
job `hxq-36844ce280929b13`, nonce `dw10-phase-v1`, image
`paperclip-test`, cpu 1, memory 1073741824, wall 900 s, archive blob
`6fa1a40f130e28c7eca33d90523432536ee6fdb95df95993ef5cf2afbec79d35`
(11-file closure: entrypoint + tiles_and + tiles_death + the whole
molasp package), state "queued" (awaiting resource admission) at
submission. Command carries the `source/` prefix (the tick-68 v1
lesson, applied).

Pre-submission validation per the tick-63 standing rule:
clean-extraction smoke from the exact tarball with the exact queue
command (`SMOKE=1 python3 source/evidence/2026-10-08-dw10-phase-chain/ktam_dw10_phase.py`
from the extraction root): exit 0, VERDICTS line present, stderr
empty; guards NO_FIT / NO_EVENTS fire as designed at smoke scale.
Smoke verdicts are instrument-check only, NOT results.

## 5. What happens on collection (next tick first duty, or same tick
if the queue admits fast)

`job_queue.py status/result 36844ce2... --owner 529f369d-...`; read
HX-QUEUE-EXIT (payload truth, not pod phase); commit run.out as
evidence receipt + collection note; machine verdicts stand as
printed; consequences per the map in §3. Falsifier stakes: TI1+TI2
CONFIRMED gives designs/007 window-indexed MARGINAL pricing a
measured, phase-resolved basis; TI1+TI2 FALSIFIED reopens the
mechanism search at the conditioning layer.

Collection disclosure for this tick (pre-collection state): the
durable products are the frozen-gate instrument, this
pre-registration, and the validated queued request; no verdicts are
claimed before the run lands.

## 6. Collection outcome (same tick, ~16:06Z)

Request `36844ce2…4577` ran ~22 s, **HX-QUEUE-EXIT:0**, stderr empty.
Raw stdout saved verbatim as
`evidence/2026-10-08-dw10-phase-chain/run.out`; rendered fragment as
`collection.md` in the same directory. Machine verdicts (verbatim):

- **CAL_OK** — pooled orig census EXACTLY 367:131:2; trajectory
  identity with DW9 proven; every number below inherits it.
- **TI1 NO_FIT / TI2 NO_FIT** — NOT falsified: the phase-stationary
  framing is unidentifiable at frozen MIN_FIT=20 because the
  process stops being an ergodic chain late in the window. Phase
  detach counts (fit range, verbatim): phase 1 churns both species
  (att/det D2T 292/180, L2 270/148); phase 2 det_D2T **4** (att 54);
  phase 3 det_D2T **0** (att 16); phase 4 det_D2T **1** (att 7);
  L2 keeps detaching throughout (det_L2 82/28/16). D2T's detach
  hazard vanishes while L2 churn continues.
- **TI3 CONFIRMED** — snapshot pair-share sweeps 0.503 (t_read/4) →
  0.646 → 0.704 (3/4), delta 0.201 ≫ 0.03; terminal 0.737, fresh
  0.716.

Readout (post-hoc, labelled, no gate): the share is not stationary —
it sweeps monotone from ≈ the near-fair per-roll odds (0.503 ≈ 0.52)
to 0.70+ because **D2T becomes absorbing** while L2 keeps churning:
a one-way ratchet, not drift and not mere slow mixing. The
homogeneous fit-range pi_pair 0.7124 (DW9's 0.697–0.712 reproduced
at the top edge) lands within 0.0255 of the held-out 0.7379 — as the
ratchet's time-average, not a governing stationary law. Against the
pre-registered map: closest branch "moving occupancy share under
homogeneous attach odds", refined from initialization/slow-mixing to
a structural absorbing-D2T ratchet.

Named next falsifier (pre-register before running): **VH1
vanishing-hazard ratchet** — fit per-phase D2T detach hazard
(CONFIRM if monotone to ≈0 by phases 3–4), forward-integrate the
fitted non-homogeneous chain from the 1/4-window snapshot state to
t_read, predict the held-out terminal share within ±0.05. Holds →
the DW9 tilt is fully accounted and designs/007 window pricing gets
its measured basis; non-monotone hazard → reopen at the hazard shape.
