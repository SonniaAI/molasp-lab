# W8 hazard-hold falsifier pre-registered and submitted

Date: 2026-10-08 (tick 74, SON-4881) — timestamps are wake and
commit-metadata times only, read back after the fact.

## What

Executed tick 73's named next step: the designs/011 pre-registered
w8 falsifier, implemented and submitted to the capped cluster queue
this tick.  `evidence/2026-10-08-w8-hazardhold/ktam_w8_hazardhold.py`
— protocol VERBATIM DW9 (BUILD1 Vp-missing, Gmc=9.5, gse=7.5, s2
lock-read arithmetic, stability on every event); the only change is
the read window, 8x400 e^Gmc.  `run_traj` is DW9's function with the
passive log and NO RNG-order change, so on DW9's own seeds the event
stream up to t_mid = t_read/2 (exactly the 4x window) is
bit-identical to DW9's — that identity IS the calibration.

## Arms (frozen before submission)

- CAL: seeds 260261107 + [0,500) — DW9's exact seeds (arm 2).
- FRESH: seeds 280261107 + [0,500) — arm 3 of the reserved stride
  block, named the next fresh base in the DW9 collection note and
  never run before this job.

## Frozen gates

- CAL: mid-window (4x) pair census over the CAL arm EXACTLY
  D2T 367 : L2 131 of 500 (tick-63/DW9 receipt); any mismatch ->
  CAL_FAIL and W8 VOID.
- W8: fresh terminal (8x) fill share s; HELD if |s - 0.83376| <=
  0.05; REFUTED if > 0.05 (designs/011's pre-registered refutation
  of the hazard-hold extrapolation); pair terminals < 50 NO_EVENTS.

Descriptive (no gates): fresh mid-window share (w4 point on fresh
seeds; cross-check vs DW9 fresh 0.716 / VH held-out 0.7379), Wilson
95 CI on the fresh terminal share, distance to the hazard-95
bracket arm 0.81585, CAL-arm terminal share at w8.

## Receipts

- SMOKE passed locally (n=8/arm; instrument check only).  One
  packaging bug caught pre-submit: `molasp/compiler.py` was missing
  from the staged archive (`offchannel.glue_strength` imports it
  lazily) — added, smoke clean.
- Cluster queue request
  `8acaa3c85db7ed7c7314422d8616bf4814556176c2eedabfa78ac8167342c7e4`
  (job `hxq-8acaa3c85db7ed7c`), image paperclip-test, 1 cpu / 1Gi /
  wall 2400 s, submitted 21:06Z; state queued (ci admission floor on
  spark-4a06) — waiting for resources is legitimate, no resubmit.
- Issue monitor scheduled on SON-4881: external_service /
  cluster-job-queue, nextCheckAt 21:35Z, timeoutAt 23:30Z,
  maxAttempts 6, recoveryPolicy wake_owner.  Collection wake will
  import run.out, read CAL/W8, and write the collection note.

## Interpretation map (recorded here, not in the machine)

- CAL_OK + W8 HELD: the w8 tier stands on a measured receipt; the
  window curve's extrapolated arm keeps its hazard-hold labelling
  with the point 0.834 now cross-seed measured.
- CAL_OK + W8 REFUTED: designs/011's w8 tier entry is retracted, the
  extrapolated arm is quarantined beyond w4, and the hazard-hold
  assumption is named falsified at w8 (the bracket stays what it
  always was: a sensitivity arm, not a fit).
- CAL_FAIL: instrument drift; everything VOID, diagnose before any
  science claim.
