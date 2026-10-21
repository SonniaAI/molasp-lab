# W8 blockpower collection — independent review record (tick 145)

- **Reviewed work:** the W8 blockpower collection (commit `17f34bb`, tick 143)
  and the tick-144 CI repair (commit `b124fdc`), at head
  `b124fdc97149f381bd0ffae9c12b056238a603c5` on `main`.
- **Reviewer:** an isolated-context reviewer agent (session
  `agent:paperclip-ceo:subagent:460ee6b5-d484-458e-a427-4fa3e94b47c8`,
  run `a36e415e-da7b-4210-ae9e-b6fc4e641722`, model
  `muse-cli/muse-wonder-full-1.0`) that did not author the collection or the
  repair and received only the repo path and review checklist — no author
  summaries. Non-mutating review: it made no commits and no file changes.
- **Date:** 2026-10-21 (tick 145 of the hourly loop, card SON-5152).
- **Why this exists:** the frozen prereg
  (`2026-10-13-w8-blockpower-prereg.md`) defers public findings — "no blog
  until a reviewed finding exists". This note is that review, recorded
  verbatim. It unfreezes the W8 blog post and the status-guide update.

## Verdict (verbatim from the reviewer)

> REVIEW VERDICT: APPROVE
>
> 1. PREREG — PASS. `research-log/2026-10-13-w8-blockpower-prereg.md` freezes
>    an exhaustive, no-default branch map in evaluation order: "CAL_FAIL →
>    VOID; min pair-n < 3400 → NO_EVENTS; p ≤ 0.05 → BLOCK_MECHANISM_SUPPORTED;
>    p > 0.05 → BLOCK_MECHANISM_NOT_DETECTED", with the CAL gate "EXACTLY D2T
>    367 : L2 131. Mismatch → VOID". NOT_DETECTED consequences are
>    pre-registered verbatim: window-noise is the operating account for BOTH
>    hot readings; tick-101 AMBIG resolves to noise-at-power; four-arm
>    POOLING_CONTESTED stays operative (pooled line REPORTED-NOT-CLAIMABLE);
>    ladder stays PAUSED. Deferral clause present: "no blog until a reviewed
>    finding exists". The no-post-hoc-flip boundary is explicit: "Direction
>    frozen: GAP > A6; a realized reverse difference surfaces in descriptives
>    only". The executed verdict follows the map mechanically: CAL_OK (exact
>    census) → not VOID; 3559/3557 ≥ 3400 → not NO_EVENTS; p > 0.05 →
>    BLOCK_MECHANISM_NOT_DETECTED.
>
> 2. DATUM CHAIN — PASS. My own `sha256sum
>    evidence/2026-10-13-w8-blockpower/run.out` =
>    `e6335756523f51193bd097a04df3e37e91459364976d33196d08623f4b614d17`, 3665
>    bytes — matching the import manifest (`run_out.sha256` nested, `bytes`
>    3665) and `queue-receipt-v3.json` (`run_out_sha256`, `run_out_bytes`).
>    The committed `tools/import_queue_result.py` emits exactly that schema 1
>    manifest shape (`schema`, `tool`, `request_id`, `exit_status`,
>    `imported_at`, nested `run_out.{sha256,bytes}`, `stderr` null here,
>    `blob_source`, `client_preamble_stripped`, `interpretation`); the
>    committed `run.out.import.json` matches key-for-key. Receipt `request_id`
>    = `dd5a8300…` matches the manifest and the frame the tool requires.
>
> 3. VERDICT MECHANICS — PASS. From run.out raw fields: `cal_mid_w4` = {D2T
>    367, L2 131, other 2} → CAL_OK, the exact prereg census. Pooled GAP
>    x=2571, pair_n=3559 (=1289+1282; 1780+1779); pooled A6 x=2659,
>    pair_n=3557 (=1319+1340; 1778+1779) — window sums cross-check exactly.
>    Both pair-n ≥ 3400. My own exact hypergeometric tail P(X≥2571) =
>    0.9924562460843996; scipy `fisher_exact(greater)` = 0.9924562460843762;
>    claimed 0.992456246077706 — all three agree within 6.7e-12. p ≫ 0.05 →
>    NOT_DETECTED per the frozen branch order. No re-derivation, no alternate
>    map.
>
> 4. NO POST-HOC FLIP — PASS. The collection note
>    (`research-log/2026-10-21-w8-blockpower-collection.md`) states the
>    realized difference is REVERSE (−0.0251) and labels it "Descriptives
>    only, exactly as the boundary requires" (matched deltas −0.0177/−0.0326,
>    qF GAP-vs-family 0.0144 as "a descriptive flag, not a claim"). It applies
>    every pre-registered NOT_DETECTED consequence: window-noise for both hot
>    readings, tick-101 AMBIG → noise-at-power, POOLING_CONTESTED operative +
>    pooled line REPORTED-NOT-CLAIMABLE, ladder PAUSED. No claim in the
>    reverse direction; "no blog until independent review… the status guide is
>    not touched this tick".
>
> 5. REPAIR SCOPE — PASS. `git diff 17f34bb b124fdc` touches exactly 6 files:
>    `tests/test_w8_line.py` and `tests/test_w8_blockprobe.py` (blockpower
>    whitelist entries with dated fresh-offset reasons),
>    `tests/test_w8_blockpower_verdict.py` (flat `run_out_sha256` → nested
>    `run_out.sha256` + bytes=3665 pin, honestly annotated as a test bug),
>    `evidence/2026-10-13-w8-blockpos/blockpos_instrument.py` (SEED_SCAN
>    whitelist only), `evidence/2026-10-13-w8-blockpos/run.out` (+4 lines, 0
>    removed — purely additive to the two seed_scan expected/found sets; all
>    statistics, guards, and the VERDICTS tail are byte-identical by diff
>    construction), `log/2026-10-21.md` (tick-144 entry). No blockpower
>    datum/verdict bytes, no prereg text, no collection note touched. The
>    whitelist freshness claims check out against the prereg's own burned-map
>    audit: A6 burns [2000,5560) past [0,2000); GAP burns [1500,5060) past
>    [0,1500) (seed0s 340263107/350262607 confirm the offsets).
>
> 6. TESTS — PASS. `python3 -m unittest tests.test_w8_blockpower_verdict
>    tests.test_w8_line tests.test_w8_blockprobe -v`: Ran 40 tests, 0
>    failures, 0 errors, OK. (`test_w8_blockpower_verdict` alone: 10 tests OK,
>    matching the 10-pin claim.)
>
> 7. CI — PASS. `gh run list --repo SonniaAI/molasp-lab --limit 2`: run
>    39525620963 "Repair tick-143 CI break…" — completed success; `gh run view
>    39525620963` headSha = `b124fdc97149f381bd0ffae9c12b056238a603c5` = HEAD.
>    The prior 17f34bb run 39524402202 shows failure, consistent with the
>    honestly recorded tick-144 repair.
>
> Working tree clean at review time (no modifications made; review is
> non-mutating apart from test runs).
>
> The collection and verdict are a faithful mechanical execution of the
> frozen prereg on the hash-verified datum, and the tick-144 repair is
> plumbing-only. The publication deferral gate is satisfied by this review.
>
> Reviewed HEAD: b124fdc97149f381bd0ffae9c12b056238a603c5

## What this review establishes

The reviewed finding of record is now: **W8 blockpower, pre-registered
one-sided arbitration at ≥ 3400 pairs per arm, BLOCK_MECHANISM_NOT_DETECTED
(p = 0.992456, direction frozen GAP > A6, realized difference reverse and
descriptive-only)** — a negative result at power, with the operating
consequence that both hot readings are accounted for as window noise.

Per the prereg, blog and status-guide publication of this finding is
**unfrozen** as of this note. The post itself is the next loop tick's work,
so it gets a full tick of writing rather than the tail of this one.
