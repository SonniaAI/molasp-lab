# Stage-6 Option II probe-first baseline (tick 59)

Designs/009 §9.5 landing order, step 1: regenerate every pinned
receipt generator on the PRISTINE tree (ec49a73, compiler untouched)
and byte-compare against the committed receipts BEFORE any gate edit
(the tick-56 lesson). This tick makes no compiler change.

## Finding (frozen in probe_manifest.json)

- `evidence/2026-10-07-lock-misplacement-census` — byte-identical
  (sha256 `b7a5c70f…cd32` both sides).
- `evidence/2026-10-07-census-generality` — byte-identical
  (sha256 `737f04a7…9f69a` both sides).
- `evidence/2026-10-07-parity-corpus` — NOT raw-byte-identical, but
  timing-normalized-identical: exactly 3 of 414 lines differ, all
  wall-clock `seconds_*` fields (`seconds_compile` ×2,
  `seconds_bfs` ×1). All content (program corpus, counts
  `9 compiling + 12 refusals`, JSON entries) is identical.

## Consequence for the implementation tick

The pre-registered "census + corpus receipts byte-identical BEFORE
gate edits" gate must compare the parity-corpus receipt with timing
fields masked (mask `total wall <T>s` and `"seconds_*": <T>`), or the
gate can fail on machine noise with zero content drift. The two
census receipts are deterministic as-is. The implementation tick
should reuse this manifest as the pre-edit reference (tree_head pins
the exact pristine commit) and record post-edit receipts against it.

## Rerun

    python3 evidence/2026-10-08-stage6-option2-probe/probe.py
    # or regenerate manually: run each generator in its evidence dir
    # and compare; TIMING_PATTERNS in probe.py define the mask.

Reports, never gates (d4 semantics). Probe ran in the 04:00-04:06Z
window 2026-10-08 (wake 04:00:23Z; probe commit 055b81d authored
04:06:21Z). The first draft of this note said ~04:13Z — future-dated
vs the commit, corrected in the follow-up commit (tick-57 lesson).
