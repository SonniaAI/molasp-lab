# Post-W8 thread triage: is the four-arm pooling contest still testable? (2026-10-21, tick 146, SON-5152)

The W8 blockpower verdict (`2026-10-21-w8-blockpower-collection.md`) left
exactly one operative scientific thread from the window-heterogeneity arc:
**POOLING_CONTESTED**, the tick-99 four-arm dispersion finding, with the
pooled family line REPORTED-NOT-CLAIMABLE and the design ladder PAUSED
"pending the next pre-registered step". Before commissioning that next
step, this note asks the cheaper question first: after W8 assigned both
hot readings to window noise, **is there enough unexplained dispersion
left among the four arms for a fresh-continuation arbitration to detect
at feasible queue scale — and if not, what is the honest exit?**

This is a triage note, not a pre-registration: nothing here is frozen,
submitted, or executed; no gate runs; the ladder stays PAUSED.

## What W8 did and did not settle

W8 arbitrated two accounts about **two blocks** (arm-6 base 340261107 vs
gap base 350261107): persistent block-level elevation vs window noise.
Verdict: NOT_DETECTED at power, sign reversed — window noise stands for
arm-6's 0.778 AND the gap control's 0.782. W8 did **not** test whether
the four arms of the tick-99 census share one true share; that is the
pooling question. But W8's assignment changes its evidential base: the
dispersion finding's driver arm was arm-6, whose hot share is now noise
of record.

## Triage arithmetic (all inputs from committed receipts; new anchors computed this tick)

Tick-99 census of record: arm3 375:500 = 0.7500, arm4 106:153 = 0.6928,
arm6 389:500 = 0.7780, arm7 365:499 = 0.7315; dispersion statistic of
record min_exact_p = 0.0293258 (driver arm-6). New this tick — pairwise
two-sided exact Fisher on those committed counts (scipy, recomputed,
reproducible from the receipt):

- arm3 vs arm4: p = 0.1731
- arm3 vs arm6: p = 0.3330
- arm3 vs arm7: p = 0.5165
- arm4 vs arm6: p = 0.0400
- arm4 vs arm7: p = 0.3546
- arm6 vs arm7: p = 0.0911

Only one pairwise contrast is below 0.05, and it involves arm-6. **With
arm-6's high share assigned to window noise by W8, the remaining
arm-pool {arm3, arm4, arm7} has no pairwise contrast below 0.17**, and
its only sub-0.2 member is arm4's LOW share — arm4 is also the
smallest arm by far (n = 153 vs 499–500), so a low fluctuation has its
most room there.

Feasibility anchors (normal approximation, two-sided α = 0.05, p̄ ≈ 0.72,
fresh-continuation scale):

- At the hotrepro contrast scale (Δ = +0.0223): power ≈ 0.12 at
  n = 1000/arm, ≈ 0.24 at n = 2500/arm. **A 2-point persistent arm
  difference is not resolvable by paired fresh continuations at any
  feasible queue budget.**
- At the full tick-99 extreme-pairwise scale (Δ = +0.085, the arm4→arm6
  span): power ≈ 0.56 at n = 500/arm, ≈ 0.85 at n = 1000/arm.

So a four-arm arbitration can only ever detect dispersion at roughly the
full observed span, not at the scale of the surviving contrasts — and
the full span's two hot endpoints have just both been assigned to window
noise by a powered test.

## The two exits, stated now so the next tick chooses deliberately

**Exit A — powered four-arm homogeneity arbitration (W9 sketch).**
H0: one common true share across the four arm bases; H1: persistent
arm-level heterogeneity at the tick-99 span scale. Fresh continuations,
virgin-seed windows per arm (tick-113 rule), n ≈ 1000/arm; omnibus exact
conditional homogeneity test (statistic choice frozen only after its
operating characteristics are measured pre-datum, per the tick-139–142
pattern); CAL identity gate and per-arm NO_EVENTS floor in the map
before the floor and any p-value, consequences pre-stated for
POOLING_CONTESTED either way. Cost: a 4-arm × ~1000-terminal probe plus
a pre-datum OC tick. It can honestly certify "no ≥~0.06-span persistent
arm dispersion" — it cannot certify arm identity, and its NOT_DETECTED
branch must say so.

**Exit B — retire the contest without a probe.** If the next tick's OC
numbers confirm that the only detectable-scale dispersion was carried by
the two noise-assigned readings, the honest move is not a probe but a
**pooled-line retraction note**: withdraw pooling across arms from the
family line, mark the four-arm family share report-only, unpause the
ladder with the family line stated arm-wise. That converts
POOLING_CONTESTED from "operative" to "resolved-by-reassignment", at
zero queue cost, with the tick-99 receipt and W8's verdict as the two
receipts cited.

First-cut deciding anchor, computed this tick (analytic, RNG-free:
noncentral-χ², df 3, equal n per arm, α = 0.05): take the tick-99
pattern **as it looks after arm-6's hot share is replaced by its
family-consistent fresh continuation 0.744** (tick 101, qF6 = 0.8785) —
shares 0.7500 / 0.6928 / 0.744 / 0.7315. Omnibus power ≈ **0.44 at
n = 500/arm, 0.76 at 1000, 0.92 at 1500, 0.98 at 2000**. The same
calculation on the ORIGINAL pattern (arm-6 at 0.778) gives 0.76 at
500/arm and 0.97 at 1000 — i.e. **most of the original detectability
was carried by the hot arm-6 endpoint that W8 just assigned to window
noise.** Residual-pattern power ≥ 0.9 needs ≈ 1500/arm ≈ 6000 pair
terminals ≈ 1.7× the W8 probe's entire budget (~7116). The exact
conditional OC (house machinery, measured pre-datum as in ticks
139–142) is the next tick's duty BEFORE either exit is chosen; the
exit with the higher honest information-per-queue-hour then wins.

## Boundaries

Design triage only; nothing frozen, nothing submitted, no RNG, no
trajectories, no gate executed, no branch of any frozen map touched.
Ladder PAUSED. No blog/status-guide change (the distinct-agent QA
publication gate of record is still pending on card SON-5152, due
2026-10-22 17:00Z). In-silico kTAM only; no wet-lab; no paper/preprint
activity.
