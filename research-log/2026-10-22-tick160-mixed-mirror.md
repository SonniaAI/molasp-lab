# Tick 160 — the mirror mixed point: k_r=2 × k_w=3

**Date:** 2026-10-22 · **Card:** SON-5152 (tick 160) · **Design:** designs/012 ·
**Receipt:** `evidence/2026-10-22-pc11-mixed-mirror/mixed_mirror.json`
(sha256 `b585cdc1…a27efef`)

## The question tick 159 left open

Tick 159 confirmed the inclusion–exclusion total law at ONE mixed
point, k_r=3 × k_w=2, with fibers {1: rest, 3: C_r\C_w, 6: C_w}. One
point does not fix a law: the mirror k_r=2 × k_w=3 was left open, and
it is the sharper test — the law says the fiber-6 overlap count stays
|C_w| while the off-overlap fiber MOVES from 3 to 2, i.e. the fiber-3
signature of M32 must vanish and the overlap fiber must stay put,
with the corner sets themselves unchanged (they are fixed by the
family geometry, not the head multiplicities).

## The prediction (registered before the census)

```
PC11-M23   p. q. s. q2 :- p. r :- q2. r :- q2.
           w :- r. w :- r. w :- r.
```

r is the relayed or-head at row n−1 with TWO duplicate unit bodies
(k_r=2, designs/012 relay), w the terminal or-head at row n with
THREE (k_w=3, tick-157 duplicate bodies). Family-local decor
alphabet tuvxyz. The law predicts

```
assemblies(n) = |I| + (k_r−1)|C_r| + (k_w−1)|C_w| + (k_r−1)(k_w−1)|C_r∩C_w|
             = C(n+4,4) + (n+1)(3n+2)/2 + 4·C(n+2,2)
             → 392/566/792/1080/1441/1887/2431  (heights 6..12)
```

with fibers mirroring to {1: rest, 2: C_r\C_w, 6: C_w} — fiber 3
disappears, fiber 6 stays on C_w. Falsifiable alternatives:
collapsed/shared-bit |I|+|C_r| (fiber 6 never), additive
|I|+|C_r|+2|C_w| (fiber 4 on C_w; numerically the T2U totals), power
|I|+|C_r|+7|C_w| (fiber 8 on C_w).

## The census (heights 6..12, all exact)

| n | presence | assemblies | mixed law | collapsed | additive | power | fiber hist |
|---|----------|-----------|-----------|-----------|----------|-------|------------|
| 6 | 210/210 | **392** | 392 | 280 | 336 | 476 | {1:140, 2:42, 6:28} |
| 7 | 330/330 | **566** | 566 | 422 | 494 | 674 | {1:238, 2:56, 6:36} |
| 8 | 495/495 | **792** | 792 | 612 | 702 | 927 | {1:378, 2:72, 6:45} |
| 9 | 715/715 | **1080** | 1080 | 860 | 970 | 1245 | {1:570, 2:90, 6:55} |
| 10 | 1001/1001 | **1441** | 1441 | 1177 | 1309 | 1639 | {1:825, 2:110, 6:66} |
| 11 | 1365/1365 | **1887** | 1887 | 1575 | 1731 | 2121 | {1:1155, 2:132, 6:78} |
| 12 | 1820/1820 | **2431** | 2431 | 2067 | 2249 | 2704 | {1:1573, 2:156, 6:91} |

Every scalar lands exactly on the registered prediction. Element-wise:
presence is the full ideal set C(n+4,4) at every height; the fiber-2
shapes are exactly C_r\C_w (set equality, not just count) and the
fiber-6 shapes exactly C_w; fibers 3, 4, 8 occur NOWHERE at any
height; every 6-fiber realizes all SIX conduit combinations
tile@(1,n−1) ∈ {Cr, Cr2} × tile@(1,n) ∈ {Cw, Cw2, Cw3} — the two
heads choose independently; readings within a fiber differ only at
the two site pairs.

## What the mirror adds beyond tick 159

1. **The overlap fiber is invariant under swapping which head is
   large.** M32: fiber 6 = k_r·k_w with k_r large; M23: fiber 6 =
   k_r·k_w with k_w large. Same set C_w, same count |C_w| — the
   product, not the maximum, not the sum.
2. **The off-overlap fiber tracks its own head's multiplicity
   alone** (3 under k_r=3, 2 under k_r=2), confirming the per-head
   correction Σ_h (k_h−1)|C_h| is genuinely per-head and the overlap
   correction is genuinely second-order.
3. **The additive alternative for the mirror is numerically the
   balanced family's measured law** (|I|+|C_r|+2|C_w| = the T2U
   totals 336/494/…/2249) — and the mirror lands strictly above it
   at every height. A shared-bit or additive world would have pinned
   the mirror to T2U's totals; it does not.

## Static structure (verified at every height)

The relay carries exactly two conduits (Cr, Cr2), both value-typed
north (N = {r}-t-done, never a body glue); the terminal row carries
three (Cw, Cw2, Cw3); all five body glues (unit1_r/unit2_r,
unit1_w/unit2_w/unit3_w) occur exactly twice in the whole inventory —
the body-identity handshake holds per head, per body, at both rows.
Unexamined neighbours still refuse (intermediate AND body, AND
consumer of a relayed head, second relayed head / stacking,
single-body chain depth > 2), all pinned in tests.

## Status and residue

The inclusion–exclusion law now holds at three of the four corners
of the {k_r, k_w} ∈ {2,3}² grid: (2,2) tick 158, (3,2) tick 159,
(2,3) this tick — each measured at seven consecutive heights. Open
next: the last corner (3,3) (predicted |I| + (n+1)(3n+2) +
6·C(n+2,2), e.g. 518 at n=6), three-head composition (does
Σ generalize to three correction terms + triple intersection?),
and the derivation of |C_r| = (n+1)(3n+2)/2 from relay geometry
(numerically confirmed at all three corners, still not derived).
Docs + static analysis + census cross-check only, zero queue spend;
the W8 post and status-guide edit remain behind the QA verdict gate.

Nothing here is a validated result until independently reviewed.
