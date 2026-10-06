# Design 002 — Atom order: lowering multi-atom recursion

Status: derived + machine-checked at τ=2 (aTAM) 2026-10-06; kTAM grid
queued (v3 value-typing carried per row); the anchored-cycle order
falsifier queued (below). Evidence:
`../evidence/2026-10-06-atom-order-2cycle/`.
Date opened: 2026-10-06. Prerequisite: designs/001 (v2.1 spine
discipline, v3 value-typed locks).

## Goal

Take the geometry-supplies-the-level-mapping claim (paper, branch (c);
IR field "level mapping", paper §toolchain table) from the single-atom
self-loop to a genuine cycle through two atoms, where no row-local
trick can substitute for an order. Witness program:

```
a.      p :- q.      q :- p.
```

Stable model `{a}`. Supported-but-unstable `{a,p,q}` — p supported by
q, q by p, pure circular support with no external anchor (semantics
anchored by the two-environment clingo cross-check,
`../evidence/2026-10-06-clingo-crosscheck/`). This is the loop the
loop-formula of L = {p,q} must forbid; the design question is what
forbids it in glue.

## Stage analysis (the compile-time solve the lowering reads order from)

Immediate-consequence iteration: T⁰ = {a}; no atom ever enters for
p or q. Least model {a}: a = true, p = q = false, stage(p) = stage(q) = ∞.
For a positive normal program the least model IS the stable model, so
this stage table is the complete semantic input the lowering needs.

**Lemma (rule-death dichotomy).** For a rule with a false head, every
wire dies in either geometry:

1. Some false body atom sits ABOVE the head row → its true-witness
   glue is not exposed by anything below the head (the designs/001
   `no-p` mechanism, now per-edge): the head's true-tile has no
   strength-2 path.
2. All false body atoms sit BELOW the head row → their rows expose
   only false-done north glues (v3 value-typing), which the head's
   true-tile does not bond: strength 0, not strength 1.

So the cycle cannot fire at ANY row position — order among false atoms
is free. Order is STRICT only on true atoms: a true atom's rule fired
from body atoms of strictly lower stage, so rows must linearly extend
the stage order on true atoms or a derivation loses its witness (see
the order falsifier below).

## Construction of record

3 columns × 3 rows above the 3-tile seed; spine glues SP1/SP2/SP3
strength 2, row-typed; value-typed decision/lock glues per v3 rule (a).

```
row3(q): [S3: S=SP3,E=go3,N=SP4] [D3T: S=rd2t-done | D3F: S=rd2f-done] [L3: W=rd3f,S=base3,N=cap3]
row2(p): [S2: S=SP2,E=go2,N=SP3] [D2T: S=q-true    | D2F: S=rd1t-done] [L2: W=rd2f,S=base2,N=base3]
row1(a): [S1: S=SP1,E=go1,N=SP2] [D1T: S=f-a       | D1F: S=u-a]       [L1: W=rd1t,S=base,N=base2]
seed:     N-glues: SP1 | f-a | base        (f-a IS the fact a.)
```

The cycle, edge by edge:

- **q → p is the cut edge** (order a < p < q): D2T's south glue
  `q-true` is a unique name in the whole system — no tile or seed face
  anywhere exposes it. Unwirable by construction; `SP4` caps the spine
  the same way.
- **p → q is wired but transitively dead**: D3T.S = `rd2t-done` — p's
  TRUE-done north glue, sitting directly below. It is exposed by
  exactly one tile face in the system (D2T's north), and D2T is never
  producible. The edge would fire if p could fire; p cannot. The
  transitive chain is anchored by the seed's facts, and no atom of a
  seedless cycle can be first.
- **Falsity chain**: D2F.S bonds row 1's true-done glue (`rd1t-done`,
  a = true), D3F.S bonds row 2's false-done glue (`rd2f-done`,
  p = false). The compiler knows every row's value at emit time (it
  solved the fixpoint), so each row's false-tile is anchored on the
  row-below's PREDICTED value glue. Terminal assembly = a linear
  certificate of the least model, one row per atom.

Tile budget: **12 tile types + 3 seed tiles**; glue alphabet
**26 names** (per added atom-row: +3 tile types, +~5 glues, +1 spine
tile +2 spine glues). Compare paper branch (b): an explicit level
argument costs a factor |atoms| in SPECIES (ground-program size), fatal
under a ~10² species ceiling; here |atoms| is a factor in assembly
DEPTH only — paid in read time (tick 10's readwindow invariant
emits T as a function of depth), not in search multiplicity.

**Machine-checked (exhaustive τ=2 BFS, `atam_check_2cycle.py`):**
20 producible assemblies, **1 terminal**, decoding `{a}`;
`D1F`, `D2T`, `D3T` producible in 0 of 20; `q-true` and `SP4` occur
exactly once system-wide; `rd2t-done` exposed only by D2T; every
value-side lock/channel pair (including `rd2t-done` vs `rd2f-done`)
strength 0; wrong tiles keep exactly b = 1 (spine bond only) in the
full correct assembly — un-lockable. The supported-but-unstable
`{a,p,q}` has NO realizing assembly: it would need D2T and D3T, and
each dies by a different mechanism (cut edge / transitive death).

## What this does not establish

1. **Body conjunction.** Every body here has ≤ 1 atom; a single south
   glue cannot read two witnesses. `r :- p, q.` needs a widened
   decision column or an in-row AND — designs/003 territory, and the
   known honest limit of the 3-column geometry.
2. **The order falsifier (anchored cycle).** Program
   `a. p :- a. p :- q. q :- p.` (stable {a,p,q}): with the correct
   stage order a < p < q, D_pT has a fact-wired variant; with the
   WRONG order a < q < p, q's true-tile reads p from above (dead) and
   the system terminates at {a,p} — a wrong-but-terminal decode that
   proves the compiler MUST emit stage order, not any order. Requires
   the OR construction (multiple true-variants per atom sharing value
   outputs); queued as the next machine check.
3. **kTAM carryover.** Rule (a) value-typing is verified per row at
   τ=2 and structurally (b = 1 wrong contexts); the per-row kTAM grid
   is queued, same protocol as designs/001 v3 (falsifier: any
   wrong-value channel above the catalogue curves).
4. **The stage order was computed by hand here.** Emitting tile sets
   from the stage table mechanically (the actual compiler pass) is not
   yet code; this design is its specification.

## Falsification criteria for this design

1. A producible path to any wrong tile at τ=2 — attack the BFS or the
   glue table.
2. A second terminal assembly, or any terminal decoding ≠ {a}.
3. A positive normal program whose stage order exists but the
   3-column geometry cannot realize (criterion 1 above is the known
   instance class; finding another is a result).
4. The order falsifier built the wrong way round and STILL decoding
   {a,p,q} — would refute the claim that stage order is load-bearing.
