# 2026-10-07 — Glue-class boundary census (tick 35, SON-4778)

The last open designs/004 item: the row scope never qualifies the
structural glue classes (spine go* entries, and*/base/w* relays,
caps). Does extending the knob to them change anything? Closed
statically, with an exact inventory proof instead of a Monte Carlo
arm — commit `evidence/2026-10-07-glue-class/` (script + receipt),
pins in `tests/test_glue_class.py`.

## Design

- `apply_lock_glue_scope(build, "class")` — the row rule PLUS every
  non-value, non-SP canonical-bond rename. Exemptions, both
  recorded in-source: the strength-2 spine self-relays (designs/002
  row-1 nucleation) and the seed row (outside canon by
  construction). Value bonds keep exactly the row treatment, so
  `class` is row + class-glue renames and nothing else — the
  tick-29/30 row semantics are bit-unchanged (pinned).
- `glue_class_census` — every glue's users (tile faces + seed
  slots) classified as `canonical_pair` / `seed_bond` /
  `inert_single` / `shared`.
- `scope_bond_identity` — the complete matching predicate (every
  opposing tile-face pair + every seed bond) compared across two
  scopes. kTAM/aTAM dynamics are a function of this predicate and
  the strengths alone, so an empty diff proves kinetic identity by
  construction.

## Why no cluster job (the pre-registered justification)

The standing rule "census over-approximates; kinetics decides"
applies to SAMPLED channel censuses (it is exactly how ticks 31-33
demolished the static elimination reading). This study enumerates
the complete inventory match predicate, not a sample of channels:
there is nothing left for trajectories to over-rule. Spending
queue compute on a provably-null arm would be spend without
information.

## Results (all machine-checked; receipt glue_class.out)

- C1 CONFIRMED — no `shared` structural glue in BUILD1/2/3. Every
  non-value glue is canonical_pair (go1/go2/go3, and1_r, base2/
  base3, SP2/SP3, w1-relay in BUILD3), seed_bond (f-p, vb1, base1,
  SP1) or inert_single (cap3, rf-relay, pf-cap).
- C2 CONFIRMED — row-vs-class predicate diff EMPTY on all three
  builds (checker sanity: family-vs-row diff is 10 entries, incl.
  the D1T.E<->L1.W lock-read split). The class scope renames only
  canonical-pair-exclusive glues, so it splits nothing.
- C3 CONFIRMED — canonical assemblies >= tau=2 everywhere under
  class.
- C4 CONFIRMED — full check_d4 reports identical row vs class.
- R1 — the rename principle, now explicit: renames kill only bonds
  whose faces land on DIFFERENT final names (one-face splits);
  they are structurally blind to displaced-pair / same-tag
  recombination. The four row-scope surviving channel bonds all
  carry equal final names on both faces — Vp.N = DBr.S =
  `p-t-done-lk3` (the H3 vertical stack), D2T.N = DAr.S =
  `q-t-done-lk3`, D2T.S = V0p.N = `p-t-done-lk2`, D2T.W = S2.E =
  `go2` (a class glue row never touched); the kill case is the
  split D1T.E `p-t` vs L1.W `p-t-lk1`. One rule, stated after the
  fact, that predicts exactly which channels survive any rename-
  based scope.

## Consequence

`lock_glue_scope` terminates at `row` for these inventories: the
honest boundary is the spine strength-2 exemption and the seed row
— both nucleation anchors, not hazard carriers. The knob family
has no third setting that changes kinetics here. A future build
family with a shared structural glue reopens the boundary;
`glue_class_census` is the emit-time check that flags it.

Program state after this tick: the repairability/squattability arc
(ticks 23-35) is fully closed — property → knob → mechanism →
thermodynamic closure → knob-terminus proof. Remaining candidates
are the founder-gated collaborator/venue shortlist (tick-29 sweep)
and designs/005 or a program-summary artifact.
