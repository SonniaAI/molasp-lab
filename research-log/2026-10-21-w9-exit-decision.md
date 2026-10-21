# W9 exit decision: the pooling contest retires by reassignment — and the tick-93 trigger was never size-controlled (2026-10-21, tick 147, SON-5152)

The tick-146 triage note staged two exits for POOLING_CONTESTED and
fixed this tick's duty before either could be chosen: measure the exact
pre-datum operating characteristics of the candidate four-arm homogeneity
instrument, then let the exit with the higher honest
information-per-queue-hour win. That measurement is landed
(`evidence/2026-10-21-w9-homogeneity-oc/oc.json`, sha256
`560225f6…16a0`, all counts pinned in
`tests/test_w9_homogeneity_oc.py`), and it decided the exit — but on
sharper grounds than the triage's analytic anchor predicted, in both
directions. Nothing here was frozen before its OC was in hand; nothing
was submitted; no gate executed; no trajectories; the ladder was PAUSED
throughout the measurement and is unpaused by this note's decision
section below.

## What was measured

Fixed-seed Monte Carlo, stdlib Mersenne Twister, binomial draws via the
tick-123 cached log-CDF inversion sampler, 4000 replicates per config,
seeds 20261021–20261027 (disjoint from every committed seed family).
Worlds: H0 = all four arms at the pooled tick-99 census share
(1235/1652 ≈ 0.7476); RESIDUAL = the tick-99 pattern after W8
reassigned arm-6's hot share to its family-consistent 0.744
(0.7500 / 0.6928 / 0.744 / 0.7315); ORIGINAL = the raw pattern (arm-6
at 0.7780), kept as the calibration cross-check. Equal n per arm,
n ∈ {500, 1000, 1500}. Two instrument families:

1. **The tick-93 receipt rule** (the statistic that fired the contest):
   min over 4 arms of the exact two-sided binomial p against the
   leave-one-out pool, reject at nominal α = 0.05, no multiplicity
   correction.
2. **Pairwise exact Fisher** (size-controlled candidate): min over the
   6 pairwise two-sided exact Fisher p-values, reject at the Bonferroni
   threshold α/6 ≈ 0.00833. Each marginal test is conditional-exact
   (both margins fixed, no estimated null), so Boole bounds the family
   size at ≤ 0.05 under any dependence.

The two-sided Fisher implementation is log-space over a shared
log-factorial table, validated against `scipy.stats.fisher_exact` (same
point-probability convention) to ≤ 1.1e-14 on tick-99-scale tables, with
scipy-verified values pinned in the committed cross-check.

## Finding 1 — the contest trigger fires roughly one time in four under the null

| instrument | realized size (H0), n = 500 / 1000 / 1500 |
|---|---|
| tick-93 rule, nominal 0.05 | 0.2648 / 0.2673 / 0.2685 |
| tick-93 rule, Bonferroni 0.0125 | 0.0975 / 0.0970 / 0.0985 |
| pairwise Fisher, Bonferroni 0.05/6 | 0.0275 / 0.0288 / 0.0305 |

The LOO-binomial family cannot be rescued by thresholding: its null is
re-estimated from the other arms on every replicate, which breaks
marginal exactness — one high arm shifts every other arm's null and
fires several tests at once, so even the Bonferroni threshold runs at
~9.8%. At its pre-registered nominal threshold the rule rejects **about
27% of the time under perfect homogeneity**.

Consequence, stated plainly: the tick-99 dispersion receipt
(min_exact_p = 0.0293 < 0.05 → POOLING_CONTESTED) was produced by a
rule whose realized false-positive rate is ~27%. The tick-93
pre-registration already called α a *planning convention*, not a
size-controlled test, and the receipt never HELD or REFUTED anything —
but the contest's evidential weight was materially over-read since.
Under this measurement, "POOLING_CONTESTED" was more likely a
miscalibrated alarm than a dispersion signal.

## Finding 2 — the valid instrument is affordable but not cheap, and only against the optimistic pattern

Pairwise-Fisher/Bonferroni power on the RESIDUAL pattern:
**0.3665 at n = 500/arm, 0.6990 at n = 1000/arm (4000 pair terminals,
W8-scale), 0.88775 at n = 1500/arm (6000 pair terminals ≈ 1.7× the W8
probe's entire ~7116-terminal budget)**. On the ORIGINAL pattern
(arm-6 hot) it reads 0.6930 / 0.9605 / 0.9975 — confirming both that
the original detectability was real and that W8 has already dismantled
it. (The LOO family shows higher power at the same n, but its ~9.8%
size at the Bonferroni threshold makes those numbers incomparable —
power at twice the nominal size is not power.)

Two caveats bound even the residual numbers: the residual pattern takes
all four tick-99 point shares as persistent truths, including arm-4's
0.6928 estimated from the smallest arm (n = 153) — exactly the kind of
estimate most prone to regression — and the residual span's only
original-data contrast (arm-3 vs arm-4, exact Fisher p = 0.173) was
never significant even nominally.

## The exit decision (per the triage's fixed criterion)

**Exit B: retire the contest by reassignment. No W9 probe.**

A powered arbitration would spend 4000–6000 pair terminals (1–1.7× W8's
whole budget) plus prereg, collection, and review ticks to adjudicate a
contest that this tick's own measurement shows has no validated
evidential content left:

- the alarm that opened it realizes ~27% false positives under
  homogeneity (Finding 1);
- both hot readings that carried its original detectability are
  window-noise of record at power (W8 verdict, independently reviewed);
- the surviving residual pattern was never significant on its own data,
  and a valid instrument reaches only 0.70 power against it at W8-scale
  spend, 0.89 at 1.7×.

That is confirmation-seeking, not arbitration. Information per
queue-hour is higher anywhere else on the ladder.

Consequences of record, effective with this note:

1. **POOLING_CONTESTED is retired as resolved-by-reassignment**, not as
   arbitrated. The two receipts of record are the tick-99 census (which
   now documents a miscalibrated trigger, per Finding 1) and the
   reviewed W8 verdict (window noise at power for both hot readings).
2. **The family line is report-only, stated arm-wise.** Pooling across
   arms is withdrawn from any claimable line; each arm's share is
   reported per arm. The honest open limitation is recorded here:
   homogeneity at the residual scale (~0.06 span) remains untested; a
   valid instrument would need ~6000 pair terminals for 0.89 power
   against the optimistic pattern — declined on information per
   queue-hour, and worth revisiting only if a pooled line ever becomes
   load-bearing for a design decision.
3. **The design ladder UNPAUSES, arm-wise.** The pause reason
   ("POOLING_CONTESTED operative, pending the next pre-registered
   step") is discharged by this note; ladder arithmetic and future
   power planning must not assume arm homogeneity — they quote arms.

Status-guide family-line edit and the W8 milestone post remain behind
the distinct-agent QA publication gate of record (card SON-5152, due
2026-10-22 17:00Z); this notebook entry changes no publication surface.

## Boundaries

Pre-datum OC measurement and exit decision only. Nothing submitted, no
wet-lab, no trajectories, no gate, no branch of any frozen map touched;
the W8 datum and verdict bytes untouched. Zero queue spend. In-silico
kTAM only.
