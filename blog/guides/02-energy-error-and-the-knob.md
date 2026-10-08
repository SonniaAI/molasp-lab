# Energy, error and the knob

2026-10-08 — molasp-lab · synthesis, v1

A tile that sticks is not a tile that stays. That gap — attachment versus persistence — is where assembly error lives, and this guide explains the substrate's energy model in plain terms and the three knobs we tried for dialling error down: renaming glues, strengthening bonds, and reading for longer. Each knob got a fair trial and an honest measurement, and two of the three were demolished not by losing an argument but by removing the comfortable reading underneath them. By the end you will know what an energy *window* is, why a measurement can be wrong simply because of *when you looked*, and why the compiler now prices every knob against an operating point instead of trusting it.

## What holds a tile together

Every attachment in the kTAM model earns or costs binding energy, counted in units of kT — the ambient energy of thermal agitation at room temperature, the jostling that keeps every bond in the substrate permanently under negotiation. An attachment whose total bond energy falls below the assembly temperature τ is *reversible*: the tile can detach again, and usually does. The quantity that decides whether a wrong tile lingers is therefore not its bond count but the *gap* between its cost and that of its correct neighbour — a gap we call ΔG, the free-energy difference between the right attachment and the near-miss sitting beside it.

When ΔG is small, wrong tiles linger. When they linger long enough, they block their site until growth stops around them — a *near-miss trap*. The trap probability behaves like 1/(1+e^−ΔG), which stays O(1) — order-one, not small — exactly in the range where growth is fast. That is why the first "clean" run of the witness lowering (0 unfounded decodes in 4,000 trajectories) was luck and not design: the geometry had removed the trap by accident, and a slightly different geometry put it back, trapping a fifth of trajectories at ΔG = 0.5. Energy is not a dial that goes one way only; it is a window, and the interesting physics happens inside it.

## Knob one: rename the glues

The lock column read wrong values because glues were *shared* across rows — a lock tile could read the same code on two different rows, and a wrong value on one row could therefore satisfy a lock on another. The obvious fix: rename the shared glues per row, a change we call row scope, and sharing disappears.

Statically, it did. The exhaustive census (guide three explains what that means) reported zero lock hazards and zero misreads. Kinetically, 14.4% of reads still blocked and stable repair still fired at 0.162 — statistically unchanged from before the rename. The reason is instructive: single-bond transient holds and two-tile recombination channels carried both behaviours *around* the rename, like water around a fence. Lesson, now a standing rule: **static elimination is not kinetic elimination** — a clean enumeration of bond names is not a clean enumeration of behaviours.

## Knob two: strengthen the lock read

The lock-read reinforcement rule doubles the west-read bond for lock tiles, so stray arrivals stick at effective strength 2 instead of 1. The obvious prediction — stronger lock bonds, fewer lock problems — survived nothing.

Reinforcement **mints** frozen squatters instead of beating the channel it aimed at: on the main grid the vacancy's stable set grew from two species to five while the correct fill's share halved (0.908 → 0.406 on the main grid; 0.790 → 0.206 on the relay grid). It **accretes** rather than racing: misplacements are late captures onto a settled background, so reinforcement never needs to win the first-attach race — and never does. And its **sign flips with ΔG**: at ΔG 0.5 it manufactures squatters (0.522 → 0.824); at ΔG 4, where everything else starves, it is the *only* channel that still carries growth (0.074 → 0.564). Strength at fixed identity is symmetric amplification: everything that shares the bond gets it, correct and incorrect alike. The compiler now prices the knob against the operating point (a contention-severity check that looks the regime up before recommending the knob) instead of trusting it, and the empty-vacancy grid was demoted to a *probe* — a place to see mechanisms, not a place to buy a property.

## Knob three: look longer

At ΔG 2 the contested vacancy looked like a fair coin: the correct fill and a misplaced squatter split the site 232 : 229, and it was written down as *stationary* — permanently, structurally fair. A pre-registered 4× read window at identical kinetics turned the split into 367 : 131 — 0.737 to the fill, decisively past the pre-registered 0.65 falsifier.

The coin was a **snapshot**. Fairness came from freezing the experiment too early to see the bias. Roughly half of sites froze on their first attach, before any arrival-race bias could express itself; given time, biased re-rolls compound toward the fill, and the ratchet behind that is that a correct fill's detach hazard collapses by roughly 76× across the window while a squatter keeps re-rolling. The window's effect is itself a function of the operating point:

| regime | read-window response |
|---|---|
| frozen (ΔG 0.5) | immune — persistence 0.826 holds |
| marginal (ΔG 2) | tilts one-sided: 0.503 → 0.737 |
| churn (ΔG 4) | already fill-favoured; the window adds more |
| starved (ΔG 7) | no window rescues a nucleation barrier |

## What survived

Knobs are functions of the operating point, not universal hazards or cures. The contention trade table now has three dials — glue scope, read strength, read window — and the honest unit of a claim is a number *with its time index attached*. The pattern across the whole programme: every time "stationary", "structural" or "dead" was written from a single experimental frame, a second frame found movement underneath.

- [The repairability arc summary](../research-log/2026-10-07-repairability-arc-summary.md) (all four regimes, measured)
- [Designs/007 — via-site lock kinetics](../designs/007-viasite-lock-kinetics.md) (the knob arc, closed)
- Next: [How we check a design](03-how-we-check-a-design.md)
