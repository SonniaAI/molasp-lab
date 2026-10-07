# 004 — Lock-site integrity: the squat census, d4, and the repairability trade-off

2026-10-07 (tick 26, SON-4778). Status: **design of record** — grounded
in the six-for-six confirmation of the repair-mechanism study
(`../evidence/2026-10-07-repair-mechanism/`, research-log
`2026-10-07-repair-mechanism.md`); implementation scheduled next tick.
Errata welcome: this document is derivation + measured numbers, the
machine check does not exist yet.

## Problem

Two confirmed mechanisms are consequences of the same design choice,
and the compiler currently makes that choice by accident:

1. **Squatting.** Value-typed glue families (`p-t`, `q-t`, `r-t`, …)
   are shared across the tiles of a row and its neighbours. Vp and V0p
   — value tiles of row 2 / row 1 — bond b=1 at *lock* sites (3,2) and
   (3,1) against the canonical background. In kTAM these squatters
   block 31.4% of build1 trajectories at dG 0.5 (11.8% at dG 2, 0.0%
   at dG 4).
2. **The lock misread.** A lock tile reads any `-t` glue on W as TRUE,
   regardless of row. With L3 absent, L2 holds (3,3) on a b=1 west
   bond to anything exposing q-t (Vp or D2T at (2,3)): 23/23 of the
   strict decodes in the L3-missing arm are this misread
   (`pqr_clean_frac` = 0.0 — the misread IS the channel).

The same sharing is also the repair channel: D1T fills the V0p vacancy
(74.9%), D2T fills the Vp vacancy (90.1%), and the interchange is
symmetric (V0p↔D1T 94%, Vp↔D2T 97%). **You cannot keep the repair
without the squat in this geometry; you can only choose the window or
narrow the family.** d2/d3 (semantic checks) are structurally blind to
all of this — they verify *what is compiled*, not *what else the
inventory admits*.

## d4 — emit-time off-channel census (the check)

Definition: given the emitted tile inventory, the seed, and the
predicted canonical assembly (one site per tile, which the compiler
already knows), enumerate every (site, tile) pair with bond ≥ 1 that is
not the canonical occupant — the reference implementation already
exists as measurement code (`trap_census.off_channel` +
`trap_census.lock_deep_probe`, tick 24). Lift it into `molasp/` as
`check_d4(build, canon)`, run at emit time.

Output, per build: the off-channel table (site → {tile: bond}); the
lock-site subset called out as **hazards**; the one-west-substitution
deep probe at lock sites (catches the L2-style misread that needs a
single background substitution).

Severity: **warning, not fatal.** d2/d3 fire on wrong compiles; a
squatter is a kinetic hazard with a measured dG dependence (→ 0 by
dG 4), not a semantic error. The report quotes the R4 decay
(0.314/0.118/0.000) so a downstream consumer can pick a read window.

### Acceptance criteria (machine-checked when implemented)

- **A1 (build1 census reproduced):** `check_d4` on BUILD1 returns
  exactly the tick-24 census: lock hazards {Vp@(3,2): 1, V0p@(3,1): 1};
  per-species off-channel sites Vp: [(1,1),(1,2),(2,1),(2,3),(3,2)],
  V0p: [(1,1),(2,2),(3,1)], D1T/D2T/DBr/L1/L2 as census; spine sites
  empty; deep probe at (3,3) = {Vp→{L2:1}, D2T→{L2:1}}.
- **A2 (no false hazards):** DAr, L3, S1–S3 contribute zero off-channel
  sites (their glues are unique) — d4 must not flag them.
- **A3 (semantic checks untouched):** existing d2/d3 behaviour and the
  full suite pass unchanged (d4 adds a report; it does not gate).
- **A4 (wrong-compile arm):** on BUILD3 (W1 dropped-literal), d4
  reports the same class of table — evidence the check is
  inventory-driven, not tuned to build1.

## Glue-family scope — the knob

`lock_glue_scope ∈ {family, row}` (compile-time, default `family`):

- **family** (current): value glues shared across the row's tiles.
  Buys: substitution repair (74.9–97%, both directions). Costs: lock
  squatters (31.4% blocked at dG 0.5) and the cross-row misread
  (23/23 of L3-arm false positives).
- **row** (variant): qualify lock-read glues per row (e.g. `q-t` →
  `q-t-lk` on L2.W and the row's value tiles' E/N). Kills the misread
  channel and the lock squat *and* the substitution repair — because
  all three are the same bonds. Cost measured on the other side of the
  same table; NOT a free fix.

d4 reports under both scopes before emit, so the trade is a decision
with numbers, not a default nobody noticed. (Measured trade table:
R3b 74.9/90.1/94/97% repair vs R3a 107/52 squatters and R3c 23/23
misread at dG 0.5; R4 decay to zero by dG 4.)

