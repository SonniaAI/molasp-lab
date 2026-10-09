# w8 waiter escalation prep — pre-staging the 02:50Z criterion

**Date:** 2026-10-09 (tick 85, run `b14f2b41`, monitor wake 01:25Z)
**Status:** WAITING — criterion NOT yet fired. This note pre-stages the
escalation so the tick that observes the horizon executes it mechanically.

## The decision rule (CEO, adopted verbatim from card comment 01:05:34Z)

> Standing escalation criterion: if the w8 waiter is still unadmitted at
> monitor timeout 02:50Z or its wall deadline lapses first, escalate the
> queue admission floor to Platform Engineering as resource-capacity -
> never a duplicate resubmit.

## The waiter (live record, probed 01:29Z this tick)

- Request `ed50c7baf2d8b935bb118f25758394ddfb04a671e902f39bfa66721b274daa85`
  (queue job alias `hxq-ed50c7ba…`; the request id is the canonical
  handle — `status`/`result`/`cancel` all key on it, verified this tick)
- Nonce `molasp-w8-hazardhold-t77`, image `paperclip-test`,
  1 cpu / 1 GiB / wall 2400 s, issue SON-4885, owner this lane.
- Recorded command (re-verified IN the request record this tick, exactly as
  admitted-ready): `python3 source/evidence/2026-10-08-w8-hazardhold/ktam_w8_hazardhold.py`
- Archive blob `2284d43a7494854fbf452e2dfc07fe009697a2100e241b3ab01518d8cfcefb22`.
- Created **2026-10-08T23:04:36Z** (v2; v1 `8acaa3c8…c7e4` was cancelled
  pre-admission at tick 77 for a recorded-command defect and never ran).
- Queue state at every probe: `queued`, reason verbatim —
  `ci admission floor; 1500m cpu must stay free on spark-4a06 for 2 x 500m ci runner slots + listener/burst slack`.
- Age at this tick's probe: **2.44 h** (wall clock; the 2400 s wall starts at
  admission, so the deadline that can lapse is the monitor timeout 02:50Z).

Probe log (all `queued`, same reason verbatim): submit 23:04:36Z (t77) →
23:57Z + 00:02Z (t80, card 64323f15 era) → 00:55Z (t83) → 01:17Z (t84) →
**01:29Z (t85, this tick)**.

## Monitor state changed: attempt budget EXHAUSTED (disclosed)

The armed monitor fired its 3rd cumulative attempt at 01:25:51Z (this wake).
`monitorAttemptCount=3`, `monitorNextCheckAt=null`. Two re-arm PATCHes this
tick (full `{"executionPolicy":{stages+monitor}}` shape, ceilings 4 then 8,
nextCheckAt 01:55Z) each returned **200 but were silently stripped** — the
response `executionPolicy` carries no `monitor`, top-level
`monitorNextCheckAt` stays null, `.changes` is `{}`. Working hypothesis
(unverified internals): the attempt counter is cumulative across armings and
a monitor whose count has reached a prior ceiling cannot be re-armed by
raising `maxAttempts` alone. 2-failure stop honored; no further monitor
writes this tick.

**Liveness therefore rests on the hourly routine tick** (contractual
scheduler for this card; six consecutive wakes within the hour: 00:03 →
00:15 → 00:55 → 01:05 → 01:25 → next expected well before 02:50Z), plus the
queued job itself as a first-class external continuation. The next tick
executes the criterion below if the waiter is still queued.

## Pre-drafted escalation artifact (child issue on SON-4885 → Platform Engineering lane)

Title: `Resource-capacity: ci admission floor on spark-4a06 has held a 1-cpu queued job >3.5h (SON-4885 w8 falsifier)`

Body (numbers verbatim from this note; no new claims required at post time):

> The persistent cluster queue's ci admission floor
> (`1500m cpu must stay free on spark-4a06 for 2 x 500m ci runner slots +
> listener/burst slack`) has kept request
> `ed50c7ba…4daa85` (paperclip-test, 1 cpu / 1 GiB / wall 2400 s) queued
> since 2026-10-08T23:04:36Z with no admission (age at criterion time
> ≥ 3.75 h). This is a resource-capacity escalation per the CEO's standing
> criterion on SON-4885 (01:05:34Z comment), not a job defect: the recorded
> command is verified admission-ready and the request is owner-scoped and
> idempotent. Recommended paths, in order:
> 1. Admit the waiter by temporarily borrowing burst slack against the floor
>    (job needs 1000m; the floor reserves 1500m for two 500m runner slots +
>    listener/burst) — one bounded exception, evidence-grade.
> 2. Accelerate the SON-4889 AC3 runner-floor path on spark-molasp-lab
>    (canary `3e20314` already on main; branch `son4889-ac3-runner-probe`
>    pushed) so the spark-4a06 CI floor relaxes structurally.
> Explicitly NOT requested: duplicate resubmission, direct Job submission,
> or deleting/altering other owners' resources.

## Collection chain (unchanged, all committed before the data exists)

`job_queue result` → `tools/import_queue_result.py` (frame → run.out,
byte-exact) → `tools/collect_w8.py` (frozen CAL/W8 gates, branch receipt) →
`tools/apply_w8_receipt.py` (figure/blog/addendum per verdict) →
pre-drafted prose branches (`research-log/2026-10-09-w8-prose-branches.md`).
On admission the collecting tick runs the chain; nothing in this note
changes those gates.
