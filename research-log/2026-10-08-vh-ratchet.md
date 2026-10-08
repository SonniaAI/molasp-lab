# VH vanishing-hazard ratchet: pre-registration and submission

Date: 2026-10-08 (tick 70, SON-4871, wake 17:00Z). Anchors: queue
receipt quoted verbatim below; commit hashes quoted after landing; no
anticipated times.

## 1. Position

DW10's collection
(research-log/2026-10-08-dw10-phase-chain.md section 6) falsified the
phase-stationary framing as unidentifiable (TI1/TI2 NO_FIT at frozen
MIN_FIT=20 — the process stops being an ergodic chain late in the
window) while confirming the snapshot-share sweep (TI3, 0.503 → 0.704,
delta 0.201) and reading out, post-hoc and labelled, that D2T becomes
absorbing while L2 keeps churning: a one-way ratchet. Its named next
falsifier, executed here verbatim:

  "VH1 vanishing-hazard ratchet — fit per-phase D2T detach hazard
   (CONFIRM if monotone to ≈0 by phases 3–4), forward-integrate the
   fitted non-homogeneous chain from the 1/4-window snapshot state to
   t_read, predict the held-out terminal share within ±0.05. Holds →
   the DW9 tilt is fully accounted and designs/007 window pricing
   gets its measured basis; non-monotone hazard → reopen at the
   hazard shape."

Hypothesis under test (H_VH): the D2T detach hazard COLLAPSES across
the window (structural absorption by assembly context), attach odds
stay homogeneous (DW10's closest branch), and the fitted
non-homogeneous chain forward-integrated from the 1/4-window snapshot
predicts the terminal pair share on data that was never used to fit.

## 2. Instrument

`evidence/2026-10-08-vh-ratchet/ktam_vh_ratchet.py`.
run_traj is DW10's function VERBATIM (hence verbatim DW9, hence
verbatim tick-47/63: BUILD1 Vp-missing, Gmc 9.5, gse 7.5, matched_s2
lock-read doubling, canonical map from the FULL build, read window
4×400·e^Gmc at dG 2) — same seeds SEED0+i, same RNG stream, so the
1000 trajectories reproduce the DW9/DW10 logs exactly; CAL proves
identity. All new science is analysis: per-phase att/det/occupancy
attribution (DW10 spell-splitting), per-phase hazards, and
forward-integration of the non-homogeneous CTMC by scaling-and-
squaring + uniformization (pure python; no scipy in the image).

Model spec (frozen, also in the instrument docstring): states
{E, D2T, L2, O}; attach E→s at λ·p_s with p_s and λ pooled on the fit
range [0,250); hazards d_s^φ per quartile phase for D2T and L2 on the
fit range; O hazard pooled whole-window (fast b=1 churn — labelled
modelling choice, not a claim); initial state = empirical SITE
occupancy distribution at t_read/4 on the fit range; integrate
exp(Q^φ·t_read/4) for φ=2..4; share_pred = v[D2T]/(v[D2T]+v[L2]).

## 3. Frozen gates (fixed before submission; machine verdicts on the
final VERDICTS line)

- **CAL instrument identity** — pooled terminal census over i ∈ [0,500)
  EXACTLY D2T 367 : L2 131 (DW9/DW10 receipt). [mismatch → CAL_FAIL,
  every VH verdict VOID]
- **VH1 hazard-ratchet shape** (fit range): per-phase D2T hazards
  d^φ = det_D2T^φ / occ_D2T^φ. CONFIRMED iff d^1 ≥ d^2 AND
  max(d^3, d^4) ≤ 0.10·d^1 — the registered "monotone to ≈0 by phases
  3–4" in noise-robust form (a 0→1-count late wiggle between adjacent
  late phases cannot flip it; late point hazards sit orders below 10%
  of d^1). FALSIFIED otherwise. [det_D2T^1 < 20 or occ_D2T^φ ≤ 0 for
  any φ → NO_FIT]
- **VH2 forward-integrated prediction** — |share_pred − share on
  held-out [250,500)| ≤ 0.05 CONFIRMED. [> 0.05 FALSIFIED: the
  ratchet-integrated chain does not predict the terminal census;
  held-out pair terminals < 50 NO_EVENTS]
- **VH3 out-of-sample fresh** — same prediction vs the fresh [500,1000)
  share. Same bands as VH2.

