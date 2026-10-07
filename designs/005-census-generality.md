# designs/005 — Census generality: is the lock-squat signature a compile property?

## Picked (tick 37, 2026-10-07)

Tick 36 named two candidate avenues: (a) a second program family to test
census generality; (b) kinetics-informed lock encoding (strength-2
lock-read glues priced against the published trade table). **This design
picks (a).** Rationale: the whole repairability/squattability arc
(ticks 23–35, summarized in `research-log/2026-10-07-repairability-arc-
summary.md`) rests on three inventories — BUILD1/2/3 — that are the
*same* program family (one correct compile + two wrong compiles of the
OR∧AND witness). Its scope-of-claim section says so. Before any new
encoding knob (b) is priced against that trade table, the table's
generality must be bounded: if the Vp/V0p lock-squat signature is an
artifact of OR-variant value-output sharing, (b)'s target is narrower
than the trade table claims; if it is constructional (the via relay
re-uses the value glue on both faces by emission), every v0.1 compile
carries it and d4's guidance is corpus-general.

(b) is deferred, not dropped — recorded below with its own honest
prerequisite.

## The question, sharply

The published census (tick 24, `evidence/2026-10-07-repair-mechanism/
trap_census.out`) found exactly two lock-column squatters in BUILD1:
`Vp@(3,2)` and `V0p@(3,1)` — both **V-class via-relay tiles** — and the
kinetic arms (ticks 25–34) showed those squats carry the read-block
(the Vp+DBr vertical stack) and the substitution-repair channel. Two
hypotheses explain the squatters:

- **H-construction**: the compiler emits every value relay with the
  same value glue on W and E faces (`V{i}{a}: W={a}-t, E={a}-t`), so a
  V tile can always present a lock-read glue to the lock column. The
  squat class then exists in *every* compile with a lock column,
  regardless of rule shape.
- **H-sharing**: the squat needs OR variants sharing value outputs
  (r's two readers both presenting `r-t`), which multiplies the faces
  carrying value glues; without variants the census goes quiet.

H-construction predicts the squat class survives OR-removal; H-sharing
predicts it vanishes. That is the falsifiable content of this design.

## Arms (all compiled through `compile_program` v0.1, family scope)

| arm | program | rows | what it isolates |
|---|---|---|---|
| `MINIMAL` | `p.` | 1 | the row-1 V0 relay + lock alone |
| `AND_ONLY` | `p. q. r :- p, q.` | 3 | BUILD1's family minus the OR unit variant |
| `UNIT_ONLY` | `p. q. r :- p.` | 3 | terminal rule with a single unit body (conduit+reader, no DB tile) |
| `DEEP_FACTS` | `p. q. s. r :- s, p.` | 4 | two stacked fact relays; AND reading (adjacent-below, row-1) |

All four compile clean (smoke: rows/tiles 1/4, 3/12, 3/12, 4/16; d4
attached, severity warning). BUILD1's own program is the fifth shape
(the OR∧AND union) and stays the reference census.

## Pre-registered gates (registered before the census runs)

Instrument: `molasp.offchannel.check_d4` on each compile (the same
emit-time census as designs/004; deterministic static enumeration).
Gates registered 2026-10-07 tick 37, before any census output for these
arms was produced:

- **G1 (V-relay squat universality)** — every arm reports ≥1 lock
  hazard, and every lock-squat tile at a lock site is a V-class via
  relay (name `V*`). *Falsified* if any arm reports zero lock hazards,
  or any non-V tile squats a lock site in any arm. (Decides
  H-construction vs H-sharing.)
- **G2 (transient class)** — no arm reports a solo stable (b≥2) lock
  hazard; all solo lock hazards are b=1 transient class. *Falsified*
  by any stable solo hazard in any arm. (Replicates BUILD1's
  {V0p:1, Vp:1} bond-class signature out-of-family.)
- **G3 (stack channels track AND reader geometry)** — the AND arms
  (`AND_ONLY`, `DEEP_FACTS`) each enumerate ≥1 vertical lock-stack
  channel; `UNIT_ONLY` and `MINIMAL` enumerate zero. *Falsified* by
  the complement in any arm. (Tests whether the measured read-block
  channel class — Vp+DBr vertical stack, 141/141 co-occurrence —
  travels with the 2-literal reader geometry or with the family.)
- **G4 (depth scaling)** — off-channel site count is strictly greater
  in `DEEP_FACTS` than in both `MINIMAL` and `AND_ONLY`. *Falsified*
  if either inequality fails (site saturation would itself be a
  finding).

Interpretation stakes, registered in advance: G1 confirmed ⇒ the
lock-squat signature is a compile-geometry property; the arc's duality
claim widens from "one family's inventories" to "every v0.1 compile
shape", and d4's measured context is corpus-general guidance. G1
falsified (zero hazards out-of-family) ⇒ H-sharing wins; the design
rule narrows to variant-sharing compiles and the trade table must be
re-scoped before (b) is priced.

## Method and spend

Static enumeration only; **no cluster job this design** (same standing
rule as tick 35: the census enumerates the complete bond-identity
predicate the dynamics are a function of; "kinetics decides" applies to
sampled channels, and no kinetic claim is made here). Kinetic
validation of one new-family arm becomes the recorded follow-up **iff**
a census class appears that the BUILD1 kinetic grid never measured
(e.g. a G2-falsifying stable solo hazard) — presence of known classes
is already kinetically bounded by the BUILD1 arms at matched protocol.

## Deferred: (b) kinetics-informed lock encoding

Not picked, not dropped. Strength-2 lock-read glues are the first
**non-rename** knob candidate (R1: renames change bond identity;
strength changes kinetics at fixed identity — the arc has no measured
instance of that lever). Its honest prerequisite: a generality-bounded
trade table (this design), so the pricing target is stated correctly.
When picked: pre-register a dG grid on BUILD1 family scope + one
designs/005 arm, predicting squat-dwell vs lock-capture-time from the
published b=1 equilibrium (~0.38 at dG 0.5) before any run.

## Evaluated (tick 37, 2026-10-07) — appended after the run

To be appended with machine verdicts; receipt at
`evidence/2026-10-07-census-generality/census_generality.out`.
