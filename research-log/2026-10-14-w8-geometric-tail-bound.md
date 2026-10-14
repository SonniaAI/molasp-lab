# Geometric tail-ratio bound eliminates the exactness transition band (tick 134)

**Date:** 2026-10-14 · **Ticket:** SON-5152 tick 134 ·
**Status:** measured + pinned (unreviewed lab note, not a validated result)

## Context

Tick 132 measured the domain-of-exactness envelope of the w8 tail helpers
(`binom_cdf` / `binom_sf_ge` in `tools/w8_exact_bands.py`). Direct branches
held the two-method bar (≤ 7.4e-11 relative domain-wide), but the complement
branch carried a **transition band**: the deep-tail guard's mass bound — the
monotone count bound `#terms·pmf(k)` — is loose by up to ~3 decades, so mid
points whose true mass was far below the switch (1e-5) stayed on the
`1 − x` branch and paid its lgamma-cancellation floor. Measured worst:
**1.689e-4 relative at mass 1.03e-8** (`cdf(2484, 2500, 0.999)`), disclosed
as the priced cost of a provably-safe guard.

## Change

The guard bound is now `min(count, geometric)`:

- **count** (tick 131): `(k+1)·pmf(k)` — pmf unimodal, monotone away from the
  mode on the guard's side.
- **geometric** (this tick): `pmf(k)/(1 − r_k)` with
  `r_k = k/(n−k+1) · q/p` the pmf down-step ratio at k (mirror
  `s_k = (n−k)/(k+1) · p/q` for the upper tail). The step ratios are strictly
  monotone in j (`r_j` increasing, `s_j` decreasing), so every term below k
  decays at least geometrically at rate `r_k`: `pmf(k−i) ≤ pmf(k)·r_k^i`,
  hence `Σ_{j≤k} pmf(j) ≤ pmf(k)/(1−r_k)` whenever `r_k < 1`. O(1)
  arithmetic on top of the same three lgamma calls; used only when the ratio
  is < 1, and min'd against the count bound (tighter for tiny #terms near
  the mode).

The bound only steers path choice: a marginal misfire routes a value down
the direct walk, which is relative-exact at any depth (tick 131) — float
slack in `r` costs nothing.

## Measured (all vs the independent per-term-lgamma logsumep oracle)

**Tightening:** 2122× at the tick-132 worst point (`2484, 2500, 0.999`:
count bound 2.196e-5 → geometric 1.035e-8 ≈ the true mass itself);
585× at k=3594 (n=4999, p=0.753304); ~2× near the mode (where the count
bound is already tight). The geometric bound is near-exact in the binomial
tail (the tail IS essentially geometric at rate r_k), so the guard now
fires within a few percent of the switch level.

**Envelope (full grid, 537 compared / 37 below floor — unchanged counts;
receipt `evidence/2026-10-14-w8-geometric-tail-bound/envelope-full.json`,
sha256 `8ed76df3…f844`):**

| class | tick 133 | tick 134 |
|---|---|---|
| cdf complement worst | 1.689e-4 @ mass 1.03e-8 | **4.750e-9 @ mass 1.38e-5** (`cdf(494,500,0.999)`) |
| sf_ge complement worst | 9.858e-5 @ mass 4.15e-7 | **2.340e-9 @ mass 3.71e-5** (`sf_ge(16,100,0.05)`) |
| deep_direct / short_side maxima | 6.76e-11 / 6.40e-11 / 7.34e-11 / 6.79e-11 | unchanged |

**The transition band is eliminated:** no complement bucket exists below
decade −5 on the whole grid — every measured point with true mass < 1e-5
now routes `deep_direct` (the old worst point computes at **2.109e-13**
relative, bucket −8 of deep_direct). The entire complement class sits
≤ 4.75e-9, inside the 1e-8 safe bar at every measured mass.

**Guard edges:** lower flip moved 3594/3595 → **3633/3634** (n=4999,
p=0.753304); upper mirror fires 1366..n (p=0.246696). `cdf(3600)` now
routes direct: 4.4276521107896456e-08 at 4.6e-11 relative (through tick
133: 4.423649579976541e-08 at 0.09% relative — the disclosed transition
error, now retired).

## Bit-conservatism

- All 7 byte-pinned deep values (`k=2601…3594`) unchanged (the firing set
  only grows; previously-direct points stay direct).
- `cp_accept_window(4999, 2e-22, 0.753304) = (3461, 4055)` unchanged;
  `sf_ge(1538, 0.246696) = 1.0091961624215313e-22` byte-identical.
- Family-level guards never fire (bounds 0.1–4 before and after) — the 10
  frozen-stratum windows and coverage pins are untouched (suite-verified).

## Honesty

- Grid-sampled, not exhaustive; oracle noise floor ~1e-12..1e-9 bounds the
  claim precision of the direct classes.
- The tick-132 receipt is retained unchanged
  (`evidence/2026-10-14-w8-exactness-envelope/`) as the historical baseline;
  figure `designs/assets/012-exactness-envelope.svg` still pins it. A 013
  figure for the new receipt (needs generator parameterization — the
  worst-point annotation x-position, transition-band caption and margin
  prose are layout-hardcoded) is deferred to the next tick.

## Waiter

Blockpower arbitration probe `d3aa0acaa37ff4c9…` still `queued`
(board-operator maintenance lease) since 2026-10-13T21:30Z — one frozen-rule
probe, no resubmit, nonce idempotent. Ladder stays PAUSED; the frozen
collection map is unchanged.
