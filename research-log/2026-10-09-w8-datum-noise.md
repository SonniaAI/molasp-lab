# 2026-10-09 — w8 datum-side census-noise map (tick 88)

**Status: pre-registered BEFORE the datum exists** (queued falsifier
`ed50c7ba…4daa85`, still awaiting cluster admission). Tool:
`tools/w8_datum_noise.py` + 12 pins in `tests/test_w8_datum_noise.py`.
The frozen W8 gate is **untouched**: HELD iff |s_w8 − 0.83376| ≤ 0.05
stays the machine verdict on the point estimate, exactly as
pre-registered. This note prices the noise the *datum itself* will
carry — the third uncertainty axis, after tick 86 (extrapolation-form)
and tick 87 (fit-parameter): the fresh arm's terminal pair census is a
binomial draw at k ≤ 500 trajectories.

## Method (pure arithmetic on committed receipts)

- Wilson-95 intervals reuse the tick-87 helper verbatim (z = 1.96),
  cross-checked by identity: `_wilson95(232, 461) = (0.45777,
  0.54868)` matches tick 87's w1-census bracket.
- Verdict-flip risks are **exact** one-sided binomial tails (log-space
  lgamma sums), not normal approximations.
- Gate-edge thresholds are **Fraction-exact** on the decimal edge
  strings, so float rounding can never move a gate comparison:
  x ≤ 391 ⇔ ŝ < 0.78376 at k=500; x ≤ 441 ⇔ ŝ < 0.88376.

## Measured results (k = 500, the protocol census)

1. **Datum Wilson-95 at the primary share 0.83376 is
   [0.79886, 0.86404]** — full width 0.06518, halfwidth 0.03259 =
   **65% of the frozen band halfwidth**. The census noise alone is
   two-thirds of the instrument's tolerance.
2. **Verdict-flip risks at the gate edges** (exact tails): a true
   share a full 0.01 *inside* the band still draws a false REFUTED
   27.4% (floor) / 27.0% (ceiling) of the time; a true share 0.01
   *outside* still draws a false HELD 31.3% (floor) / 21.5%
   (ceiling). At 0.03 from an edge the wrong-verdict risk falls to
   2.9–6.3%. Full grid in the tool JSON (δ ∈ {0.005, 0.01, 0.02,
   0.03} × both edges × k ∈ {50…500}).
3. **Quiet core** (wrong-verdict risk ≤ 2.5%, both edges): at k=500
   it is **[0.81743, 0.85263]** — and the primary 0.83376 sits inside
   it with ~±0.017 slack. At the MIN_EVENTS floor census k=50 the
   quiet core is **empty**: no share is verdict-safe at 2.5%.
4. **Region resolvability** (tick-86 five-region map): the
   form-ambiguous overlap [0.78376, 0.81415] (width 0.03039) is
   **narrower than the census CI at k=500** (0.07026 at region
   midpoint) — sub-region attribution there needs a point-estimate
   census **k ≥ 2673 ≈ 5.3 protocol arms**. HELD/hold-only
   attribution is resolvable at k=500, but only just (k_needed 407 <
   500). Same story at every k in the grid for the overlap region.

## Pre-registered reading overlay (prose discipline, NOT a gate)

Collection-day attribution prose may name a form/fit indictment only
if the datum's Wilson-95 interval lies **entirely inside** the
attributed tick-86 region; otherwise the prose must say
"**region-ambiguous at census k**". The verdict itself never moves.
Concretely: a HELD verdict with ŝ near 0.81415 cannot claim
"hold-last-only" (region 2) unless its Wilson-95 clears 0.81415; a
REFUTED verdict cannot claim "trend-alive" (region 3) unless its
Wilson-95 stays above 0.71415; and at k=500 no datum can cleanly
claim region 1 at all — it must be reported as form-ambiguous.

## Near-miss disclosure

The first draft's ceiling block swapped the `false_refuted` /
`false_held` labels (the floor orientation was baked in; the numbers
were right, the semantics inverted at the upper edge). Caught
pre-landing by re-deriving each direction before pinning; the
orientation is now explicit (`side: lo|hi`) and pinned in tests, plus
an at-the-edge ~50/50 coincheck as a standing guard. Lesson: when a
table is symmetric by construction, verify each orientation
independently — symmetry of *values* is not evidence of correct
*labels*.

## Chain of custody

All inputs are committed receipts (PRIMARY, BAND, tick-86 region
bounds). Deterministic pure-python arithmetic; identical inputs give
byte-identical output. No datum input exists yet; nothing here
touches the frozen gate, the five-step collection chain, or the
pre-drafted prose branches (which now gain one overlay rule to apply
at collection time).
