# 2026-10-22 — Tick 162: the unified law's coefficients are now DERIVED from staircase geometry

Issue: SON-5152 (hourly research loop). Follows tick 161 (`research-log/2026-10-22-tick161-m33-corner.md`),
which closed the {k_r, k_w} square but left every coefficient of the total law
**measured**. This tick closes the remaining open item: *derive
|C_r| = (n+1)(3n+2)/2 from relay geometry* — and goes one step further: **all
three** coefficient sets of the unified law are now derived in closed form from
the four-column staircase, with every census demoted to a cross-check.

## The ideal staircase

Presence ideals of the PC11 decorative family at height n are exactly the
staircase height vectors `n >= h0 >= h1 >= h2 >= h3 >= 0` with ideal
`{(x, y) : y <= h_x}`. Everything below is arithmetic on these tuples.

## Derivations (all machine-checked at every height 5..12, receipt
`evidence/2026-10-22-pc11-coefficient-ladder/ladder.json`)

- **L0 (box law).** |I| = C(n+4,4): weakly decreasing 4-tuples from {0..n},
  witnessed live by the hockey-stick induction DP `T(top, k) = sum_{v<=top}
  T(v, k-1)` whose closed form is C(top+k, k) — checked, never assumed.
- **L1 (stratification — the tick's core).** The relay corner set
  C_r = ideals containing (1, n−1) is `h1 >= n-1`, partitioning into exactly
  three (h0, h1) strata: (n, n) with C(n+2,2) trailing pairs, (n, n−1) and
  (n−1, n−1) with C(n+1,2) each. Hence
  **|C_r| = C(n+2,2) + 2·C(n+1,2) = (n+1)(3n+2)/2** — 51/70/92/117/145/176/
  210/247 at n=5..12, matching enumeration element-wise at every height.
  Geometric reading: the relayed or-head sits one row below the terminal head
  (row n−1 vs n), so its contention corner is (1, n−1); the strata say how far
  the leading column climbs above it (full / shoulder / even).
- **L2 (containment — why the overlap collapses).** C_w = ideals containing
  (1, n) is h1 = n (forcing h0 = n), which satisfies h1 ≥ n−1: **C_w ⊆ C_r
  element-wise**, because the two corners share column 1 one row apart. The
  overlap term of the inclusion-exclusion is |C_w| itself — the collapse of
  the total law to |I| + (k_r−1)|C_r| + k_r(k_w−1)|C_w| is geometry, not
  coincidence.
- **L3 (difference set).** C_r \ C_w is exactly the two h1 = n−1 strata, each
  C(n+1,2) — the "northwest shoulder pair", total n(n+1) — matching the
  fiber-2/fiber-3 shapes measured in ticks 158–161.
- **L4 (the depth ladder — falsifiable prediction).** The same stratum count
  at corner depth m (site (1, n−m), where a chain of m+1 or-heads would
  contend if the compiler ever admits depth > 2):
  **|C^(m)| = Σ_{j=0..m} (j+1)·C(n−j+2, 2)** — h1 = n−j admits j+1 choices of
  h0. Predicted before enumeration: m=2 lands 115/155/201/253/311/375/445 at
  n=6..12 and m=3 lands 155/215/285/365/455/555/665; both verified exact at
  every reachable (m, n), m ≤ 3. Each deeper corner adds one stratum:
  |C^(m)| − |C^(m−1)| = (m+1)·C(n−m+2,2). Pinned to n = 20, beyond the
  census's alphabet reach.
- **S1 (square, derived-only).** With L0+L1+L2 the unified law
  `C(n+4,4) + (k_r−1)(n+1)(3n+2)/2 + k_r(k_w−1)C(n+2,2)` is a closed-form
  function of (n, k_r, k_w) with **no enumerated input**; it reproduces all
  28/28 scalars of the four receipts of record and the live census legs of
  this tick (T2U 336/494/702/970/1309/1731/2249 at n=6..12; M33 518/730 at
  n=6,7).

## Self-caught error (method, not luck)

The first implementation of L4 flipped the stratum weight —
Σ(m−j+1)·C(n−j+2,2) instead of Σ(j+1)·C(n−j+2,2). The enumeration
cross-check caught it before anything landed (m=1 predicted 77 vs enumerated
70 at n=6), exactly the discipline the receipts exist for. The test suite
also caught a wrong increment recurrence in its own first draft
(C(n+3,3)−C(n−m+2,3) vs the correct (m+1)·C(n−m+2,2)) — fixed pre-landing.

## Three-head composition: the guard fence, probed live

Tick 161's other open item was three-head composition. The unexamined
neighbours probed live at n=6, both **refused** by the v0.2 geometry guard,
verbatim and identical:

> UnsupportedGeometry: rule atom 'w' at non-terminal row 6: a second relayed
> OR head in one chain is unexamined (designs/012 §1)

for a second terminal OR consumer (`v :- r. v :- r.`) *and* a second terminal
unit consumer (`v :- r.`) of the relayed head — adding any second consumer
pushes the first consumer off the terminal row and hits the second-relayed-
head fence. So three-head composition does not exist in compiler v0.2 along
this axis; the forward paths are (a) a designs/013-style fragment that admits
a genuine third head at its own terminal row, or (b) the L4 ladder, which now
pre-derives the contention coefficients for any future deeper-relay family.

## Status

Docs + static analysis + census cross-check only, zero queue spend. Not a
validated result until independently reviewed. The W8 post and status-guide
edit remain behind the QA verdict gate (due 2026-10-22 17:00Z, still absent).

**Open next:** designs/013 sketch for an admitted third head; or push the
derived ladder into a family-independent note (the coefficients of any
future or-head family are now a lookup in L4).