## Open measurement (pre-registered, queued)

The Vp residual (clean-conditional gap 0.146 at n=500) is being
dissected by an n=2000 history-tracking arm — predictions P1–P3 with
falsifiers in `../evidence/2026-10-07-vp-residual/ktam_mc_vp_residual.py`,
written before submission. Its outcome decides whether d4's report
should carry a dwell-time estimate (visitation delay) in addition to
the static table.

## Non-goals

Kinetic rates (d4 is static arithmetic); proofreading/tile
concentration tuning; multi-geometry generalisation — the census runs
on whatever geometry the compiler emits, but the *numbers quoted here*
are the 4-column AND build only.

## Evaluated (tick 29, 2026-10-07)

The knob is implemented and measured: `molasp/offchannel.py::
apply_lock_glue_scope` + `lock_glue_scope_reports` (d4 under both
scopes at emit time), pinned in `tests/test_glue_scope.py`, numbers
and related-work positioning in
`research-log/2026-10-07-glue-scope-related-work.md`.
Row scope on BUILD1: lock hazards {} and lock misreads {} with the
canonical assembly intact (every site still ≥ τ=2); repair bonds
D1T/D2T at their vacancy sites 2/2 → 1/1 — "kills the misread
channel and the lock squat and the substitution repair" holds as
stated, all three being the same bonds. Honest boundary found on
BUILD3: Fp@(3,3) survives row scope (its hold rides false-family
glues the current `-t`/`-t-done` qualification does not cover) —
extending the rule to `-f`/`-f-done` is the recorded follow-up;
until then the knob eliminates the value-family hazard class, not
every hazard.

## Evaluated (tick 30, 2026-10-07)

The tick-29 boundary is closed: the qualification rule now covers all
four shared value-family suffixes (`-t`/`-t-done`/`-f`/`-f-done`;
`SHARED_VALUE_SUFFIXES` in `molasp/offchannel.py`). Row scope zeroes
the lock-hazard and misread classes on all three AND inventories —
BUILD1 (value family), BUILD2 (the falsity chain: `Vp@(3,2)` and
`Fr@(3,3)` rode `q-f`/`r-f` lock reads) and BUILD3 (`Fp@(3,3)` rode
`p-f`) — with every canonical assembly still >= tau=2 (pinned in
`tests/test_glue_scope.py`, suite 219 OK / 1 skip). The remaining
boundary is glue CLASS, not family: non-value glues (spine, `go*`
entries, caps, `and*`/`w*` relays) are never qualified; no lock
hazard in the current inventories rides them.

The kinetic arm of the evaluation is pre-registered and queued
(`../evidence/2026-10-07-row-scope-ktam/ktam_row_scope.py`,
predictions RS1-RS4 with falsifiers, committed before the job runs).
Two smoke observations recorded pre-registration: raw read-time
occupancy of a b=1 transient hold is ~0.38-0.5 at this protocol
point (equilibrium arithmetic), so RS2 gates STABLE (b>=2) fill;
and one n=8 terminal showed a D2T+Vp mutual pair reconstituting
b=2 under row scope — the recombination risk RS2 honestly carries
into the n=500 run.

## Evaluated (tick 31, 2026-10-07) — kinetic arm closes the glue-scope study

The pre-registered row-scope kTAM validation ran (RS1–RS4, n=500/arm at
dG 0.5, read-time census; script pre-registered at fb3e08e; the v1
invocation failure and byte-identical v2 rerun are pinned in the
receipts). Machine verdicts: RS1 FALSIFIED (row squat-block 0.144, not
≤ 0.02 — b=1 transient holds still block reads), RS2 FALSIFIED (stable
D2T repair survives at 0.162, not ≤ 0.02), RS3 CONFIRMED (misread 0.000
AND row pqr 0.762 = family + 0.18), RS4 CALIBRATED (0.044/0.019
deviations vs the v2 references).

The knob's measured trade at this protocol point, replacing the static
extremes recorded at ticks 29/30:

- family: squat-block 0.27, stable repair 0.908, misread 0.056, pqr 0.582
- row: squat-block 0.144, stable repair 0.162, misread 0.000, pqr 0.762

Consequences for this design doc:

1. "Row scope zeroes the hazard classes" is a statement about b≥2 holds
   only. The d4 census must add (or at least footnote) a b=1 transient
   layer: kinetically ~0.14 read-block at dG 0.5 survives qualification
   (family 0.27).
2. The repair floor under row scope is 0.162 stable fill — degraded
   5.6x, not eliminated. The repairability/squattability duality
   survives the knob that removes the value-family sharing:
   single-bond geometry keeps both the read-cost and a recombined
   repair channel alive.
3. Canonical kinetics IMPROVE under row scope (+0.18 strict-pqr): trap
   relief at the scope level, consistent with R2/P1.

