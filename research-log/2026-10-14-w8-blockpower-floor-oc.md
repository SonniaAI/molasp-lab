# Pre-datum OC of the NO_EVENTS floor branch (2026-10-14, tick 140, SON-5152)

**Automated pre-datum measurement; independent QA review pending.** While
the repaired blockpower attempt (`dd5a8300…`, nonce
`molasp-w8-blockpower-t138-b`) waits behind the board-operator maintenance
lease, this tick measured the last un-measured branch of the frozen
arbitration map — the `NO_EVENTS` floor, which fires BEFORE any p-value is
read. Zero kTAM trajectories; no gate executed; the ladder stays PAUSED;
no branch of the frozen map is touched or re-derived.

## What was measured and why it was worth measuring

Tick 139 calibrated the Fisher test the map uses at the design
n = 3560/group. But `branch_map`
(`evidence/2026-10-13-w8-blockpower/ktam_w8_blockpower.py`) reads
`if ng < MIN_EVENTS or na < MIN_EVENTS: return "NO_EVENTS"` — either
group's pooled terminal pair census below 3400 defuses the arbitration
before the test runs. Each group attempts 3560 seeds; a seed lands in the
pair census unless its terminal reading is `other`, so pair_n ~
Binomial(3560, q) with q the per-seed terminal-pair yield. The prereg's
stated basis is empirical: terminal `other` ≤ 0.5% in every committed w8
window → q ≥ 0.995 → expected pair-n ≥ ~3542, "floor 3400 carries ~4.5%
headroom". That is a normal-approximation eyeball, not a measurement; this
module measures what the floor actually does, before any datum exists.

## Findings (receipt `evidence/2026-10-14-w8-blockpower-floor-oc/floor-oc.json`,
sha256 `9c72da35…03c`, pins in `tests/test_w8_blockpower_floor_oc.py`)

1. **NO_EVENTS cannot fire by statistical chance under any historically
   observed yield.** At q = 0.995 the per-group risk P(Bin(3560, q) < 3400)
   is 3.10e-95 and the two-group map risk 6.19e-95. If the branch fires,
   it is an execution/substrate anomaly signal (nonterminal flood, archive
   damage), not a sampling outcome — sharpening the prereg's consequence
   reading before the datum lands.
2. **The floor tolerates an ~8× terminal-yield collapse before it matters.**
   Per-group NO_EVENTS risk reaches 5% only at q = 0.96037 (other-rate
   3.96% vs historical ≤ 0.5%; multiple 7.93×) and 50% at q = 0.95487
   (other-rate 4.51%). The floor is a guardrail against catastrophic
   yield loss, not a plausible statistical outcome.
3. **The floor does not erode the arbitration at its edge.** At pair_n =
   3400/group exactly — the worst census the map still adjudicates — the
   tick-139 exact Fisher instrument delivers realized size 173/4000 =
   0.04325 (Wilson [0.03737, 0.05000], ≤ 0.05) and MC power 3569/4000 =
   0.89225 at Δ0.030 (Wilson [0.88226, 0.90149]) — inside the tick-139
   n=3560 band 0.89775 [0.88798, 0.90676]. Even a floor-edge datum keeps
   ~89% power at the pre-registered effect size.
4. **Two-method guard.** Every grid point is a defining-side sum
   (k = 0..3399); the float walk (log-factorial start, exact integer
   ratio walk down, recorded 1e-25 negligible-term cutoff) agrees with
   exact-rational Decimal ground truth at prec 80 (integer-power start,
   small-integer ratio steps) within 3.83e-12 relative at all four
   anchors — the float side's lnC start is ulp-limited near 4e-12 by
   cancellation of ~2.8e4-magnitude log-factorials (the tick-136 bounded
   oracle-noise pattern); the Decimal side carries the certified digits.
   The two-group map risk is computed in the cancellation-safe form
   2r − r² because 1 − (1−r)² evaluates to exactly 0.0 in float at
   historical yields.

## Honesty box

- The yield model treats per-seed terminal-pair outcomes as independent
  Bernoulli(q) within a group and independent across groups — the same
  exchangeability the Fisher PRIMARY already assumes; a seeded
  substrate-level yield collapse would violate it, which is precisely the
  regime the floor exists to catch.
- Inversions (q05/q50) are bisection-limited by the float walk's own
  precision, not the bisection; grid is q ∈ {0.900, 0.905, …, 0.995}.
- Floor-edge MC: 4000 replicates, synthetic binomial counts, seeds
  20261020/20261021 — disjoint from census-sim (20261013/14), from the
  tick-139 OC family (20261015–19) and from every committed trajectory
  seed family. Wilson intervals quantify simulation error only.
- Pre-datum: measured while request `dd5a8300…` is still queued; zero
  trajectories; none of the probe's virgin windows consumed.
