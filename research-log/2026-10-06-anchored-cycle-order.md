# Anchored-cycle order falsifier (designs/002 criterion 4) — 2026-10-06, tick 14

Program `a. p :- a. p :- q. q :- p.` — the anchored 2-cycle. Semantics
settled by the pod's clingo module before any tile was drawn: exactly
one stable model {a,p,q} (least fixpoint stages a:0, p:1, q:2), and
{a,p} is not satisfiable under assumptions {a,p,¬q} — it is neither
stable nor even a model (the rule q :- p has a true body and absent
head).

## What was built (the OR construction)

An atom with k defining rules gets k TRUE-variant tiles sharing value
outputs (E = r&lt;atom&gt;-t, N = r&lt;atom&gt;-t-done); the south glue alone
encodes which rule the variant reads. Three builds, one BFS each:

- **CORRECT** rows a&lt;p&lt;q, cut edge p:-q (body above head). 13 tile
  types + 3 seed, 27 glues.
- **WRONG_CUT** same rows, cut edge flipped onto q:-p (the readable
  edge), p:-q nominally wired by name.
- **WRONG_ROWS** rows a&lt;q&lt;p (a non-stage order), name-typed wiring.

## Predictions (recorded before running)

CORRECT → unique terminal {a,p,q}; WRONG_CUT → wrong-but-terminal
{a,p}; WRONG_ROWS → {a} — predicted DURING the build, with the
designs/002 draft's "{a,p} under a wrong order" re-derived: the draft
guessed q's true-tile dies and the anchor survives, but under a&lt;q&lt;p
the anchor edge p:-a ALSO dies, because the read channel is the
immediately-below row and q's row sits between a and p. The {a,p}
outcome belongs to the wrong-CUT build, not the wrong-ROWS build.

## Measured (exhaustive τ=2 BFS, `atam_anchored.out`)

| build | producible | terminals | terminal decode | locked rows |
| --- | --- | --- | --- | --- |
| CORRECT | 20 | 1 | {a,p,q} | 3 |
| WRONG_CUT | 16 | 1 | {a,p} | 2 |
| WRONG_ROWS | 10 | 1 | {a} | 1 |

In CORRECT, D1F/D2F/D2TQ/D3F are producible in 0 of 20; the wired
edge's witness glue rp-t-done is exposed north by exactly the OR pair
[D2TA, D2TQ]. Both wrong builds terminate — each in a NON-model of P.
Criterion 4 answered: **no wrong build decodes {a,p,q}**. Stage order
and the cut discipline are both load-bearing; a compiler that emits
any order, or the right rows with the cut on the wrong edge, produces
a system that terminates confidently in a non-model.

## Taxonomy correction (measured, not assumed)

First draft of the structural check claimed the dead variant D2TQ
keeps b=2 in the finished context; the assertion failed and the probe
returned **3 of 4** (W spine + E shared output bonding the lock + N
shared output bonding the row above; only the dead rule-read south
glue stays unmatched). Growth-dead VARIANT tiles are value-equivalent
and lock-compatible — they die by growth order alone. Un-lockability
(b=1, spine only, measured for D1F/D2F/D3F) is a wrong-VALUE
property. Two families, two mechanisms; designs/001's catalogue entry
(a) covers only the second.

## What this does not establish

kTAM carryover per row (queued, same protocol as designs/001 v3);
body conjunction (designs/003); the stage order and the cut placement
are still computed by hand — this remains the compiler-pass
specification, now with a machine-checked acceptance test the pass
must satisfy: emit the stage order and the body-above-head cut, or
the terminal decode is wrong by construction.

Tests: `tests/test_tiles_anchored.py` (12 tests; suite 78/78).
Unreviewed promotion; no C-claim advanced; C2 unchanged.
