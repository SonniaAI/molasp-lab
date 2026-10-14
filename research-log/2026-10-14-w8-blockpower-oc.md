# Pre-datum OC of the frozen Fisher-exact arbitration instrument (2026-10-14, tick 139, SON-5152)

**Automated pre-datum measurement; independent QA review pending.** While
the repaired blockpower attempt (`dd5a8300…`, nonce
`molasp-w8-blockpower-t138-b`) waits behind the board-operator maintenance
lease, this tick measured the operating characteristics of the instrument
that will adjudicate it — before any datum exists. Zero kTAM trajectories;
synthetic binomial counts only; no gate executed; the ladder stays PAUSED;
no branch of the frozen map is touched.

## What was measured and why it was worth measuring

The tick-120 pre-registration states power by **normal approximation**
(SE 0.010332, power 0.896 at Δ0.030 / 0.979 at Δ0.038 / 0.696 at Δ0.0223,
anchor p̄ ≈ 0.745). The instrument itself is the **exact conditional
one-sided Fisher test** (scipy-`greater` convention: p = P[X ≥ x],
X ~ Hypergeometric(margins fixed)). Exact tests are conservative by
construction, so the pre-registered power numbers were unverified claims
about the exact instrument until now. This module closes that gap the
pre-datum way: fixed-seed Monte Carlo (stdlib Mersenne Twister, cached
log-CDF binomial inversion sampler imported from the tick-123 census-sim
module — stdlib-only, hosted-CI-safe), n = 3560/group, 4000 replicates,
α = 0.05, RNG seeds 20261015–20261019 (disjoint from census-sim 20261013/14
and from every committed trajectory seed family; none of the probe's
virgin windows consumed).

## Findings (receipt `evidence/2026-10-14-w8-blockpower-oc/oc.json`,
sha256 `142ddfb9…25a6`, all pins in `tests/test_w8_blockpower_oc.py`)

1. **The prereg's power claims are confirmed on the exact instrument.**
   Every normal-approximation claim lands inside the exact instrument's
   MC Wilson-95 interval: Δ0.030 → 3591/4000 = 0.89775 [0.88798, 0.90676]
   vs claim 0.896; Δ0.038 → 3916/4000 = 0.979 [0.97408, 0.98301] vs
   0.979; Δ0.0223 → 2777/4000 = 0.69425 [0.67979, 0.70834] vs 0.696.
   The exact test gives up nothing material at these margins.
2. **Realized size 193/4000 = 0.04825 ≤ 0.05** (Wilson
   [0.04203, 0.05534]) — conservative as expected for an exact
   conditional test, and close to nominal at these large margins.
   Branch-map interpretation is therefore calibrated: a NOT_DETECTED
   outcome genuinely means "no persistent between-block elevation of the
   pre-registered size at ~90% power".
3. **A hotrepro-sized effect survives NOT_DETECTED at only ~0.69 power**
   (measured on the exact instrument, not asserted from the normal
   approximation). If the branch lands NOT_DETECTED, the +0.0223-scale
   reading remains undetected-at-power, not excluded — the consequence
   note in the prereg already says this qualitatively; it is now a
   measured number.
4. **The prereg's anchoring ambiguity is immaterial.** The power section
   does not fix where Δ sits relative to p̄ (H0-variance SE formula);
   both readings were measured at Δ0.030 — baseline (0.775 vs 0.745):
   0.89775; midpoint (0.760 vs 0.730): 0.8915 (3566/4000) — Wilson
   intervals overlap fully. Neither choice changes any interpretation.

## Honesty box

- Monte Carlo, 4000 replicates; Wilson intervals quantify simulation
  error only. Not an exhaustive enumeration; not a physical-replicate
  or exact-confidence claim.
- The Fisher tail walk is float (log-factorial start, exact integer
  term-ratio walk, no 1−x complements); verified against exact
  `fractions.Fraction` hypergeometric sums to ≤ 3e-14 on small cases
  (two-method pattern, pinned live in the tests).
- Pre-datum by construction: the queued request has produced no datum;
  nothing here re-derives or touches the frozen branch map
  (`research-log/2026-10-13-w8-blockpower-prereg.md` remains the sole
  authority); the ladder stays PAUSED.

## Reproduction

```
python3 tools/w8_blockpower_oc.py \
  --out evidence/2026-10-14-w8-blockpower-oc/oc.json
```

Deterministic; the receipt sha is pinned and the suite re-runs the full
MC path live at n=200 (896/1200 rejections, seed 424242).
