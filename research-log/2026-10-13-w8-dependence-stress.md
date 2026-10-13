# W8 dependence stress test — the independence premise priced under common-mode drift (tick 128)

**Tick 128, 2026-10-13 late evening UTC — landed while blockpower
`d3aa0acaa37ff4c9…` sits queued (resource/owner limit, since 21:30:03Z;
nonce `molasp-w8-blockpower-t120-a` idempotent; no resubmit, ladder
PAUSED, zero trajectories, no gate).**

Module: `tools/w8_dependence_stress.py` + `tests/test_w8_dependence_stress.py`
(14 pins). Suite: **Ran 973 / OK (skipped=1)** = 959 + 14. No RNG anywhere;
every number byte-reproducible.

## Why this tick

The calibration arc priced simultaneity (tick 124, Bonferroni-Wilson at
1.3458×/1.2700× width), the correction choice (tick 125, exact Šidák
reclaims ≤0.27%), the real lever (tick 126, n at exact multiples
4.0032×/4.1046×), and exactness (tick 127, Clopper-Pearson premium
1.006–1.040). All four left one premise implicit: **independence of the
strata**. This tick stress-tests it in the deliberately adverse
direction for AND-events.

## Model (exact, no RNG)

Common-mode rate shock: every stratum shifts together, p_i → p_i + s·u,
u ~ U[-1, 1] (41-node trapezoid), shock scale s ∈ {0, 0.01, 0.02, 0.03,
0.05, 0.08, 0.12, 0.18}. Conditional on u the strata stay independent,
so family coverage is the exact 1-D integral

  F(s) = E_u[ Π_i cov_i(p_i + s·u) ],

each cov_i an exact binomial sum (tick-127 machinery). cov_i(u) peaks
near u ≈ 0 and collapses comonotonely as |u| grows — the shared-latent
coupling that Šidák's product form ignores, and the physically
motivated hazard (a shared calibration/concentration error moves every
window/arm the same way).

**Quadrature bar (honesty):** the integrand is a step function of rate,
so trapezoid error floors ≈1e-4 and oscillates (world A d(41,121) =
1.47e-5 but d(121,361) = 2.52e-5; worst measured 41-vs-121 delta
2.41e-4). Grid-averaged numbers carry **±2.4e-4**; s = 0 identities
carry none (single node). Every breach conclusion holds with margin
≥ 4× the bar (narrowest: Bonferroni-Wilson interior minimum 0.950964).

## Results

### s = 0 — first EXACT families for plain Wilson-95 and Šidák-Wilson

| calibration | world A (m=6) | world B (m=4) |
|---|---|---|
| plain per-stratum Wilson-95 | 0.7354224045110968 | 0.8194013046888571 |
| Šidák-Wilson | **0.9499025929034176** | 0.9540651459728295 |
| Bonferroni-Wilson | 0.9514275331073687 | 0.9540651459728295 |
| Bonferroni-CP | 0.9536212649481456 | 0.9612935741333267 |

