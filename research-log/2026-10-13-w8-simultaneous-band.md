# 2026-10-13 — Simultaneous per-stratum bands, priced (tick 124)

**Scope.** Planning math only, landed while the blockpower arbitration
datum (queue request `d3aa0acaa37ff4c9…`, queued since 21:30:04Z) is
outstanding. Zero kTAM trajectories, no gate executed, ladder stays
PAUSED, pooled contested line stays REPORTED-NOT-CLAIMABLE. This note
pre-dates the arbitration datum; nothing here reads it.

## Question

Tick 123 (`fdab2ec`) pinned a design caveat on the frozen stratified
census menu: the conservative band is a **θ-interval**, not a
stratum-simultaneous band (contested world: covers θ\* at 0.99975, all
four stratum shares in 0/4000 replicates). Per-stratum Wilson-95 is the
named per-stratum authority — but it is *per-stratum nominal*, not
simultaneous. What does a genuinely simultaneous per-stratum band cost,
and does it deliver?

## Method

Bonferroni per-stratum Wilson at family level 0.95 with per-stratum
level 1 − α/m (m = number of strata): z₆ = 2.638257273476751,
z₄ = 2.4977054744123737 (`statistics.NormalDist`, stdlib-only module per
the tick-123 CI lesson). Measured by fixed-seed Monte Carlo over the
**same paired datasets** as tick 123 — identical worlds (A: homogeneous
six-window; B: contested four-arm), seeds (20261013 / 20261014), 4000
replicates, and `_BinomialCDF` draw order — so every replicate here is
byte-identical to its tick-123 counterpart. Pairing fingerprint: first
replicate counts 3695/3658/3722/3728/3671/3682 (A), 381/101/396/374 (B),
pinned in `tests/test_w8_simultaneous_band.py`.

## Numbers (4000 replicates, exact for these frozen datasets)

| quantity | A (m=6) | B (m=4) |
|---|---|---|
| all-strata coverage, plain Wilson-95 | 0.73675 | 0.81625 |
| all-strata coverage, Bonferroni-Wilson | 0.94975 | 0.95275 |
| min per-stratum coverage, Bonferroni | 0.9895 | 0.9865 |
| mean per-stratum width, nominal | 0.024394190338 | 0.092464638098 |
| mean per-stratum width, Bonferroni | 0.032828531666 | 0.117434594394 |
| **width price of simultaneity** | **1.3458×** | **1.2700×** |

## Reading

1. **The gap is real and exactly where predicted.** Plain per-stratum
   Wilson-95 all-strata coverage lands at 0.73675 / 0.81625, tracking
   0.95^m (0.7351 / 0.8145) — nominal-per-stratum was never a
   simultaneous guarantee, in either branch world.
2. **Bonferroni-Wilson restores it at family level.** 0.94975 / 0.95275
   all-strata coverage — the union bound guarantees ≥ 0.95 *in
   expectation*, and the frozen world-A realization lands one replicate
   short of it (3799/4000 = 0.94975), well inside the ±0.0068 MC error;
   min per-stratum 0.9895 / 0.9865.
3. **The price is modest and structural.** +34.6% (m=6) / +27.0% (m=4)
   mean per-stratum width — the width ratio tracks the z ratio within
   0.03% (Wilson widths are near-linear in z at these n's). Compare: the
   conservative band's honesty premium was 2.448× / 1.928× *over pooled*
   and it still bought θ-coverage, not simultaneity.
4. **Complement, not replacement.** Bonferroni-Wilson is the missing
   per-stratum simultaneous authority at a priced premium; the
   conservative band remains the θ-interval honesty summary; per-stratum
   nominal Wilson remains the primary reporting unit. Three statements,
   three jobs, all now priced.

## Honesty box

- Fixed-seed MC: values are exact for these frozen synthetic datasets;
  across replicate resampling the MC standard error at a 0.95 proportion
  is ~0.0034 (95% ~±0.0068). Synthetic binomial worlds calibrated to
  committed receipts — no claim about physical replicates, kTAM
  trajectories, or the pending arbitration.
- Bonferroni is conservative by construction (union bound); tighter
   simultaneous bands (e.g. Studentized-maximum or exact
   max-coverage calibration) could shave the width price — not attempted
   here; recorded as a named avenue.
- Branch-conditional relevance: NOT_DETECTED → pooled census stays
  primary and this is a secondary readout option; SUPPORTED → the
  stratified route becomes primary and this supplies its per-stratum
  simultaneous statement at the measured price.

## Artifacts

- `tools/w8_simultaneous_band.py` (stdlib-only, deterministic)
- `tests/test_w8_simultaneous_band.py` (18 pins/fingers, measured
  first then frozen)
- This note; suite and CI status on the card.
