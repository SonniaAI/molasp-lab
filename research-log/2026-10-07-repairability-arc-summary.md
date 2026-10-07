# 2026-10-07 — Program summary: the repairability/squattability
# arc (ticks 23–35, SON-4778)

Consolidation artifact — **no new measurements**. Every number
below traces to a committed receipt (table at the end);
pre-registered gates were fixed in commits that precede their
jobs. Suite at the arc's close: `Ran 276 tests OK (skipped=1)`
(the skip is the species-death run.out gate, a different study).

## The claim, in one paragraph

In our kTAM model of ASP-compiled tile systems, repairability and
squattability are one property: value-glue sharing. The same
shared bonds that let a vacancy be repaired by substitution
(74.9–97% fill across four reader/value arms) also admit
off-channel squatters onto lock sites (the top squatters are
exactly the two exceeds-parity species, Vp@(3,2) and V0p@(3,1))
and a structural misread channel (23/23 of L3-missing strict-pqr
terminals). The obvious compile-time fix — renaming glues to
scope the sharing (row scope) — zeroes every static hazard class
and still leaves half the read-block (0.144 vs 0.27) plus a
surviving 16% stable-repair channel, because b=1 transient holds
and redundant 2-of-3 stacks reconstitute what single bonds lost.
Both surviving stack channels then starve monotonically to zero
by dG 4: redundancy is why the knob failed at dG 0.5, and dG is
why redundancy loses. For these inventories the rename terminates
at row scope — class-scope renaming is inert by complete
enumeration of the bond inventory, and the rename principle (R1)
states the general reason: renames kill only bonds whose faces
land on different final names; every surviving channel bond
carries equal final names on both faces.

## Where it started (tick 23)

The species-death grid demolished the aTAM taxonomy as a
predictor of kinetic class: decision/via removals repair at
parity and three removals exceed build1's own strict-pqr yield
(build1 0.7813 vs Vp-missing 0.927 at n=500, dG 0.5) — removing
a value tile can *improve* the canonical readout. One channel was
already a misread (L3, cross-row lock substitution). Ticks 24–35
explain all of it.

## Mechanism I — trap relief and substitution repair
## (ticks 24–25, n=500/arm, dG 0.5)

- **Trap relief is the dominant repair mechanism** (R2): removing
  V0p (exceeds-parity 1.23x) is pure trap relief — conditional
  clean-lock gap vs build1 just 0.016; the 0.146 residual belongs
  to Vp-missing, the arm whose repair is the D2T substitution.
- **Squatters = exactly the census squatters** (R3a): Vp@(3,2)=107
  and V0p@(3,1)=52 of 500 — the only two lock-column squatters,
  and exactly the two exceeds-parity removals; plus a mutual
  squatter stack Vp@(3,2)+DBr@(3,3).
- **Substitution repair is symmetric across reader/value
  families** (R3b): D1T fills the V0p vacancy 256/342=74.9%, D2T
  fills the Vp vacancy 389/432=90.1%; reverse arms 94% and 97%.
  Value-typed glue families interchange readers and values in
  both directions.
- **The L3 misread is structural** (R3c): every one of the 23/500
  L3-missing strict-pqr terminals held L2@(3,3) with the Vp west
  enabler — fraction 1.0, pqr_clean_frac 0.0.
- **Both faces decay with dG** (R4): squat rate 0.314 / 0.118 /
  0.000 at dG 0.5/2/4; the Vp squatter ratio crosses below 1 by
  dG 4 (0.704).

## The residual is a dwell cost, not death (tick 27, n=2000/arm)

- Clean-conditional gap real at 4x power: build1 0.8011 vs
  Vp-missing 0.9246, gap 0.1235 >= 0.10 (P1) — not n=500 selection
  noise.
- Read-clean non-pqr lock dwell is 4.51x read-clean pqr dwell
  (1.146e6 vs 2.543e5, P2): squats are a read-time sink. Severity
  in the emit-time census is dwell-weighted for exactly this
  reason.
- Calibrated against tick-23 references (deviations 0.0198 /
  0.0024, P3); census-order squatters reproduce at 4x power
  (Vp@(3,2)=429, V0p@(3,1)=259); blocked_frac collapses
  0.286 -> 0.065 without Vp.

