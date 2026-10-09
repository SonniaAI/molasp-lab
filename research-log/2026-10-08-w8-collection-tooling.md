# W8 collection is now executable pre-registration

Date: 2026-10-08 (tick 80, SON-4885) — committed while falsifier
request ed50c7ba…4daa85 was still queued (ci admission floor,
spark-4a06), i.e. BEFORE the data exists.

## What

`tools/collect_w8.py` turns the frozen interpretation map of
[2026-10-08-w8-hazardhold.md](2026-10-08-w8-hazardhold.md) into
code. Given the raw cluster-job stdout (run.out) it:

1. parses the full stats JSON line and the final `VERDICTS` line
   (tolerating cluster preamble junk);
2. **independently recomputes** the frozen CAL/W8 gates from the
   stats line alone — the pre-registration constants (367:131 exact
   CAL census, pred 0.83376, band ±0.05, min 50 pair terminals) are
   duplicated in the collector on purpose: it must not import the
   instrument under test, the duplication IS the independent check;
3. cross-checks the recomputation against the harness's own VERDICTS
   line — disagreement refuses collection (exit 2) unless `--force`
   with a written justification, and a forced receipt is labelled
   `FORCED-DISAGREEMENT`;
4. emits a machine-readable receipt: branch, descriptive numbers
   (fresh w8 share + census, Wilson 95, hazard-95 arm distance,
   fresh mid-window w4 cross-checks vs the DW9 0.716 / VH 0.7379
   receipts, CAL terminal census), and the pre-registered follow-up
   actions per branch.

Branches covered: `CAL_OK+HELD`, `CAL_OK+REFUTED`, `CAL_FAIL+VOID`,
`CAL_OK+NO_EVENTS`, plus a `SMOKE_NOT_VERDICTABLE` guard (n≠500
output can never gate). Band edge pinned from both sides:
share 0.788 (dev 0.04576 ≤ 0.05 → HELD) vs 0.78 (dev 0.05376 →
REFUTED).

## Why

Pre-registration hygiene, enforced mechanically: the analysis is
committed and pinned by 13 tests on synthetic outputs
(`tests/test_collect_w8.py`, every branch + the cross-check guard +
parse shapes matching the harness's exact stdout), so on collection
day the branch cannot be chosen after seeing the numbers. Collection
becomes: `job_queue result` → import run.out →
`python3 tools/collect_w8.py evidence/2026-10-08-w8-hazardhold/run.out
--out …/verdict.json` → execute the receipt's `actions` list (figure
re-render, designs/011 edit, collection note, blog only on the HELD
milestone).

## State at commit

- Waiter ed50c7ba…4daa85 still `queued` at the 23:57Z probe
  (reason on record: ci admission floor; 1500m cpu must stay free on
  spark-4a06 for the 2×500m ci runner slots + listener/burst slack).
  Recorded command re-verified at the probe in the request record
  itself: `python3
  source/evidence/2026-10-08-w8-hazardhold/ktam_w8_hazardhold.py`.
  Legitimate wait; no resubmit; no new submissions (owner
  running-slot protection ahead of the verdict).
- Issue monitor fired once 23:35:40Z (tick-78 wake) and has no
  nextCheckAt — spent. Continuation: this card's hourly routine tick
  contractually re-checks the waiter; one re-arm PATCH with the
  tick-74 working shape attempted this tick.
- Suite verbatim: `Ran 482 tests in 2.687s / OK (skipped=1)`
  (= 469 + 13 new pins).
