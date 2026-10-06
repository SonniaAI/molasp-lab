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

## kTAM arm (queue job hxq-20828594 — collected 23:40Z, evaluated)

Receipts: `../evidence/2026-10-06-species-death-survey/ktam_grid.out`
(header + 52 point rows + 13 system totals + verdicts) and
`ktam_grid_queue_receipt.json` (image digest, node spark-4a06, exit 0,
18m42s wall). 13 systems × 4 points × 500 trajectories = 26,000 runs.
Protocol of record unchanged; deterministic seeds from 20261031.

**S4 calibration: PASS, essentially exact.** build1 strict "pqr"
0.540/0.794/0.986/0.874 at dG 0.5/2/4/7 vs the tick-19/22 curve
0.540/0.790/0.984/0.870 — ratios 1.000/1.005/1.002/1.005 (gate 2×).

**SV2 repair classes** — strict "pqr" fraction, ratio vs build1 in
parentheses; class by the pre-registered thresholds:

| removed | dG 0.5 | dG 2 | dG 4 | dG 7 | class | aTAM label |
| --- | --- | --- | --- | --- | --- | --- |
| — build1 | 0.540 | 0.794 | 0.986 | 0.874 | reference | — |
| D1T | 0.584 (1.08) | 0.822 (1.04) | 0.966 (0.98) | 0.018 | REPAIRED | COLLAPSED |
| D2T | 0.544 (1.01) | 0.748 (0.94) | 0.976 (0.99) | 0.004 | REPAIRED | FAITHFUL_SUB |
| V0p | 0.674 (1.25) | 0.772 (0.97) | 0.932 (0.95) | 0 | REPAIRED | COLLAPSED |
| Vp | 0.824 (1.53) | 0.928 (1.17) | 0.648 (0.66) | 0 | REPAIRED | FAITHFUL_SUB |
| DAr | 0.476 (0.88) | 0.660 (0.83) | 0.700 (0.71) | 0.004 | REPAIRED | FAITHFUL_SUB |
| DBr | 0.242 (0.45) | 0.116 (0.15) | 0.020 (0.02) | 0 | PARTIAL | FAITHFUL_SUB |
| L3 | 0.036 (0.07) | 0.010 (0.01) | 0 | 0 | PARTIAL→DEAD | FAITHFUL_SUB |
| L1, L2, S1, S2, S3 | 0 | 0 | 0 | 0 | DEAD | COLLAPSED / FS |

**Verdicts against the pre-registration (all machine-computed in the
job's final line):**

- **P1 — half-refuted.** DAr repairs (0.88/0.83/0.71 at dG ≤ 4; this
  grid reproduces tick 22's system: 0.476/0.660/0.700 vs 0.442/0.658/
  0.726 there). DBr does NOT: max ratio 0.448 at dG 0.5, monotone
  decreasing — PARTIAL everywhere. The tick-22 mirror-symmetry
  hypothesis is false; the repair trap is asymmetric.
- **P2 — falsified at L3 only** (strict "pqr" 18/500 and 5/500 at dG
  0.5/2; 0 at dG ≥ 4). The falsifier fired through **cross-row lock
  substitution**: with L3 absent a foreign L-tile can transiently
  hold (3,3) on a b=1 west bond, and because value-typed lock glues
  end in "-t" regardless of row, the strict decoder reads row r
  TRUE. A misread channel, not a repair — and a design lesson (F6:
  lock values must be row-unique). L1, L2, S1, S2, S3 are DEAD at
  every point as predicted: the spine and the lock chain are true
  single points of failure.
- **P3 — refuted decisively.** All four decision/via removals repair
  at ratio ≥ 0.5 somewhere at dG ≤ 4 — indeed at ≈ parity (0.66–1.53;
  D1T, V0p and Vp EXCEED build1 at dG 0.5). The "chains of b=1
  coincidences can't repair" argument was wrong: single-species
  substitution repair is the NORM at low-to-mid dG, not the
  exception.
- **P4 — holds.** No removal reaches ratio 0.5 at dG 7 (max 0.021,
  D1T). Loose decodes at dG 7 read the aTAM terminal: DBr-missing
  {p,q} 499/500 (drop_r_rule), Vp-missing {p,q} 489/500, build1
  itself {p,q,r} 487/500. Notably L3-missing reads {p,q,r} on the
  loose readers 423/500 while strict reads 0 — the reader column
  computes the model; the lock column is what dies. Read-WINDOW,
  not rate, controls error visibility: tick 22's collapse
  generalises to every removal.

**Synthesis — the survey's headline: the aTAM taxonomy does NOT
predict the kinetic class.** aTAM-COLLAPSED D1T/V0p repair to
parity; aTAM-FAITHFUL_SUB DBr repairs least of the eight
non-structural removals. What tracks repair is whether the
strict-decode path — spine S1–S3 (b=2 south bonds) plus lock chain
L1→L2→L3 (south b=1 each, west b=1 to column-V partners V0p, Vp,
DBr) — keeps its bonding channels. Removing a column-D reader
(D1T/D2T/DAr) leaves every lock's west partner intact → repair ≈
certainty. Removing DBr deletes L3's ONLY west partner → L3 hangs
on a single b=1 south bond → 0.45 and falling. The D1T (1.08) >
DAr (0.88) > DBr (0.45) gradient at dG 0.5 tracks DBr's own bond
multiplicity at (2,3): 2 / 1 / 0 (DAr's death breaks DBr's west
bond; DBr's death removes the tile). Honest open items: Vp is L2's
west partner yet Vp-missing is the BEST repairer (1.53) — a
substituted D2T can sit at (2,2) on its own south b=1 and re-expose
q-t east for L2, so substitution repair is two-way; and the
exceeds-parity repairs (Vp 1.53, V0p 1.25, D1T 1.08 at dG 0.5) have
no confirmed mechanism. Trajectory-level study is the queued
follow-up; measurements here are pinned, mechanisms are hypotheses.

## Honest limits

- One geometry (4-column AND, 3 rows), single-species removals only,
  n=500/point, no-mismatch kTAM; the taxonomy is exhaustive for
  THIS build's glue arithmetic, not a law about tile systems.
- clingo anchors computed on the pod (module clingo); the queue
  image's in-job anchor table may be empty if clingo is absent
  there — the pod receipt is authoritative.
- The kinetic classes are this build's; the west-partiner gradient
  is correlational (3 points), the Vp counterexample breaks the
  simple version of the story, and the exceeds-parity repairs are
  unexplained. Nothing here licenses a prediction about other
  geometries.

## Next queued (suggestion for the next tick)

Trajectory-level mechanism study of substitution repair: per-event
logs for Vp-missing vs build1 at dG 0.5 (where does the excess parity
come from?), plus the row-unique lock value design (F6 consequence)
as a small designs/004 candidate section.
