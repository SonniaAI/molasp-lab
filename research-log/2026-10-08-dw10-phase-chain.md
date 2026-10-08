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
