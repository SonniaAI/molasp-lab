# designs/007 — via-site lock placement kinetics under s2 (the census's solo class)

## Why

Tick 39's census (designs/006, receipt
`evidence/2026-10-07-lock-misplacement-census/lock_misplacement_census.out`)
split the lock-misplacement hazard into two layers:

- the KINETIC-DOMINANT lock-site misplacements (L2@(3,3), L3@(3,2) in
  the tick-38 MC) carry ZERO solo bond — one-substitution-enabled,
  already caught by the pair layer `lock_misreads`;
- the SOLO class the new layer surfaced is VIA-SITE lock placements:
  `L1@(2,1)` and `L2@(2,2)`, W-read carried (`w_read` true), bond 1
  at family arithmetic → bond 2 under the tick-38 s2 rule. Present in
  BOTH BUILD1 and UNIT_ONLY census views (constructional), never
  tabulated kinetically — the tick-38 MC counted lock sites only.

The census prediction is arithmetic, not rate: b=1 transient at family
strength, b=2 (frozen) under s2. This study measures it.

## The race mechanism (prediction, fixed in advance)

At a via site the canonical via tile is stable once placed (b>=2 via
its own bonds at family strength). A lock tile arriving there is b=1
at family strength — it detaches, the canonical occupant wins a
lopsided race. Under s2 the lock's W read doubles: BOTH competitors
are frozen, the race becomes effectively first-come. So the s2
via-lock terminal fraction is the flip probability of a coin the
family encoding never tosses — the kinetic echo of tick-12's
fair-coin collapse and tick-38's migration finding (strength at fixed
identity is symmetric amplification).

## What lands

`evidence/2026-10-07-viasite-lock-ktam/ktam_viasite_lock.py` — the
tick-38 protocol of record (Gmc=9.5, Gse=Gmc-dG, T_read=400*e^Gmc,
no-mismatch kTAM, per-run RNG, `matched_s2` bond rule verbatim), with
VIA-SITE instrumentation: per-trajectory terminal occupancy, terminal
matched-b, attach-event counts, and dwell of `L*` tiles at every
canonical via site (column x=2). Strict completion is refined to
FULL canonical occupancy (`strict_filled`: every canonical site holds
its canonical tile) — the looser decode-only check would misread a
frozen via-lock as completion; both numbers are reported, no gate
depends on the old one. Arms: fam_b1, s2_b1, s2_b1_dG2, fam_unit,
s2_unit; n=500 each. Fresh seed base 180261107 stride 2e7 (disjoint
from 160261107/20261107/40261107/80261107/100261107/120261107).

## Pre-registered gates (V1–V6; falsifiers fixed before submission)

- **V1 EXISTENCE**: s2_b1 stable via-lock terminal fraction (L* at a
  via site at terminal with matched b>=2) >= 0.05 AND >= fam_b1's +
  0.02 — the census's b=1→b=2 flip is kinetic reality.
  [falsified: s2_b1 < 0.05 OR s2_b1 <= fam_b1 + 0.02]
- **V2 TRANSIENCY SPLIT**: fam_b1 mean via-lock dwell fraction
  (dwell of L* at via sites / read window, over trajectories with any
  via-lock attach) <= 0.15 AND s2_b1's >= 0.8 (frozen).
  [falsified: fam >= 0.5 OR s2 <= 0.5; no attach events → NO_EVENTS]
- **V3 COMPLETION COST**: among s2_b1 terminals that are not
  strict_filled, the via-lock-carrying fraction >= 0.10 — the channel
  is a real completion hazard, not decoration.
  [falsified: <= 0.02; n_nonstrict < 10 → NO_EVENTS]
- **V4 CALIBRATION**: fam_b1 lock-site blocked within 0.05 of 0.308
  AND s2_b1 within 0.05 of 0.314 (tick-38 receipt values, same
  instrument). [>= 0.10 off either → FALSIFIED: protocol drift]
- **V5 dG DIRECTION**: s2 via-lock stable terminal fraction at dG 2
  < at dG 0.5. [>= → FALSIFIED]
- **V6 GENERALITY**: s2_unit stable via-lock fraction >= 0.05.
  [< 0.02 FALSIFIED; 0.02–0.05 INCONCLUSIVE]

## Honest boundaries, fixed in advance

- Via sites are the canonical column-x=2 sites of BUILD1/UNIT_ONLY
  only; other off-channel lock placements (row 3+ columns) are
  census-recorded but not instrumented here.
- The vacancy-background channel (L3@(3,2) 82/500, Vp-missing arm)
  remains outside: no missing-species arm in this study.
