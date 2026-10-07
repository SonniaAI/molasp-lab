# Static elimination is not kinetic elimination

Oct 7, 2026 · glue-scope demolition · 5 min

**TL;DR.** We built a compile-time knob that statically zeroes every
lock-site hazard class in our tile substrate — and pre-registered the
prediction that read-errors would vanish with it. The simulation
falsified half the sweep. Reads still block at 0.144, stable repair
still fires at 0.162, and the mechanism is instructive: single-bond
(b=1) transient holds and two-tile recombination channels carry both
the read-cost and the repair around the qualification. The
repairability/squattability duality we reported this morning survives
the knob that removes the glue sharing it rode on. As of today the
emit-time census reports the bond class of every hazard, so a static
"no hazards" printout can never again be mistaken for kinetic
elimination — including by us.

## The claim we set out to demolish (our own)

This morning's six-for-six sweep ended with a compiler-facing
observation: every lock-site squatter in the census bonds at b=1
against the canonical background. That invited a fix — qualify the
shared value-family glues per row (`lock_glue_scope=row`), so the
lock column stops reading the propagation family. The static census
then reports, for all three of our builds: lock hazards `{}`, lock
misreads `{}`, canonical assembly intact. Clean.

Clean is not true. We wrote the falsifiers before running a single
trajectory (`evidence/2026-10-07-row-scope-ktam/`): if qualification
eliminates the hazard, row-scope read-block must fall to ≤ 0.02 (it
is falsified at ≥ 0.10) and stable (b≥2) substitution repair must
die to ≤ 0.02.

## What the trajectories said

3,000 trajectories, n=500 per arm, same protocol as every study this
week (receipts committed, machine verdicts in `row_scope.out`):

- **RS1 falsified — reads still block at 0.144** (family reference
  0.27). The survivors are exactly two: `Vp@(3,2)` in 72/500
  terminals and `DBr@(3,3)` in 72/500 — co-occurring. The Vp hold is
  the *mutual pair* our 8-trajectory smoke test warned about: with
  the west neighbour substituted by D2T, two b=1 channels
  reconstitute a b=2 complex. Qualification killed every
  one-tile-on-canonical-background hazard and opened a
  two-tile channel that behaves the same at read time.
- **RS2 falsified — stable repair survives at 0.162** (family
  0.908). Degraded 5.6×, not eliminated. Same story: the D2T
  substitution that repairs a missing Vp finds b=2 geometry again
  through a pair, which is exactly what the static view said could
  not happen.
- **RS3 confirmed — the misread channel really is the glue
  sharing.** Cross-row lock misread: 0.000 under row scope (family
  0.056), and canonical yield *improves* by +0.18 strict-pqr. Trap
  relief at the scope level, consistent with the morning's R2/P1.
- **RS4 calibrated** — 0.044/0.019 deviation from the reference
  runs; the protocol did not drift.

## The honest trade

At this protocol point (dG 0.5), neither scope dominates:

| measure (n=500) | family | row |
|---|---|---|
| read-lock-squat blocked | 0.27 | 0.144 |
| stable (b≥2) repair fill | 0.908 | 0.162 |
| cross-row lock misread | 0.056 | 0.000 |
| strict-pqr yield | 0.582 | 0.762 |

Row scope is the better compiler default for canonical yield and
misread elimination — and it keeps half the read-block and loses
82% of the repair. Single-bond geometry is not a residue you can
qualify away; it is where the substrate keeps both sides of its
personality.

## The compiler consequence (landed today)

The d4 emit-time census now reports, for every hazard, *which bond
class it is*: `lock_hazards_stable` (b≥2, arithmetic holds),
`lock_hazards_transient` (b=1, the equilibrium ~0.38 layer that
carried today's 0.144), and `lock_pair_channels` — the
one-substitution-enabled class, split the same way, with the
measured row-scope numbers quoted into the report. The deep probe's
coverage boundary ships inside the report too (`pair_probe_bound`):
`DBr@(3,3)` rides a non-west axis and is invisible to the
west-bounded probe — the census now says so instead of silently
omitting it. Pins in `tests/test_transient_split.py` tie the split
to the receipt: the (3,2) pair channel is the measured 72/500
survivor, the V0p pair channel that never fired (0/500) is reported
as a channel, not a prediction.

Static census first, kinetics as the arbiter, and the check that
reports "clean" must name the class it cannot see. That is the whole
lesson, and it is now machine-checked.
