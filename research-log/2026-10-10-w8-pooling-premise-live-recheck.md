# W8 pooling-premise live recheck and escalation consumption (2026-10-10 tick)

**Scope:** in-silico collection-day bookkeeping + design reading. No wet-lab,
no submission, no new datum. Unreviewed working notes; the only verdict
surfaces remain the frozen collector and atlas.

## Live rechecks (done fresh this tick)

- Queue request `d158d5fbfb988dd4bd1c09450e07dbe34114419b29b7d2cd9f274ff1e4a94977`
  (job `hxq-d158d5fbfb988dd4`, the arm-5 arb5 instrument) was **probed live:
  Complete, succeeded=1**, exit 0, image verified. The earlier waiter chain
  (`ed50c7ba…` hazardhold → admitted+collected tick 96; `d158d5fb…` arb5 →
  admitted+collected tick 98) is fully drained. No live queue waiter and no
  uncollected result is outstanding this lane this tick.
- CI admission-floor escalation pre-staged on the blocked loop card (the
  "escalate the queue admission floor to Platform Engineering as
  resource-capacity — never a duplicate resubmit" criterion) is therefore
  **consumed**: the floor cleared on 2026-10-09 (both waiters admitted and
  ran), so no escalation issue is needed and the blocked card was closed as
  superseded with this file as pointer.

## Premise status (design reading, not a datum)

- Arm-5 arbitration (tick 98, `research-log/2026-10-09-w8-arb5-arbitration.md`)
  resolved POOLING_CONTESTED **in favour of (S)**: ARM4_SMALLN branch; P3
  0.60568 vs arm-3 rate, P4 0.022641 vs arm-4 rate, alpha .05; three-arm
  dispersion receipt POOLING_SUPPORTED, min_exact_p 1.385823e-1.
- Consequence now live: the iid-pooling premise that the tick-97 receipt
  contested is **restored at arm level**, so the pooled line datum (481/653,
  Wilson-95 [0.70150, 0.76893]) is claimable as one binomial census, and the
  ladder may resume mechanically.
- Frozen-policy reading for the pooled datum (rerun this tick from the
  committed tool, stdlib, no datum authority claimed): `policy(481, 653)` =
  grow, k_line_prac **1524**, R3 window **[1123, 1162]**, total arms 4 (2
  additional arms x 2400 s; serial wall 1.3333 h). The pool datum sits BELOW
  the [489, 491] stage-1 line window, so the frozen reading is grow-or-stage-2,
  never a verdict; if ambiguity survives growth, stage-3 says stop and
  receipt — no automatic stage 4.

## Named next action (for the next tick, pre-register before submitting)

Execute the resumed ladder: grow toward the k_line=1524 attribution target
with the reserved stride-block arm(s), first arm **arm-6 = seeds
340261107 + [0,153)** (never run), same instrument verbatim (BUILD1
Vp-missing, WIN_MULT=8, CAL identity gate). Pre-register the dispersion gate
(POOLING_CONTINUES / POOLING_CONTESTED at the new pool size) before
submission; if the pre-registration fits the 30-minute tick budget, smoke and
submit in the same tick through the capped queue (one running job per owner;
2 additional arms x 2400 s fits the queue envelope). No duplicate-resubmit
path and no sleeping workers.
