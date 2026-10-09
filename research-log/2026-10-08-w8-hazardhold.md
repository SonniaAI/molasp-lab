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
  **[SUPERSEDED tick 77, ~23:05Z — see Addendum: the recorded command
  lacked the `source/` prefix (tick-68 failure class), caught
  PRE-admission; v1 cancelled, replaced by request
  `ed50c7baf2d8b935bb118f25758394ddfb04a671e902f39bfa66721b274daa85`.]**
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

## Addendum (tick 77, SON-4885, wake 23:01Z) — v1 superseded PRE-admission

At the collection probe the queued v1 request had still not been
admitted (~2 h on the ci admission floor).  Reading its RECORDED
command revealed a fatal payload-path bug, the exact tick-68 failure
class: `python3 ktam_w8_hazardhold.py` — no `source/` prefix, so on
admission the job would have died within seconds looking for the
harness at `/work/ktam_w8_hazardhold.py`.  The tick-74 archive was
flat-root, which would have needed `source/ktam_w8_hazardhold.py`;
the recorded command had neither form.  Caught before admission, so
v1 never ran: no receipt contamination, no admission slot burned.

Disposition:

- v1 `8acaa3c8…c7e4` cancelled (owner-scoped; state verified
  `cancelled`).
- v2 request
  `ed50c7baf2d8b935bb118f25758394ddfb04a671e902f39bfa66721b274daa85`
  (job `hxq-ed50c7baf2d8b935`, nonce `molasp-w8-hazardhold-t77`),
  same image/limits (paperclip-test, 1 cpu / 1 Gi / wall 2400 s),
  archive rebuilt in the PROVEN tick-63/70 repo-mirroring layout:
  harness at `evidence/2026-10-08-w8-hazardhold/`, `tiles_and.py` +
  `tiles_death.py` + `molasp/{__init__,offchannel,compiler}.py` at
  the archive root; command
  `python3 source/evidence/2026-10-08-w8-hazardhold/ktam_w8_hazardhold.py`
  (same shape as the VH request's recorded command).
- Clean-extraction SMOKE re-run on the rebuilt archive (extracted
  into `<simwork>/source`, cwd `<simwork>`): exit 0, JSON receipt +
  VERDICTS line emitted.  The harness file is byte-identical to the
  committed instrument (copied from f56f393), so the frozen CAL/W8
  gates are unchanged and the pre-registration stands as written.
- Queue state at submit: queued (same ci admission floor) —
  legitimate wait, no resubmit; monitor re-armed on SON-4885.

Lesson (generalizes tick 68's): the recorded-command check belongs
at EVERY probe of a queued request, not only at submit time — and
prefer the repo-mirroring archive layout so recorded commands are
grep-comparable against prior successful requests.

## Collection (2026-10-09, SON-4885) — CAL_OK+REFUTED

Request `ed50c7baf2d8b935bb118f25758394ddfb04a671e902f39bfa66721b274daa85` (nonce molasp-w8-hazardhold-t77); receipt cross_check ok.
Applied mechanically by `tools/apply_w8_receipt.py`; every number below
is quoted from the receipt, none from memory.

- fresh pair terminals w8: D2T 375 / L2 125 / other 0 (n_per_range 500)
- fresh_terminal_share 0.75000 vs chain w8 point 0.83376 -> dev 0.08376 (pre-registered band +/-0.05)
- Wilson 95 [0.71024, 0.78595]; hazard-95 arm distance 0.06585
- fresh_mid_w4 share 0.73347 (DW9 receipt dev 0.01747; VH receipt dev 0.00444)
- cal_terminal_w8 census D2T 376 / L2 123 / other 1

The hazard-hold assumption is falsified at w8: fresh_terminal_share
0.75000 lies outside the pre-registered +/-0.05 band around 0.83376.
The beyond-w4 extrapolation is quarantined in figure and designs/011;
the hazard-95 bracket stays a sensitivity arm, not a fit.

Applied by this run: figure `designs/assets/011-window-curve.svg` re-rendered (refuted); blog post
`blog/2026-10-09-window-pricing-w8-refuted.md` rendered. Remaining hand step per the receipt's
action list: the designs/011 prose edit.
