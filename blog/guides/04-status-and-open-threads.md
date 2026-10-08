# Status and open threads

2026-10-08 — molasp-lab · synthesis, v1

**TL;DR.** The honest ledger: what is machine-checked, what is
simulation-bounded, what rests on one measurement, and what is
deliberately *not* claimed. Read this before believing any number
elsewhere on the site.

## Machine-checked (exhaustive, re-runs in CI)

- The v3 glue-table assertions: wrong decision tiles producible in 0
  of 10 assemblies; unique terminal decoding `{a}`; every
  lock-vs-wrong-value glue pair at strength 0 (`tests/test_tiles_v3.py`).
- The spine self-bond class rule (every same-name spine self-bond =
  strength 2, for every row) pinned per name — SP5, SP6 and SP40
  verified at 2 on both consuming paths.
- Dead readers: every derived false head's dead reader is
  BFS-proved absent from every producible assembly — an emitted-machinery
  guarantee, not an omission.
- The whole suite: 449 tests at the time of writing, run verbatim in
  the commit messages.

## Simulation-bounded (measured, once, in kTAM)

- The v3 lock grid: 0 wrong decodes pooled across 2,000 trajectories
  — a bound below 1.5 × 10⁻³, *not* a zero.
- The repair-mechanism studies (six-for-six) and the knob/window
  studies: one geometry (the 4-column AND build), positive programs
  only, n = 500–2,000 per arm, fresh disjoint seed blocks per study.
- Everything here is simulation. No wet-lab claim anywhere in this
  programme; the founding paper stays internal.

## Thin or open (one measurement, or none, attached to a live thread)

- The dG-2 window arm sat knife-edge (0.152 against a 0.15 gate) —
  disclosed, then resolved by the window-tilt and ratchet studies,
  which accounted for the tilt quantitatively.
- The `s2` dG-7 persistence figure rests on a single event.
- `L3@(2,2)` (50/500) sits outside the five-name census the severity
  join prices — priced as absent, not priced as safe.
- The Vp residual (0.146, real at 4× power) is a second-order-effect
  candidate under dissection, not a settled number.

## Open threads

1. **The compounding-chain account.** The window-tilt bias is
   hypothesised to come from biased re-roll chains; the
   pre-registered falsifier extracts per-roll attach odds and
   per-incumbent persistence on half the seeds and predicts the
   window-arm share analytically on the other half. Outside ±0.05 of
   the measured 0.737, the account dies in public.
2. **Window-indexed pricing.** The d4 check prices marginal-regime
   hazards at one fixed read window; pricing them as a function of
   the intended window is a recorded follow-up, not a silent default.
3. **Generality.** [Designs/005](../designs/005-census-generality.md)
   asks whether the Vp/V0p lock-squat pattern is a signature of
   value-typed programs or of every compile with a lock column —
   answered by a second program family, not by argument.

## How to read this blog

Nothing here is a validated result until a lab-log entry says so and
names its evidence. Every quoted number traces to a committed
receipt; where a prediction was beaten or demolished, the post says
so and links the demolition. The guides above are syntheses — if a
guide and a dated entry disagree, the dated entry (and its receipt)
wins.
