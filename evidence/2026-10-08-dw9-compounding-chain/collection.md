# DW9 compounding-chain collection (tick 68, same tick as submission)

Request `6a1259244274e4e7f6aca5ac61a8f21167b2bac8bc1d7b6280e9cea755746eff`
(job `hxq-6a1259244274e4e7`, nonce `dw9-compound-v2`, paperclip-test,
1 cpu / 1GiB / 1800s): admitted 15:11:04Z, finished 15:11:26Z (~22 s),
HX-QUEUE-EXIT:0. Raw payload verbatim in `run.out`.

## Machine verdicts (frozen gates, this receipt)

| gate | verdict | decisive numbers |
|---|---|---|
| CAL instrument identity | CAL_OK | pooled orig terminal census EXACTLY 367 D2T : 131 L2 : 2 other (tick-63 receipt) |
| CC1 registered falsifier | FALSIFIED | fit [0,250) P_mix 0.5761 vs held-out [250,500) share 0.7379 — deviation 0.1618 > 0.05 |
| CC2 out-of-sample | FALSIFIED | refit [0,500) P_mix 0.5734 vs fresh [500,1000) share 0.7160 — deviation 0.1426 > 0.05 |
| CC3 fresh replication | CONFIRMED | fresh share 0.7160, |0.7160 − 0.737| = 0.021 ≤ 0.05 |

## Reading (pre-registered scope only)

The compounding-chain account registered in
research-log/2026-10-08-dw9-window-tilt.md S5 — frozen first-stable
survivors plus compounded re-rollers, species-aggregated
time-homogeneous CTMC — is **FALSIFIED as an explanation of the
window tilt**. Both predictions miss by ~3× the band. The tilt
itself replicates out-of-sample (CC3): 0.737 is a stable regime
number, and the mechanism search reopens.

Fitted parameters (receipt values): per-roll pair attach odds
0.520 (fit-half) / 0.547 (fit-all) — near-fair, NOT the 0.575
first-attach race of tick 41; dwell asymmetry is the big lever
(mean spell D2T 1.66e7 vs L2 7.29e6, ratio ≈ 2.3); freeze fraction
f 0.396/0.402; first-stable pair share fs_pair 0.368/0.390
(L2-favored).

## Post-hoc observation (hypothesis-generating ONLY — not a
validated result, no gate was pre-registered for it)

The PURE stationary prediction pi_pair (no freeze mixture) is
0.712 (fit-half) / 0.697 (fit-all) — within 0.02–0.04 of the
measured shares (0.738 / 0.716), while the freeze mixture that the
S5 account implies underpredicts badly. The failure is localized
to the mixture's frozen-survivor component, not to the chain's
rate structure. Candidate next falsifier (to be pre-registered
before running): a time-inhomogeneous chain — attach odds and
detach hazards fitted per window phase — testing whether the
terminal census is late-window-dominated (assembly-completeness
drift) rather than a first-stable/stationary mixture.

## v1 failure root cause (request 7822cd5b…06e4, HX-QUEUE-EXIT:2)

Command lacked the `source/` prefix: the queue extracts the
archive into `/work/source` and runs from `/work`; the working
shape is `python3 source/evidence/…` (verified against the tick-63
v2 request record). Archive content was never at fault —
clean-extraction smoke had passed, CAL_OK proves the payload is
the tick-63 instrument. Ops lesson recorded: before submitting,
read the recorded `command` of a prior SUCCESSFUL request
(`status <id> --owner …`), not just its research-log prose; the
tick-63 note's "mimicking /work" smoke description elided the
`source/` root and propagated the drift.
