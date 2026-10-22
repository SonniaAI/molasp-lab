# Why the contention law holds: a gap-bijection derivation of PC11 (2026-10-22, tick 154, SON-5152)

Ticks 152-153 left the PC11 decorative family with a measured
two-term law, assemblies(n) = C(n+4,4) + C(n+2,2), confirmed at six
consecutive heights with a structural signature. This tick promotes
the law from measured to **derived**: it follows from two pure
counting lemmas plus one machine-verified compile-level fact, so the
only empirical content left is that last fact.

## The three lemmas

**L1 (box law).** Ideals of the four-column region are exactly the
column-height sets with weakly decreasing heights (h0, h1, h2, h3)
bounded by n. The gap map

    (h0, h1, h2, h3) -> (h0-h1, h1-h2, h2-h3, h3, n-h0)

is a bijection onto the compositions of n into 5 nonnegative parts
(each gap is >= 0 by monotonicity; suffix sums invert it; the five
gaps sum to n). Hence |ideals(n)| = C(n+4,4). No compiler in the
loop — this is stars-and-bars.

**L2 (corner law).** An ideal contains site (1, n) iff h1 = n, iff
(h0, h1) = (n, n). The free tail (h2, h3) runs over weakly decreasing
pairs in [0, n], and (h2, h3) -> (h2-h3, h3, n-h2) is a bijection
onto the compositions of n into 3 parts. Hence the corner ideals —
exactly the contended presence sets of ticks 152-153 — number
C(n+2,2).

**L3 (multiplicity partition; machine-verified).** Every ideal
carries exactly one name-level assembly, except the corner ideals,
which carry exactly two, whose two readings differ only at the
or-support conduit pair (1, n) / (2, n). This is the compile-level
fact, re-verified live at every measured height this tick
(`molasp.parity.producible`, element-wise, both directions, plus the
partition closure singles + pairs = presence and
singles + 2·pairs = assemblies).

**Theorem.** assemblies(n) = |ideals(n)| + |corner ideals(n)|
= C(n+4,4) + C(n+2,2).

The bijections are verified as *set* equalities, not just counts:
the gap-derived ideal sets equal `all_ideals(n)` exactly, the
height-encodings of the enumerated ideals equal the full composition
pool exactly, and the gap-derived corner sets equal
`ideals_containing((1, n))` exactly, at every measured height.

## A new height predicted first

The derivation was written before any n = 11 census ran; its numbers
were pinned from the closed form alone, then the census ran:

| rows | presence pred/seen | contended pred/seen | assemblies pred/seen |
|---:|---:|---:|---:|
| 11 | 1365 / 1365 | 78 / 78 | **1443 / 1443** |

Seven consecutive heights now (147, 238, 366, 540, 770, 1067, 1443),
every structural claim element-wise at every height.

## Beyond the census range

The bijections themselves are stress-checked at n = 20 — far past
any census run of the anchor family — where the gap-derived ideal
count is exactly C(24,4) = 10626 and both bijections remain exact
set equalities. (This pins L1/L2 as counting facts; it says nothing
about L3 at n = 20, which stays a census question.)

## What remains empirical

Only L3. The open problem it hands to the next ticks: derive the
multiplicity-2-at-the-corner behaviour from the conduit geometry
itself (why exactly the (1, n) / (2, n) or-support pair admits two
name-level readings and nothing else does), which would remove the
last measurement from the law.

## Receipt and pins

`tools/pc11_law_derivation.py` (stdlib-only, deterministic, no RNG)
emits `evidence/2026-10-22-pc11-law-derivation/derivation.json`
(sha256 62508ea8…9680) as a pure function of the census and the
bijections. `tests/test_pc11_contention_derivation.py` re-derives
every scalar live, pins the n = 11 prediction constants, the
partition closures, the bijection stress at n = 20, and the receipt
hash. Zero queue spend. Nothing here is a validated result until
independently reviewed.
