# Species-death survey — which removals the substrate repairs, which
# it reads faithfully (tick 23, SON-4775)

Card: SON-4775. Build and receipts:
`../evidence/2026-10-06-species-death-survey/` (atam_survey.out, the
queue receipts, run.out). Tests: `../tests/test_species_death_survey.py`.

## Question

Tick 22 removed one species (DAr) and found kinetic repair through a
DBr+L3 mutual b=2 trap, with the honest limit: *one geometry, one
species — not yet a general law*. This tick is the queued
generalisation: **BUILD1 minus EACH of its 12 tile species in turn**,
aTAM arm by exhaustive tau=2 BFS, kTAM arm under the protocol of
record (Gse=9, Gmc {9.5,11,13,16}, T=400·e^Gmc, n=500/point, seeds
from 20261031). The question per removal: does the substrate
kinetically repair the true-model readout (strict "pqr"), or does it
read the aTAM terminal faithfully?

## Pre-registration (written before the kTAM run; queued as job
hxq-20828594, request 20828594fc9d…)

- SV1: aTAM taxonomy per removal (exhaustive, so a measurement):
  PRESERVED / FAITHFUL_SUB / COLLAPSED / AMBIGUOUS labels, terminal
  decodes, producibility.
- SV2: repair classes per point — REPAIRED (strict pqr / build1 pqr
  ≥ 0.5), PARTIAL (0 < ratio < 0.5), DEAD (0).
- P1 (from tick 22): DAr AND DBr removals repair at some dG ≤ 4.
- P2: lock/spine removals (L1,L2,L3,S1,S2,S3) DEAD everywhere —
  their strict-decode sites admit no alternate occupant.
  Falsifier: strict pqr > 0 on those rows.
- P3: decision/via removals (D1T,D2T,V0p,Vp) ratio < 0.5 everywhere
  (repair needs chains of b=1 coincidences, not one mutual pair).
  Falsifier: any ratio ≥ 0.5 on those rows.
- P4: every removal repaired at dG ≤ 4 starves at dG=7 (tick-22
  S3(iii) generalisation). Falsifier: ratio ≥ 0.5 at dG=7.
- S4: build1 within 2x of the tick-19 curve (0.540/0.790/0.984/0.870).

## aTAM arm (exhaustive, machine-checked; receipt atam_survey.out)

Every removal has a **unique terminal** — no AMBIGUOUS rows; the
readout stays confident in all 12 deaths. Four COLLAPSED, eight
FAITHFUL_SUB, zero PRESERVED:

| removed | label | terminal | anchors | never producible |
| --- | --- | --- | --- | --- |
| S1 | COLLAPSED | "" (0 locks) | — | all 11 others |
| D1T | COLLAPSED | "" (0 locks) | — | D2T,DAr,DBr,L1,L2,L3,V0p,Vp |
| V0p | COLLAPSED | "" (0 locks) | — | DBr,L1,L2,L3,Vp |
| L1 | COLLAPSED | "" (0 locks) | — | L2,L3 |
| S2 | FAITHFUL_SUB | "p" | drop_q_fact, p_only | D2T..L3,S3,Vp |
| D2T | FAITHFUL_SUB | "p" | drop_q_fact, p_only | DAr,DBr,L2,L3,Vp |
| Vp | FAITHFUL_SUB | "p" | drop_q_fact, p_only | DBr,L2,L3 |
| L2 | FAITHFUL_SUB | "p" | drop_q_fact, p_only | L3 |
| S3 | FAITHFUL_SUB | "pq" | drop_r_rule | DAr,DBr,L3 |
| DAr | FAITHFUL_SUB | "pq" | drop_r_rule | DBr,L3 |
| DBr | FAITHFUL_SUB | "pq" | drop_r_rule | L3 |
| L3 | FAITHFUL_SUB | "pq" | drop_r_rule | — |

Structural findings, all from the receipt:

1. **Every non-collapsed death reads a residual program's stable
   model** — {p,q} (drop_r_rule) for the four row-3-adjacent
   removals, {p} (drop_q_fact) for the four row-2-adjacent ones.
   Species absence lands on solver answers, like rule death does,
   but WITHOUT re-layout.
2. **The interlock is transitive: four removals collapse everything
   above them.** Losing S1, D1T, V0p or L1 leaves a terminal with
   ZERO locked rows — even p becomes unreadable. V0p's collapse is
   the non-obvious one: L1.W=p-t bonds V0p.E, so the lock column
   dies with the via column's stub, not just its own row. Column V
   and column L are one structure for survival purposes.
3. **The taxonomy is width-graded**: row-1 deaths collapse (0
   locks), row-2 deaths read {p}, row-3 deaths read {p,q} — the
   readout degrades to the deepest intact row, exactly the
   "completion as deepest locked prefix" picture the strict decode
   assumes.

## kTAM arm (queue job hxq-20828594)

RESULTS PENDING COLLECTION — filled below after the job lands; the
pre-registration above was committed to the harness header before
submission.

## Honest limits (to be finalised with the kTAM numbers)

- One geometry (4-column AND, 3 rows), single-species removals only,
  n=500/point, no-mismatch kTAM; the taxonomy is exhaustive for
  THIS build's glue arithmetic, not a law about tile systems.
- clingo anchors computed on the pod (module clingo); the queue
  image's in-job anchor table may be empty if clingo is absent
  there — the pod receipt is authoritative.
