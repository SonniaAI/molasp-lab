# w8 decision atlas — the joint collection-day reading surface

Date: 2026-10-09 (tick 89, wake 02:09Z) · SON-4885 · run 77b77e62 ·
waiter ed50c7ba…4daa85 still queued at the 02:12Z probe (ci admission
floor, reason verbatim in the record) — this is the fourth
pre-datum piece, landed BEFORE the datum exists.

## What this is

`tools/w8_decision_atlas.py` — one command that turns the eventual
datum (fresh-arm pair census x of k) into the full pre-registered
reading by composing the three uncertainty axes ticks 86-88 committed
before the datum:

1. **form axis (tick 86)** — the five-region reading map (region
   bounds receipt-quoted; identity-pinned to
   `w8_sensitivity.compute()["reading_map"]["region_bounds_computed"]`);
2. **fit axis (tick 87)** — per-branch framing lines: HELD quotes the
   initial-condition bracket (w1 census Wilson-95 induces w8 width
   0.02481, entirely inside HELD; no ±0.04 odds probe reaches
   refutation); REFUTED-low indicts the late-L2 leak rate
   (haz_l2[4] ×0.5→×2 spans 0.12956, crossing the floor between ×0.5
   and ×0.75); REFUTED-high reads unmodeled acceleration;
3. **datum-noise axis (tick 88)** — the datum's Wilson-95, the
   attribution overlay, and the k=500 quiet core (receipt-quoted
   [0.81743, 0.85263], membership reported at k=500 only).

The frozen gate is untouched: the VERDICT is Fraction-exact on the
decimal edge strings (HELD iff 0.78376 ≤ x/k ≤ 0.88376), constants
duplicated from receipts on purpose (the reading surface must not
import the instrument under test; `collect_w8.py` remains the
collector), and every duplicated constant is pinned back to the
tick-86/88 modules in `tests/test_w8_decision_atlas.py` (13 pins).
Below the MIN_EVENTS floor (k<50) the atlas refuses to read
(NO_EVENTS), matching the frozen gate's refusal.

## Measured headlines (pure arithmetic, no datum input)

- **The attribution window at the protocol census is razor-thin.**
  `attribution_windows(500)`: the tick-88 overlay rule (indictment
  prose only if the datum's Wilson-95 lies entirely inside the
  attributed region) is satisfiable at k=500 only in region 2
  (hold-only), and only for **x ∈ {425, 426, 427}** (ŝ ∈
  [0.850, 0.854]). Regions 1 and 3 are attribution-empty at every
  census tested (k=50…500): no integer datum's Wilson-95 fits inside
  the overlap [0.78376, 0.81415] (width 0.03039 < the interval width)
  or strictly inside [0.71415, 0.78376).
- **Even the exact-center datum cannot claim form attribution.**
  417/500 = 0.83400: HELD, quiet-core, region 2 — but its Wilson-95
  [0.79886, 0.86404] dips below 0.81415, so the honest reading is
  "region-ambiguous at census k=500". Pinned as
  `test_center_datum_is_region_ambiguous_k500`.
- Consequence for collection-day prose (pre-registered here, not a
  gate): expect "region-ambiguous" to be the normal attribution
  reading at k=500; a claimable hold-only attribution is the ~3-in-500
  exception, not the rule. The VERDICT and the tick-87 fit framing
  are unaffected by this narrowness.

## Discipline and near-miss

- The verdict comparison is Fraction-exact; the overlay compares
  5-dp-rounded Wilson endpoints (prose discipline, documented
  in-file) — the asymmetry is deliberate and stated.
- No new science numbers: every constant is a committed receipt
  (tick 86 region bounds, tick 87 brackets, tick 88 quiet core and
  Wilson anchors). The only new quantities are compositions
  (attribution windows over the census grid).
- Suite verbatim on the exact CI command:
  `Ran 567 tests in 3.106s / OK (skipped=1)` (= 554 + 13), all 13
  new test names present in verbose discovery.

## Chain of custody

Deterministic pure-python arithmetic; identical inputs give
byte-identical output. No datum input exists yet. The frozen W8
gate, the five-step collection chain (import → collect → apply →
prose), and the pre-staged 02:50Z escalation artifact (tick 85,
`2026-10-09-w8-waiter-escalation-prep.md`) are all untouched.
