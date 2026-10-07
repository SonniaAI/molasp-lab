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
