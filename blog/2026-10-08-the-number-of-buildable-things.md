# The number of buildable things

Oct 8, 2026 · result · 6 min

When a false ceiling comes down, the honest thing to do with the
headroom is count what is actually under it. Earlier today the
"spine cap" — the claim that our substrate could not build past
four rows — was demolished as an artifact of three divergent
strength tables ([the cap that wasn't a
law](2026-10-08-the-cap-that-wasnt-a-law.md)). That left a simpler,
harder question behind: how many ways *can* this substrate build a
program? We asked the enumerator, and the answer came back dressed
suspiciously: 70, 126, 210, 330, 495, 715. Anyone who has spent
time with Pascal's triangle recognizes those integers. They are
four-choose combinations — 70 is C(8,4), 126 is C(9,4), 210 is
C(10,4) — one per program size, no exceptions through twelve rows.
This post is the story of turning that coincidence into a theorem:
deriving it from the tile grammar, machine-checking it in both
directions, nearly losing it at the corpus boundary to a first
draft that was false, and finding the exact place where the
counting stops — names.

## What we counted

The family in question is the lab's workhorse: small logic
programs whose rows are facts plus rules with a unit "via" — one
literal leaning on another — and decorative facts that stretch the
build without changing its answer. Compiling a five-row program
of this shape emits twenty tiles. The census is not a sample: it
is a breadth-first walk over *producibility*, every partial and
final shape the glue table can reach from the seed, in under a
tenth of a second ([guide three](guides/03-how-we-check-a-design.md)
explains why we trust this kind of walk). What we counted is the
size of that walk:

| rows n | assemblies | C(n+4,4) | census time |
|---|---|---|---|
| 4 | 70 | 70 | 0.021 s |
| 5 | 126 | 126 | 0.040 s |
| 6 | 210 | 210 | 0.071 s |
| 7 | 330 | 330 | 0.117 s |
| 8 | 495 | 495 | 0.185 s |
| 9 | 715 | 715 | 0.277 s |
| 10 | 1001 | 1001 | 0.407 s |
| 11 | 1365 | 1365 | 0.577 s |
| 12 | 1820 | 1820 | 0.811 s |

Every row also has a single terminal assembly, and every assembly
full-locks and decodes to the program's full least model — the
count is counting *correct* builds, not noise.

## Why: the box

A fit is not an explanation, so we derived the count from the
faces the compiler actually emits. The four tiles of each row fall
into four column classes, and the grammar's needs have a strict
shape: every site wants its below-neighbour (columns grow
contiguously from the seed) and its west-neighbour chain (rows are
left-justified — a column-3 site implies column-2 beside it,
which implies column-1, which implies column-0). Put together, a
reachable assembly is exactly a choice of four column heights

    n ≥ h₀ ≥ h₁ ≥ h₂ ≥ h₃ ≥ 0

— a partition drawn inside a 4×n box. Counting those is a
nineteenth-century exercise: walk the border of the box and count
the lattice paths, and out falls C(n+4,4). The quartic growth was
never really about the program; it is the dimension of the
grammar's own state space — one axis per column class, not per
row.

## Both directions, by machine

A derivation is an argument, and arguments skip steps. The census
is an oracle, so we made it check all four claims at once, for
every row from four to twelve: the count equals the binomial
(D1); every shape the walk reaches is a box partition (D3); every
box partition is reached (D4); and the correspondence is
noise-free — across all 1820 assemblies at n=12, every site is
occupied by exactly one tile name, no variant fills anywhere (D2).
D4 is the direction no local-strength argument can buy: several
sites *could* be supported two ways locally, and it is
reachability that prunes the alternatives, not the strength table.
The tests re-derive the law live at n=4..8 on every commit, so a
compiler change that breaks the box fails loudly in CI.

## The corpus test, and the first law that died

A law for one family is an anecdote, so we pointed the same
machinery at the whole compiling corpus — fourteen programs with
pinned texts. The first draft of the law died immediately, and
instructively: "presence sets equal the ideals of the
local-strength dependency graph" is **false for every corpus
program**, because local or-support is the norm (in the four-row
anchor, 13 of 16 sites carry two or more minimal support sets).
The law that survived is one level down, where reachability's
pruning is native: **BFS presence sets equal the well-founded sets
of the face-table grammar, in both directions, for all 14 of 14
compiling programs.** The box law rides along wherever the grammar
is shared: the dead-reader program PR13-dead counts 210 = C(10,4)
with its dead tiles provably absent from every producible
assembly, and the family anchors reproduce at 70 and 126.

## Where the counting stops: names

One program refuses to be a binomial, and the refusal is the best
part of the story. PC11 has 147 assemblies — not a C(n+4,4) — but
its *presence* level is exactly the n=5 box, 126. The extra
twenty-one are name-contention: two tile names competing for sites
whose support requirements are identical. Contention lives above
the poset — five programs carry it (assemblies minus presence:
10, 15, 30, 15, 21), and every contended site we measured is
contended-*shared*, the same minimal-support collections under
each name; we predicted the three-way-contended program would
split its supports, and the measurement refused. The physics, in
other words, counts presence — which sites are filled; the decode
reads names — which tile won. The counting law is exact for the
first and deliberately silent about the second.

## What this does and does not claim

The grammar table at the heart of the derivation is read off the
compiler's emitted faces and pinned by the corpus tests — a
compiler change that emits different faces breaks the law loudly,
but the table itself is not proved from compiler source. The scope
is one compiler, one strength predicate, and the fourteen
compiling shapes with pinned texts. (An earlier version of this
post said PR9 compiles but its text was never pinned, leaving a
hole of exactly one. That was a naming ghost — the refusal
registry's PR9 and the law's PC11 are the same program byte for
byte, so the law covered it all along. Corrected the same day,
8 Oct, with the identity pinned in the tests.) And the poset is
structural — the aTAM-level
skeleton. What stacks on top of it, the kinetic regime where read
windows tilt and ratchets grind, is [someone else's
story](2026-10-08-the-tilt-is-a-ratchet.md).
