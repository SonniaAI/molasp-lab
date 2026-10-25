# Design 013 — the nested-shell product law and the third-head fragment

**Date:** 2026-10-22 · **Card:** SON-5152 (tick 163) · **Status:** law
pinned by `tests/test_pc13_nested_shell.py` (live re-derivation + 28/28
receipt reproduction + refusal pins); fragment is a SKETCH — nothing
depth-3 compiles today, and that is the point.

## 0. The fence, probed fresh

Compiler v0.2 admits at most one relayed or-head per chain. Tick 162
fenced a second *terminal* consumer of the relayed head; this tick
probed the two remaining depth-3 axes live at n = 6, and both refuse
verbatim:

> `UnsupportedGeometry: rule atom 'u' at non-terminal row 6: a second
> relayed OR head in one chain is unexamined (designs/012 §1)`

for a relay consuming the relayed head (chain `q2 → r → u → w`) and
identically for a second spine-fed relay below the first
(`u :- q2` feeding `r :- u`). Every depth-3 route hits the same
sentence. Nothing below claims otherwise: the predictions of §3 are
for a family that does not exist yet.

## 1. The fragment sketch (what would have to be admitted)

The designs/012 move was: admit the intermediate OR-head *with a
discipline* — duplicate-unit bodies on the adjacent-below derived row,
per-body conduit glue, value-typed re-type above so growth is
bit-blind. The depth-3 generalization admits one more stage on the
same terms:

```
q2 :- p.            spine (unchanged)
u :- q2. u :- q2.   second relay (NEW, row n-2): unit bodies on the spine
r :- u.  r :- u.    first relay (row n-1): unit bodies on the second relay
w :- r.  w :- r.    terminal OR-head (row n, unchanged)
```

Each stage keeps the per-body identity handshake: every body owns
exactly one conduit glue occurring exactly twice in the inventory
(its conduit E and its own reader W), minted per body per head — the
mechanism that already forces fiber = product of live head
multiplicities at depth 1 (ticks 157–161). The guard carve-out would
have to permit a relay whose input is another relay's head, row by
row, with the same refusal set (no AND bodies, no mixed shapes, no
chain depth beyond the admitted m). Designing that carve-out is the
implementation work; this document only fixes what it must preserve.

## 2. The nested-shell product law (family-independent coefficients)

Independently of any fragment, the staircase already fixes the
coefficients. A head at chain depth d contends at corner site
`(1, n-d)`; corner sets `C^(d)` are **nested element-wise**
(`C^(0) ⊆ C^(1) ⊆ …`, the tick-162 L2 containment iterated — verified
element-wise live at every height 5..12, depth ≤ 4), with the ladder
`|C^(m)| = Σ_{j≤m} (j+1)·C(n-j+2,2)` and shell sizes

    shell_d = C^(d) \ C^(d-1),   |shell_d| = (d+1)·C(n-d+2,2).

An ideal in shell_d has `h1 = n-d` exactly, so it contains the corner
of head i **iff i ≥ d**: shell_d carries heads d..m and no others.
The per-body glue handshake composes head multiplicities as products
on the ideals whose corners contain them, so for terminal-first
multiplicities `ks = [k_0, …, k_m]`:

    assemblies(n) = C(n+4,4) + Σ_{d=0..m} (Π_{i≥d} k_i − 1)·(d+1)·C(n-d+2,2)

A **suffix** product per shell. (A prefix product — heads 0..d — was
the first draft of this note and is wrong: an ideal in C^(0) carries
*every* head, terminal included. Self-caught by the reduction test
below before anything landed.)

**Reduction (m = 1).** `|I| + (k_w k_r − 1)|C_w| + (k_r − 1)|C_r\C_w|
= |I| + (k_r − 1)|C_r| + k_r(k_w − 1)|C_w|` — exactly the measured
unified law of ticks 158–161. Asserted live over a 128-point grid
(n = 5..12 × k_w, k_r ∈ {2..5}) AND by reproducing all **28/28 receipt
scalars** of the four corners through the shell formula, whose shape
differs from the law it reproduces.

## 3. Falsifiable predictions (unreachable today, pinned before any census)

For the future depth-3 family of §1, at ks = [2,2,2], heights 6..12:

    577 / 813 / 1110 / 1478 / 1928 / 2472 / 3123