## Compiler consequence (tick 28, designs/004 A1–A4)

`molasp/offchannel.py check_d4` lifts the census to emit time:
off-channel (site,tile) table, lock hazards, one-west-substitution
deep probe, cross-row lock misreads, and the measured kinetic
context quoted into every report. WARNING severity — reports,
never gates. Pinned bit-for-bit against the tick-24 receipt AND a
live recompute by the independent trap_census implementation
(A1); zero false hazards from non-off-channel species (A2); d2/d3
semantics untouched (A3); wrong compiles carry the same-class
table with MORE hazards (A4, BUILD3: V0q@(3,1), Fplus@(3,2),
Fp@(3,3)) — inventory-driven, not tuned to build1.

## The knob, statically (ticks 29–30)

`lock_glue_scope` (family|row) renames canonical lock-read bonds
and vertical value-family relay bonds on both faces. Row scope
zeroes lock hazards AND misreads on all three inventories
(BUILD1/2/3, false families covered by tick 30) with every
canonical assembly still >= tau=2 (pinned). The static trade:
family buys 74.9–97% substitution repair and pays 0.314 squat
decay + 4.51x dwell + the misread; row zeroes the hazard classes
and degrades stable repair bonds 2 -> 1.

## The knob, kinetically — half-falsified (tick 31, n=500/arm)

| metric (dG 0.5) | family | row |
|---|---|---|
| read-lock-squat blocked fraction | 0.27 | 0.144 |
| stable (b>=2) D2T vacancy repair | 0.908 | 0.162 |
| L3-missing misread fraction | 0.056 (28/500) | 0.000 |
| strict-pqr yield | 0.582 | 0.762 |

- RS1 falsified: row blocked 0.144 (gate <= 0.02) — Vp@(3,2) and
  DBr@(3,3) survive at 72/500 on b=1 transient holds; the V0p@(3,1)
  squat dies. RS2 falsified: stable repair survives at 0.162
  (raw b=1 occupancy 0.44 vs the smoke-predicted ~0.38
  equilibrium). Static hazard-zeroing is NOT kinetic elimination.
- RS3 confirmed: the misread channel needs the value-family
  sharing (0.000 vs 0.056) and strict-pqr yield *improves* under
  row scope (+0.18) — trap relief at the scope level.
- RS4 calibrated: family 0.27 vs 0.314 reference (dev 0.044),
  fill 0.9202 vs 0.901 (dev 0.019).

## Mechanism II — redundant cooperative stacking
## (tick 33, n=1000/arm, history-aware)

- The surviving row-scope repair is NOT a 2-bond mutual pair
  (H1 falsified): 153/155 stable holds are b=3 stacks
  N->DAr + S->V0p + W->S2, 2-of-3 redundant — no single
  load-bearing partner (lb_any 0.0129). The canonical E->L2 bond
  appears in zero row holds; family holds stay canonical
  (711/886 classic 2-bond, H1b).
- The row read-block is the Vp@(3,2)+DBr@(3,3) VERTICAL lock
  stack — 141/141 co-occurrence; the west D2T co-stack is not
  load-bearing (mutual_pair_link 0/141; H3 refined).
- With Vp absent, site (3,2) is never squatted (H2 no_events):
  the channel re-routes to the relay stack rather than dying.
- Calibration holds (H4: 0.141 / 0.155 / 0.273 vs 0.144 / 0.162 /
  0.27 references, max dev 0.007).

Headline: redundancy is why the knob failed. Row scope killed
every canonical single bond it aimed at; both surviving channels
ride 2-of-3 relay stacks around the same (2,2)/(3,2)/(3,3)
junction. Single-pair hazard models under-call cooperative
stacking — check_d4 gained stack classes for this (tick 34).

## Thermodynamic closure (tick 34, n=500/arm, dG {0.5, 2, 4})

- Vertical lock stack starves: 0.140 -> 0.006 -> 0.000, and at
  every dG with events the blocked cohort IS the stack
  (co-occurrence 1.0) — S1.