Follow-ups opened: d4 b=1 layer split (compiler guidance),
trajectory-level mechanism of the surviving stable channel
(history-aware rerun), kinetic test of the glue-CLASS boundary
(never-qualified relays).

## Follow-up implemented (tick 32): the d4 b=1 layer split

`check_d4` now reports the bond class of every lock hazard —
`lock_hazards_stable` (b>=2), `lock_hazards_transient` (b=1, the
layer that carried the measured 0.144 row-scope read-block) — and
the substitution-enabled class separately (`lock_pair_channels`,
split the same way), with the measured row-scope numbers quoted in
`measured_context.row_scope_kinetics` (read-block 0.144; survivors
Vp@(3,2)/DBr@(3,3) 72/500 each; V0p pair channel 0/500 fired;
stable repair floor 0.162; b=1 equilibrium ~0.38).  The deep
probe's west-bounded coverage is recorded in-report
(`pair_probe_bound`): DBr@(3,3) rides a non-west axis and is
outside the probe by construction.  Pins:
`tests/test_transient_split.py` — the row (3,2) pair channel
{west D2T -> Vp} IS the measured 72/500 survivor, and the V0p pair
channel is reported as a channel although it fired 0/500 (the
census over-approximates; kinetics decides — labeled as such).
A static `lock_hazards {}` is no longer readable as kinetic
elimination.  Remaining follow-ups: trajectory-level mechanism of
the surviving stable channel (history-aware rerun); kinetic test
of the glue-CLASS boundary (never-qualified relays).

## Refinement (tick 33, 2026-10-07) — stack classes, not pair channels

The history-aware recombination study (evidence/2026-10-07-
recombination, job hxq-e38ad7f3d5f377b9, pre-registered at 3fa1b4a)
kinetically refines the tick-32 pair-channel reading:

- The row read-block (0.141) is carried by the VERTICAL lock stack
  Vp@(3,2) N<->DBr@(3,3) (141/141 co-occurrence), not the
  {west D2T -> Vp} pair: D2T@(2,2) co-stacks (E-bond 141/142) but
  no D2T removal unseats Vp (mutual_pair_link 0/141).
- The row stable repair channel (0.155) is a 2-of-3 REDUNDANT
  relay stack N->DAr + S->V0p + W->S2 (153/155 at b=3; E->L2 in
  zero row holds). Single-partner load-bearing analysis is
  therefore the WRONG severity axis for the row-scope regime.
- d4 follow-up (next implementer): extend check_d4 reporting with
  (a) the vertical lock-stack class and (b) the vacancy relay-stack
  class, with the measured row context (0.141 vertical-stack block;
  0.155 relay-stack repair, 98.7% b=3) quoted in
  measured_context.row_scope_kinetics. Pair channels stay, labeled
  as sub-classes. Acceptance: pins against recombination.out.

## Follow-up implemented (tick 34): stack classes are emit-time
## report fields

`check_d4` now carries both cooperative classes, per the refinement
above (pins: `tests/test_stack_classes.py`, suite 255 OK / 1 skip):

- `lock_stack_channels` — a two-site mutual-support enumeration at
  vertically adjacent lock sites.  Each pair records the mutual
  N-S bond, the in-stack totals, and the SOLO bonds against the
  pure canonical background: the measured read-block channel
  `Vp+DBr @ 3,2|3,3` enumerates with solo 0/0 under row scope —
  cooperative-only, invisible to the one-site census, matching the
  141/141 co-occurrence (H3).  Under family scope the same pair
  reads solo 1/0 (Vp's b=1 transient layer): the class is a
  property of the scope, not the tile names.
- `vacancy_relay_stacks` — per-site filler relay FANS: per axis,
  the direct canonical contact (if any) and every squatter relay
  tile whose axis glue matches.  D2T at the vacancy (2,2)
  enumerates the measured 2-of-3 stack exactly (S canonical V0p +
  N DAr + W S2 relays; solo total bond 1 under row scope, 2 under
  family), and `measured_context.row_scope_kinetics` quotes the
  redundancy numbers (stable fill 0.155, b=3 fraction 0.9871,
  lb_any 0.0129) so no single-partner severity axis is read off a
  fan by accident.

Human-readable `d4_report_lines` filters to the cooperative-only
stacks and high-redundancy fans; the machine report carries the
full enumeration (census over-approximates; kinetics decides —
the standing rule).  WARNING severity unchanged; d4 never gates.

Open (pre-registered, queued): the dG sweep of both stack channels
— does 2-of-3 redundancy starve with dG the way the solo family
channel did (0.314 → 0.118 → 0.000)?  Script + gates committed at
the pre-registration commit BEFORE the job (see
`evidence/2026-10-07-stack-dg-sweep/`).