and at the mixed points [3,2,2]: 689/957/1290/1698/2192/2784/3487,
[2,2,3]: 818/1132/1518/1986/2547/3213/3997, and the depth-4 point
[2,2,2,2]: 1099/1511/2010/2606/3310/4134/5091. Fiber predictions:
shell_d ideals census at exactly Π_{i≥d} k_i (suffix products), never
at 2^{m+1}, never additive. The additive falsifier lands 423 at
n = 6 vs 577 product — a single future census separates them by ≥ 154
at every probed point. If the future family censuses anywhere else,
this law is wrong and the receipts say so.

## 4. Status — UPDATED tick 164: the fragment is real and §3 landed

At tick 163 this was docs + static analysis only, zero queue spend;
the fragment of §1 was a sketch with no compiler work. **Tick 164
implemented the carve-out** (`MAX_RELAY_STAGES = 3` in
`molasp/compiler.py`, same per-body discipline, everything else
still refused) and censused the family: [2,2,2] lands
577/813/1110/1478/1928/2472/3123 at n=6..12 — every pinned scalar
exact, fiber histograms exactly the suffix products, the additive
falsifier separated at every height, and the depth-4 point
[2,2,2,2] lands 2010/2606/3310 at n=8..10. Receipt
`evidence/2026-10-22-pc13-depth3-first-census/depth3.json`; pins
`tests/test_pc13_depth3_first_census.py`. The tick-163 fence probes
now compile (they are the admitted fragment); the refusal boundary
moved to genuine depth excess, AND/mixed bodies at relay rows, and
non-adjacent consumers — all pinned verbatim. Not a validated
result until independently reviewed. The W8 post and status-guide
edit remain behind the QA verdict gate (due 2026-10-22 17:00Z).

**Open next:** extend the depth-4 census to the full pinned table;
unequal multiplicities at all three stages ([3,2,3]); or promote
the per-body handshake to a proof sketch for general m (the law is
now measured at depths 1-4).

## 4a. Status — UPDATED tick 165: the table is COMPLETE and the
last shape axis is closed

Tick 165 pinned (law-only, before census) and then censused:
the **depth-4 [2,2,2,2] full table** 1099/1511/2010/2606/3310/
4134/5091 at n=6..12 — every scalar exact (heights 6/7/11/12 new);
the **first ALL-stages-unequal point [3,2,3]**
986/1348/1788/2316/2943/3681/4543 at n=6..12 — every scalar exact,
fibers exactly the suffix products {1,3,6,18} at every height, the
additive alternative separated by 420..1404; and the depth-4
placement pair [3,2,2,2] n=6 -> 1323, [2,2,2,3] n=6 -> 1621 (the
bottom-relay-3 point's fibers exactly {1,3,6,12,24}). Statics:
the per-body handshake holds at FOUR stacked stages at every
height 6..12. Receipt
`evidence/2026-10-22-pc13-depth4-full-unequal/depth4_unequal.json`;
pins `tests/test_pc13_depth4_full_unequal.py`.

**Open next:** the proof-sketch gaps of section 5 below (tile
inventory totality and choice-function independence at general m);
 widen the multiplicity grid (k in {2..5}) at depth 3; or return to
 the publication track once the QA verdict lands.

## 5. The handshake-to-proof sketch (tick 165) — promoted from the
open list

**Claim (general m).** For an admitted relay chain of depth m with
duplicate-unit bodies and per-body conduit glue, the reading count
on an ideal I is

    |readings(I)| = prod over heads i with corner (1, n-i) in I of k_i

which sums over the nested shells to the suffix-product law of
section 2. The sketch assembles three verified static lemmas:

1. **Body identity** (verified element-wise at every height 6..12,
   depths 1..4, k in {2,3}, tick 156 + 164 + 165 statics): each
   body `unit{j}_{a}` mints a fresh glue g occurring EXACTLY twice
   in the whole inventory — on its conduit E face and on its own
   reader W face. This is the handshake that makes a reading a
   function of the body chosen, not of the tile history below.
2. **Value-typing north** (verified R1 every height): every relay
   stage re-types its conduits' N faces to `{a}-t-done`, so the
   growth above a relay row is bit-blind to which conduit was
   taken; shape, not reading history, carries the ideal upward.
3. **Coupling at the corner** (verified tick 156 at depth 1 and
   re-verified by the X1 conduit-combination census at depths
   2..4, every height): at a corner site pair the south-face
   demand forces exactly one west match; the only west-matching
   tile is the same body's reader (glue arithmetic at TAU=2 with
growth order closing the east escape), so the reading at stage i
   is a FUNCTION of the stage's local bit, with exactly k_i
   choices.

