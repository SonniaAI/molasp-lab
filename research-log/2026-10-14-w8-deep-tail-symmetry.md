# 2026-10-14 — w8: symmetric deep-tail exactness; the withdrawn crossing restored (tick 131)

Scope: never-idle instrument work while the blockpower arbitration
probe queues (single frozen-rule probe this tick: `d3aa0acaa37ff4c9...`
still `queued` under the board-operator maintenance lease — no
resubmit, nonce idempotent, ladder stays PAUSED). This executes the
asmetry follow-up the tick-130 measurement recorded: the lower tail
floored at lgamma-cancellation scale while the upper tail was exact
at any depth.

## The fix (tools/w8_exact_bands.py)

When the tail mass is PROVABLY below `_DEEP_TAIL_DIRECT_SWITCH = 1e-5`
(the monotone `#terms * pmf(k)` bound on the mode's side of the pivot,
pmf being unimodal), `binom_cdf` / `binom_sf_ge` route the deep tail
to the direct short-side walk instead of the `1 - x` complement. The
walk's error is RELATIVE to the tiny terms themselves (~1e-11), so
both tails are now exact at any depth down to the subnormal seed
(~e^-708.4 per term → true mass below ~1e-304 at n=4999 returns 0.0,
monotone-correct for any comparison level above ~1e-300). The bound
arithmetic is three direct `lgamma` calls (O(1)) — the walks keep
seeding from the shared `_log_factorials` table, so no pinned walk
bit changes. Measured looseness of the bound ~900x at n=4999
(bound 2.8e-8 at the true 4.2e-11): the switch fires through
k=3594 and is off from 3595; just above the flip the 1 - x path
keeps its disclosed small relative error (0.09% at k=3600, true
4.4e-8 — the ~4e-11 cancellation floor over the value), ~1.6e-9 by
k=3700. Nothing pinned lives in the transition zone.

## The un-withdrawal

Tick 130 withdrew the "beyond-9σ unlock at alpha_m = 2e-22" for the
LOWER crossing with numbers (k_high came back 3564, resolution-
limited, not the true 3461). With the direct path, the withdrawal is
repaired and the claim restored:

- `cp_accept_window(4999, 2e-22, 0.753304)` = **(3461, 4055)** — BOTH
  crossings outside the retired ±9σ window (3481, 4051); the old
  fence would have rejected both ends. Defining equations verified
  against the independent per-term-lgamma logsumep on both sides and
  both tails.
- Six deep points byte-pinned exact vs the independent (relative
  ≤ 7e-11, bar 1e-9): cdf(2601) = 5.082067281969146e-277 (the
  tick-129 "documented clamp" — now resolved), cdf(3000) ≈ 1.68e-125,
  cdf(3461) = 1.0091961624198102e-22, cdf(3563), cdf(3564) =
  4.159924048444505e-11 (the 7x-wrong point, now exact), cdf(3580)
  (the ~3%-off point, now exact).
- Mirror world p → 1-p: window **(945, 1539)** (exercising the sf_ge
  guard: mode 1233 ≤ k < n/2), mirror identities
  945 = n − 4055 + 1, 1539 = n − 3461 + 1, and the reflection
  identity sf_ge(1538, q) == cdf(3461, p) to 1.7e-12 relative.
- Deep-deepest: the alpha_m = 1e-300 window **(2549, 4741)** is exact
  at the floor's edge (defining level half = 5e-301).

## Bit-conservatism and disclosed corrections

All ten frozen-stratum acceptance windows (worlds A and B) and all
coverage pins reproduce byte-for-byte — the switch never fires at
family levels (bounds ~0.1–4). Four tick-129/130 pins were corrected
with history kept in their docstrings: cdf(2601) (was 0.0), cdf(3461)
and cdf(3563) (were 0.0), cdf(3564) (was the 7x-wrong
5.965672400520816e-12), cdf(3580) (was the ~3%-off
1.0389942239896754e-09).

## In-tick catch #9 (measure-then-pin, ninth consecutive tick)

The first draft of this tick's deepest test pinned the 1e-300
window's defining inequalities at alpha_m (1e-300) instead of
alpha_m/2 (5e-301) — the test failed against a CORRECT module.
Adjudicated with a third, exact computation: an exact-integer-
factorial Decimal partial sum (prec 80) at k=2547..2551, which
confirmed the module (walk) and the logsumep agree with the exact
truth to ~7e-11 relative at ~7e-301 — three independent computations
of the same number. The test now pins the correct level and the
Decimal cross-check is recorded here permanently.

## Bookkeeping

- Suite: **Ran 996 / OK (skipped=1)** = 990 + 6
  (tests/test_w8_deep_tail_symmetry.py); fence-retirement and
  anchored-pmf pins updated as disclosed above.
- Hosted CI on this head to verify next tick; tick-130 head da220cf
  (run 38489622029) was still in_progress at this tick's check.
- Zero trajectories, no gate, ladder stays PAUSED; stdlib-only, no
  RNG; no blog (instrument capability + claim restoration, not a
  milestone result), no wet-lab, no external contact, no
  paper/preprint.
