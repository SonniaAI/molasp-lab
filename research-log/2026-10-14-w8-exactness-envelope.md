# Domain-of-exactness envelope for the w8 tail helpers

Date: 2026-10-14 (tick 132, SON-5152, while blockpower
`d3aa0acaa37ff4c9…` stays queued on the board-operator maintenance
lease).

## Scope and motivation

Ticks 129–131 repaired and then symmetrised the deep-tail behaviour of
`tools/w8_exact_bands.binom_cdf` / `binom_sf_ge`, verifying the fixes
at isolated byte-pinned points (six deep points, one mirror world, the
switch edges). This tick turns those isolated pins into a measured
envelope over the advertised domain: a stratified sweep, module vs the
independent per-term-lgamma logsumexp oracle, max RELATIVE deviation
recorded per branch class. Instrument-validity sections of any eventual
paper need exactly this number: "max relative error of the tail
helpers across the domain, per code path, against an independent
method" — not six hand-picked points.

## Method

`tools/w8_exactness_envelope.py` (deterministic, stdlib only, no RNG;
local execution, no cluster job — the tick-37 static rule):

- Grid: `n ∈ {100, 500, 1000, 2500, 4999}`,
  `p ∈ {0.05, 0.246696, 0.25, 0.5, 0.753304, 0.95, 0.999}`
  (the mirror pair 0.246696/0.753304 exercises both guards
  symmetrically), `k ∈ {0, n, mode, mode ± 2σ, ± 5σ, ± 9σ}` clipped
  and deduped — 574 helper-evaluations, **537 compared**.
- Oracle: per-term lgamma + logsumexp (`math.fsum`), no shared code
  with the module (the established two-method bar, ticks 129–131).
- Classification: `short_side` (direct short-side sum),
  `deep_direct` (tick-131 guard: tail mass provably < 1e-5 by the
  monotone `#terms·pmf(k)` bound), `complement` (the 1−x branch).
- Comparison floor 1e-290: **37 points below floor** counted, not
  compared (the documented subnormal-seed behaviour — the walk returns
  0.0 below ~1e-304 true mass at n≈5000, monotone-correct). A module
  0.0 against an above-floor oracle mass is a hard failure (exit 2);
  it never fired.

## Measured envelope (full grid, evidence receipt sha256 b8664201…725b)

| helper | class | max rel dev | argmax (k, n, p) | true mass |
|---|---|---|---|---|
| binom_cdf | short_side | 6.40e-11 | (2429, 4999, 0.5) | 2.38e-2 |
| binom_cdf | deep_direct | 6.76e-11 | (4611, 4999, 0.95) | 5.25e-17 |
| binom_cdf | complement | 1.689e-4 | (2484, 2500, 0.999) | 1.033e-8 |
| binom_sf_ge | short_side | 7.34e-11 | (2500, 4999, 0.5) | 5.00e-1 |
| binom_sf_ge | deep_direct | 6.79e-11 | (389, 4999, 0.05) | 3.26e-17 |
| binom_sf_ge | complement | 9.858e-5 | (1403, 4999, 0.25) | 4.148e-7 |

Complement decade buckets (max rel dev by decade of true mass):

- cdf: ≥1e-2 → ≤1.04e-9; 1e-5 → 4.75e-9; 1e-6 → 3.81e-5;
  1e-7 → 8.96e-5; 1e-8 → 1.689e-4.
- sf_ge: ≥1e-2 → ≤1.26e-9; 1e-5 → 2.34e-9; 1e-6 → 4.76e-6;
  1e-7 → 9.858e-5.

## Claims this upgrades

1. **The two-method bar (≤1e-10) now holds domain-wide** for the
   direct code paths: short_side ≤ 7.4e-11 and deep_direct ≤ 6.8e-11
   across the whole grid — tick 131 verified this at six points; it is
   now a measured property of the classes, argmax structure included.
2. **The complement branch is relative-exact (≤4.8e-9) for every
   measured mass ≥ 1e-5.** Below that sits the transition band —
   where the monotone bound is ≥1e-5 but the true mass is smaller (the
   bound is loose by up to ~3 decades: worst case mass 1.03e-8 with
   bound ≥1e-5) — and relative error degrades monotonically in mass to
   the measured worst 1.689e-4. This is the honest price of the
   conservative guard: it was chosen to be PROVABLY safe, not tight.
   No frozen consumer compares below 8.3e-3 (family levels), five
   decades above the band; the deepest consumer comparison to date is
   α_m/2 = 5e-301, which routes through deep_direct (exact, tick 131).
3. **The subnormal floor is clean:** all 37 below-floor points sit
   where the module documents 0.0 (monotone-correct), and no
   above-floor point ever returned 0.0.

## Honesty box

- The envelope is grid-sampled, not exhaustive; the argmax structure
  (p→1 extremes, k near n, masses ~1e-8) says where complement worst
  cases live, and the monotone-in-mass buckets bound the story between
  grid points only by inference, not measurement.
- The oracle itself carries ~1e-12–1e-9 logsumexp noise; class maxima
  at 6–7e-11 partly reflect the ORACLE's floor, not module error
  alone — this is the two-method bar, not absolute truth. The deepest
  ground truth remains tick 131's exact-integer-factorial Decimal
  adjudication (7e-11 relative at 7e-301).
- The transition-band worst cases (1.7e-4) are the module working as
  designed and disclosed (tick 131 measured 9e-4 at a single point);
  nothing new is withdrawn.

## Bookkeeping

- Evidence: `evidence/2026-10-14-w8-exactness-envelope/envelope-full.json`
  (sha256 b8664201…725b, pinned). Tool:
  `tools/w8_exactness_envelope.py` (`--grid full|quick`). Pins:
  `tests/test_w8_exactness_envelope.py` (full-grid receipt values,
  sha256, class bars, decade buckets + monotone structure, quick-grid
  bit-conservatism recompute) — suite count in the commit message.
- Waiter unchanged: blockpower `d3aa0acaa37ff4c9…` still `queued`
  (board-operator maintenance lease, one frozen-rule probe, no
  resubmit, nonce `molasp-w8-blockpower-t120-a` idempotent, monitor
  disarmed, hourly tick owns the next check). Ladder stays PAUSED.
- Hosted CI on tick-131 head `7396e79` re-checked at this tick (state
  in the card report); this tick's head to verify next tick.
- Zero trajectories, no gate, no blog (instrument measurement, not a
  milestone), no wet-lab, no external contact, no paper/preprint.
