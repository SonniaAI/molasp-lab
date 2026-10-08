# VH vanishing-hazard ratchet — collection (tick 70, SON-4871)

Request `e6c0c16d18f7b5f907befff192e3d075bb4e6c96e804248928669e15840f6394`,
job `hxq-e6c0c16d18f7b5f9`, nonce `vh-ratchet-v1`, image `paperclip-test`,
cpu 1, memory 1073741824, wall 900, archive blob
`3712c5c49cd423ab9c6c29d6d8ff5607b651926b331f95485092b992f4c5c097`
(11-file closure, pre-reg commit acb1f2d). Admitted ~2 s after submit,
ran ~22 s, **HX-QUEUE-EXIT:0**, stderr empty. Raw envelope verbatim as
`run.out`; machine verdicts stand as printed:

```json
{"CAL": "CAL_OK", "VH1": "CONFIRMED", "VH2": "CONFIRMED", "VH3": "CONFIRMED"}
```

## Readout

- **CAL_OK** — orig [0,500) census EXACTLY 367:131:2; DW9/DW10
  trajectory identity proven; every number below inherits it.
- **VH1 CONFIRMED** — per-phase D2T hazards (fit range [0,250)):
  d^1 = 4.0466e-07 >= d^2 = 5.3481e-09; max(d^3, d^4) = 1.0322e-09 <= 0.10*d^1 = 4.0466e-08.
  The hazard collapses ~76x from phase 1 to 2 and sits ~400x below the
  10%-of-early line in both late phases (point hazards 0 and 1.03e-9;
  Poisson-95 upper bounds 3.28e-9 / 3.10e-9). L2 keeps detaching
  throughout (2.17e-07 -> 4.36e-08): the ratchet is D2T-specific, not a global
  freeze.
- **VH2 CONFIRMED** — share_pred = 0.7414 vs held-out [250,500) share
  0.7379: deviation 0.0035 (band 0.05); the homogeneous stationary misses
  by 0.0255 — the integrated ratchet beats it ~7x on held-out data.
- **VH3 CONFIRMED** — same prediction vs fresh [500,1000) share 0.716:
  deviation 0.0254, in band; ~1.26 SE of the fresh block share estimate
  (SE ~ 0.020 at n=500, p~0.72) — within sampling noise.
- Reproductions (instrument identity, pinned): homogeneous fit-range
  pi_pair 0.7123954307622173 == DW9 fit_half bit-exact; snapshot shares
  0.503/0.646/0.704 == DW10. Predicted terminal vector: E 0.00018, D2T 0.7379,
  L2 0.2574, O 0.0044 — the site is essentially never empty at read time.

## Consequence (per the pre-registered map)

VH1+VH2+VH3 CONFIRMED: the DW9 window tilt is quantitatively accounted
by a **vanishing-hazard ratchet under homogeneous attach odds** — D2T's
effective detach hazard collapses across the read window while L2 keeps
churning, so the pair share sweeps monotonically from the near-fair
attach odds (0.503 at t/4) to 0.70+ and the terminal census inherits the
asymmetry. designs/007 window-indexed MARGINAL pricing now has its
measured basis (per-phase hazards + homogeneous odds + forward
integration, all fitted without touching the prediction ranges).
Public-story note: the tick-67 blog's regime account gains its mechanism;
blog candidate next tick per the arc convention.