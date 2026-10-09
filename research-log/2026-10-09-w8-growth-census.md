# W8 stage-1 growth census — pre-registered before submission

Date: anchored to the pre-registration commit (see git log, tick 97) ·
SON-4917 · run 258ba97c

## What this is

The first growth step of the pre-registered tick-92 census policy,
executed mechanically on the tick-96 datum:

- datum (arm 3, w8 terminal census): x1 = 375, k1 = 500, p̂ = 0.75,
  Wilson-95 [0.71024, 0.78595] — region-ambiguous (crosses the R3
  edges), so the ladder says GROW.
- `tools/w8_census_policy.policy(375, 500)` live receipt (this tick,
  before the harness was written):

```
line k=653 (theoretical opening k=597), x_line=490, region R3
practical window at line k: [489, 491]
cost: 1 additional arm(s) x 2400 s, one running job per owner; pooled census 2 arms total
attribution probability AT the line census: 0.108
P>=0.50 at k=1049 (3 arm(s), wall 2.00 h)
P>=0.80 (stage-2 decisive census) at k=1612 (4 arm(s), wall 2.67 h)
```

- arm semantics (planner `arms_for_k`): arms are 500-terminal budget
  blocks; the line census lands at pooled k = 653 = the datum's 500 +
  **153 new terminals**, one additional 2400 s arm-budget.

## Instrument

`evidence/2026-10-09-w8-growth/ktam_w8_growth.py` — VERBATIM copy of
`evidence/2026-10-08-w8-hazardhold/ktam_w8_hazardhold.py` (the
tick-77/96 job `ed50c7ba…4daa85`, run.out sha256 `cea9d335…`):
`matched_s2`, `run_traj`, `mid_class`, `census`, `wilson` are
byte-identical (diff-verified this tick); the CAL identity arm is
UNCHANGED (seeds 260261107+[0,500), gate: mid-window pair census
EXACTLY D2T 367 : L2 131 — else CAL_FAIL and the census is VOID).

The only changes:

- GROWTH arm seeds = **arm 4 of the reserved stride block**,
  `220261107 + 4·2e7 = 300261107`, named as the growth arm in the
  tick-96 collection note; never run before this job.
- GROWTH arm size n = 153 (lands pooled k exactly at 653).
- Machine verdicts carry NO science reading: `{"CAL": …, "GROWTH":
  COUNTED|NO_EVENTS|VOID}`. The tick-74 HELD/REFUTED falsifier is
  closed (REFUTED, tick 96); this is a census.

## Collection-day reading (frozen, mechanical)

1. import run.out (`tools/import_queue_result.py`),
2. CAL gate must be CAL_OK (else everything VOID),
3. dispersion receipt FIRST: `tools/w8_dispersion_receipt.py` on arms
   [(375, 500), (x4, 153)] — POOLING_CONTESTED stops pooling,
4. pooled ladder reading: `tools/w8_census_policy.policy(375+x4, 653)`
   — verdict-ready / grow / stage-2 per the pre-registered ladder,
   never re-derived by hand.

Receipt-side expectations under p̂ = 0.75 (not gates): E[x4] = 114.75;
the line window [489, 491] ⇔ x4 ∈ {114, 115, 116};
P(Bin(653, 0.75) ∈ window) = 0.108 — an out-of-window datum is the
ladder's business, not protocol failure.

## Submission record

- archive: repo-mirroring layout (harness + `tiles_and.py` +
  `tiles_death.py` + `molasp/{__init__,offchannel,compiler}.py`),
  clean-extraction SMOKE exit 0 (n=8/arm, CAL_OK, GROWTH NO_EVENTS at
  the 50-event floor — expected at smoke scale).
- command: `python3 source/evidence/2026-10-09-w8-growth/ktam_w8_growth.py`
  (grep-compared against the tick-77/96 successful request record).
- nonce: `molasp-w8-growth-t97`; alias paperclip-test, 1 cpu, 1 GiB,
  wall 2400 s. Request id: recorded on the card comment and in the
  collection receipt (`queue-receipt.json`, `collected: null` house
  style).

## Boundaries

- No HELD/REFUTED reading exists for this datum until the ladder
  attributes (possibly after stage-2 at k=1612); by pre-registration
  an ambiguous line datum grows, it does not interpret.
- Stage-3 ambiguity indicts iid pooling and stops growth (tick-92).

## Collection (same tick, 2026-10-09)

- Job hxq-341c27b37fe0e6e5, request 341c27b3…c54 (nonce molasp-w8-growth-t97):
  submitted 09:24:15Z, admitted+ran immediately, finished 09:24:39Z (24 s),
  exit 0; run.out sha256 4816e509… (manifest
  evidence/2026-10-09-w8-growth/run.out.import.json).
- **CAL_OK** — mid-window census over the CAL arm EXACTLY D2T 367 : L2 131.
  Instrument identity chain intact: DW9 (tick 63) -> VH (tick 70) -> w8
  (tick 96) -> this job.
- Growth arm (arm 4, seeds 300261107+[0,153)): terminal pair census
  **x4 = 106 D2T : 47 L2**, other 0; share 0.6928, Wilson-95
  [0.61573, 0.76044].
- **Dispersion receipt (BEFORE any pooling claim, as pre-registered):
  POOLING_CONTESTED** — arms 375:500 vs 106:153, min_exact_p 5.6667e-3
  < 0.05 (arm-3 leave-one-out test; arm-4's own p 0.112). The frozen rule
  fires: the pooled line census (481/653, Wilson-95 [0.70150, 0.76893])
  is REPORTED but NOT claimable as one binomial census, and the ladder's
  next instruction (policy(481,653): grow to k=1524, R3 window
  [1123,1162], 2 more arms) is NOT auto-executed — its premise (iid
  pooling) is exactly what the receipt contested. Stage-3 discipline:
  stop growing, receipt dispersion, escalate with recommended path.
- **Finding (first-order)**: per-arm overdispersion evidence in the w8
  terminal share across independent reserved stride blocks under one
  CAL-verified protocol — arm-3 0.750 (n=500) vs arm-4 0.6928 (n=153)
  differ beyond binomial noise (two-sided exact p 5.7e-3; ~1-in-176
  under iid). Descriptive only: arm-4's interval upper edge 0.76044
  sits just below the tick-86 trend-arm point 0.76415; no atlas read —
  the atlas reads pooled censuses and pooling is contested.
- Honest scope: with two arms this is one test, not a many-arm
  indictment — but the gate was frozen and pre-registered; it is
  honored, not reinterpreted after seeing the datum.
- Consequence flagged for prior receipts: the DW9/VH cross-seed
  stability statements (CC3 0.716 vs 0.7379 within 0.021; VH3 fresh
  dev ~1.26 SE) assumed exchangeable fresh arms; real overdispersion
  would widen them. No prior verdict overturned (those were w4-level
  shares; this is w8-level).
- **Next avenue (pre-register before running)**: overdispersion
  arbitration that needs no pooled attribution — RECOMMENDED (a) arm-5
  census (seeds 320261107+[0,500), reserved block arm 5) with PAIRWISE
  exact tests vs arms 3 and 4 (a third arm that sides with either, or
  splits, decides fluke vs real); alternative (b) beta-binomial refit
  across the three arms. Same instrument verbatim, n=500, one arm.
