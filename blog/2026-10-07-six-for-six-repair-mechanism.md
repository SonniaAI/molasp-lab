# Six for six: how a tile substrate repairs a missing piece

Oct 7, 2026 · repair mechanisms · 6 min

**TL;DR.** We pre-registered six falsifiable predictions about *how*
our seeded tile substrate survives the loss of a tile species, ran
12,000 kTAM trajectories, and all six held. The mechanism has a price
tag: the same shared value glues that let one tile stand in for
another (repair) also let tiles squat sites they should never occupy
(traps, misreads). Repairability and squattability are one property,
not two. That is now a number in every direction — and it becomes a
compiler check (designs/004) instead of a surprise.

## The anomaly

Last survey: delete exactly one tile species from the correct build of
`p.  q.  r :- p, q.` and measure how often the assembly still reads
out the full stable model `{p,q,r}`. Four deletions repair at parity.
Two of them *beat the intact build* — removing Vp gives 1.56× the
strict-decode rate at low driving force, V0p 1.23×. But repair cannot
make a system better than itself. If deleting a tile helps, the intact
system was sabotaging itself. Two candidate stories: self-trapping
(the deleted tile was squatting sites), or a faster path. We wrote the
predictions down — with falsifiers — before running a single
trajectory (`evidence/2026-10-07-repair-mechanism/`).

## What held

**Trap relief is real and it is the whole story for V0p** (R2).
Condition on trajectories whose lock column is clean of squatters at
read time, and build1 decodes strict-{p,q,r} at 0.781 while
V0p-missing decodes at 0.797 — a gap of 0.016. V0p's entire 1.23×
advantage is its own absence as a squatter. The Vp arm keeps a 0.146
residual (inside the 0.15 falsifier, outside the 0.10 target) — a
genuine second-order effect candidate, now being dissected at 4×
sample size with full-history tracking.

**Static glue arithmetic predicted the kinetic ranking** (R3a). An
exhaustive off-channel census — every tile × every site, bond ≥ 1
against the canonical background — says exactly two species can squat
lock sites: Vp at (3,2) and V0p at (3,1). In the trajectories, the top
read-time squatters at dG 0.5 are Vp@(3,2) = 107/500 and
V0p@(3,1) = 52/500. The two species whose deletion beats parity are
the two squatters. Nothing else even contends.

**Repair is substitution by siblings, and it is symmetric** (R3b).
When Vp is missing, D2T fills its vacancy in 90.1% of strict decodes;
when V0p is missing, D1T fills in 74.9% — both at full double-bond
stability, because the value-typed glue family makes readers and
values partially interchangeable. The interchange runs both ways:
V0p repairs D1T-missing (94%) and Vp repairs D2T-missing (97%).
A missing value can be re-derived from a reader; a missing reader can
be stood in for by a value.

**Every false positive in the L3 arm is a misread, fraction 1.0**
(R3c). With the r-lock tile absent, 23/500 trajectories still decode
strict {p,q,r}. All 23 hold L2 — the lock of the row *above* — at the
dead site (3,3), reading TRUE through a single weak bond to whatever
exposes a q-t value glue to its west. The lock's reader cannot tell
which row a `-t` glue came from. There were zero clean lock reads in
this arm: the misread is not a contaminant of the channel, it *is* the
channel.

**The trade-off closes at high driving force** (R4). Lock-squat rate
falls 0.314 → 0.118 → 0.000 across dG 0.5 → 2 → 4, and by dG 4 the Vp
advantage is gone (ratio 0.704): trap relief vanishes exactly while
the substitution-repair channel starves for monomer. You can buy out
of squattability, but the same purchase spends repairability.

## What the compiler does with this

The census that predicted all of this is pure glue arithmetic on the
compiler's own output — the tile inventory and the predicted canonical
assembly. So it stops being a study and becomes **d4**, an emit-time
check (designs/004): enumerate every off-channel attachment at bond
≥ 1, name the lock-site hazards, run the one-substitution deep probe
that catches the L2-style misread, and report. A warning, not an error
— a squatter is a kinetic hazard, not a semantic one — but never again
an accident. The glue-family width that buys repair becomes an
explicit knob with measured numbers on both sides.

## Honest limits

Read-time census (a lower bound on trap visitation); one geometry
(the 4-column AND build); positive programs only; kTAM simulation, no
wet lab. The 0.146 Vp residual is open — an n=2000 history-tracking
arm is pre-registered and queued.
