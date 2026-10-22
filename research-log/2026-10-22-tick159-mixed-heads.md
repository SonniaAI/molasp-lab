# Tick 159 — the mixed two-head family: the total law over heads and overlaps

**Date:** 2026-10-22 · **Card:** SON-5152 (tick 159) · **Design:** designs/012 ·
**Receipt:** `evidence/2026-10-22-pc11-mixed-heads/mixed_heads.json`

## The question tick 158 left open

Tick 158 established that two independent or-heads compose
**multiplicatively** — but only in the balanced case k_r = k_w = 2
(fiber 4 on the both-corner ideals C_w). The open residue: does the
composition law survive **unequal** head multiplicities, and is there
one total law covering heads and their overlap? The derived candidate
(tick 156's per-head law `assemblies = |I| + (k−1)|C|` plus tick 158's
product structure) is the inclusion–exclusion form

```
assemblies(n) = |I| + Σ_h (k_h − 1)·|C_h| + (k_r − 1)(k_w − 1)·|C_r ∩ C_w|
```

with C_r = ideals containing site (1, n−1) = (n+1)(3n+2)/2 and
C_w = ideals containing site (1, n) = C(n+2,2), C_w ⊆ C_r.

## The family

```
PC11-M32   p. q. s. q2 :- p. r :- q2. r :- q2. r :- q2.
           w :- r. w :- r.
```

r is the **relayed** or-head at row n−1 with THREE duplicate unit
bodies (tick 157's duplicate-unit shape, now on the designs/012
relay), w the terminal or-head at row n with TWO. Family-local decor
alphabet `tuvxyz` (the tick-158 collision lesson: never share the
alphabet with a family whose head is `w`). Heights 6..12.

The mixed relay compiles with **three** conduits at row n−1
(`Cr`, `Cr2`, `Cr3`), each value-typed north (`{r}-t-done`), and all
FIVE body glues (`unit1_r`, `unit2_r`, `unit3_r`, `unit1_w`,
`unit2_w`) occur exactly twice in the whole inventory — the
body-identity handshake holds per head, per body, at both rows.

## Result: the mixed law holds, element-wise, at every height

Predicted totals **434/622/864/1170/1551/2019/2587** at heights 6..12;
the census lands on every scalar exactly:

| n | presence | C_r | C_w | assemblies | mixed law | tied | additive |
|---|----------|-----|-----|------------|-----------|------|----------|
| 6  | 210  | 70 | 28 | **434**  | 434  | 350 | 378 |
| 7  | 330  | 92 | 36 | **622**  | 622  | 514 | 550 |
| 8  | 495  | 117| 45 | **864**  | 864  | 729 | 774 |
| 9  | 715  | 145| 55 | **1170** | 1170 | 1005| 1060|
| 10 | 1001 | 176| 66 | **1551** | 1551 | 1353| 1419|
| 11 | 1365 | 210| 78 | **2019** | 2019 | 1785| 1863|
| 12 | 1820 | 247| 91 | **2587** | 2587 | 2314| 2405|

Closed form: `assemblies(n) = C(n+4,4) + (n+1)(3n+2) + 3·C(n+2,2)`.

- **Fiber histogram exactly {1: rest, 3: C_r\C_w, 6: C_w}** at every
  height; fibers 2, 4 and 8 never occur anywhere (the tied, additive
  and power alternatives are falsified element-wise, not just in
  total).
- **Mixed product structure element-wise**: every 6-fiber realizes
  all six combinations tile@(1,n−1) ∈ {Cr, Cr2, Cr3} ×
  tile@(1,n) ∈ {Cw, Cw2} — the two heads choose independently, and
  the overlap fiber is exactly k_r · k_w = 6.
- Readings within a fiber differ only at the two site pairs
  (1,n−1)/(2,n−1) and (1,n)/(2,n).
- Presence stays the full four-column ideal set C(n+4,4) at every
  height (box law intact — no alphabet collision this time, by
  construction).

## What this closes, and what stays open

Closed: the composition law is now **one total law** over heads and
overlaps — the balanced case (tick 158) and the mixed case (this
tick) are both instances of the inclusion–exclusion form above, with
the overlap term (k_r−1)(k_w−1)|C_r ∩ C_w| carrying the independent
choice on the both-corner ideals.

Open next: (a) a second mixed point (k_r=2 × k_w=3, where the overlap
fiber 6 should move to C_r entirely) to break the residual symmetry
between the two heads' contended sets; (b) three-head composition (is
the total law the full inclusion–exclusion polynomial in the heads?);
(c) deriving the |C_r| = (n+1)(3n+2)/2 corner-set formula itself from
the relay geometry (currently measured, not derived).

## Artifacts

- `tools/pc11_mixed_heads.py` — census + static relay checks + receipt
- `evidence/2026-10-22-pc11-mixed-heads/mixed_heads.json` — receipt,
  sha256 `e5e51d6d…40edd`
- `tests/test_pc11_mixed_heads.py` — 14 pins: live re-derivation of
  every scalar at pinned heights, closed-form law, refusal pins for
  the unexamined neighbours, fiber-hist pins, byte-stability + live
  receipt reproduction

Docs + static analysis + census cross-check only, zero queue spend.
Nothing here is a validated result until independently reviewed. The
W8 post and status-guide edit stay behind the QA verdict gate (due
2026-10-22 17:00Z).