- **Šidák's family is BELOW nominal in world A at the design rates
  themselves** (0.949903 < 0.95, exact — no MC error to hide behind;
  tick-125's MC 0.949 was right). The ≤0.27% width saving was never
  paid for, even with independence holding.
- **World B: Šidák ≡ Bonferroni bit-identically** (0.9540651459728295,
  last bit). Coverage is a step function of z; no world-B stratum's
  acceptance window jumps between z_Šidák = 2.49092 and
  z_Bonf = 2.49771. Exact count-based families can be literally
  insensitive to a calibration change.
- Bonferroni-Wilson/CP reproduce tick-127 bit-for-bit (Wilson, exact
  identity test) / to 1e-12 (CP via the independent fast path below).
- MC cross-checks: plain 0.73675/0.81625 and Bonferroni 0.94975/0.95275
  and Šidák 0.949/0.95275 (ticks 124/125) all inside their 2σ bars.

### Under drift — who keeps the 0.95 floor

- **Bonferroni-Wilson: never breaches** inside 99.5% of the feasible
  range in either world (cap families 0.9512047527976644 /
  0.9518504378079542), and is drift-FLAT (scan max−min 0.000462 /
  0.003101) — score intervals self-center, so the family pays for
  simultaneity in width, not in drift-fragility. In-expectation over
  THIS shock model, not a guarantee.
- **Šidák-Wilson: no floor.** World A hovers 0.949903–0.950033 across
  the whole scan (breached at zero). World B oscillates about nominal
  (values on both sides of 0.95 at every s ≥ 0.01) and first crosses at
  s* = 0.0297266 (verified bracket: family 0.950176 ≥ 0.95 > 0.949998);
  with the quadrature bar the honest statement is **s* ≈ 0.03**, an
  order of magnitude inside the feasible range, on a curve that has no
  margin anywhere.
- **Bonferroni-CP: structural floor verified pointwise.** Per-stratum
  CP coverage ≥ 1−α/m at EVERY scanned (rate, s, u) — margins +7.3e-6
  (world A, touching the guarantee boundary almost exactly) and +1.7e-4
  (world B). Worst-mode floors (min over the 41-node grid, the stronger
  statement — even the worst common mode): 0.9521453017662579 /
  0.9544317739730184, above (1−α/m)^m = 0.9510301646897641 /
  0.9509297119140627 ≥ 0.95. Never breaches (cap families
  0.9538542448186497 / 0.959916860228442). Union bound needs no
  independence: this certificate is coupling-free by construction,
  which is exactly what the stress cannot break.

### Certificate menu (closed under drift)

CP = dependence-free exactness certificate (0.6–4% width premium,
tick 127) · Bonferroni-Wilson = house authority, drift-robust by
self-centering but per-stratum approximate (union bound gives no
structural family floor: tick-127 measured the worst Wilson stratum
below nominal) · Šidák = retired — its saving never held the floor in
world A and has no margin in world B. Tick-125's decision ("a ≤0.3%
saving does not buy an independence premise") is now load-bearing with
exact numbers. Bonferroni stays house authority.

## Method notes

- **CP acceptance windows with zero interval solves:** from the
  defining equations, hi_CP(k) ≥ p ⟺ cdf(k,n,p) ≥ α/2 and lo_CP(k) > p
  ⟺ sf_ge(k,n,p) < α/2 — the interval's defining equations ARE the
  coverage statement; both crossings are binary searches over exact CDF
  values.
- **Boundary-rate rules (exact, not artifacts):** p ≥ 1 → k = n surely:
  CP hi(n)=1 covers, Wilson hi(k=n) < 1 misses (score intervals never
  touch 1); p ≤ 0 → both lo(0) ≤ 0 cover. The breach search caps at
  0.995·s_feasible so these fire only through genuine interior limits.
- Bisection thresholds are self-bracketing (bracket endpoints verified,
  first-crossing-on-the-scanned-path statements, no global-monotonicity
  claim).

## Catch #5 in the measure-then-pin streak (withdrawn numbers inside)

The first measurement run produced a CP family collapse under drift
(world A: 0.846 at s=0.02, 0.632 at s=0.05 — **withdrawn, superseded by
the fenced numbers above**). Root cause: seed underflow in the shared
tick-127 helper `_pmf_terms` — for deep-tail walk starts the seed pmf
underflows to 0.0 and the O(1) multiplicative recurrence can never
recover: `binom_sf_ge(2500, 4999, 0.753304)` returns 0.0 where the true
value is ≈0.9958. A naive CDF-quantile search starting at k = n/2 walks
straight into that cliff. Tick-127's pinned numbers are unaffected
(all its seeds sit within a few σ of the mode; validated against
analytic identities). **Fence:** both searches run inside
assert-bracketed np ± 9σ windows (seed log-pmf deficit ≤ ~40.5, never
underflows; 9σ two-sided mass ~1e-15 keeps every α/2 quantile used here
interior), and the hazard itself is pinned as a test.
**Follow-up (next ticks):** anchored-walk fix inside `w8_exact_bands`
(mode-anchored seeding for up-walks that straddle the mode).

Also repaired same-tick before any push: the first local suite run
FAILED (3 defects — s0_summary computed in `run()` but read from
`world_scan()`, a 1e-6 trapezoid tolerance that ignored the
step-function error floor, and the KeyError fallout); second run
surfaced a NameError from the fix itself. Final state: 973/OK. Main
never went red.

## Honesty box

Single common-mode coupling family (uniform, comonotone); NOT a claim
about the physical substrate. Other dependence structures are not
enumerated — deliberately: the point of the CP certificate is that the
union-bound floor is coupling-free, and Wilson's drift-flatness is
stated in-expectation over this shock model only. Real-data bands are
unchanged and descriptive; the pooled contested line stays
REPORTED-NOT-CLAIMABLE (POOLING_CONTESTED, tick 119). Zero kTAM
trajectories, no gate executed, ladder PAUSED, no blog/external/paper.
