# w8 collection-day application tooling (tick 82)

Commit that closes the executable pre-registration chain end-to-end:
on collection day nothing is hand-assembled anymore.

## What exists now

The full chain, each link pinned by tests committed BEFORE the data:

1. `job_queue result` → import `run.out` (request
   `ed50c7baf2d8b935bb118f25758394ddfb04a671e902f39bfa66721b274daa85`).
2. `tools/collect_w8.py` → verdict receipt (independent gate
   recomputation, harness cross-check, pre-registered action list).
3. **NEW** `tools/apply_w8_receipt.py` → one command that executes the
   receipt's mechanical actions:
   - `CAL_OK+HELD` — figure re-rendered with the w8 point CLOSED/
     measured (+ Wilson 95 bar, census label, measured-verdict line;
     prediction arm and hazard bracket stay visible as predictions);
     milestone blog post via the real `render_w8_post.py`; collection
     addendum appended to `research-log/2026-10-08-w8-hazardhold.md`
     with every number quoted from the receipt.
   - `CAL_OK+REFUTED` — figure re-rendered WITHOUT the beyond-w4
     extrapolation (quarantine per the pre-registered action);
     demolition post; addendum with the falsification sentence.
   - `CAL_FAIL+VOID` / `CAL_OK+NO_EVENTS` / `SMOKE_NOT_VERDICTABLE` /
     FORCED-DISAGREEMENT — REFUSED (exit 2, no file written anywhere),
     printing the receipt's own action list: those branches need
     diagnosis, never auto-writing.

## Discipline notes

- Gate order matters and is pinned: the BRANCH gate fires before the
  cross-check gate, because smoke receipts legitimately carry
  `cross_check: "skipped (smoke)"` and must land in the branch refusal
  with their action list, not in a misleading forced-receipt message.
- `window_curve_svg.py` pending mode is pinned byte-identical to the
  committed `designs/assets/011-window-curve.svg` — the default render
  cannot drift as the mode support ages.
- The addendum append is idempotent (marker `## Collection (<date>,
  SON-4885) — <branch>`); re-running apply rewrites figure/blog
  deterministically and never duplicates the note.
- Remaining hand step, on purpose: the designs/011 prose edit the
  receipt's action list spells out (tier wording is judgment, not
  transcription).

## Tests

8 new pins in `tests/test_apply_w8_receipt.py`: HELD end-to-end
(figure/blog/note contents, verbatim number flow, seed preservation),
note idempotency, REFUTED quarantine + demolition, all four refusal
classes with zero-write assertions, pending byte-identity.  Receipts
built through the REAL collector; the tmp repo root isolates writes.

Suite verbatim: `Ran 505 tests in 2.734s / OK (skipped=1)`
(= 497 + 8).

Waiter at commit time: still queued (ci admission floor on
spark-4a06), recorded command re-verified at probe; no new queue
submissions this tick — owner running-slot protection ahead of the
verdict.  No wet-lab work; no paper/preprint step.
