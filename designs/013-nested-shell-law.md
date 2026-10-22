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

## 4. Status

Docs + static analysis only, zero queue spend; the fragment of §1 is
a sketch with no compiler work. Not a validated result until
independently reviewed. The W8 post and status-guide edit remain
behind the QA verdict gate (due 2026-10-22 17:00Z).

**Open next:** implement the §1 carve-out and census the first true
depth-3 family against §3; or pin the ladder to n = 20 in a note.
