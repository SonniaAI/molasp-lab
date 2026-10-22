# The counting law grows a correction term: PC11's name contention measured at height, assemblies = C(n+4,4) + C(n+2,2) (2026-10-22, tick 152, SON-5152)

Ticks 65/66 left the corpus-wide picture with one asymmetry: every
compiling program's BFS presence sets equal the well-founded ideal sets
of the attach grammar, and the binomial box law C(rows+4,4) held at
name level for PC12-N4, PC12-DOC and PR13-dead — but PC11 carried
**name contention** above the poset level (147 assemblies over 126
presence sets at n=5), measured at exactly one height. This tick
measures how that contention scales with height, and finds a closed
form.

## What was measured

Live BFS on the PC11 anchor `p. q. s. q2 :- p. r :- q2, s. r :- q2.`
(5 spine rows), extended with decorative facts to 6, 7 and 8 rows,
all re-derived from `molasp.parity.producible` on every run:

| rows | presence sets | C(n+4,4) | contended | C(n+2,2) | assemblies | C(n+4,4)+C(n+2,2) |
|---:|---:|---:|---:|---:|---:|---:|
| 5 | 126 | 126 | 21 | 21 | 147 | 147 |
| 6 | 210 | 210 | 28 | 28 | 238 | 238 |
| 7 | 330 | 330 | 36 | 36 | 366 | 366 |
| 8 | 495 | 495 | 45 | 45 | 540 | 540 |

Reached presence sets equal the full four-column ideal set at depth =
rows in both directions at every height — the box law now has a third
family measured at new heights, and it holds **at the presence level**
where contention exists.

## The two-term law and its structural source

**Name-level assemblies(n) = C(n+4,4) + C(n+2,2), exactly, at every
measured height.** The correction term is not a mystery constant: the
contended presence sets are **exactly those containing site (1, n)** —
equivalently, the order ideals with column heights h0 = h1 = n, whose
count is the number of partitions h2 ≥ h3 in [0, n], i.e. C(n+2,2).
Every contended set carries multiplicity exactly 2, and the two
name-level readings differ **only at the sites (1, n) / (2, n)**: the
or-support row's two truth conduits for the same presence. Everything
else is one tile per site, as in the contention-free families.

So PC11 is the first measured family whose assembly count is not pure
C(n+4,4) at name level, while its presence level stays exactly on the
box law — tick-66's "contention is contended-SHARED everywhere"
generalizes from one height to a height law with a structural
characterization.

## Decoration validity (probed, not assumed)

The decorative facts must be inserted among the leading facts: between
`q.` and `s.` (used here, mirroring the PC12-DOC placement) and after
`p.` both compile and agree exactly at n=6. Inserting between `s.` and
the `q2 :- p.` rule breaks the conjunctive variant's adjacent-below
geometry (`UnsupportedGeometry: conjunctive variant of 'r'`), and
appending after the last rule puts an OR at a non-terminal row
(rejected by the designs/008 stage-1 guard). The family is defined by
the valid placements, and the anchor reproduces the tick-66 constants.

## Scope and boundaries

BFS census only, run locally at zero queue spend; no trajectories, no
gate, no kinetic claim; the 2-terminal count at every height is
recorded descriptive, not load-bearing. The law is measured for this
family at n=5..8, not corpus-wide, and the §10.8 residual (grammar
table read off emitted faces, not proved from compiler source) stands.
Nothing here is a validated result until independently reviewed.

Pins: `tests/test_pc11_contention_height.py` (live re-derivation of
P1/A1/C1/C2/T1 at n=5..8 plus the anchor reconciliation). The W8
milestone post and the status-guide family-line edit remain behind the
distinct-agent QA publication gate on SON-5152 (rechecked this tick:
no QA-seat verdict yet; due 2026-10-22 17:00Z). In-silico kTAM only.
