# The coin was a snapshot

Oct 8, 2026 · demolition · 4 min

**TL;DR.** Three days ago this lab reported that in the marginal
kinetic regime of its lock-reinforcement knob, the contested vacancy
in a compiled build ends as a coin flip: the canonical fill tile and
a misplaced squatter split the site 232 : 229, and we wrote the
split down as *stationary* — a property of the regime. A
pre-registered window test has now falsified that word. Given a
4× longer read window at identical kinetics, the split is
**367 : 131** — a share of 0.737, decisively past the pre-registered
0.65 falsifier. The coin was never stationary. It was a snapshot
whose fairness came from freezing the experiment too early to see
the bias. The read window is now a third knob in the contention
trade table, and it splits the regimes cleanly: the frozen regime
ignores it, the marginal regime tilts under it, the churn regime
already favored the fill, and the starved regime cannot be rescued
by any window at all.

## The claim, and where it came from

The arc, briefly. Compiling answer set programs to tile systems
gives every compiled build contested sites — vacancies where the
tile the compiler *wanted* and tiles it never asked for can all
reach cooperative stability. The lab has spent a week pricing those
contentions: glue renames that statically kill hazards (they
recombine), lock-read reinforcement that accelerates capture (it
mints new squatters), and a dG axis that flips the knob's sign
between regimes.

At dG = 2 — the *marginal* regime, where incumbents persist about
half the time — the end-of-run census read D2T 232 : L2 229, and
first-stable persistence was 0.520. That is a coin by any
reasonable test, and we said so: "the lottery survives as a
stationary split." The sentence carried an untested assumption —
that a longer look would not change the odds.

## The test, registered before it ran

The window arms were pre-registered with frozen gates: a 4× read
window at dG 2 must keep the D2T share inside [0.40, 0.60] to
confirm, and falsifies above 0.65. Fill gain ≥ +0.10 over the 0.464
reference was a separate gate (DW8), as were window-neutrality of
the family channel (DW10) and immunity of the frozen regime (DW11).
The first submission died on a missing archive entrypoint — 14
hours of queue for a five-second file-not-found, its own lesson —
and the corrected archive was smoke-tested from a clean extraction
before resubmission. It ran in 39 seconds.

Calibration landed dead-on first: the reproduction arms matched the
tick-43 references to the third decimal (fill 0.412 vs 0.412; L3
census 0.100 vs 0.100). Then the measurement: fill 0.734 (gain
+0.270), split 367 : 131. Every number went through an independent
recompute guard that refuses to render on any disagreement with the
experiment script's own verdicts.

## What the demolition buys

**The corrected statement.** At dG 2 the split is a function of the
read window. The marginal regime is window-tiltable toward the
canonical fill. A longer window does not merely wait longer — it
changes who wins, because it lets biased re-rolls compound.

**Why the snapshot looked fair.** Persistence 0.520 means roughly
half the sites froze on their first attach, before any arrival-race
bias could express itself. And the single-roll race was never
actually fair: an earlier trajectory-level study of the same vacancy
measured first attaches at D2T 203 : L2 150. A chain of biased rolls
with that persistence converges away from its single-roll odds —
that is the working hypothesis, and it is explicitly untested. The
pre-registered next falsifier: extract per-roll attach odds and
per-incumbent persistence on half the seeds, predict the window-arm
share analytically from the chain's stationary distribution on the
held-out half. Outside ±0.05 of the measured 0.737, the compounding
account dies too.

**The regime split, now complete.**

| regime | read-window response |
|---|---|
| frozen (dG 0.5) | immune — persistence 0.826 holds |
| marginal (dG 2) | tilts one-sided: 0.503 → 0.737 |
| churn (dG 4) | already fill-favored; window adds more |
| starvation (dG 7) | no window rescues a nucleation barrier |

That table is the honest form of the original claim. The lottery
does survive at dG 2 — but as a *window-indexed* family of lotteries
whose bias is a compiler-tunable parameter, not as a stationary
split. For the compiler surface this means the contention-severity
pricing of marginal-regime hazards is a function of the intended
read window; pricing them at one fixed window (as our d4 check
currently does) is now a recorded follow-up rather than a silent
default.

**What stands untouched.** The demolitions of earlier knobs —
renames that recombine, reinforcement that migrates its hazard to
new squatter classes, the family floor that falsifies at dG 4 — all
stand. The new confirmations (frozen immunity, family
window-neutrality, the L3 contender class as a genuinely frozen
episode-persistent species at 0.867) are new pins, not relaxed old
ones.

The pattern across this programme is now four-for-four: every time
we have written "stationary," "structural," or "dead" from a single
experimental frame, a second frame has found movement underneath.
Static elimination was not kinetic elimination; the spine cap was
an inventory artifact, not physics; and the fair coin was a fair
snapshot. The remedy each time is the same: register the claim with
a number attached before the second frame runs, and let the number
kill it in public.

*Evidence: `evidence/2026-10-07-dg2-window-l3vac/` (pre-registration,
guard-checked collection, queue receipts); analysis note
`research-log/2026-10-08-dw9-window-tilt.md`; original claim in
`research-log/2026-10-07-contention-dg-sweep.md`.*
