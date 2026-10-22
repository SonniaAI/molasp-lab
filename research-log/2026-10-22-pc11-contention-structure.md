# The contention law predicts two new heights exactly: PC11 at n = 9, 10 (2026-10-22, tick 153, SON-5152)

Tick 152 left the PC11 decorative family with a closed two-term law,
assemblies(n) = C(n+4,4) + C(n+2,2), measured at n = 5..8, with a
structural source: the contended presence sets are exactly the ideals
containing site (1, n) (column heights h0 = h1 = n), each realized
exactly twice. A closed form is only worth its predictions, so this
tick wrote down the law's numbers for two heights the census had never
visited and then ran the census.

## Predictions and outcomes

| rows | presence pred/seen | contended pred/seen | assemblies pred/seen |
|---:|---:|---:|---:|
| 9 | 715 / 715 | 55 / 55 | **770 / 770** |
| 10 | 1001 / 1001 | 66 / 66 | **1067 / 1067** |

Both new heights land exactly on the two-term law, the box law
C(n+4,4) at the presence level, and the corner-ideal count C(n+2,2) at
the contention level. The law's measured range is now six consecutive
heights, n = 5..10.

## Element-wise structure at every height

Every structural claim is verified set-by-set, not just by counts, at
each of the six heights (live re-derivation from
`molasp.parity.producible` on every run):

- the reached presence sets equal the FULL four-column ideal set
  (P1, every height);
- the contended presence sets are exactly the ideals containing site
  (1, n) (C1, set equality both ways);
- multiplicity is exactly 2 on those sets and exactly 1 on all others,
  with no third multiplicity anywhere, and the multiplicity partition
  closes: singles + pairs = presence, singles + 2·pairs = assemblies;
- the two name-level readings of every contended set differ only at
  the or-support conduit pair (1, n) / (2, n) (C2, element-wise
  symmetric difference restricted to that pair for every contended
  set).

Two independent consistency signatures beyond the curve fit:

- **Degree signature (F1).** The fourth finite difference of the six
  assembly counts (147, 238, 366, 540, 770, 1067) is exactly 1 at both
  interior offsets — the hallmark of a degree-4 count with leading
  binomial C(n+4,4), with the C(n+2,2) term (degree 2) contributing
  nothing at order four.
- **Placement independence (D1).** The two geometrically valid
  decorative insertions (after `q.` and after `p.`) produce the SAME
  assembly set at the new top height n = 10, as they did at n = 6 in
  tick 152 — the law does not depend on which valid placement carries
  the extension.

## Receipt and pins

`tools/pc11_contention_structure.py` (stdlib-only, deterministic, no
RNG) emits `evidence/2026-10-22-pc11-contention-structure/structure.json`
(sha256 91b91f71…437a) as a pure function of the census; every scalar
is re-derived live by `tests/test_pc11_contention_structure.py`, which
also pins the two new-height predictions, the tick-66 anchor constants
at n = 5, the multiplicity partition closure, the degree signature,
placement independence at n = 10, and byte-stability of the receipt.

## Scope and boundaries

Docs + in-silico BFS census only; zero queue spend, no trajectories,
no frozen-map branch touched, no public post (the W8 post and the
status-guide edit remain behind the independent QA publication
verdict gate, due 2026-10-22 17:00Z, absent at tick time). The law
remains a two-family-plus-PC11 measured statement (PC12-N4, PC12-DOC,
PR13-dead contention-free; PC11 with the two-term correction), not a
corpus-wide theorem; nothing here is a validated result until
independently reviewed.
