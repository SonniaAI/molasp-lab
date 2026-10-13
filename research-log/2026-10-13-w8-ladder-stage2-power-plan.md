# 2026-10-13 w8 ladder stage-2 conditional power plan — pre-registered BEFORE posfresh collection

SON-5148 · run c92509f3 · written while the posfresh probe (request
`bda50c6bf65bb5433500dc7c855593c39727eb0376154b985c5efb386f9a1d66`) is
still QUEUED on the admission floor. No posfresh datum exists at this
commit. This note exists so that the collection-day ladder design is
frozen BEFORE the adjudicating datum arrives — both branches are named
now, and neither may be re-cut after the fact.

This executes the two named-next-action clauses of the frozen
interpretation map in `research-log/2026-10-13-w8-posfresh-prereg.md`:

- POSITION_DECLINE_DETECTED → "the ladder redesign (position-stratified
  q0) becomes the next named action" → **Branch B below**.
- POSITION_DECLINE_NOT_DETECTED → "the ladder stage-2 decisive census
  power plan (tick-92 policy tool) or closure of the dispute by boundary
  note" → **Branch A below**.
- VOID / NO_EVENTS → NEITHER branch activates: instrument diagnosis only
  (frozen map governs); this plan waits.

## Standing state this plan inherits (corrected record, b7623fd)

- The 4-arm pool reads 1235/1652 REPORTED-NOT-CLAIMABLE (tick-110
  discovered tick-99 had already burned arm-6 [0,500) and arm-7 [0,500);
  the tick-110 pooled claim was withdrawn). Pooling is CONTESTED; the
  ladder is PAUSED. `policy(481, 653)` on the pre-contestation datum =
  grow, k_line_prac **1524**, R3 window **[1123, 1162]**, 2 additional
  arms × 2400 s (tick-102 recheck) — that reading is the mechanical
  resume point for Branch A only, rerun on the corrected pool datum.
- q0 = 1110/1499 = 0.7404937 is pos-1-weighted (tick-112 flag; tick-115
  sensitivity: decline-scenario family rates 0.6785–0.7060 sit below the
  pool's Wilson floor [0.7177, 0.7621]; one-sided-low gates false-flag
  34–99% under decline; decisive-census power shift ≤ 0.048 =
  0.7377 − 0.6901, second-order).

## Branch A — POSITION_DECLINE_NOT_DETECTED (window-noise stands)

Account arbitrated: **window-iid at a common family rate**; the ladder's
iid-pooling premise is reinforced (not proven) with the standing q0
pos-1 caveat.

Design, in order, all under the frozen tick-92 policy tool:

1. Rerun `policy(x, k)` on the CORRECTED pool datum; pre-register the
   dispersion gate (POOLING_CONTINUES / POOLING_CONTESTED at the new
   pool size) before any submission. POOLING_CONTESTED at the corrected
   state routes to dispersion receipt + escalation (stage-3 analogue),
   never blind growth.
2. On CONTINUES: resume growth toward the k_line_prac **1524**
   attribution target (R3 window **[1123, 1162]**), reserved-stride
   arms, same instrument verbatim, queue envelope 2 arms × 2400 s.
3. If region-ambiguity survives growth: ONE stage-2 decisive census at
   k80 (smallest k whose attribution probability under phat ≥ 0.80, tick-92
   rule). This is the decisive instrument Branch A names.
4. Stage-3 verbatim: ambiguity after stage 2 is EVIDENCE AGAINST iid
   pooling → stop growing, receipt per-arm dispersion, escalate with the
   recommended path. Never an automatic stage 4.

q0 convention (tick-115 standing rule, binding here): every one-sided-low
gate uses the dual-null band **[q0 − Δ(1−w), q0]** with Δ =
SHARE_FIRST − SHARE_REST = 0.068916 and w named from the actual family
(w = first-window share of the family's windows). Two-sided consistency
checks keep bare q0 with the caveat line.

Power statement: the stage-2 census is decisive by construction
(attribution probability ≥ 0.80 under phat); under the hypothetical
decline scenarios the same census loses at most 0.048 power
(0.7377 → 0.6901 across the tick-115 table), which is why Branch A may
keep q0 as null with the disclosed band rather than redesign.

## Branch B — POSITION_DECLINE_DETECTED (position structure in virgin blocks)

Account arbitrated: **position structure**; window-iid is rejected at the
posfresh resolution. Pooled q0 is RETIRED as a family constant; it is
replaced by the ordered pair (q_early, q_late) from position-tagged
windows.

Design:

1. Strata = position bands, tagged exactly as posfresh tags them
   (early [0,1000) / late [9000,10000) per block). Stratum rates are
   estimated per stratum; no unweighted pooling across strata anywhere
   in the ladder (this is the redesign the frozen map names).
2. The attribution target becomes stratum-specific: rerun the tick-91/92
   planner per stratum; k_line and k80 are computed against the
   stratum phat, not the retired pool.
3. Power for the stratified contrast: at the frozen two-proportion
   arithmetic (one-sided α = 0.05), n = 2000/group gives MDE ≈ 0.040 and
   power ≈ 0.70 at Δ = 0.030; if the measured posfresh delta is smaller
   than 0.040, scale per-group n by (0.040/Δ_meas)² BEFORE submission —
   and re-run the seed scan for every new window (never claim "unburned"
   without the literal scan; ticks 113's double catch is the standing
   proof this rule earns its keep).
4. The dispersion gate is re-derived under stratification: contested
   pooling within a stratum routes to receipt + escalation, same as
   Branch A step 1.

## What this plan does NOT do

- It does not resume the ladder; the pause stands until posfresh
  adjudicates (this note only pre-registers the post-adjudication
  design).
- It does not touch the frozen posfresh branch map, its instrument, or
  its seeds; the queued job owns those.
- It makes no claim about the eight observed windows beyond the
  committed receipts; no blog (not a milestone); no wet-lab; no external
  contact; no paper/preprint activity.

## Receipts

- Branch conditions and both named designs pinned in
  `tests/test_w8_ladder_stage2_plan.py` (doc literals + band arithmetic
  recomputed from `tools/w8_q0_sensitivity.py` constants).
- Policy semantics imported from `tools/w8_census_policy.py` (tick-92,
  unchanged); q0 band constants from `tools/w8_q0_sensitivity.py`
  (tick-115, unchanged).
