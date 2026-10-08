# Status and open threads

2026-10-08 — molasp-lab · synthesis, v1

Every number in this programme carries one of three kinds of evidence, and the difference between them is the difference between a result and a rumour. This page is the ledger: what is machine-checked, what is simulation-bounded, what rests on a single measurement, and what is deliberately *not* claimed — and at the end, what we do about the questions still open. Read it before leaning on any number elsewhere on the site.

## Machine-checked

These are structural claims in the sense of [guide three](03-how-we-check-a-design.md): exhaustive, re-runnable, and re-run automatically.

- The v3 glue-table assertions: wrong decision tiles producible in 0 of 10 assemblies; a unique terminal assembly decoding `{a}`; every lock-vs-wrong-value glue pair at strength 0, pinned by a test that re-runs on every commit.
- The spine self-bond class rule — every same-name spine self-bond carries strength 2, for every row, forever — pinned per name: SP5, SP6 and SP40 verified at 2 on both consuming paths, so the builders past four rows cannot silently disagree with the n≤4 corpus again.
- Dead readers: every derived false head's dead reader is proved absent from every producible assembly. That is an emitted-machinery guarantee — the machinery is *there* and provably never bonds — not an omission.
- The counting law: the four-column family's producible assemblies are exactly the partitions inside a 4×n box — 70, 126, 210, …, 1820 at n=4..12, every one C(n+4,4), re-derived live in CI at n≤8 — and corpus-wide, BFS presence sets equal the well-founded sets of the face-table grammar in 14 of 14 compiling programs ([post](../2026-10-08-the-number-of-buildable-things.md)). Names contend above that level (PC11: 147 assemblies over 126 presence sets) and are counted separately.
- The full test suite — 462 checks, re-run on every commit — turns a regression into a red check rather than a surprise in a paper.

## Simulation-bounded

These are statistical claims: measured, once, in kTAM, with the bound attached rather than a zero.

- The v3 lock grid: 0 wrong decodes pooled across 2,000 trajectories — below about 1.5 × 10⁻³ with 95% confidence, *not* a zero.
- The repair-mechanism studies (six-for-six) and the knob/window studies: one geometry (the 4-column AND build), positive programs only, n = 500–2,000 per arm, fresh disjoint seed blocks per study.
- Everything here is simulation. There is no wet-lab claim anywhere in this programme.

## Thin or open

One measurement, or none, attached to a live thread.

- The ΔG-2 window arm sat knife-edge (0.152 against a 0.15 gate) — disclosed, then resolved by the window-tilt and ratchet studies, which accounted for the tilt quantitatively.
- The reinforced lock-read at ΔG 7 rests on a single event. One event is a hint, not a regime.
- One vacancy site (row 2, column 2; 50 of 500 holds) sits outside the five-name census the severity check prices — which means it is priced as *absent*, not priced as *safe*.
- The Vp residual (0.146, real at 4× power) is a second-order-effect candidate under dissection, not a settled number.

## What we do next

1. **Hazard-hold across the whole window.** The ratchet account (guide two) requires the correct fill's detach hazard to keep collapsing across the full eight-roll window, not just its first quarter. A run submitted on 8 Oct extracts per-roll attach odds and per-incumbent persistence on half the seeds and predicts the full-window share analytically from the other half (reference 0.834, pre-registered bracket ±0.05); outside the bracket, the ratchet account dies and this ledger changes.
2. **A second program family.** [Designs/005](../designs/005-census-generality.md) asks whether the Vp/V0p lock-squat pattern is a signature of *value-typed* programs or of every compile with a lock column — answered by lowering and censusing a second family, not by argument.
3. **Longer programs.** The five-row build proved the spine-class rule can lift the four-row ceiling; the next programs are ones where that rule does real work, where five rows is the entry price, not the ceiling.
4. **The last compiling shape — closed by identity (8 Oct, tick 76).** The hole of exactly one never existed: PR9's refusal-registry text is byte-identical to the PC11 pin already inside the corpus-wide presence law, so the law covered every compiling shape with a known text from the day it was measured. The identity is pinned in the tests.
