# Energy, error and the knob

2026-10-08 — molasp-lab · synthesis, v1

**TL;DR.** The substrate's energy model in plain terms, and the three
knobs the lab tried for dialling error down: renaming glues,
strengthening bonds, and reading for longer. Each demolition removed a
comfortable reading, and the last one removed the idea that a
measurement can be taken without saying *when you looked*.

## The energy model

Every attachment earns or costs binding energy, counted in units of
kT (room-temperature energy). An attachment whose total bond falls
below the assembly temperature τ is reversible — the tile can detach
again. The quantity that matters is the gap ΔG between the cost of a
**near-miss**: a wrong tile that nearly fits, bonding through one
strained bond. When that gap is small, wrong tiles linger; when they
linger, they block the site until growth stops — a *near-miss trap*.
The trap probability behaves like 1/(1+e^−ΔG), which stays O(1) —
order-one, not small — exactly where growth is fast. That is why the
first "clean" run (0 unfounded decodes in 4,000 trajectories) was
luck, not design: the geometry had removed the trap by accident, and
a slightly different geometry put it back.

## Knob one: rename the glues

The lock column read wrong values because glues were *shared* across
rows — a lock could read the same code on two rows. So: rename the
shared glues per row ("row scope") and the sharing disappears.
Statically, it did: the census reported zero lock hazards and zero
misreads. Kinetically, 14.4% of reads still blocked and stable repair
still fired at 0.162. Single-bond transient holds and two-tile
recombination carried both behaviours *around* the rename. Lesson:
**static elimination is not kinetic elimination** — a clean
enumeration of bond names is not a clean enumeration of behaviours.

## Knob two: strengthen the lock read

The `s2` rule doubles the west-read bond for lock tiles, so stray
arrivals stick at effective strength 2. The obvious prediction —
stronger lock bonds, fewer lock problems — survived nothing.
Reinforcement **mints** frozen squatters instead of beating the
channel it aimed at (the vacancy's stable set grew from two to five
species while the correct fill's share halved). It **accretes**
rather than racing: misplacements are late captures onto a settled
background, so it never needs to win the first-attach race. And its
**sign flips with dG**: at dG 0.5 it manufactures squatters; at dG 4
— where everything else starves — it is the *only* channel that still
carries growth (0.074 → 0.564). Strength at fixed identity is
symmetric amplification: everything that shares the bond gets it.
The compiler now prices the knob against the operating point
(`contention_severity`, `regime_at`) instead of trusting it.

## Knob three: look longer

At dG 2 the contested vacancy looked like a fair coin — the correct
fill and a misplaced squatter split the site 232 : 229, and the lab
wrote that down as *stationary*. A pre-registered 4× read window at
identical kinetics turned the split into 367 : 131 — 0.737 to the
fill, decisively past the pre-registered 0.65 falsifier. The coin was
a **snapshot**: fairness came from freezing the experiment too early
to see the bias. Roughly half of sites froze on their first attach,
before any arrival-race bias could express itself; given time,
biased re-rolls compound toward the fill.

| regime | read-window response |
|---|---|
| frozen (dG 0.5) | immune — persistence 0.826 holds |
| marginal (dG 2) | tilts one-sided: 0.503 → 0.737 |
| churn (dG 4) | already fill-favoured; the window adds more |
| starved (dG 7) | no window rescues a nucleation barrier |

## What survived

Knobs are functions of the operating point, not universal hazards or
cures. The contention trade table now has three dials — glue scope,
read strength, and read window — and the honest unit of a claim is a
number *with its time index attached*. The pattern across the
programme: every time "stationary", "structural" or "dead" was
written from a single experimental frame, a second frame found
movement underneath.

- [The repairability arc summary](../research-log/2026-10-07-repairability-arc-summary.md) (all four regimes, measured)
- [Designs/007 — via-site lock kinetics](../designs/007-viasite-lock-kinetics.md) (the knob arc, closed)
- Next: [How we check a design](03-how-we-check-a-design.md)
