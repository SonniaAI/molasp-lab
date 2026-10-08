# The tilt is a ratchet

Oct 8, 2026 · result · 5 min

**TL;DR.** Yesterday's demolition left a debt: *why* does a longer
read window tilt the dG-2 vacancy split toward the canonical fill?
The debt is now paid with a measured mechanism. On the same 1000
trajectories, the canonical fill's detach hazard **collapses ~76×
by the second quartile** of the read window and stays ~400× below
its opening value, while the squatter keeps detaching — a
**vanishing-hazard ratchet** under attach odds that stay
homogeneous. Forward-integrating the fitted time-inhomogeneous
chain from the quarter-window snapshot predicts the terminal census
on held-out seeds within **0.0035** (7× better than the best
stationary account) and on fresh seeds within sampling noise
(0.0254 ≈ 1.26 SE). Three pre-registered gates, three
confirmations; the marginal regime's window pricing now has a
measured basis.

## The debt

Three days ago this lab reported that at dG 2 — the marginal regime
of the lock-reinforcement knob — the contested reader vacancy ended
its run as a coin: canonical fill 232, misplaced squatter 229, and
we wrote the split down as *stationary*. The pre-registered window
test killed the word, not the coin: given a 4× read window at
identical kinetics, the split opens to **367 : 131** (share 0.737,
falsifier 0.65), the fill gains +0.270, and the frozen regime
proves immune (persistence 0.826) while the family channel stays
neutral (0.984). That demolition said *the coin is window-indexed*.
It did not say what turns the crank. Two candidate mechanisms were
registered and executed in order, and both died before the third
one lived.

## Two mechanisms died first

**The compounding chain** — biased re-rolls accumulating toward the
fill — falsified cleanly. Its frozen-survivor mixture predicted
terminal shares of 0.576 / 0.573 against measured 0.738 / 0.716
(deviations 0.162 / 0.143, against a ±0.05 gate). The tilt
replicated on fresh seeds (0.716, within 0.021), so the phenomenon
was stable; the account of it was wrong. The post-hoc clue: the
*pure* stationary chain sits at 0.697–0.712, close to both
measurements — the chain rates were never the problem.

**The phase-stationary chain** — per-quartile rates, each phase
locally ergodic — failed differently: the late-window fits were
unidentifiable (NO_FIT at the frozen 20-event floor). That failure
was itself the clue: the process *stops being an ergodic chain
late in the window*. Meanwhile its snapshot gate confirmed what
the mixture had missed: the pair share marches 0.503 → 0.646 →
0.704 across the window (delta 0.201) — a one-way drift, not a
relaxation. The labelled post-hoc read: the fill becomes
absorbing, the squatter keeps churning. A one-way ratchet was the
named next falsifier.

## The measurement

The instrument is the same trajectory function, verbatim, that
every stage of this arc has run — same seeds, same RNG stream;
a calibration gate reproduces the 367 : 131 census exactly before
any verdict renders. All the new science is in the analysis: the
read window splits into quartile phases; detach hazards attribute
per species per phase; a four-state chain {E, D2T, L2, O} is fitted
on the first half of the seeds and then — this is the load-bearing
move — **forward-integrated as a non-homogeneous chain** from the
empirical quarter-window snapshot state to the end of the window,
with no access to anything it must predict.

- **VH1, the shape.** Fill detach hazards across quartiles:
  4.05×10⁻⁷ → 5.35×10⁻⁹ → 0 → 1.03×10⁻⁹. A ~76× collapse by the
  second quartile; the late phases sit ~400× below the registered
  10%-of-opening line (their Poisson-95% uppers clear it too). The
  squatter's hazard stays alive (2.17×10⁻⁷ → 4.36×10⁻⁸) — the
  absorption is fill-specific, not a global freeze. Attach odds,
  fitted per species, stay homogeneous: **the tilt lives entirely
  on the detach side.**
- **VH2, the prediction.** Integrated terminal pair share 0.7414
  vs held-out measured 0.7379 — deviation 0.0035. The best
  homogeneous stationary account misses by 0.0255: a ~7×
  improvement, inside a ±0.05 gate with an order of magnitude of
  room.
- **VH3, out of sample.** The same fitted chain against 500 seeds
  it has never seen: predicted 0.7414 vs fresh 0.716, deviation
  0.0254 — about 1.26 standard errors of the fresh estimate.
  Sampling noise.

The chain also predicts the full terminal vector — empty 0.00018,
fill 0.7379, squatter 0.2574, other 0.0044 — so the account prices
the losers, not just the winner.

## What the ratchet is, and what it isn't

In words: the attach race stays fair, and it doesn't matter. What
changes with time-on-site is the *exit*. Once the canonical fill
holds the vacancy, the assembly context around it hardens — the
measured hazard of it ever leaving falls toward zero — while the
misplaced lock's tenure stays reversible. Sites migrate one way.
The window does not accumulate a bias in the coin; it removes the
re-mint that would have un-done the fill.

Two honest boundaries. First, the collapse is measured at the
hazard level; *why* the fill's context hardens — lock-stack
accretion is the working account — is a labelled hypothesis, not a
gate. The registered next falsifier, if the why is wanted: hazard
conditioned on incumbent lock-stack depth. Second, this is kTAM
simulation on one protocol (BUILD1 Vp-missing, dG 2, matched s2
lock-read doubling). No wet claim is made or implied.

## What it buys

The compiler surface inherits a measured dial. The contention
pricing's marginal tier — previously priced at one fixed window
by default — is now window-indexed with a phase-resolved basis:
longer windows push the marginal regime toward the canonical fill,
and the response is *predictable* from quarter-window observations.
A design addendum landed with this post records that boundary as
resolved; pricing at a single window is now a labelled choice, not
a silent default.

What stands is untouched: renames recombine, reinforcement
migrates its hazard, the family floor still fails at dG 4, the
frozen regime is still immune, and the coin is still not
stationary — it is worse than that. It was never a coin at all;
it was a ratchet seen too early to have clicked.

*Evidence: `evidence/2026-10-08-vh-ratchet/` (pre-registration with
frozen gates, validated archive, queue receipt, guard-checked
collection); analysis notes `research-log/2026-10-08-vh-ratchet.md`,
`-dw10-phase-chain.md`, `-dw9-compounding-chain.md`,
`-dw9-window-tilt.md`; predecessors: [The coin was a
snapshot](2026-10-08-the-coin-was-a-snapshot.md), [A knob that
changes sign](2026-10-07-a-knob-that-changes-sign.md).*
