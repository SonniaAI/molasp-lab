# Arm-wise family-wise bands: all four arms clear the 0.55 floor, none separates from the 0.75 tier boundary (2026-10-22, tick 151, SON-5152)

Ticks 148–149 established the report-only arm-wise baseline: the four corrected
w8 arm counts with pointwise Wilson-95 intervals, and design 011's descriptive
tier labels applied per arm — every pointwise interval crossed the 0.75 tier
boundary, so no point label was interval-stable. The explicit caveat in both
notes was that the intervals were pointwise, not simultaneous. This tick closes
that caveat with the smallest honest step: Bonferroni-adjusted Wilson bands over
the family of the four observed arms, read against the two boundaries design
011's tier semantics actually use.

`tools/w8_familywise_bands.py` imports the receipt-pinned counts from
`tools/w8_stratified_census.CONTESTED_FOUR_ARM_STRATA` (provenance and hashes
pinned by its own tests) and adds no data, no trajectories, no gate. Bonferroni
over k=4 at α=0.05 is valid under any dependence structure, so no cross-arm
model — the thing the tick-147 exit retired — is smuggled back in.

| arm | x / n | share | simultaneous 95% band (two-sided, z=2.49771) | one-sided family-95 lower (z=2.24140) |
|---|---:|---:|---:|---:|
| 3 | 375 / 500 | 0.75000 | [0.69875, 0.79509] | 0.70425 |
| 4 | 106 / 153 | 0.69281 | [0.59363, 0.77688] | 0.60420 |
| 6 | 389 / 500 | 0.77800 | [0.72831, 0.82084] | 0.73369 |
| 7 | 365 / 499 | 0.73146 | [0.67927, 0.77794] | 0.68485 |

## The two family-wise statements

1. **No arm earns a family-wise stable tier label.** All four simultaneous
   two-sided 95% bands straddle the 0.75 tier boundary (arm 3's band is
   [0.69875, 0.79509] around a point estimate that *is* 0.75). Tick 149's
   pointwise instability finding therefore survives multiplicity control
   exactly: widening the intervals for the family only makes each straddle
   surer.
2. **Every arm exceeds the 0.55 floor, family-wise.** All four one-sided
   family-95% lower bounds clear the floor tier, the smallest being arm 4 at
   0.60420 (its two-sided lower endpoint, 0.59363, also clears). With
   probability ≥95% (Bonferroni guarantee), all four true census shares lie
   above 0.55 simultaneously. This is the first statement of the resumption
   that is *new* at the family level, not just a widened restatement.

## Scope and boundaries

The family is these four observed tick-99 arms — a fixed census vector, not a
random sample of arms, and not a population of molecular systems. These are
simultaneous coverage statements about four census shares; they are not a test
of equality or dispersion across arms (that question was recorded open and
declined-on-cost at the tick-147 exit), they revive no pooled family claim, and
they change no frozen decision, the W8 verdict, or design 011's retracted w8
extrapolation. The tier boundaries themselves remain labelled descriptive
choices in design 011, not inferential thresholds. Since both statements follow
from committed counts by exact arithmetic, no new sampling or queue spend is
justified; any future arm-specific collection still needs a prospective
precision objective tied to a concrete design decision.

Numbers and conventions pinned in `tests/test_w8_familywise_bands.py`
(z-quantiles to 12 places, all eight band endpoints, both minima, both family
statements, count cross-check against the stratified-census module).
