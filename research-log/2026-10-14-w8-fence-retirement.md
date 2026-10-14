# 2026-10-14 — w8: the ±9σ fence retired; the honest resolution floor measured (tick 130)

Scope: the recorded tick-128 follow-up ("anchored-walk fix, **then the
±9σ fence can simplify**"), executed the tick after the anchored
re-seed repair landed (`1fe220b`). `cp_accept_window`'s two crossing
searches now binary-search the full `[0, n]` range; `_quantile_window`
is deleted. The boundary identities keep both predicates well-posed
with no bracket: `cdf(n) = 1 >= half` always, `sf_ge(0) = 1 >= half`
always, and `sf_ge(n) >= half` means the upper exit is impossible
(`k_low = n + 1`, handled explicitly).

## Bit-conservatism (retirement changes no value)

All ten frozen-stratum acceptance windows — world A (m=6, six-window
census) and world B (m=4, contested arms) — reproduce the fenced
code's windows **byte-for-byte**, pinned in
`tests/test_w8_fence_retirement.py` from a reference dump captured
immediately before the edit. Per-stratum CP coverages unchanged (mins
0.991984 / 0.988518, the tick-127 pins). Suite: **Ran 990 / OK
(skipped=1)** = 985 + 5.

## Catch #8 (measure-then-pin streak): the real resolution floor

The first-draft plan for this tick was to demo the unlock at
`alpha_m = 2e-22` ("beyond 9σ"). Measurement killed the lower-tail
half of that claim and corrected a documented number:

- The `1 - x` branch of `binom_cdf` (lower-tail values with `k > n/2`)
  resolves only down to **lgamma-cancellation scale, ~4e-11 at
  n = 4999, p = 0.753304** — NOT the "~1e-13" walk-rounding scale the
  tick-129 docstring recorded (now corrected). The seed's ~1e-11
  *relative* error on the O(1) complement mass is inherited by the
  whole up-walk.
- Below the floor: computed `0.0`. The TRUE crossing of `1e-22` sits
  at `k = 3461` (independent per-term-lgamma logsumep) — floored.
- First decade above the floor: wrong by up to **~7×** — computed
  `5.965672400520816e-12` at `k = 3564` where the independent logsumep
  gives `4.15992404828027e-11` — then converging (~3% at true ~1e-9:
  `1.0389942239896754e-09` vs `1.0742669044362198e-09` at k=3580).
- Direct short-side sums stay ~13-digit exact at any depth (the
  down-walk's error is *relative to tiny terms*); the asymmetry is the
  whole story: **upper-tail crossings have no floor** (sf_ge sums the
  short upper side directly), lower-tail crossings beyond n/2 do.

## The withdrawal and the genuine unlock

- **Withdrawn (same tick, with numbers):** the "beyond-9σ unlock at
  `alpha_m = 2e-22`" for the LOWER crossing. `k_high` returns 3564
  (resolution-limited), not the true 3461 — the full-range search is
  exact only for `alpha_m >= 1e-8` (`half >= 5e-9`, >100× above the
  floor). The module's family levels (`alpha_m >= 8.3e-3`) sit more
  than 1e8× above it (margin pinned as a test).
- **Genuine unlock:** the UPPER crossing at `alpha_m = 2e-22` is exact
  at depth — `k_low = 4055` at **9.49σ beyond np**, OUTSIDE the old
  ±9σ window `(3481, 4051)`: the retired fence would have rejected the
  very call. Defining equations byte-pinned on the helper
  (`sf_ge(4055) = 8.911166361078581e-23 < 1e-22 <= sf_ge(4054) =
  1.256186946808807e-22`) and inequality-verified against the
  independent logsumep.

## Bookkeeping

- `w8_exact_bands.binom_cdf` clamp docstring corrected to the measured
  cancellation floor; `test_w8_dependence_stress` header and hazard
  test docstrings updated (fence retired, pointer to the new pins).
- Suite stdout prints the collection-rehearsal "next: ..." lines every
  run (`import_queue_result.py:164` invoked by the rehearsal tests) —
  expected noise, NOT a waiter state change: the queue client still
  reports the blockpower request uncollected/queued.

Waiter unchanged: blockpower arbitration probe `d3aa0acaa37ff4c9...`
still queued (board-operator maintenance lease active) at this tick's
single frozen-rule probe — no resubmit, nonce idempotent, monitor
disarmed, hourly tick owns the next check. Zero trajectories, no gate,
ladder stays PAUSED; stdlib-only, no RNG; no blog/external/paper.
