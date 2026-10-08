# DW10 collection — 2026-10-08 ~16:06Z (SON-4869 tick 69)

Request `36844ce280929b13b6b32a4e17c4d0e1c11afa6f77bafb16a9ecec5894f64577`
(nonce `dw10-phase-v1`): state complete, **HX-QUEUE-EXIT:0** (payload
truth), HX-FILE:status 0, stderr empty, ~22 s runtime, admitted
2026-10-08T16:06:21Z. Raw stdout saved verbatim as `run.out`
(payload JSON + verdicts + VERDICTS line). Archive blob
`6fa1a40f…79d35` (the validated 11-file closure).

## Machine verdicts (verbatim, frozen gates)

```
VERDICTS {"CAL": "CAL_OK", "TI1": "NO_FIT", "TI2": "NO_FIT", "TI3": "CONFIRMED"}
```

- **CAL_OK** — pooled orig [0,500) terminal census EXACTLY D2T 367 :
  L2 131 : 2 other. The instrument reproduced the DW9 trajectories
  bit-for-bit; every number below inherits that identity.
- **TI1 NO_FIT / TI2 NO_FIT** — not FALSIFIED: the phase-stationary
  question is unanswerable at the frozen MIN_FIT=20, because the
  process stops being an ergodic chain in the late window. Detach
  counts by phase (fit range, verbatim from run.out): phase 1 churns
  both species (att_D2T 292 / det_D2T 180, att_L2 270 / det_L2 148);
  phase 2 det_D2T **4** (vs att_D2T 54); phase 3 det_D2T **0** (att 16); phase 4 det_D2T **1**
  (att 7); L2 keeps detaching throughout (det_L2 82 / 28 / 16 in
  phases 2/3/4). D2T's detach hazard vanishes while L2 churn
  continues.
- **TI3 CONFIRMED** — snapshot pair-share over orig [0,500):
  t_read/4 → **0.503**, t_read/2 → 0.646, 3·t_read/4 → **0.704**;
  |0.704 − 0.503| = **0.201** ≥ 0.03 (the pre-registered band).
  Terminal 0.737; fresh 0.716.

## Readout (post-hoc, labelled, no gate)

The occupancy share is not stationary across the window — it sweeps
monotone from near-even (0.503 ≈ the near-fair per-roll odds 0.52) to
0.70+ as the window progresses. The mechanism the counts show:
**D2T becomes absorbing** (0–1 detach events in late phases) while L2
keeps churning, so occupancy ratchets toward D2T and the terminal
census is the endpoint of that ratchet, not a stationary split. The
time-inhomogeneity hypothesis (H_TI) is therefore answered *more
strongly than its drift formulation*: rates do not merely drift, the
D2T exit direction closes. The homogeneous fit-range π_pair = 0.7124
(reproducing DW9's 0.697–0.712 at the top edge) lands within 0.0255
of the held-out share 0.7379 — but as the ratchet's time-average, not
as a governing stationary law.

Against the pre-registered map: closest branch is TI1-fail +
TI3 CONFIRMED (moving occupancy share under near-homogeneous attach
odds), refined from "slow mixing" to a **structural ratchet** —
initialization matters because the clock only runs one way once D2T
seats.

## Next falsifier candidate (pre-register before running)

**VH1 (vanishing-hazard ratchet):** fit the per-phase D2T detach
hazard on the fit range; CONFIRM if it declines monotonically to
≈0 by phase 3–4; then forward-integrate the fitted non-homogeneous
chain from the 1/4-window snapshot state to t_read and predict the
held-out terminal share within ±0.05. If VH1's forward prediction
holds, the DW9 tilt is fully accounted by an absorbing-D2T ratchet
and designs/007 window-indexed pricing gets its measured basis; if
the hazard is non-monotone, the search reopens at the hazard shape.