- Relay-stack repair starves: 0.128 -> 0.040 -> 0.000 — S2.
- Among survivors the redundant b>=3 fan is the last channel
  standing (0.9844 / 0.90 of stable holds; lb_any <= 0.1) — S3.
  Calibration holds (S4).

Redundancy does not survive thermodynamics: the stack closes by
dG 4 exactly as the solo family channel did in R4.

## Knob terminus (tick 35, exact enumeration, no sampling)

- C1: no non-value glue in BUILD1/2/3 is shared (all
  canonical_pair, seed_bond or inert_single) — no off-channel use
  exists for class glues at all.
- C2: the row-vs-class complete matching-predicate diff is EMPTY
  on all three builds — class scope is kinetically identical to
  row by construction.
- C3/C4: canonical assemblies >= tau=2 and the full d4 report
  identical, row vs class.
- R1 (rename principle): a scope rename kills only bonds whose
  faces land on DIFFERENT final names (one-face splits); it is
  structurally blind to displaced-pair recombination. All four
  row-scope surviving channel bonds carry EQUAL final names
  (Vp.N=DBr.S p-t-done-lk3; D2T.N=DAr.S q-t-done-lk3;
  D2T.S=V0p.N p-t-done-lk2; D2T.W=S2.E go2 — a class glue row
  never touched). One rule that states the static reason RS1/RS2
  were falsified.

So `lock_glue_scope` terminates at row for these inventories; its
honest boundary is the two recorded exemptions (strength-2 spine
self-relays, the seed row — nucleation anchors, not hazard
carriers). `glue_class_census` is the emit-time flag for any
future build family that introduces a shared structural glue.

## What is deliberately NOT claimed

- Scope: three inventories (BUILD1/2/3 of the p-and-q program
  family), one protocol point per study (dG 0.5) plus the
  {0.5, 2, 4} sweeps, n=500–2000 per arm, fresh disjoint seed
  blocks per study. No claim beyond these.
- "Elimination" is reserved for measured-zero at every tested dG
  with co-occurrence 1.0 (S1/S2) — never for static
  hazard-zeroing.
- No wet-lab claim; no submission claim; the founding paper stays
  internal.

## Receipt table

| study | receipt | landed |
|---|---|---|
| species-death grid (arc start) | evidence species-death survey run.out | 424d4dc (tick 23) |
| static census + R2–R4 | evidence/2026-10-07-repair-mechanism/{trap_census.out,trap_grid.out} | 6b95430 -> f036324 |
| Vp-residual P1–P3 | evidence/2026-10-07-vp-residual/vp_residual.out | 295fbf8 -> 692506c |
| d4 census | molasp/offchannel.py + pins | eaf87f6 |
| knob + related-work sweep | research-log/2026-10-07-glue-scope-related-work.md | 27c3602 |
| false-family row scope | molasp/offchannel.py (SHARED_VALUE_SUFFIXES) | fb3e08e |
| row-scope kinetics RS1–RS4 | evidence/2026-10-07-row-scope-ktam/row_scope.out | 3a1cdea |
| transient/stack split | molasp/offchannel.py + tests | ef64e85, 7000301 |
| recombination H1–H4 | evidence/2026-10-07-recombination/recombination.out | 3fa1b4a -> 8f5d74e |
| dG sweep S1–S4 | evidence/2026-10-07-stack-dg-sweep/stack_dg.out | 7000301 -> 04fd2a7 |
| class terminus C1–C4+R1 | evidence/2026-10-07-glue-class/glue_class.out | 83e0bcc |

Blog milestones along the arc: six-for-six repair mechanism;
static-elimination-is-not-kinetic-elimination;
redundancy-is-why-the-knob-failed.

## Open avenues (not started)

- designs/005 candidates: (a) kinetics-informed lock encoding
  beyond renames — e.g. strength-2 lock-read glues priced against
  the measured trade table, pre-registered MC; (b) a second
  program family to test census generality (is the Vp/V0p
  lock-squat pattern a signature of value-typed programs, or of
  every compile with a lock column?).
- Collaborator/venue shortlist from the tick-29 sweep —
  founder-gated, not a lab default.
