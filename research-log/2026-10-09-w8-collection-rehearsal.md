# 2026-10-09 — w8 collection-day REHEARSAL: the full chain end-to-end on synthetic data (tick 90)

## What

`tools/w8_collection_rehearsal.py` drives the ENTIRE five-step
collection chain through the real command lines — `import_queue_result.py`
→ `collect_w8.py` → `w8_decision_atlas.py` — as subprocesses, on
clearly-labeled SYNTHETIC data, in an isolated rehearsal root that a
guard refuses to place inside `evidence/`.  Fifth pre-datum piece
(after ticks 84/86/87/88/89): piecewise pins existed for every stage,
but nothing had proven the chain composes through the actual CLIs —
argument surfaces, exit codes, file plumbing, byte-exact recovery.

Scenarios drilled (synthetic stats in the harness's pinned output
shape, stamped `REHEARSAL-SYNTHETIC — not the datum`):

| scenario | datum | collector branch | atlas verdict | atlas region |
|---|---|---|---|---|
| held | 384/461 | CAL_OK+HELD (cross-check ok) | HELD | hold-only |
| refuted | 300/500 | CAL_OK+REFUTED | REFUTED | chain-falsified |
| no_events | 30/40 | CAL_OK+NO_EVENTS | NO_EVENTS (refusal) | — |

Refusal spot-checks at CLI level (exit 2, message verified): wrong
request id in the frame; empty stdout section.  The rehearsal receipt
records `"synthetic": true` and `interpretation: "none …"` — the drill
adds ZERO interpretive authority; the frozen gates stay in
`tools/collect_w8.py`, untouched.

## Near-miss disclosed (caught by the drill itself)

The first `synth_blob` draft built the protocol-2 frame by
`"\n".join(parts)` with empty-string elements for the echo blank
lines — that emits ONE newline too many per section (separator + blank
line collapse differently).  The rehearsal's own byte-exactness
assertion (`run.out == synthetic stdout`) failed on the first run and
refused to proceed.  This is precisely the class of framing slip that
would have cost minutes on collection day; rebuilt by explicit
concatenation (`file content + one echo newline` per section, as tick
84 pinned from the client source) and pinned in
`tests/test_w8_collection_rehearsal.py`.

## Why it matters

Collection day is now one mechanical run whose every joint has been
exercised: queue blob → byte-exact run.out → collector receipt
(cross-check ok) → atlas reading → pre-drafted prose branches
(tick 87).  The only thing the drill cannot rehearse is the datum
itself — by design.

## Evidence

- Drill output (verbatim):
  `PASS held datum [384, 461] -> CAL_OK+HELD / atlas HELD (hold-only)`
  `PASS refuted datum [300, 500] -> CAL_OK+REFUTED / atlas REFUTED (chain-falsified)`
  `PASS no_events datum [30, 40] -> CAL_OK+NO_EVENTS / atlas NO_EVENTS (None)`
  `PASS refusal wrong_request_id exit=2 (refused=True)`
  `PASS refusal empty_stdout exit=2 (refused=True)`
- Suite: `Ran 574 tests in 3.834s / OK (skipped=1)` (= 567 + 7 new
  pins in tests/test_w8_collection_rehearsal.py: evidence-tree guard,
  frame round-trip, stamp, all-scenario verdicts, on-disk artifacts,
  refusal spot-checks).

## Queue state at this tick

Waiter `ed50c7baf2d8b935bb118f25758394ddfb04a671e902f39bfa66721b274daa85`
probed 02:19Z: still `queued` — ci admission floor ("1500m cpu must
stay free on spark-4a06 for 2 x 500m ci runner slots + listener/burst
slack"), reason verbatim in the request record, recorded command
re-verified in the record.  No resubmit, no new submissions; owner
running-slot protection holds.  CEO 02:50Z criterion NOT reached at
probe (~31 min out) — the ~02:46Z tick owns the mechanical escalation
decision (pre-staged artifact `de4e4c9`).
