# Stage-6 Option II probe-first baseline (tick 59)

Date: 2026-10-08, work started ~04:13Z (wake 04:00Z); time anchored
to this tick's commit, not an anticipated finish (tick-57 lesson).
Run: SON-4850. Compiler PRISTINE — no gate edits this tick.

## What this tick did

Executed step 1 of the landing order pre-registered in
`research-log/2026-10-08-stage6-option2-design.md` (designs/009 §9.5):
regenerate every pinned receipt generator on the pristine tree
(ec49a73) and byte-compare against the committed receipts, freezing
the result as the pre-edit reference manifest for the implementation
tick (`evidence/2026-10-08-stage6-option2-probe/probe_manifest.json`,
tree_head = ec49a73d79ceb0777fa04c7b5264a65424887bec).

## Measured results

1. Both census receipts regenerate byte-identically on the pristine
   tree: lock-misplacement-census (sha256 b7a5c70f…cd32) and
   census-generality (sha256 737f04a7…9f69a). Deterministic as-is.
2. The parity-corpus receipt does NOT regenerate raw-byte-identically:
   exactly 3 of 414 lines differ, all wall-clock timing fields
   (`seconds_compile` 0.002→0.001 and 0.008→0.007, `seconds_bfs`
   0.002→0.001). With timing fields masked (`total wall <T>s`,
   `"seconds_*": <T>`), the receipts are identical — zero content
   drift; the corpus embeds machine-noise timings.

## Consequences (pre-registered for the implementation tick)

- The "receipts byte-identical BEFORE gate edits" gate MUST use the
  timing-masked compare for the parity corpus, or it can fail on
  noise with no content drift. Census receipts stay raw-compared.
- Use this manifest as the frozen pre-edit reference; post-edit
  receipts record against it (same masking rule).
- Everything else in the landing order is unchanged: gate A union
  (both head polarities), §9.2 consumer-aware layout + reader swap,
  pin order receipts → PC9/PC10 byte-stability → PC12 → PR13-dead →
  PR14, honest boundaries as in §9.5.

## Queue receipt (first duty)

Tick-47 waiter request 9e79de4389423dfbdb8d5313afcc7603a1abc8bf
5097743157b7ad15ff58e145 (nonce dg2win-l3vac-v1, job
hxq-9e79de4389423dfb): STILL QUEUED at the ~04:02Z owner-scoped
status probe (~11 h; reason "queued: resource/owner limit; gateway
and engine margin preserved"). collected: null. No resubmission
(idempotent request stands); monitor on SON-4846
(nextCheckAt 03:05Z, timeoutAt 04:15Z, wake_owner) remains the
standing collector path; if its wake fires after timeoutAt with the
job still queued, the next tick must decide monitor re-arm vs
lane/CPU re-check with evidence from the live probe.

## Boundaries

Design-only + probe tick: no compiler change, no new pins, no model
claims beyond the receipts above. Suite verbatim
`Ran 421 tests in <t>s / OK (skipped=1)` (docs-only change).
