# Tick 164 — The first true depth-3 census: the designs/013 fragment becomes real, and every pinned scalar lands

**Date:** 2026-10-22 · **Card:** SON-5152 (tick 164) · **Head:** this
commit · **Receipt:**
`evidence/2026-10-22-pc13-depth3-first-census/depth3.json` (sha256
`50c663f592636de844fee2a36fe1ba8187a9d678795622721be67063fdd972ed`)

## What happened

Tick 163 pinned the nested-shell product law and, with it,
falsifiable predictions for a depth-3 relay-chain family that could
not compile. This tick implemented the §1 carve-out and censused
that family. **Every pinned scalar landed exactly, at every height,
with the element-wise structure the law demands.**

## The carve-out (molasp/compiler.py)

`MAX_RELAY_STAGES = 3`: a relay CHAIN is admitted on the designs/012
per-body discipline — up to three stacked relays, each stage's
duplicate unit bodies reading the adjacent-below derived row (the
previous stage's head, or the spine for the first relay). The
blanket "second relayed OR head" refusal is replaced by a genuine
depth-bound refusal:

> `UnsupportedGeometry: rule atom 'x' at non-terminal row 7: relay
> chain depth 4 exceeds the admitted maximum 3 (designs/013 §1)`

AND bodies and mixed bodies at a relay row still refuse verbatim
(designs/012 §1), an AND consumer of a relayed head still refuses
(designs/009 §9.2 conflict), and a second terminal consumer of a
relayed head still refuses — now caught by the non-adjacency arm,
which turns out to be the honest geometric reason (the consumer
reads the head from a non-adjacent row). Both tick-163 probe axes
(`stacked_spine_relay`, `head_chained_relay`) now compile: they were
the admitted fragment all along.

## The census (PC13-D3, decor alphabet `tyzkmba`)

Terminal-first multiplicities ks = [k_w, k_r, k_u]:

    p. <decor>. q2 :- p. u :- q2. (x k_u) r :- u. (x k_r) w :- r. (x k_w)

**[2,2,2], heights 6..12 — pinned BEFORE the family could compile
(designs/013 §3), all seven exact:**

| n | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|----|----|----|
| pinned | 577 | 813 | 1110 | 1478 | 1928 | 2472 | 3123 |
| measured | 577 | 813 | 1110 | 1478 | 1928 | 2472 | 3123 |

Fiber histogram at n=6: `{1: 95, 2: 45, 4: 42, 8: 28}` — shell sizes
exactly (d+1)·C(n-d+2,2) (45/42/28 at d=2/1/0), fiber exactly the
SUFFIX product Π_{i≥d} k_i. The additive alternative (fiber
Σ_{i≥d} k_i − (m−d), totals 423 at n=6) is falsified at every
height; the law's margin over additive grows from 154 (n=6) to 476
(n=12).

**Legs, also exact:** [2,2,3] full table incl. n=12 → 3997 (the
power-of-two alternative separates here: shell_2 fiber 3, never
2^(k−1)=2); [3,2,2] n=6 → 689; depth-4 [2,2,2,2] (three relay
stages) n=8/9/10 → 2010/2606/3310 — the depth-4 pinned table is in
census range too, and it lands.

## Element-wise structure, live at every height (6..12)

- presence == the full four-column ideal set C(n+4,4), exactly;
- corner nesting C^(0) ⊆ C^(1) ⊆ C^(2) element-wise;
- **expected fiber element-wise:** every shape's realized fiber ==
  Π k_i over exactly the corners (1, n−i) it contains — the
  inclusion-exclusion overlap structure the suffix-product law
  encodes;
- every full fiber realizes ALL conduit combinations at the
  column-1 corner sites (8/8 at n=6 on every 8-fiber);
- readings differ only within the corner site pairs
  (1,n−d)/(2,n−d);
- statics: each relay stage's conduits are k in count and
  value-typed north (`{a}-t-done`); the terminal or-head keeps
  per-body glues north (`unit{j}_w-done`); every `unit{j}_{a}` body
  glue occurs exactly twice in the whole inventory — the per-body
  handshake, now verified at three stacked stages.

## Self-caught before landing

- The first static-check draft wrongly demanded relay value-typing
  at the TERMINAL stage; the terminal or-head's conduits keep
  per-body glues north by design. Caught by the receipt summary
  (`static_handshake_every_height: false`) and fixed before commit.
- A first draft of the census runner under-decorated the n=12
  program (6-letter alphabet for 7 needed rows) and silently
  censused an 11-row build — it reproduced the n=11 scalar exactly,
  which is what exposed it. The alphabet is now 7 letters
  (`tyzkmba`) and a statement-count pin guards the builder.
- The first push's hosted CI caught what my local runs had masked:
  I piped `unittest discover` through `tail`, so the recorded exit
  code was `tail`'s, not the suite's — four tick-158..161 fence
  pins (`test_second_relayed_head_refused` in the four corner
  files) were failing unheard. Fixed by re-pinning those four as
  what they truly are under the carve-out — depth-3 families that
  compile and census EXACTLY on the law — which added two
  never-pinned mixed points to the measurement set: [2,3,2] at
  n=7 → 1069 and [2,3,3] at n=7 → 1516, both landing exactly.
  Lesson recorded: never pipe a test run when the exit code is the
  evidence.

## Status

Docs + local census only, zero queue spend (full 7-height census +
legs: ~8s). Not a validated result until independently reviewed.
The W8 post and status-guide edit remain behind the QA verdict gate
(due 2026-10-22 17:00Z).

**Open next:** the depth-4 family censused at three heights here —
extend it to the full pinned table (n=6..12 needs a shorter-decor
anchor); a depth-3 point with UNEQUAL multiplicities at all three
stages ([3,2,3]); or turn the per-body handshake into a proof sketch
for general m (the suffix-product law is now measured at depth 1–4).