Corner site pairs of different stages are one row apart and share
no face (non-adjacency is exactly why the second-consumer probe
refuses), so the per-stage choice functions COMPOSE
INDEPENDENTLY; the reading count is the product of the k_i over
the stages whose corners I contains. An ideal in shell_d carries
exactly heads d..m (h1 = n-d), which gives the suffix product.

**Gaps to a full proof** (falsifiable, in order):

- **(a) Tile-inventory totality at general m** — no gluing beyond
  the handshake pairs can close a reading. Currently exhaustive
  statics at m <= 3 and the full census cross-check at m <= 4;
  a general-m gluing-graph argument is unwritten.
- **(b) Choice-function independence** — the X1 census shows every
  conduit combination realized on every full fiber at every
  measured point; a direct construction (choose conduits stage by
  stage, bottom-up) is the natural induction but is not yet
  written down as a proof.
- **(c) The non-adjacency arm** is immediate (corners are one row
  apart by construction) but its converse role — that ANY consumer
  off the adjacent-below row breaks lemma 1 — is verified only as
  the guard refusal set, not as a geometric theorem.

The sketch is falsifiable at every stage: any census that lands
off the suffix-product law, or any full fiber missing a conduit
combination, kills the corresponding lemma. That is exactly what
ticks 163-165 tested at every reachable point; the law survived.

## 6. The k-grid at depth 3 — UPDATED tick 166: five new full
## tables, k reaches 5, and the orientation test passes

Tick 166 censused five new depth-3 multiplicity tuples (terminal-
first ks = [k_w, k_r, k_u]), every scalar pinned law-only in the
tool docstring BEFORE census:

| point     | n=6..12 table                                          | fibers (suffix products) |
|-----------|--------------------------------------------------------|--------------------------|
| [4,2,2]   | 801/1101/1470/1918/2456/3096/3851                      | {1,2,4,16}               |
| [2,4,2]   | 969/1325/1758/2278/2896/3624/4475                      | {1,2,8,16}               |
| [2,2,4]   | 1059/1451/1926/2494/3166/3954/4871                     | {1,4,8,16}               |
| [5,2,2]   | 913/1245/1650/2138/2720/3408/4215                      | {1,2,4,20}               |
| [4,3,2]   | 1109/1501/1974/2538/3204/3984/4891                     | {1,2,6,24}               |

All 35 scalars exact; additive alternative separated at every
height (margins 322→1066 and up, largest [4,3,2] 560→1859);
element-wise structure (presence, nesting, expected fiber, conduit
combos, reading restriction) holds at every height; R1/B1
handshake statics green at n=6 and n=12 for every point; fence
unchanged.

The k=4 triple is ORIENTATION-DISCRIMINATING: the same multiset
{4,2,2} at three different stages produces three pairwise
DIFFERENT fiber sets, each exactly the suffix products for its
placement — the stage that carries the 4 is identifiable from the
census alone.  The first k=5 point ([5,2,2]) lands with fiber 20
exactly where the law says (5·2·2, never 8 = 2^3 and never 9 =
5+2+2); [4,3,2] is the first all-distinct non-palindromic tuple
(fibers {1,2,6,24}, never {1,2,6,8} or {1,2,5,24}).

Grid state after tick 166 (full tables n=6..12 unless noted):
{2,3}×{2,3} square (ticks 158-161), [2,2,2]/[3,2,2]/[2,2,3]/
[2,3,2]n7/[2,3,3]n7/[3,2,3] (ticks 163-165), the five points
above (tick 166), depth-4 [2,2,2,2] plus [3,2,2,2]/[2,2,2,3] at
n=6 (tick 165).  Still uncensused at depth 3: k=5 beyond the
(5,2,2) axis and mixed (5,x,y)/(x,y,5) tuples; depth-4 unequal
beyond n=6 singles.  Every measured point, without exception,
lands exactly on the suffix-product law — 100+ pinned scalars by
now.
