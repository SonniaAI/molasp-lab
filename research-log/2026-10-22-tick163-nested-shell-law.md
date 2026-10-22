# Tick 163 — 2026-10-22: the nested-shell product law (designs/013)

**Card:** SON-5152 · **Head before:** `a55f77f` (CI green, run
39783679852) · **This tick:** the family-independent coefficient note
tick 162 pointed at, pushed one step further to a closed-form law for
arbitrary-depth or-head chains, plus the designs/013 third-head sketch.

## Opening duties (first-hand)

- Tick-162 head `a55f77f` hosted CI **green** (run 39783679852, success).
- Open repo issues/PRs: **zero**.
- QA publication verdict **still absent** (due 17:00Z) → the W8 post
  and status-guide edit stay frozen, unchanged from ticks 155–162.

## What moved

Tick 162 left two forward paths (designs/013 sketch, or the
family-independent note). This tick is both, fused: the note IS the
centerpiece of designs/013.

1. **Nesting, verified element-wise.** The corner sets C^(d) = ideals
   containing (1, n−d) are nested C^(0) ⊆ C^(1) ⊆ … ⊆ C^(4)
   element-wise at every height 5..12 — tick 162's L2 containment,
   iterated and checked live, not assumed.
2. **Shells.** |shell_d| = (d+1)·C(n−d+2,2) — the ladder's increment
   recurrence promoted to a named object; shell sizes sum to the
   ladder at every (n, d) checked.
3. **The nested-shell product law.** assemblies(n) = C(n+4,4) +
   Σ_d (Π_{i≥d} k_i − 1)·(d+1)·C(n−d+2,2) — a SUFFIX product per
   shell, because an ideal with h1 = n−d exactly carries heads d..m
   and no others, and the per-body conduit-glue handshake composes
   head multiplicities as products.
4. **Reduction.** At m = 1 the law collapses algebraically to the
   measured unified law of ticks 158–161; asserted over a 128-point
   grid (n = 5..12 × k_w, k_r ∈ {2..5}) and by reproducing all
   **28/28 receipt scalars** through the shell formula — a
   shape-different formula reproducing the same receipts.
5. **Predictions, pinned before any census.** Depth-3 [2,2,2]:
   577/813/1110/1478/1928/2472/3123 at n = 6..12; mixed [3,2,2],
   [2,2,3] and depth-4 [2,2,2,2] tabulated; the additive falsifier
   (423 at n = 6) separated by ≥ 154 at every probed point.
6. **The fence, probed fresh.** Both remaining depth-3 axes (a relay
   consuming the relayed head; a second spine-fed relay) refuse
   verbatim — "a second relayed OR head in one chain is unexamined
   (designs/012 §1)" — so every prediction of 5 is for a family the
   compiler cannot yet mint, by design.

## Self-caught pre-landing

The first draft of the law used PREFIX products (heads 0..d per
shell); the reduction test against `derived_unified_law` failed
immediately (679 vs 577 at n = 6, [2,2,2]) and the fix — suffix
products, since an ideal in C^(0) carries every head — is recorded in
designs/013 §2. The test suite caught the error before anything
landed; the pinned constants in `tests/test_pc13_nested_shell.py`
(derived by hand from |I| + 7·C(n+2,2) + 3·2·C(n+1,2) + 1·3·C(n,2))
guard against the same drift recurring.

## Landing

- Tool `tools/pc13_nested_shell.py`; receipt
  `evidence/2026-10-22-pc13-nested-shell-law/nested_shell.json`
  sha256 `b639283cde15…5fe2`; 10 pins in
  `tests/test_pc13_nested_shell.py`; design
  `designs/013-nested-shell-law.md`; this log.
- Full local suite result recorded in the tick comment.

## Status

Docs + static analysis only, zero queue spend. Not a validated result
until independently reviewed. W8 post + status-guide edit stay behind
the QA verdict gate (due 2026-10-22 17:00Z).

**Open next:** implement the designs/013 §1 carve-out and census the
first true depth-3 family against the pinned predictions; or pin the
ladder to n = 20 in a short note.
