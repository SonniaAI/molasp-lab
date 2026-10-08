# Status and open threads

2026-10-08 — molasp-lab · synthesis, v1

## Start here

Every number on this site deserves to be doubted in one of three ways, and knowing which kind you are holding is the difference between a result and a rumour. This page is the honest ledger: what is machine-checked, what is simulation-bounded, what rests on a single measurement, and what is deliberately *not* claimed. Read it before believing anything else on the site, and re-read it when a new guide seems to have quietly made a claim stronger than its evidence.

## Machine-checked

These are structural claims in the sense of [guide three](03-how-we-check-a-design.md): exhaustive, re-runnable, and re-run automatically.

- The v3 glue-table assertions: wrong decision tiles producible in 0 of 10 assemblies; a unique terminal assembly decoding `{a}`; every lock-vs-wrong-value glue pair at strength 0 (`tests/test_tiles_v3.py`).
- The spine self-bond class rule — every same-name spine self-bond carries strength 2, for every row, forever — pinned per name: SP5, SP6 and SP40 verified at 2 on both consuming paths, so the builders past four rows cannot silently disagree with the n≤4 corpus again.
- Dead readers: every derived false head's dead reader is BFS-proved absent from every producible assembly. That is an emitted-machinery guarantee — the machinery is *there* and provably never bonds — not an omission.
- The whole suite: 462 tests, run verbatim in the commit messages, so a regression shows up as a red check and not as a surprise in a paper.

## Simulation-bounded

These are statistical claims: measured, once, in kTAM, with the bound attached rather than a zero.

- The v3 lock grid: 0 wrong decodes pooled across 2,000 trajectories — below about 1.5 × 10⁻³ with 95% confidence, *not* a zero.
- The repair-mechanism studies (six-for-six) and the knob/window studies: one geometry (the 4-column AND build), positive programs only, n = 500–2,000 per arm, fresh disjoint seed blocks per study.
- Everything here is simulation. There is no wet-lab claim anywhere in this programme, and the founding paper stays internal.

## Thin or open

One measurement, or none, attached to a live thread.

- The dG-2 window arm sat knife-edge (0.152 against a 0.15 gate) — disclosed, then resolved by the window-tilt and ratchet studies, which accounted for the tilt quantitatively.
- The `s2` dG-7 persistence figure rests on a single event. One event is a hint, not a regime.
- `L3@(2,2)` (50/500) sits outside the five-name census the severity join prices — which means it is priced as *absent*, not priced as *safe*.
- The Vp residual (0.146, real at 4× power) is a second-order-effect candidate under dissection, not a settled number.

## Open threads

1. **The compounding-chain account.** The window-tilt bias is hypothesised to come from biased re-roll chains. The pre-registered falsifier extracts per-roll attach odds and per-incumbent persistence on half the seeds and predicts the window-arm share analytically on the other half. Outside ±0.05 of the measured 0.737, the account dies in public — and a dead account here is worth more than a kept one in physics.
2. **Window-indexed pricing.** The d4 check prices marginal-regime hazards at one fixed read window (the 160-roll default). Pricing them as a function of the *intended* window is a recorded follow-up, not a silent default.
3. **Generality.** [Designs/005](../designs/005-census-generality.md) asks whether the Vp/V0p lock-squat pattern is a signature of *value-typed* programs or of every compile with a lock column — answered by a second program family, not by argument.

## How to read this blog

Nothing here is a validated result until a lab-log entry says so and names its evidence. Every quoted number traces to a committed receipt; where a prediction was beaten or demolished, the guide says so and links the demolition. The guides are syntheses — if a guide and a dated entry disagree, the dated entry (and its receipt) wins, and the guide gets edited the same day the disagreement is noticed.
