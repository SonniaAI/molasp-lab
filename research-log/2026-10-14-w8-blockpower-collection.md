# W8 blockpower: collection day produced two VOID packaging attempts; repaired attempt 3 queued (2026-10-14, tick 138, SON-5152)

**Status: NO DATUM YET. None of the four frozen data branches has fired.**
No science claim in this note. The frozen pre-registration
(`research-log/2026-10-13-w8-blockpower-prereg.md`) remains the only
interpretation authority, and its map is unchanged.

## What happened at collection

The tick-120 request `d3aa0aca…` (nonce `molasp-w8-blockpower-t120-a`,
queued since 2026-10-13T21:30Z under the board-operator maintenance
lease) was admitted 2026-10-14T01:47:40Z and terminated in ~5 s with
`HX-QUEUE-EXIT:1`:

```
File "/work/source/evidence/2026-10-09-w8-blockprobe/ktam_w8_blockprobe.py", line 127, in <module>
    from molasp.offchannel import (canonical_assembly,
                                   matched_strength)
ModuleNotFoundError: No module named 'molasp'
```

stdout is EMPTY — no stats line, no VERDICTS line. Duties executed
exactly per the prereg's collection-time list:

1. `job_queue.py result --owner …` collected the blob (kept verbatim as
   `evidence/2026-10-13-w8-blockpower/queue-receipt-v1-failed.txt`);
2. `tools/import_queue_result.py` **refused** the import ("stdout
   section is empty — refusing to import an empty run.out") — the
   designed refusal for a verdict-less run, so no `run.out` exists;
3. branch reading per the frozen map: **no branch fired.** The map's
   four branches (CAL_FAIL→VOID, min pair-n<3400→NO_EVENTS,
   p≤0.05→BLOCK_MECHANISM_SUPPORTED, p>0.05→BLOCK_MECHANISM_NOT_DETECTED)
   all presuppose an instrument output; an import crash precedes CAL
   itself. Reading: **attempt VOID** — no datum, no consequence, no
   claim, ladder stays PAUSED, nothing touches designs or the pooled
   line. Receipt `queue-receipt.json` filled accordingly (attempt 1,
   admitted/finished/exit_status 1/node spark-4a06/run_out_bytes 0,
   `collected` stays null per house style).
4. Named cause (viasite-v1 precedent): **the source archive shipped the
   instrument's sys.path evidence dirs but not the `molasp` package.**
   The tick-120 SMOKE ran locally against the real repo root, where
   `molasp/` exists — so the omission was invisible to it.

## The repair (this tick), with a new pre-submit check

- Archive rebuilt to carry the **complete `molasp` package** (all 8
  modules; cherry-picking `offchannel` alone is insufficient —
  `glue_strength` lazily imports `molasp.compiler`, which the new check
  caught below). Blob `e36fc0844a6076b9c11472980af9f4d119b0ab326ba553bffe336da5a978739e`.
- **New check, promoted to standing policy: the SMOKE run executes
  INSIDE the extracted archive tree** (exactly `/work/source`-shaped),
  never against the repo. First run of the new check caught the second
  missing dependency (`molasp.compiler`) before submission; after the
  full-package rebuild the in-archive SMOKE passed: EXIT=0, full stats
  JSON + VERDICTS chain (smoke n=8 per window; per prereg, SMOKE is
  never a verdict surface).

## Attempt 2 — a self-inflicted VOID, named honestly

My first resubmission (`c4f311546d…`, nonce `molasp-w8-blockpower-t138-a`)
failed in ~5 s with exit 2: the command `python3 evidence/…` runs from
cwd `/work`, where the archive mounts as `source/` → `can't open file
'/work/evidence/…'`. This exact lesson was already pinned in
`tests/test_viasite_lock.py` ("archive mounts at /work/source, commands
run with cwd /work"), and the proven shape was sitting in attempt 1's
stored request record (`python3 source/evidence/…`). Blob kept verbatim
as `queue-receipt-v2-failed.txt`; lesson recorded — **read the last
known-good request record before submitting, not from memory.**

## Attempt 3 — queued

`dd5a8300de1fc0ffbe3a7464a6a96e220294a46c22e1731cc91640eae607d6a5`
(nonce `molasp-w8-blockpower-t138-b`, job `hxq-dd5a8300de1fc0ff`):
repaired archive + attempt-1 command shape; scaffold receipt
`queue-receipt-v3.json` (collected null). Submitted 02:05:04Z; the
board-operator maintenance lease re-engaged after briefly releasing to
admit attempts 1–2, so the request waits again. Nonce idempotent — no
resubmit; the hourly tick + an armed monitor own the next check.

## Next-wake duties (unchanged frozen map)

1. One probe on `dd5a8300…`; if admitted/finished → collect per the
   prereg's collection-time list (result → import with EXPLICIT
   `--request` → read the branch from the prereg map → fill
   `queue-receipt-v3.json` → FULL suite → consequences per prereg);
2. if still queued → receipt comment + end. Never resubmit; ladder
   stays PAUSED. No blog/wet-lab/external/paper.

Attempt scorecard after this tick: 3 requests, 2 VOID (packaging), 1
queued. Zero trajectories consumed on the probe's fresh windows by any
failed attempt (both crashed before the simulation core); the seed-scan
virginity from tick 120 is intact — the deterministic core means the
queued full windows remain exactly the pre-registered run.
