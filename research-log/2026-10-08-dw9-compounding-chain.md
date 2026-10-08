# DW9 compounding-chain falsifier: pre-registration and submission

Date: 2026-10-08 (tick 68, SON-4867, wake 15:00Z). Anchors: queue
receipt verbatim below; commit hashes quoted after landing; no
anticipated times.

## 1. What was pre-registered

This executes the falsifier registered in
research-log/2026-10-08-dw9-window-tilt.md S5 ("Next falsifier
(pre-register before running)"), verbatim scope: trajectory-level
re-roll chain extraction at dG 2, per-roll attach probabilities and
per-incumbent persistence fit on half the seeds, then an analytic
stationary-distribution prediction of the window-arm share on the
held-out seeds. A prediction outside +/-0.05 of the measured share
refutes the compounding-chain account.

Instrument: `evidence/2026-10-08-dw9-compounding-chain/ktam_dw9_compound.py`.
The protocol is the tick-47/63 instrument verbatim (BUILD1
Vp-missing, Gmc=9.5, s2 lock-read doubling, canonical map from the
FULL build, stability checked every event, 4x window at dG=2) with
ONE addition: passive SITE-occupancy event logging at the existing
churn hook. No RNG-order change, so the original 500 seeds
reproduce the tick-63 trajectories exactly — enforced by the CAL
gate (pooled terminal census must be EXACTLY D2T 367 : L2 131).

## 2. Frozen gates (fixed before submission)

- **CAL instrument identity** — pooled i in [0,500) terminal census
  == 367 : 131 exactly. Any mismatch: CAL_FAIL, all CC verdicts
  VOID.
- **CC1 registered falsifier** — fit the chain on seeds [0,250),
  predict the held-out share on [250,500). Model: CTMC on
  {empty, D2T, L2, other} with species-aggregated attach odds p_s
  and detach hazards d_s from the fit range's event logs;
  stationary pi_s/pi_E = p_s/d_s, so pi_pair = x_D2T/(x_D2T+x_L2),
  x_s = p_s/d_s (the attach flux cancels). Freeze-mixture
  prediction P_mix = f*fs_pair + (1-f)*pi_pair, with f = fitted
  first-stable persistence and fs_pair = fitted D2T share among
  pair first-stables (the S5 mechanism account: frozen survivors +
  compounded re-rollers). CONFIRMED iff |P_mix - share| <= 0.05;
  FALSIFIED if > 0.05; NO_EVENTS < 50 pair terminals; NO_FIT if
  any fit count < 20.
- **CC2 out-of-sample generalization** — refit on all 500 original
  seeds, predict the fresh-seed share [500,1000). Same bands.
- **CC3 fresh-seed replication** — |share_fresh - 0.737| <= 0.05
  CONFIRMED; > 0.10 FALSIFIED (0.737 not a stable regime number);
  middle INCONCLUSIVE.

Seeds: seed0 = 260261107 (tick-63 arm index 2), i in [0,500) = the
exact tick-63 trajectories (fit/held-out split), i in [500,1000) =
fresh, never-run seeds inside the same reserved stride block
(arm-2 block, next arm base 280261107 — disjoint by construction;
grep found no other references).

## 3. Submission receipt (v1, validated archive)

Request `7822cd5b3393f4f7f2b27032871bf82d642586b0e21dc9661b0e874fd91706e4`,
job `hxq-7822cd5b3393f4f7`, nonce `dw9-compound-v1`, image
`paperclip-test`, cpu 1, memory 1073741824, wall 900, archive blob
`8f338b9a36bce2a3ac5ab77336117855ee4eced958f361129f3b3210f7fb361f`
(11-file closure: entrypoint + tiles_and + tiles_death + the whole
molasp package), state "queued" (awaiting resource admission) at
submission.

Pre-submission validation per the tick-63 standing rule:
clean-extraction smoke from the exact tarball (SMOKE=1, n=8/range)
exit 0, VERDICTS line present, stderr empty; guards NO_FIT /
NO_EVENTS fire as designed at smoke scale. Smoke verdicts are
instrument-check only, NOT results.

## 4. What happens on collection (next tick first duty)

`job_queue.py status/result 7822cd5b... --owner 529f369d-...`; read
HX-QUEUE-EXIT (payload truth, not pod phase); commit run.out as
evidence receipt + collection note; machine verdicts stand as
printed. Falsifier consequences: CC1 FALSIFIED -> the compounding
chain does not explain the window tilt (the S5 hypothesis dies, the
search for the mechanism reopens); CC1 CONFIRMED + CC3 CONFIRMED ->
the window-tilt mechanism is quantitative (per-roll odds x dwell
asymmetry), and the designs/007 window-indexed MARGINAL pricing
gets a measured basis. CC3 FALSIFIED alone -> 0.737 is
seed-history-dependent, reopening DW9's number as an estimate.

Collection disclosure for this tick: the durable products are the
frozen-gate instrument, this pre-registration, and the validated
queued request; no verdicts are claimed before the run lands.

## 5. Collection outcome (same tick, ~15:12Z)

v2 request `6a1259244274e4e7f6aca5ac61a8f21167b2bac8bc1d7b6280e9cea755746eff`
ran ~22 s, HX-QUEUE-EXIT:0. Verdicts (receipt:
evidence/2026-10-08-dw9-compounding-chain/run.out + collection.md):

- **CAL_OK** — pooled orig census EXACTLY 367:131:2: the
  instrument is the tick-63 instrument; passive logging perturbed
  nothing.
- **CC1 FALSIFIED / CC2 FALSIFIED** — the compounding-chain
  account (frozen survivors + compounded re-rollers) misses the
  held-out share by 0.162 and the fresh share by 0.143 (~3x the
  band). The S5 mechanism hypothesis dies; the mechanism search
  reopens.
- **CC3 CONFIRMED** — fresh-seed share 0.716; the DW9 tilt is a
  stable regime number (|delta| = 0.021).
- Post-hoc (labeled, no gate): the PURE stationary pi_pair
  (0.697-0.712) sits within 0.02-0.04 of both measured shares —
  the failure is the mixture's frozen-survivor component, not the
  chain rates. Next falsifier candidate: time-inhomogeneous chain
  per window phase, to be pre-registered before running.
- Fitted parameters: per-roll pair odds 0.52-0.55 (near-fair, not
  the 0.575 first-attach race); dwell ratio D2T:L2 ~ 2.3; f
  0.396-0.402; fs_pair 0.368-0.390 (L2-favored first stables).

## 6. v1 failure (root-caused, superseded same tick)

Request `7822cd5b...06e4` (nonce dw9-compound-v1) failed in ~11 s:
command lacked the `source/` prefix — the queue extracts the
archive into /work/source and runs from /work (verified against
the tick-63 v2 request record's command
`python3 source/evidence/...`). Archive content was never at fault
(clean-extraction smoke had passed; CAL_OK on v2 proves the
payload). Ops lesson: read the recorded command of a prior
SUCCESSFUL request before submitting; the tick-63 research log's
"mimicking /work" smoke prose elided the source/ root and
propagated the drift.
