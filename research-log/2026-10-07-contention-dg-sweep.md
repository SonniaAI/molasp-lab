# 2026-10-07 — Contention dG / read-window sweep (tick 43, SON-4813)

**Question** (tick-42 queue): the minted contention set was priced at a
single operating point (dG 0.5, family fill 0.908 vs s2 0.406, five
frozen contenders).  *When does first-come contention stop matter?*

**Design.**  BUILD1 Vp-missing (protocol of record: Gmc 9.5,
gse = Gmc − dG, T_read = mult·400·e^Gmc, canonical map kept from the
full build), family vs s2 lock-read arithmetic, dG ∈ {0.5, 2, 4, 7},
plus 4×-read-window arms at dG 4 (s2 + family control).  n = 500/arm,
fresh seed base 200261107 (grepped disjoint from all seven prior
bases).  Pre-registered gates DW1–DW7 fixed at commit `236f91b`
before submission; queue job `hxq-05864a1974ee155e` (paperclip-test,
1 core / 1 GiB, exit 0, admitted 14:06:35Z, collected in the same
tick).  Raw records + verdicts: `../evidence/2026-10-07-contention-dg-sweep/`.

**Verdicts: DW1–DW5, DW7 CONFIRMED; DW6 FALSIFIED** (the
falsification is the headline).

| arm | fill | frozen nonfill | persist | dwell | partial | terminal occupants (2,2) |
|-----|------|----------------|---------|-------|---------|--------------------------|
| fam dG .5 | 0.904 | 0.094 | 0.542 | 0.994 | 0.992 | D2T 452, L2 32, S2 12 |
| s2  dG .5 | 0.412 | 0.588 | 0.872 | 0.996 | 0.984 | D2T 206, L2 149, DBr 82, L3 50 |
| fam dG 2  | 0.970 | 0.018 | 0.088 | 0.980 | 0.987 | D2T 485 |
| s2  dG 2  | 0.464 | 0.534 | 0.520 | 0.993 | 0.990 | D2T 232, L2 229 |
| fam dG 4  | **0.074** | 0.000 | 0.000 | 0.113 | 0.633 | None 437, D2T 47 |
| s2  dG 4  | 0.564 | 0.430 | 0.288 | 0.967 | 0.844 | D2T 282, L2 215 |
| s2  dG 7  | 0.000 | 0.000 | 0.000 (n=1) | ~0 | 0.001 | None 500 |
| s2  dG 4, win 4× | 0.798 | 0.198 | 0.062 | 0.988 | 0.924 | D2T 399, L2 99 |
| fam dG 4, win 4× | 0.054 | 0.002 | 0.000 | 0.112 | 0.633 | None 453 |

(fill = stable-b≥2 D2T at the (2,2) vacancy at read end; persist =
first stable occupant survives to read end; dwell = site occupied
fraction; partial = canonical-site occupancy fraction.)

**Findings.**

1. **Three regimes on the dG axis** (DW2/DW3/DW4 confirmed;
   churn ratio s2 dG4/dG0.5 ≈ 21.8×):
   - *Frozen (dG 0.5):* first-come is destiny — s2 persistence 0.872,
     site dwell 0.996, the minted lottery decided once (calibration
     DW1 replicates tick 42 cross-seed: 0.904/0.412 vs 0.908/0.406).
   - *Marginal (dG 2):* persistence halves (0.520) but the re-roll
     is a near-fair coin — D2T 232 vs L2 229; fill only 0.464.  The
     lottery survives as a stationary split.
   - *Churn (dG 4):* re-rolls accumulate and the split favors the
     fill — 0.564, and the 4× window pushes it to 0.798 (DW5:
     +0.234 ≥ 0.10; window gain is real, not noise — the n=8 smoke
     direction was noise and the gate was left untouched).
   - *Starvation (dG 7):* everything dies (fill 0, partial 0.0008;
     DW7 confirmed; tick-15/22 dG-7 walls echo).
2. **DW6 FALSIFIED — the family channel is not dG-robust.**  fam dG 4
   fill 0.074 (gate ≥ 0.70): the vacancy is empty 89 % of the time
   (dwell 0.113), the site flaps ~2040 times per read, and the
   assembly stalls at partial 0.633.  Mechanism: b=1 nucleation
   intermediates cannot survive to their stabilizing partner at
   gse 5.5; the 4× window does not rescue it (0.054, churn 8211) —
   a window cannot fix a nucleation barrier.  The tick-42 trade
   table's family row was a low-dG number; **the trade table needs
   a dG axis.**
3. **The s2 knob's sign flips with dG** (principle #7 candidate):
   at dG 0.5 s2 *hurts* the fill (0.904 → 0.412: mints frozen
   contenders); at dG 4 s2 is the *only* channel that carries growth
   (0.074 → 0.564; win4 0.054 vs 0.798) — the doubled lock-read lets
   attachments stick at effective b=2 on arrival, lifting dwell
   0.113 → 0.967 and partial 0.633 → 0.844/0.924.  Reinforcement
   pricing is regime-dependent: the same knob that freezes a fair
   lottery also bridges the churn regime the bare family channel
   cannot cross.

**Honest boundaries.**
- DW2's margin is a knife-edge: gain 0.152 against a ≥ 0.15 gate
  (disclosed, not re-registered).
- The dG-2 stationary split was not window-tested (win arms sit at
  dG 4 only).
- persist at s2 dG 7 rests on a single event (persist_n = 1).
- fill counts stable-b≥2 D2T occupancy; decode/strict_filled is not
  defined for a missing-species build (partial is the reported
  completion proxy).
- L3 appears at the vacancy terminal class (50/500, s2 dG 0.5) —
  outside tick-42's five-name census list; recorded as measured, not
  forced into the prior taxonomy.

**Instrument notes.**  Two pre-registration fixes caught at smoke
(n=8), zero post-hoc: (1) first-stable detection must check
stability on *every* event, not only occupancy changes — tiles that
attach at b=1 and stabilize in place when a neighbor arrives are the
dominant low-dG path (change-only version undercounted persist_n
3/8 with 8/8 stable terminals); (2) dwell renamed site_dwell (any
occupant) for honest naming.  Smoke verdicts (DW1/DW5 "falsified" at
n=8) were binomial noise; gates were left verbatim and the n=500 run
confirmed both — the discipline of not rewriting gates after smoke
earned its keep.

**Receipts.**  `../evidence/2026-10-07-contention-dg-sweep/`:
`contention_dg.out` (9 arm records + verdicts), `queue-receipt.json`
(job, request id, archive head `236f91b`, exit 0), pre-registration
in the git history at `236f91b`.  Pins: `tests/test_contention_dg.py`.
