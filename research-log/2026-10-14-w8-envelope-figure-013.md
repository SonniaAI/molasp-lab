# Envelope figure regenerated from the geometric-bound receipt; annotations parameterized (tick 135)

**Date:** 2026-10-14 · **Ticket:** SON-5152 tick 135 ·
**Status:** measured + pinned (unreviewed lab note, not a validated result)

## Context

Tick 133 pinned figure 012 (`designs/assets/012-exactness-envelope.svg`) as a
pure function of the tick-132 envelope receipt, but three pieces of its
geometry were still layout-hardcoded: the worst-point annotation x-position
(pinned at the plot's left edge, `fx(-8)`), the "≈5 decades below" margin
prose, and the transition-band caption. Tick 134 then replaced the receipt
itself — the geometric tail-ratio bound eliminated the transition band
(complement worst 1.689e-4 → 4.750e-9, no bucket below decade −5) — and named
this figure as the follow-up: re-render the chart from the new receipt
without hand-tuning labels, keeping 012 byte-identical.

## Change

`tools/w8_envelope_figure.py` now derives every data-dependent label from the
receipt it renders; nothing in the layout knows which receipt it is reading:

- **worst-point annotation x** follows `floor(log10(mass_at_argmax))` —
  tick-132's worst mass (1.03e-8 → decade −8) reproduces the old left-edge
  position exactly; tick-134's (1.38e-5 → decade −5) moves the annotation to
  the measured point.
- **margin prose** is the floor-decade difference
  `floor(log10(8.3e-3)) − floor(log10(worst mass))`: "≈5 decades" then,
  "≈2 decades" now.
- **direct-path bar label** is the ceil-2-significant-figure domain maximum
  over `short_side`/`deep_direct` from the receipt (`ceil_2sig`): both
  receipts measure 7.3416e-11 → "≤ 7.4e-11 domain-wide", conservative round-up
  preserved.
- **transition band** is drawn only while the receipt still has complement
  buckets below its edge decade (−5); the tick-134 receipt has none, so 013
  carries the elimination caption and no amber fill. The old receipt keeps
  its band and its disclosed-price caption, byte-for-byte.
- **subtitle** (grid span, rate count, oracle floor, evidence name) comes from
  the receipt fields; the evidence name is passed in by the caller (default:
  the receipt's directory name), since a JSON receipt cannot know its own path.
- **collision guard**: when the receipt's worst point sits low-right, the
  annotation pair is lifted one line so its prose cannot overlap a curve
  label in the right gutter (13 lines of deterministic geometry, no style
  choice). The tick-132 point sits high-left and never triggers it.

The tick-133 text-width audit (0.6·font-size per character, catch 10a) is
promoted from one-off pre-pin check to `audit_text_bounds()` in the generator
(returns every out-of-canvas or overlapping text box; `main()` prints it) and
is pinned for BOTH assets.

## Evidence

- New asset `designs/assets/013-exactness-envelope-geometric.svg`
  (sha256 `e5b30ee3861833cd7d9f6c3dbdbdce279a0f6281e786d2faa10e9e1c38c60263`),
  rendered from `evidence/2026-10-14-w8-geometric-tail-bound/envelope-full.json`
  (the tick-134 receipt, sha `8ed76df3…f844`). 10 bucket points (6 cdf + 4 sf),
  none below decade −5; both captions state what their own receipt measures.
- 012 is **byte-identical** after the refactor: fresh regeneration from the
  tick-132 receipt equals the committed asset (sha `f37b264c…c6d19`, unchanged
  from the tick-133 pin).
- Pins: `tests/test_w8_envelope_figure.py` reorganized into
  `EnvelopeFigure012Pins` (6) + `EnvelopeFigure013Pins` (7); the 013 class
  checks the elimination caption against the receipt itself (asserts NO
  complement bucket below −5 exists), derives the direct label from the
  receipt maxima, and audits text bounds for both figures.

## Honest notes

- The audit's character-width model is the same 0.6·font-size estimate as
  tick 133 — a heuristic, not a font-metric measurement; it bounds label
  collisions, it does not prove them impossible for arbitrary fonts.
- "≈2 decades below the shallowest consumer comparison" is a weaker statement
  than the old "≈5": with the band eliminated, the worst complement point
  sits nearer the consumer floor than it used to, because it is now a
  *different, far smaller* deviation (4.75e-9 vs 1.689e-4). The figure says
  exactly what the receipt measures; no interpretive claim is added.
- Figure only renders an already-pinned receipt; no new numeric claim is
  made here. Zero trajectories, no gate, ladder stays PAUSED, stdlib-only,
  no RNG, no network.