- n=500/arm gives binomial CI ~±0.04 at p=0.3; gates with 0.02
  margins are read as stated, INCONCLUSIVE band honored.

## Evaluated (tick-40 collection, c286cb6 pre-registration)

Job hxq-380801377b9433e5 (nonce viasite-v2, exit 0; viasite-v1
exit-2'd on the /work-vs-/work/source path mistake, envelope kept).
Verdicts: **V1/V3/V5/V6 CONFIRMED, V2/V4 INCONCLUSIVE** (both inside
their pre-registered bands, neither falsified).

- **V1** — the flip is real and large: stable via-lock terminals
  0.416 (s2_b1) / 0.448 (s2_unit) vs 0.082 / 0.086 family.
- **V2** — mechanism confirmed at falsifier level (fam dwell 0.18,
  attach 3425 events = many-transient; s2 dwell 0.96, 526 events =
  rare-frozen), but fam dwell beat the 0.15 confirmed-band (events
  accumulate ~6.9/traj) → INCONCLUSIVE as registered.
- **V3** — 208/480 = 43% of not-strict_filled s2_b1 terminals carry
  a stable via-lock: the leading completion hazard under s2.
- **V4** — fam blocked 0.240 vs ref 0.308 (0.068 off, fresh seeds);
  decode-only strict 0.614 vs 0.568 consistent → INCONCLUSIVE, not
  protocol drift.
- **V5** — 0.326 at dG 2 < 0.416 at dG 0.5 (starvation direction).
- **V6** — 0.448 on UNIT_ONLY: corpus-general, matching the census.

Reading: reinforcement converts the via-site race from lopsided
(canonical occupant wins) to first-come (both frozen) — the coin
flip the family encoding never tosses. Combined with tick-38's
migration finding, the lever family is now bounded twice over:
reinforcement moves hazard between classes AND mints new frozen
squatters from the transient background. d4 consequence: the
lock_misplacements transient layer (tick 39) is the right warning
surface — its w_read channels are exactly what freezes under any
future read-reinforcement knob.

### Evaluated addendum (tick 41, SON-4808): the vacancy background measured

The Vp-missing s2 arm's fill starvation (tick 38: 0.904 -> 0.412) is
not a single-channel effect. Pre-registered probe VB1–VB5
(evidence/2026-10-07-vacancy-background/, job hxq-d1a6980228f8b409):

- VB2 CONFIRMED, 78/78: every terminal L3@(3,2) rides the W ->
  DBr@(2,2) read — the static pair layer's one-substitution claim,
  now kinetic.
- VB3 INCONCLUSIVE with the residual as the finding: fill survives
  at 0.481 even with NO terminal L3, because the misplaced
  CANONICAL lock L2 squats the via site (2,2) itself (150/500,
  this design's solo class under s2). The vacancy background is a
  three-way contention: classic fill vs L2 via-site squatter vs
  DBr->L3 stack; fill | L3 present = 0.0.
- VB5 FALSIFIED: L3 loses the first-attach race (0.214); family
  contrast shows L3 first-attaching at 0.72 yet never terminal.
  Misplacements are ACCRETED (late capture onto a settled
  background), not raced into. Principle #6: reinforcement does
  not need to win races — it only needs to make one late arrival
  permanent.
- VB4 INCONCLUSIVE as registered: the dwell clause normalized over
  all 500 trajectories (flaw); the stability clause alone passed at
  1.0. Kept un-promoted.

Design consequence: any future lock-reinforcement knob must be
priced against the FULL contention set of the affected vacancy
(fill, via-site lock squat, reader stack), not against a single
hazard class.

### Priced (tick 42, SON-4810): the contention set made executable

The design consequence above is now a d4 layer, not a note:
`molasp.offchannel.vacancy_contention` — per-species vacancy
backgrounds, every contender classified (fill / via_squatter /
lock_squatter / stack_partner) and priced under every knob at once
(default `{"family", "s2"}`; `matched_s2` promoted into the census
module).  Receipt `evidence/2026-10-07-vacancy-contention/` (static
enumeration, tick-37 rule — no cluster job).

- **C1–C3, C5 CONFIRMED; C4 CONFIRMED after a disclosed
  registration-defect correction** (the first clause's `>= 50`
  threshold swept L3 (54) into a required set its own boundary
  clause excluded; v1 receipt kept falsified, corrected clause
  names the three dominant occupants — 203/150/78 vs 54).
- **Family is minority-dominance, not monopoly**: BUILD1 Vp@2,2
  family-stable = {D2T fill b=2, L2 via-squatter's stack channel}
  — matching the measured family occupants 454/36 of 500.  Under
  s2 the stable set mints to five {D1T, D2T, DBr, L2, V0p} while
  the fill share collapses 454→203 (0.908→0.406): pricing story =
  the knob does not need to beat the fill, it needs only to mint
  enough frozen contenders to make the vacancy first-come.
- **DBr's channel is priced as a stack partnership** (own family
  bond 1; enables L3@(3,2) s2 b_with=2 > b_without=0) — the class
  a solo-bond census cannot see (tick-39's M2 falsification, now
  arithmetic).
- **Minting is constructional**: every BUILD1/2/3 vacancy grows
  its stable set under s2; lock and spine vacancies go from empty
  to 3–6 frozen contenders (the lock's own vacancy is the most
  knob-sensitive site class).
- Honest boundary: L3@(2,2) (54/500) needs a second background
  event — outside single-species scope by construction, recorded
  not asserted (C4 correction).

## Evaluated — dG / read-window extension (tick 43, SON-4813)

The single-operating-point trade table above is now resolved on
the dG axis (`evidence/2026-10-07-contention-dg-sweep/`, gates
DW1–DW7 pre-registered at `236f91b`, n=500/arm):

- **Three regimes.**  Frozen (dG 0.5): first-come is destiny — s2
  persistence 0.872, fill 0.412 (tick-42 calibration replicated
  cross-seed).  Marginal (dG 2): persistence 0.520 but the re-roll
  is a near-fair coin (D2T 232 : L2 229), fill 0.464 — the lottery
  survives as a stationary split.  Churn (dG 4): fill 0.564,
  4×-window 0.798 — re-rolls accumulate and favor the fill.
  Starvation (dG 7): fill 0, partial 0.0008.
- **The family row of the trade table was a low-dG number** (DW6
  FALSIFIED): at dG 4 the bare family channel collapses — fill
  0.074, site dwell 0.113, partial 0.633; b=1 nucleation
  intermediates cannot survive to their stabilizing partner, and
  the 4× window does not rescue it (0.054) — a window cannot fix
  a nucleation barrier.
- **The s2 knob's sign flips with dG** (principle #7): the same
  doubling that mints frozen squatters at dG 0.5 is the only
  channel that carries growth at dG 4 (0.074 → 0.564; win4
  0.054 vs 0.798) — attachments stick at effective b=2 on
  arrival, dwell 0.113 → 0.967.  Compiler guidance: lock-read
  reinforcement is regime-dependent; price it against the
  operating point's nucleation barrier, not as a universal
  hazard or cure.

## Closed — compiler-facing severity ranking with the dG axis (tick 44)

The design consequence of both extensions is now the compiler
surface: `molasp.offchannel.contention_severity` — the census
joined to the measured regimes.  For every knob-sensitive
vacancy it emits a severity TIER at the requested dG, priced
against `REGIME_ANCHORS` (contention_dg.out verbatim, quoted —
never asserted), and `check_d4` auto-attaches it at the protocol
equilibrium `DEFAULT_DG = 0.5`, with `d4_report_lines` naming the
regime, the knob verdict, and each tier ≥ moderate.

| dG regime | knob verdict | tier logic | measured anchor |
|---|---|---|---|
| frozen (≤1.0) | hazard | critical: mints over a family fill; high: mints, no family fill | fill 0.904→0.412, persist 0.872 |
| marginal (1.0–3.0) | hazard | critical (the lottery survives as a stationary split) | 232:229 coin, persist 0.52 |
| churn (3.0–6.0) | mitigation | mitigating: knob is the growth carrier; starved: family-only b=1 nucleation | 0.074 vs 0.564, dwell 0.113 |
| starvation (≥6.0) | moot | moot: refuse the operating point, do not price it | fill 0, partial 0.0008 |

Boundary discipline carried into the artifact: `interpolated`
flags any dG off the measured points 0.5/2/4/7 (nearest-regime
pricing); `boundary_notes` records the untested dG-2 window arm,
the persist_n=1 starvation caveat, and L3@(2,2)'s exclusion from
the five-name census.  Static arithmetic only — no cluster job
(tick-37 rule; every kinetic number is already receipted).

Pins: `tests/test_contention_severity.py` (14) — anchors
verbatim, regime boundaries, BUILD1 Vp@2,2 critical/high/mitigating/moot
across the four regimes, lock-vacancy high, BUILD2 minting
generalisation, BUILD3 tier validity + minting constructional,
check_d4 integration, determinism.

designs/007 is CLOSED: the via-site lock story ran property →
knob → mechanism → thermodynamic closure → regime pricing →
compiler surface.  Remaining honest boundaries (dG-2 window arm,
L3-at-vacancy class) are recorded in the artifact, not owed by
this design.
