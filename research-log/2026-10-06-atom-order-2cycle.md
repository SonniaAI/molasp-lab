# 2026-10-06 — designs/002: the 2-cycle witness, atom order made executable

**Tick 13 (SON-4743). Unreviewed notebook promotion per lab convention;
no C-claim advanced; C2 unchanged.**

## What was derived

Designs/002 opens the multi-atom recursion line the queue carried since
tick 4. Witness `a. p :- q. q :- p.` — stable `{a}`, supported-but-
unstable `{a,p,q}` (circular support through a genuine 2-cycle, the
loop a loop formula must forbid; semantics anchored by the tick-7
clingo cross-check). The lowering: one row per atom on the designs/001
v2.1/v3 discipline, rows ordered by the immediate-consequence stage
function (a < p < q; stage(p) = stage(q) = ∞).

The design's claim is the **rule-death dichotomy**: a rule with a false
head dies in either geometry — false body atom above the head leaves
its true-witness glue unexposed (the `no-p` mechanism, now per-edge);
false body atom below leaves only a false-done north glue, which the
head's true-tile does not bond (v3 value-typing, strength 0, not 1).
Order among false atoms is therefore free; order is strict only on
true atoms. In the built system the cycle dies twice over: q→p is the
CUT EDGE (D2T's south glue `q-true` is a unique name system-wide —
unwirable), and p→q is WIRED but transitively dead (D3T.S =
`rd2t-done`, exposed north by exactly one tile: D2T, itself never
producible). No atom of a seedless cycle can be first.

## Numbers

- 12 tile types + 3 seed tiles; 26-name glue alphabet. Scaling per
  atom-row: +3 tiles, ~+5 glues — |atoms| is a factor in assembly
  DEPTH (paid in read time per the tick-10 readwindow invariant), not
  in species/search multiplicity. This is the executable answer to the
  paper's branch-(b) critique (level argument ⇒ |atoms| factor in
  species, fatal at a ~10² ceiling).
- Exhaustive τ=2 BFS (`atam_check_2cycle.py`, output `atam_2cycle.out`):
  **20 producible assemblies, 1 terminal, decode {a}**; D1F/D2T/D3T
  producible in 0 of 20; `q-true`, `SP4` occur exactly once
  system-wide; `rd2t-done` exposed only by D2T; all six value-side
  lock/channel pairs strength 0 (including `rd2t-done` vs
  `rd2f-done` — the dead edge cannot ride p's false row); wrong tiles
  keep exactly b = 1 in the FULL correct assembly (spine bond only) —
  un-lockable, v3 rule (a) carried row by row.
- The supported-but-unstable `{a,p,q}` has NO realizing assembly — it
  would need D2T and D3T, and each dies by a different mechanism.

## Status and what is queued

CI pins the structural facts (`tests/test_tiles_2cycle.py`: aTAM
invariants incl. 20/1/{a}, unique-name inertness, witness exposure,
falsity-chain bonds, full-context un-lockability). Honest limits,
stated in the design: body conjunction (single south glue cannot read
two witnesses — designs/003), the anchored-cycle order falsifier
(`a. p :- a. p :- q. q :- p.` must decode {a,p,q} under stage order and
{a,p} under a wrong order — proves stage order is load-bearing; needs
the OR construction), the per-row kTAM grid, and the fact that the
stage order was computed by hand — this design is the specification
for the compiler pass, not yet the pass.