Consequences (this note, not the machine): VH1+VH2 (+VH3) CONFIRMED →
the DW9 tilt is quantitatively accounted by a vanishing-hazard ratchet
under homogeneous attach odds; designs/007 window-indexed MARGINAL
pricing gets its measured basis; the tick-67 blog's regime story gains
its mechanism. VH1 FALSIFIED → reopen at the hazard shape. VH1
CONFIRMED + VH2/VH3 FALSIFIED → the ratchet exists but its integrated
prediction misses — mechanism search reopens at the conditioning layer
(DW10's terminal-vs-occupancy candidate).

Descriptive (labelled, no gates): per-phase L2 hazards; per-phase
attach counts/odds; Poisson 95% upper bounds (3/occ) for zero-count
late D2T hazards; snapshot shares at 1/4, 1/2, 3/4 on orig [0,500)
(must reproduce DW10's 0.503/0.646/0.704); homogeneous fit-range
pi_pair (must reproduce DW9's 0.7124); |dev_pred| vs |dev_homo|.

Seeds: SEED0 = 260261107 (tick-63 arm index 2), i ∈ [0,1000) — the
exact DW9/DW10 trajectories; nothing in [1000,∞) is touched.

## 4. Pre-submission validation (disclosed)

- expm validated standalone against: the 2-state closed form
  P(0→0) = (b + a·e^{−(a+b)t})/(a+b) over three rate/time regimes; a
  stiff 4-state chain at the working scale (rows sum to 1 within 1e-9,
  nonneg); the absorbing-state column (zero D2T hazard → E[D2T][E]
  < 1e-15). Two instrument bugs were caught and fixed BEFORE this
  registration: (1) the series initialized E = I while its own k=0
  term supplies e^{−μh}·I, doubling the identity component (row sums
  2^(2^m) — caught by the 2-state check); (2) the O hazard read a
  literal "O" key while occupancy keys are raw species names —
  aggregated non-pair species now. The in-code row-sum assert is
  1e-6 (regime drift at 29 squarings is 5.5e-8; working scale passes
  at 1e-9).
- SMOKE=1 (n=8 per range): exit 0, VERDICTS present, guards fire as
  designed (VH1 NO_FIT: det_D2T^1 = 7 < 20; VH2/VH3 NO_FIT: zero
  phase-4 L2 occupancy at n=8 → the integrated path is validated by
  the standalone battery instead, per the tick-41 rare-branch rule).
  Smoke verdicts are instrument-check only, NOT results.

## 5. Submission receipt (validated archive)

Request `e6c0c16d18f7b5f907befff192e3d075bb4e6c96e804248928669e15840f6394`,
job `hxq-e6c0c16d18f7b5f9`, nonce `vh-ratchet-v1`, image `paperclip-test`,
cpu 1, memory 1073741824, wall 900, archive blob
`3712c5c49cd423ab9c6c29d6d8ff5607b651926b331f95485092b992f4c5c097`
(11-file closure: entrypoint + tiles_and + tiles_death + the whole molasp
package, built at pre-reg commit acb1f2d), state "queued" (awaiting resource
admission) at submission. Command carries the `source/` prefix (tick-68 v1
lesson). Pre-submission validation per the tick-63 standing rule:
clean-extraction smoke from the exact tarball with the exact queue command —
exit 0, VERDICTS line present, stderr empty; guards NO_FIT fire as designed at
smoke scale. Smoke verdicts are instrument-check only, NOT results.

## 6. Collection outcome (same tick, ~17:12Z)

Admitted ~2 s after submission, ran ~22 s, **HX-QUEUE-EXIT:0**, stderr empty.
Raw envelope verbatim as `evidence/2026-10-08-vh-ratchet/run.out`; rendered
fragment as `collection.md`. Machine verdicts (verbatim):

- **CAL_OK** — pooled orig census EXACTLY 367:131:2; DW9/DW10 trajectory
  identity proven.
- **VH1 CONFIRMED** — D2T hazards 4.05e-7 -> 5.35e-9 -> 0 -> 1.03e-9 across
  quartiles (fit range): collapse ~76x by phase 2, late phases ~400x below
  the 0.10*d^1 line (Poisson-95 uppers 3.3e-9/3.1e-9); L2 keeps detaching
  (2.17e-7 -> 4.36e-8) — D2T-specific absorption, not a global freeze.
- **VH2 CONFIRMED** — share_pred 0.7414 vs held-out 0.7379, dev 0.0035
  (homogeneous stationary misses by 0.0255; ~7x improvement).
- **VH3 CONFIRMED** — same prediction vs fresh 0.716, dev 0.0254 (~1.26 SE
  of the fresh share estimate — within sampling noise).
- Reproductions bit-exact: homo pi_pair 0.7123954307622163 (DW9 fit_half),
  snapshot shares 0.503/0.646/0.704 (DW10). Predicted terminal vector:
  E 0.00018, D2T 0.7379, L2 0.2574, O 0.0044.

Consequence (pre-registered map): the DW9 window tilt is quantitatively
accounted by a **vanishing-hazard ratchet under homogeneous attach odds**;
designs/007 window-indexed MARGINAL pricing has its measured basis. Blog
candidate next tick per the arc convention (the tick-67 regime story gains
its mechanism).
