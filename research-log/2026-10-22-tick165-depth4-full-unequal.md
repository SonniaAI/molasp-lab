# Tick 165 — the depth-4 table completes and the last shape axis closes: all-stages-unequal lands

**Date:** 2026-10-22 · **Card:** SON-5152 (tick 165) · **Head:** see
commit · **Receipt:**
`evidence/2026-10-22-pc13-depth4-full-unequal/depth4_unequal.json`
sha256 `efdebabab902b994…23d7a4` · **Pins:**
`tests/test_pc13_depth4_full_unequal.py` (17)

## What tick 164 left open

Three paths (designs/013 §4): the depth-4 full table, unequal
multiplicities at ALL three stages, and promoting the per-body
handshake to a proof sketch. This tick executed all three.

## Predicted first, law-only, before any census

Written as literals in the tool docstring, then censused:

- depth-4 [2,2,2,2] full table n=6..12:
  **1099/1511/2010/2606/3310/4134/5091** (tick-163 pins; heights
  6/7/11/12 never censused before)
- [3,2,3] — the design's named all-stages-unequal point — n=6..12:
  **986/1348/1788/2316/2943/3681/4543**
- depth-4 placement singles: [3,2,2,2] n=6 → **1323**,
  [2,2,2,3] n=6 → **1621**
- fiber predictions: [3,2,3] exactly {1,3,6,18}; [2,2,2,3] exactly
  {1,3,6,12,24}

## What landed

Every scalar exact. Depth-4 full table: all seven pinned values,
structure element-wise at every height (presence = ideal set
C(n+4,4), nesting, expected fiber, conduit combos, corner-pair
readings; n=12 fiber hist {1:1155, 2:220, 4:198, 8:156, 16:91}).
[3,2,3]: all seven exact, fibers exactly the suffix products at
every height, additive alternative separated by 420→1404.
Placement singles exact; the bottom-relay-3 fibers are exactly
{1,3,6,12,24} (the terminal choice of which stage carries the 3 is
now measured both ways). Statics: per-body handshake at FOUR
stacked stages at every height — every stage value-typed north,
every `unit{j}_{a}` glue exactly twice. Fence unchanged (depth-5,
AND/mixed bodies, second consumer still refuse; both admitted
axes compile). All 16 receipt summary flags true.

## The proof sketch (designs/013 §5, new)

The handshake argument is now written as a three-lemma induction
skeleton — body identity, value-typing north, corner coupling —
with non-adjacency giving independent composition and shell
membership giving the suffix product. Three explicit gaps to a
full proof are named: tile-inventory totality at general m,
choice-function independence, and the non-adjacency converse.
Each gap is falsifiable by exactly the census machinery this tick
ran; the law survived everything reachable.

## Self-caught

Two pre-landing corrections: (1) my first draft of the n=12
depth-4 fiber-histogram pin was written from the [3,2,3] pattern
instead of the receipt — verification against the actual receipt
caught it (1375/198/156/120/71 → 1155/220/198/156/91); the pin now
quotes the receipt. (2) While reading the tick-164 receipt I
briefly misread a truncated JSON print as a rows-convention
discrepancy (presence 210 vs 495); re-deriving from `all_ideals`
showed the histogram sums consistently — no discrepancy, lesson:
never audit a truncated print, audit the file.

## Method

Docs + local census + statics only; stdlib-only, deterministic,
zero queue spend. Not a validated result until independently
reviewed. The W8 post and status-guide edit remain behind the QA
verdict gate (due 2026-10-22 17:00Z; still absent at tick open).

## Open next

General-m proof gaps (a)/(b) of §5; multiplicity grid widening
(k ∈ {2..5}) at depth 3; publication track once the QA verdict
lands.
