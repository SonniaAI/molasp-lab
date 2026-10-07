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

## Evaluated (tick 37, 2026-10-07)

Receipt `evidence/2026-10-07-census-generality/census_generality.out`;
pre-registration (this file + the script, gates verbatim) landed at 79d1f90
BEFORE the census ran. Machine verdicts: **G1 CONFIRMED, G2 CONFIRMED,
G3 FALSIFIED as registered (refined below), G4 CONFIRMED.**

- **G1 CONFIRMED — H-construction wins.** Every arm, down to the
  one-fact `p.` compile, reports lock squatters, and every squatter is
  a V-class via relay at b=1: MINIMAL `{V0p@(3,1)}`;
  AND_ONLY/UNIT_ONLY `{V0p@(3,1), V2p@(3,2)}`; DEEP_FACTS `{V0p, V2p,
  V3p}` — one per fact relay, exactly what the emission rule
  (`V{i}{a}: W={a}-t, E={a}-t`) predicts. The lock-squat signature is
  NOT an OR-sharing artifact; the arc's trade table and d4 guidance
  are corpus-general at census level.
- **G2 CONFIRMED** — no stable solo hazard in any arm; BUILD1's
  bond-class signature ({V0p:1, Vp:1} transient) replicates
  out-of-family unchanged.
- **G3 FALSIFIED as registered — and the refinement is the finding.**
  UNIT_ONLY enumerates stack channels (24 pairs across two adjacent
  lock-site pairs), so "stack channels track AND reader geometry" is
  wrong. The receipt shows the discriminating class is the **lo-read
  stack**: the terminal reader's SOUTH face carries the row-1 via
  glue (`p-t-done`) whether the body is a 2-literal AND (`DBr.S`) or
  a unit read (`Ur.S`), and the V relay below presents it north.
  AND_ONLY `V2p+DBr @ 3,2|3,3` and UNIT_ONLY `V2p+Ur @ 3,2|3,3`
  enumerate with the SAME signature (lower solo 1, upper solo 0,
  mutual vertical 1) — BUILD1's measured family-scope read-block
  channel exactly. DEEP_FACTS repeats the class per depth
  (`V3p+DBr @ 3,3|3,4`). The cooperative stack class is as
  constructional as the solo squat class: expect it in every ≥2-row
  v0.1 compile (census-level claim).
- **G4 CONFIRMED** — off-channel sites 3 (MINIMAL) < 7 (AND_ONLY,
  UNIT_ONLY) < 10 (DEEP_FACTS); depth scales the census monotonically
  in the via relays.

Consequences:

1. The duality claim's scope widens, at census level, from "one
   family's three inventories" to "every v0.1 compile shape with ≥2
   rows". Kinetic bounds remain BUILD1-measured — no new kinetic claim
   is made here (honest boundary; RS1/RS2 taught exactly this
   distinction).
2. d4 interpretation note: `lock_stack_channels` pairs where the
   reader's south face is the row-1 via glue are the read-block
   class regardless of rule shape — flag them as lo-read stacks when
   reading a census.
3. Deferred (b) strength-2 lock encoding: prerequisite MET (the trade
   table is corpus-general at census level). When picked, price
   against BOTH classes — the solo b=1 transient squat and the
   lo-read cooperative stack.

No cluster job (registered method; deterministic static enumeration,
complete predicate — same standing rule as tick 35).

## (b) Picked + pre-registered (tick 38, 2026-10-07)

Prerequisite met (tick 37: trade table corpus-general at census level).
The encoding: **strength-2 lock-read bond** — the first kinetic lever at
fixed bond identity (R1 contrast: renames change identity, strength
changes kinetics). A lock tile's W-face glue pair counts 2 instead of 1,
on both evaluation sides (the lock's own W bond and any tile's E bond
into a placed lock); site-agnostic and structural (any `L*` W read).
Value relays, done glues, base relays and squatter bonds stay strength 1
— both hazard classes keep their intrinsic bonds.

Pre-registration (gates fixed before any MC ran; script
`evidence/2026-10-07-strength2-lock/ktam_strength2.py`, this commit):

- Arms (family scope): BUILD1 plain + Vp-missing x {family, s2} at dG
  0.5; s2 at dG 2.0 (both); UNIT_ONLY (the designs/005 generality arm)
  x {family, s2} at dG 0.5. n=500/arm, 8 arms. Protocol of record;
  fresh seed base 160261107 stride 2e7.
- K1 s2_b1 blocked <= 0.22 [>= 0.27 falsified; between inconclusive]
- K2 s2_b1_Vp stable D2T fill >= 0.85 [<= 0.70 falsified] (the classic
  fill's E->L2 bond doubles, so repair holds or rises)
- K3 s2_b1 blocked cohort is the Vp+DBr lo-read stack, co-occurrence
  >= 0.7 [<= 0.4 falsified; n_blocked < 10 -> NO_EVENTS]
- K4 s2_b1 strict-pqr >= 0.55 [<= 0.45 falsified]
- K5 calibration fam refs 0.27 blocked / 0.908 fill within 0.05
  [any >= 0.10 off: protocol drift, stop reading]
- K6 dG direction: s2 blocked and fill both strictly lower at dG 2
  [either >= falsified]
- K7 generality: s2_unit blocked <= fam_unit blocked
  [> fam + 0.02 falsified]
- K8 lock capture: median first-passage of L2@(3,2) strictly lower
  under s2 [>= falsified] — the registered squat-dwell vs
  lock-capture-time prediction, priced against the published b=1
  equilibrium ~0.38 at dG 0.5.

n=8 smoke (instrument only, gates not evaluated) caught three defects
before registration: a dropped `dg` argument, the missing-species canon
inheritance (Vp-missing keeps BUILD1's canonical map — the vacancy is a
site whose canonical occupant was removed), and the `is_vp` arm-name
predicate missing the `_dG2` suffix arms. All fixed; smoke exit 0.
