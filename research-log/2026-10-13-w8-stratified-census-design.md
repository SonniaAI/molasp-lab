# W8 provenance-stratified census estimation — pre-registered design (tick 122)

Date: 2026-10-13 · SON-5152 · run 2afb0480. This is a design and
pre-registration artifact, written BEFORE the blockpower arbitration
datum (`d3aa0acaa37ff4c9…`, queued since 21:30:04Z) lands. **Zero new
trajectories were run for this note; no scientific result is claimed; no
gate is executed.** Automated pre-registration; independent QA review is
pending. In-silico provenance only.

## Why now, and what question this serves

Tick 121's related-work scan named the lab-ownable gap this note starts to
close: **provenance-stratified census estimation** — estimating the pair-
terminal D2T share per seed-base provenance stratum instead of pooling
across families whose pooling is contested. The blockpower probe
arbitrates exactly one provenance contrast (GAP 350261107 vs A6
340261107). Whatever branch lands, the lab needs a census route that does
not silently depend on the losing assumption. This note freezes that
route, branch-conditionally, before the datum exists — the same posture as
the stage-2 power plan (`2026-10-13-w8-ladder-stage2-power-plan.md`).

## Frozen data inventory (all counts from committed receipts)

Pure-math tool: `tools/w8_stratified_census.py`; pins:
`tests/test_w8_stratified_census.py`. Every number below is recomputed
by the tool and pinned against the receipts it transcribes.

**Six-window homogeneity study (tick 102/103), HETEROGENEITY_NOT_DETECTED:**

| stratum | x:n | share | Wilson-95 |
| --- | ---: | ---: | --- |
| block8 (380261107) | 3644:4999 | 0.72895 | [0.71645, 0.74109] |
| block9 (400261107) | 3707:4998 | 0.74170 | [0.72938, 0.75364] |
| block10 (420261107) | 3692:4999 | 0.73855 | [0.72619, 0.75054] |
| block11 (440261107) | 3675:4999 | 0.73515 | [0.72274, 0.74720] |
| block12 (460261107) | 3696:4998 | 0.73950 | [0.72715, 0.75148] |
| block13 (480261107) | 3697:4996 | 0.73999 | [0.72765, 0.75197] |
| **pooled** | **22111:29989** | **0.737304** | **[0.73229, 0.74225]** |

Pearson X²(5) = 2.7713095514, p = 0.7351922075 — reproduced by the tool
to 1e-12 against the receipt (`receipt cross-check pins`).

**Contested four-arm pool (tick 99, corrected tick 119; descriptive ONLY,
the pooled line stays REPORTED-NOT-CLAIMABLE):** arm3 375:500, arm4
106:153, arm6 389:500, arm7 365:499 → pooled 1235:1652 = 0.747579,
Wilson-95 [0.72607, 0.76794] — reproduces the tick-118 quoted interval
exactly. Descriptive Pearson X²(3) = 5.5865 (NOT a gate; the frozen
dispersion authority is the exact min-p instrument, POOLING_CONTESTED
stands).

**Calibration anchor:** CAL mid-w4 367:498 = 0.736948 (pair census
367:131, other=2) — the identity-check chain anchor, unchanged.

## The estimator (frozen before the datum)

For strata i with counts (x_i, n_i):

1. **Per-stratum Wilson-95** — the primary reporting unit under
   stratification.
2. **Size-weighted pooled share** Σx/Σn with Wilson-95 — valid as a
   *primary* reading ONLY where the applicable homogeneity gate says
   pooling is safe (six-window study: yes at n=5000/window; contested
   four-arm: no).
3. **Inverse-variance-weighted share** θ̂ = Σ w_i p̂_i / Σ w_i with
   w_i = n_i/(p̂_i(1−p̂_i)), delta-method SE = (Σ w_i)^{−1/2}. On the six
   windows: θ̂ = 0.737347, SE = 0.002541.
4. **Conservative simultaneous band** θ̂ ± Σ (w_i/Σw)·h_i where h_i is
   stratum i's Wilson half-width — overstates by construction; on the six
   windows: ±0.012196. This is the honesty-first summary when
   heterogeneity is unresolved.

## Branch-conditional consequences (pre-registered)

- **BLOCK_MECHANISM_NOT_DETECTED** → the stage-2 plan (1dd0e8b) proceeds
  unchanged; pooled census stays primary where its homogeneity gate
  passes; the stratified estimator is the secondary, variance-reducing
  readout. Nothing in this note unfreezes the ladder by itself.
- **BLOCK_MECHANISM_SUPPORTED** → the pooled line is retired by the
  frozen map; THIS design becomes the primary census route: report
  per-stratum Wilson + the conservative band; any growth allocates by
  Neyman (below); NO cross-family pooling without a fresh homogeneity
  gate at the new n; the pooled six-window reading remains valid only
  within its own provenance family (blocks 8–13).
- VOID / NO_EVENTS → neither branch activates; instrument diagnosis only
  (unchanged frozen rule).

## Allocation and power numbers (planning, not data)

- **Neyman allocation** (largest-remainder integers): worst-case
  σ=0.5 gives an equal split for k=2 (the A6/GAP shape). On the measured
  six-window σ's, block8 (lowest share, largest σ) takes the largest
  allocation, block9 the smallest — allocation ordering pinned.
- **Design cross-check at the blockpower envelope** (n=3560/group,
  p̄=0.74, one-sided α=0.05, 80% power): SE = 0.010397, normal-approx
  MDE90 = 0.025851; power ≈ 0.89 at Δ=0.030 (consistent with the
  prereg's exact-instrument 0.896); minimal one-sided n at Δ=0.030 =
  2644. The frozen (0.040/Δ)² rule's 3560 is the more conservative
  envelope and **stays the authority** — this cross-check documents the
  margin, it does not revise any frozen sample size.

## Honesty box

- Zero trajectories run for this note; every count is transcribed from a
  committed receipt and pinned. No gate executed; no branch claimed; the
  ladder stays PAUSED pending blockpower; the contested pooled line stays
  REPORTED-NOT-CLAIMABLE.
- The X²(3)=5.5865 on the contested pool is descriptive arithmetic, not
  the frozen dispersion gate (exact min-p), and must not be cited as one.
- Wilson z=1.96 and power z-conventions are stated in the tool docstring;
  the normal-approx cross-check is not the preregistered exact instrument.
- Literature anchors referenced by motivation are snippet-level per the
  tick-121 scan's honesty box.

## Next

Mechanical collection of blockpower when the queue admits it (frozen map,
unchanged recipe); this design then activates per the branch table above.
No blog (design, not a milestone), no wet-lab, no external contact, no
paper/preprint activity.
