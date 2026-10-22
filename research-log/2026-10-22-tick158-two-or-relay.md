# Tick 158 — two or-heads compose multiplicatively (the truth-OR relay)

**Date:** 2026-10-22 · **Card:** SON-5152 (tick 158) · **Design:** designs/012 ·
**Receipt:** `evidence/2026-10-22-pc11-two-or/two_or.json`

## The question tick 157 left open

Tick 157 closed the single-head question — a k-body or-head censuses at
fiber exactly k, never 2^k — and named the composition question: two
**independent** or-heads in one assembly. Do the contentions **add**
(one shared bit, fiber 3 on the overlap) or **multiply** (independent
bits, fiber 4)?

The question was unreachable: compiler v0.2 refused any OR at an
intermediate derived row ("needs a northward truth-OR relay"), and one
of the two heads must sit one row below the terminal. Probed live
first — both natural two-or programs refused with exactly that guard.

## Fragment extension by design (designs/012)

The **northward truth-OR relay**: a duplicate-unit OR-head may sit at
an intermediate row; its per-body machinery is byte-identical to the
terminal case (each body still mints its own conduit glue
`unit{j}_r`, the east–west body-identity handshake), and only the
**northward** faces re-type to the *value* glue `{r}-t-done`
(conduit N faces and `d_north`). Everything above bonds south against
the value glue only, so growth north of the relayed head is bit-blind
— which is precisely what the old variant-typed north face would have
broken (row n's conduit would have bonded only against body 1,
killing the contention it was supposed to carry).

Refused, loudly, still: intermediate AND bodies, mixed bodies,
non-adjacent unit bodies, an AND consumer of a relayed head (the
designs/009 §9.2 passthrough re-type would clobber the relay), a
second relayed head in one chain, and single-body chain depth > 2.
All pinned in `tests/test_pc11_two_or.py`.

## The family and the three candidate laws

```
PC11-T2U   p. q. s. q2 :- p. r :- q2. r :- q2. w :- r. w :- r.
```

r = relayed or-head at row n−1 (two duplicate unit bodies on q2),
w = terminal or-head at row n (two duplicate unit bodies on r);
decorative extension as in PC11, heights 6..12. With
`C_w` = ideals containing (1, n) = C(n+2,2) (the corner law) and
`C_r` = ideals containing (1, n−1) = (n+1)(3n+2)/2:

| law | total | fiber on C_w |
|---|---|---|
| multiplicative | \|I\| + \|C_r\| + 2\|C_w\| | 4 |
| additive | \|I\| + \|C_r\| + \|C_w\| | 3 |
| collapsed | \|I\| + \|C_r\| | 2 |

## Result — multiplicative, at every height 6..12

assemblies(n) = C(n+4,4) + (n+1)(3n+2)/2 + 2·C(n+2,2), landing
**336 / 494 / 702 / 970 / 1309 / 1731 / 2249** — every scalar exact;
the additive and collapsed totals are falsified element-wise at
every height. Fiber histogram exactly
{1: rest, 2: |C_r|−|C_w|, 4: |C_w|}; **fiber 3 never occurs
anywhere**; the fiber-2 shapes are exactly C_r∖C_w and the fiber-4
shapes exactly C_w. The multiplicative structure is **element-wise**:
every 4-fiber realizes all four combinations (tile at (1,n−1) ∈
{C_r, C_r2}) × (tile at (1,n) ∈ {C_w, C_w2}) — a product, not a
selection. Readings differ only at the two site pairs.

Static side, verified from the emitted inventory at every height:
both of r's conduits expose N = `r-t-done` (value-typed north, never
a body glue), every row-n south read into row n−1 is
`r-t-done`/spine/base only, and all four body glues
(unit1_r/unit2_r/unit1_w/unit2_w) occur exactly twice in the whole
inventory — tick-157's L-east handshake intact at both rows.

## A construction bug the census caught (methodological note)

The first receipt run used the shared PC11 decor alphabet
"tuvwxyz" — whose 4th letter **w** collides with this family's
terminal head atom. The presence box law broke exactly at n=10 (the
first height inserting "w." as a fact while w is also the or-head:
the fact row and the head row mint the same {w}-t-done glue and the
geometry wrecks), with the n=10..12 censuses shifted one height
down. The box law is a real invariant checker, not bookkeeping: the
collision was caught, not silently mis-censed. The family now uses
its own alphabet t,u,v,x,y,z (skipping w).

## Why this matters

The two composition primitives of the fragment now have measured
arithmetic: same-site bodies are **additive over corner ideals**
(assemblies = |I| + (k−1)·|corner|, tick 157) and **distinct sites
are multiplicative** (this tick, fiber 4 = 2×2 on the overlap). That
is exactly the structure of a product measure over per-head bits —
the census-level signature of the per-body glue handshakes composing
independently. Open next: a mixed two-head family (k_r = 3 relayed ×
k_w = 2 terminal, predicted fiber 6 on C_w), and the additive total
law |I| + Σ_h (k_h−1)|C_h| + Π-corrections on overlaps.

Zero queue spend: BFS censuses only, stdlib, no RNG. Nothing here is
a validated result until independently reviewed.
