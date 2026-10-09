# w8 collection-day census policy — the mechanical growth ladder, pre-registered before the datum

**Date:** 2026-10-09 (tick 92, run `f3f39125`)
**Tool:** `tools/w8_census_policy.py` + 19 pins (`tests/test_w8_census_policy.py`)
**Trigger:** tick 91 priced the per-region census openings but left the
collection-day decision qualitative — given the first arm's actual
census, "how many more arms NOW?" had no fixed answer. This note fixes
the ladder mechanically, pre-datum, so the first arm's collection
triggers an automatic next submission with no judgment call in the gap.

## The stage ladder (fixed before any datum exists)

- **stage 0:** the already-queued first arm (`ed50c7ba…4daa85`,
  k1 ≤ 500 fresh-arm terminals).
- **stage 1:** Wilson-95 interval of the first census. If it lies inside
  a single tick-86 s-region → **VERDICT-READY** (the atlas reads it; no
  growth census). Otherwise grow to **k_line**: the smallest pooled
  census k whose ≥3-count practical aim window contains the
  point-estimate line x = round(p̂·k), ties away from zero
  (p̂ = x1/k1, the MLE).
- **stage 2:** only if the grown census is STILL region-ambiguous →
  ONE final census at **k80**: the smallest k whose attribution
  probability under p̂ is ≥ 0.80.
- **stage 3:** ambiguity after stage 2 is EVIDENCE AGAINST the iid
  pooling assumption (tick-91 assumption 1) → stop growing, receipt
  per-arm dispersion, escalate WITH the recommended path per the
  loop-card rule. Never an automatic stage 4.
  An edge-pointing first datum (p̂ within ~0.012 of 0.81415 etc.) hits
  the same terminal bucket directly: no k ≤ 6000 puts a practical line
  window at such a p̂, and the report carries an outside-cap
  extrapolation k_ext ≈ z²·p̂(1−p̂)/d² (d = nearest-edge distance) so
  the escalation names a size, not a bare stop.

## Measured receipts (canonical first-arm cases, k1 = 500)

| first datum | reading | policy |
|---|---|---|
| 417/500 (tick-88/89 expected collection-day datum) | region-ambiguous [0.79886, 0.86404] | grow: line k=1442 (x=1203, R2 window [1203,1250]) — **3 pooled arms = 2 additional, 1.33 h growth wall** |
| 426/500 | VERDICT-READY R2 (tick-89 razor window) | no growth |
| 400/500 (p̂=0.80 in R1) | ambiguous | grow toward R1 |
| 407/500 (edge-pointing, p̂=0.81400) | **stage-3** | no k ≤ 6000; outside-cap extrapolation **k ≈ 25,849,433** (edge distance 0.00015) |
| 100 / 337 / 456 / 470; 0; 500 | VERDICT-READY R4/R5 | no growth |

**Ladder pricing under p̂ = 0.834** (the datum the tick-88/89 atlas
expects): attribution probability AT the line census k=1442 is
**0.507 → expected collection days ≈ 2.0** — one grown census is a
coin-flip, and the note pre-registers that expectation so an ambiguous
second datum is not misread as protocol failure. P ≥ 0.50 opens already
at k=1419; the **stage-2 decisive census (P ≥ 0.80) is k=2895 = 6 arms
= 4.0 h serial** — adjacent to tick-91's practical R1/R2 boundary
numbers but a different quantity: P(attribution) under the MLE
hypothesis, not a guaranteed aim window.

**Continuity with tick 91:** the p0-line (truth = hold-last identity
0.83376) first attributes at k=1476 (x=1231); the policy's p̂=0.834
line opens at k=1442 — the same 3 pooled arms; the k difference is
pure p̂-vs-p0 rounding. Window identity against the planner is pinned
at 11 (region, k) cells including all four tick-91 receipts; the
binary-search window finder matches the planner's linear scan exactly.

## Assumptions (pre-registered, falsifiable at collection)

1. **Point-estimate discipline:** the ladder is priced under p = p̂
   (MLE), not a posterior integration. If the grown datum lands outside
   the p̂-priced window, the stage-2/3 rules engage — the policy is not
   re-fitted after seeing the datum.
2. **iid pooling** (tick-91 assumption 1, carried): per-arm dispersion
   must be receipted before pooling; stage-3 ambiguity voids the arm
   math, not the frozen gates.
3. **Zero verdict authority:** the policy prices growth only;
   `tools/collect_w8.py` and `tools/w8_decision_atlas.py` remain the
   only collection-day readers.
4. The thresholds (0.50 planning floor / 0.80 decisive) are planning
   conventions fixed now, before the datum.

## Operational state (03:41Z, this tick)

- Waiter `ed50c7ba…4daa85` re-probed ~03:24Z: **still queued** (ci
  admission floor; reason verbatim in the record; command re-verified).
  Age ~4.3 h. No resubmit.
- **SON-4895** (Platform Engineering, high, child of this card) still
  `todo`, no PE response at ~15 min old — too early to re-request; the
  next tick owns the follow-up (one plain re-request with cost, never a
  duplicate escalation).
- Hosted CI on `66060f9`: checks success 03:19Z. Observed: an **AC3
  runner probe (SON-4889)** ran workflow_dispatch success 03:24:40Z —
  movement on the escalation's second path (no conclusion drawn).
- Binding constraint unchanged: every arm count above assumes queue
  admission capacity on spark-4a06.
