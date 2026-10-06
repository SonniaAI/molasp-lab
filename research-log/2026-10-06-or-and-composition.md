# OR ∧ AND composition — machine-checked (tick 20, 2026-10-06)

Card: SON-4763. Design: designs/003 (honest-limit item 3, resolved).
Evidence: `../evidence/2026-10-06-or-and-composition/` (tiles,
checker, JSON receipt). Tests: `../tests/test_tiles_orand.py`
(17 new; suite 133/133 under `python3 -m unittest discover -s tests`).

## Question

designs/002 built the OR pair (k rules → k TRUE variants sharing
value outputs). designs/003 built the AND (sequential gating over a
4th column). Does an atom needing BOTH — one conjunctive rule, one
unit rule — compose, or does the composition introduce new leak
paths?

## Witness family

- P_OA = `p. q. r :- p, q. r :- p.` — stable {p,q,r} (clingo)
- P_OA−q = `p. r :- p, q. r :- p.` — stable {p,r} (clingo)
- P_OA−p = `q. r :- p, q. r :- p.` — stable {q} (clingo)
- W2 = dropped-unit-rule wrong compile of P_OA−q (solver model {p})

r ⇔ p logically: deleting q must not kill r (OR rescue); deleting p
must (foundedness). The pair discriminates OR semantics from the
pure-AND behaviour of designs/003 build 2 (same deletion → {p}).

## Construction

4-column geometry S | D | V | L unchanged. r's row carries two
variant reader paths sharing r-t/r-t-done and lock L3:

- conjunctive: DAr (W=go3, S=q-t-done, E=and1_r) + DBr (W=and1_r,
  S=p-t-done, E=r-t) — designs/003 build 1 verbatim;
- unit: Cr (W=go3, S=row-below predicted-value done, E=unit1_r) — a
  CONDUIT relaying the spine across slot A, south face not a
  semantic read — + Ur (W=unit1_r, S=p-t-done, E=r-t): the semantic
  read of p happens at the V column, one slot later than a
  designs/002 unit reader, because p's witness only surfaces at the
  via's north face two rows down.

Hybrid exclusion by glue identity: and1_r ≠ unit1_r mispairs bond at
strength 1 < τ. r-t-done: inventory count 2 (OR-pair fingerprint),
per-assembly ≤ 1 (site competition).

## Pre-registered criteria vs measured

| Arm | Prediction | Measured | Verdict |
| --- | --- | --- | --- |
| G1 P_OA | terminals all decode {p,q,r}, both variants realize, no mixing | 2 terminals, both {p,q,r}, 3/3 locked, 1 per variant, 0 hybrids | PASS |
| G1-cut | p-seed surgery: r-t producible 0 | terminal {}, r-t 0 | PASS |
| G2 P_OA−q | unique {p,r} (OR rescue) | unique {p,r}, 3/3 locked; q-t/q-t-done/and1_r 0; DAr/DBr nowhere | PASS |
| G3 P_OA−p | unique {q} | unique {q}; p-t/r-t 0 | PASS |
| G4 W2 | {p} ≠ clingo {p,r}; certificate + closure fire | exactly; d3 fires on `r :- p` | PASS |

d1 (via discipline) 0 violations, all builds. d2 (AND discipline)
holds where in scope (r predicted true: builds 1, 2). Inertness
unique-name rule holds for SP4/cap3/and1_r-done/unit1_r-done/
rf-relay/u-cutp.

## What it establishes

1. The composition is sound at τ=2: OR rescue works (G2 vs pure-AND
   build 2), foundedness works (G3), and the wrong compile is
   caught twice (BFS-vs-clingo certificate AND static d3).
2. **(d3) compile-model closure/support**, promoted to required
   emit-time check: the predicted-true set compiled into the locks
   must be a supported model of the program. Static, BFS-free;
   catches dropped rules, complementing d2 (dropped literals).
3. Emission policy pinned: reader paths are rule-local — dead
   variants are emitted (when a sibling rule predicts the atom
   true) and killed by value typing, not by omission.
4. Cost: 14 tile types + 4-wide seed = designs/003 build 1 + 2
   (conduit + reader), lock and value chain shared; ~(b) slot types
   per added rule variant of body width b. Linear at fixed max
   body width.

## Honest limits

- aTAM only; no kTAM grid on these builds yet (queued behind the
  structural-death reassertion build, which needs the same protocol).
- > 2 rule variants and b ≥ 3 bodies untested (same slot-widening,
  expected but unmeasured).
- The stage table / row order / cut choice is still computed by
  hand: with d2 + d3 + the tick-14 order acceptance test, the
  compiler-pass prototype now has all its acceptance tests — the
  pass itself is unbuilt.

## Tooling notes

Two checker bugs caught locally before landing (frozenset-of-pairs
vs dict `.values()` confusion in the variant filters; a double
comma from a mid-edit), zero science bugs — BFS verdicts were right
on the first run. `seen` is a set of frozensets of (pos, name)
pairs; `terminals` is a list of dicts: iterate accordingly.
