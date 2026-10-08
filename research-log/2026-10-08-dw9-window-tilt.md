# DW9 demolished: the dG-2 "near-fair coin" was a snapshot, not a stationary split

Date: 2026-10-08 (tick 67, SON-4865). Anchors: commit hashes and queue
receipts quoted; no anticipated times.

## 1. The claim being demolished

Tick 43 (research-log/2026-10-07-contention-dg-sweep.md, n=500/arm)
measured the marginal regime of the s2 lock-reinforcement knob at
dG = 2 and read its census as a lottery: the canonical fill D2T and
the misplaced via-lock L2 ended the run holding the contested
reader vacancy at **232 : 229** — a share of 0.503 — with
first-stable persistence 0.520. The registered reading: *"the
re-roll is a near-fair coin … the lottery survives as a stationary
split."*

That sentence smuggled in a claim the experiment never tested: that
the split is **stationary**, i.e. a property of the regime rather
than of the read window. Tick 43 had no window arm at dG 2 (its
window arm ran at dG 4); the boundary note said so.

## 2. The pre-registered window test

Tick 47 (commit df958f2, gates frozen before submission) registered
DW9 with an explicit band: under a 4× read window at dG 2, the D2T
share **confirms in [0.40, 0.60]** and **falsifies above 0.65**.
Three companion gates: DW8 (window fill gain ≥ +0.10 over the 0.464
reference), DW10 (family channel window-neutral), DW11 (frozen
regime immune), plus LV1/LV2 making the L3 contender class
first-class. The v1 request died on a missing archive entrypoint
(forensics in 2026-10-08-dg2win-collection.md §1–2); v2
(request 5a243215…77e8e, blob bbe3aba4, clean-extraction smoke
before submission) ran 39 s and was collected through the
collect.py independent-recompute mismatch guard.

## 3. The measurement

n=500/arm, seeds base 220261107 (grepped disjoint from all prior
bases). Calibration arms landed dead-on (probe fill 0.412 vs the
tick-43 reference 0.412; L3 terminal census 0.100 vs 0.100).

- **DW9 FALSIFIED.** D2T 367 : L2 131 — share **0.737** over 498
  events, decisively above the 0.65 falsifier.
- **DW8 CONFIRMED.** Fill 0.734 vs reference 0.464 — window gain
  **+0.270**.
- **DW10 CONFIRMED.** Family fill 0.984 — the family channel is
  window-neutral.
- **DW11 CONFIRMED.** Frozen-regime persistence 0.826 ≥ 0.80 — the
  dG-0.5 destiny regime is immune to the window.
- **LV1 CONFIRMED.** L3 episode persistence 0.867 over 113 episodes
  (terminal census 0.100) — a frozen contender class, not a
  transient.
- **LV2 CONFIRMED.** L3 census moves 0.004 under the window.

Receipt: evidence/2026-10-07-dg2-window-l3vac/run.out + collection.md
(guard-checked; every number above is in the committed receipt).

## 4. The corrected statement

The dG-2 split is **not stationary; it is window-length-dependent**.
The marginal regime is window-tiltable toward the canonical fill:
a longer read window does not merely wait longer, it changes who
wins. This puts the read window itself into the contention trade
table as a third knob axis beside glue identity (renames) and glue
strength (reinforcement) — and it splits the regimes cleanly:

| regime | window response | evidence |
|---|---|---|
| frozen (dG 0.5) | immune — persistence holds 0.826 | DW11 |
| marginal (dG 2) | tilts one-sided: 0.503 → 0.737, fill +0.270 | DW8+DW9 |
| churn (dG 4) | already fill-favored; window adds more | tick 43 DW5 |
| starvation (dG 7) | window cannot rescue a nucleation barrier | tick 43 |

The compiler surface consequence: the contention_severity MARGINAL
tier (tick 44) is priced at the standard window; its honest form is
a function of the read window, and d4's regime pricing should say so
(recorded as the designs/007 follow-up, not yet implemented).

## 5. Mechanism (hypothesis, explicitly untested)

Why does the window tilt the coin? Plausible account: the
standard-window census froze roughly half the sites on first attach
(persistence 0.520) before any arrival-race bias could express
itself, while the 4× window admits multiple detach/re-attach cycles
and re-rolls compound. The single-roll race was never actually fair:
tick 41's three-way vacancy background measured D2T 203 vs L2 150
(0.575 among the pair) at first attach. A persistence-biased chain
of rolls converges away from the single-roll odds — but which chain
parameters produce exactly 0.737 is unmeasured.

**Next falsifier (pre-register before running):** trajectory-level
re-roll chain extraction at dG 2 — per-roll attach probabilities and
per-incumbent persistence, fit on half the seeds — then predict the
window-arm share analytically from the chain's stationary
distribution on the held-out seeds. A prediction outside ±0.05 of
0.737 refutes the compounding-chain account.

## 6. What this does not touch

DW9's demolition does not reopen the falsified levers of ticks 38–44
(strength-2 migration, rename recombination, family floor at dG 4);
those receipts stand. The frozen-regime and family-channel
confirmations are new load-bearing pins, not old ones relaxed.
