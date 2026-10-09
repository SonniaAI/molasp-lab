# w8 extrapolation-form sensitivity — pre-registered before the datum

Date: 2026-10-09 (tick 86, SON-4885). Registered BEFORE the w8 falsifier
datum exists: the instrument sits in the cluster queue as request
`ed50c7ba…4daa85` (queued since 23:04:36Z, ci admission floor). Every
number below is deterministic arithmetic on committed receipts (tick-37
rule): the `VH_BASIS` tables in `molasp/offchannel.py`, quoted from the
evidence receipts listed there. Tool: `tools/w8_sensitivity.py`
(10 pins in `tests/test_w8_sensitivity.py`; suite `Ran 530 tests / OK
(skipped=1)` = 520 + 10).

## What this is and is not

The frozen W8 gate is NOT touched: `HELD iff |s_w8 − 0.83376| ≤ 0.05`
(`evidence/2026-10-08-w8-hazardhold/ktam_w8_hazardhold.py`), and the
five-step zero-decision collection chain (tick 84) is unchanged. This
note answers the question collection day would otherwise answer by
improvisation: **the 0.83376 centre rests on holding phase-4 hazards
beyond w4 — how much does that choice matter, and which choices would
a verdict datum still be consistent with?**

## Arms

All four integrate the same validated chain from the w1 snapshot
through the fit grid (phases 2–4, w1 each); they differ ONLY in the
hazard policy for phases ≥ 5 (beyond the w4 fit-grid edge). The tool's
integrator passes the TRUE phase index (unlike
`molasp.offchannel._vh_share`, which caps it at 4 — that cap IS the
hold-last semantics).

| arm | policy beyond w4 | w8 prediction | dev from primary |
| --- | --- | --- | --- |
| A hold-last | phase-4 hazards held (designs/011 primary) | **0.83376** | 0 (identity with `_vh_share(8)`) |
| B hazard95-d2t | late D2T hazards at Poisson-95 upper bounds (VH1) | **0.81585** | 0.01791 (identity with the committed bracket) |
| C l2-loglinear-trend | ln(haz_l2) linear in phase over 2–4, extrapolated (ratio 0.5341/phase; hazards 2.1915e-8 → 3.3393e-9 at phases 5→8) | **0.76415** | 0.06961 — OUTSIDE the frozen band |
| D l2-zero-beyond-w4 | no L2 detach at all | **0.62767** | 0.20609 — far outside |

Anchors reproduced, not asserted: arm A ≡ `_vh_share(8)` and the quoted
primary (≤ 5e-6); arm B ≡ `marginal_window_pricing()["8"]["hazard95_share"]`
(exact); the fixed-hazard stationary ceiling ≡ 0.97865 (designs/011 P3;
left null vector of Q(hd4, hl4), π = [0.00003, 0.97793, 0.02134, 0.00071]).
Attach-odds pair share at E: p_D2T/(p_D2T+p_L2) = 0.52045.

## Finding (the opposite of a robustness rubber-stamp)

The beyond-w4 **L2 hazard form is the dominant w8 sensitivity** — spread
0.20609 across hazard forms, versus the frozen band's ±0.05 halfwidth.
Mechanism, from the hold-last state vectors: at w4 the pair pool is
[D2T 0.73792, L2 0.25745]; the per-window L2 leak at the held hazard is
haz_l2[4] × quarter = 4.36e-8 × 5.34e6 ≈ 23% of L2 mass per window, and
leaked mass re-attaches at odds 0.520:0.480 into D2T:L2 while D2T itself
leaks only ~0.55%/window. The w4→w8 crawl (share 0.74135 → 0.83376,
D2T +0.0932 / L2 −0.0917) is carried almost entirely by that
leak-and-reenter differential — so changing the leak rate changes the
crawl speed directly. If the late-L2 hazard instead follows the log-linear
phase trend (arm C), w8 lands at 0.76415, BELOW the frozen band floor
0.78376; with no leak at all (arm D) the share nearly freezes at its w4
value (0.62767 — D also drifts DOWN through the D2T leak/re-split
asymmetry and the O-churn feed).

## Pre-registered reading map (fork-free collection day)

Region bounds: primary band [0.78376, 0.88376]; trend band [0.71415,
0.81415]; overlap [0.78376, 0.81415].

1. **s ∈ [0.78376, 0.81415]** — HELD, and BOTH hold-last and trend forms
   alive: the datum cannot separate them. Reading: chain account intact,
   extrapolation form formally ambiguous. No action beyond the frozen
   HELD actions; the ambiguity is disclosed, not resolved.
2. **s ∈ (0.81415, 0.88376]** — HELD, hold-last only: the trend band tops
   at 0.81415, so this region confirms the hazard-HOLD over the trend.
3. **s ∈ [0.71415, 0.78376)** — REFUTED by the frozen gate, but
   trend-consistent: the falsified content is the hazard-HOLD choice,
   NOT the chain account. Frozen refutation actions still apply in full
   (quarantine of the beyond-w4 arm etc.); the trend form becomes the
   working hypothesis for a FOLLOW-UP design (a w6 anchor arm, or a
   direct late-L2 hazard measurement) — pre-registered as a candidate
   next step, never an automatic un-quarantine.
4. **s < 0.71415** — REFUTED, no hazard-form arm alive (D's band
   [0.57767, 0.67767] covers only s below even this and itself predicts
   the share falling below w4's 0.74135): the flux/chain account itself
   is falsified beyond w4. Strongest reading of the frozen actions.
5. **s > 0.88376** — REFUTED high: no arm predicts above the primary
   band; only the stationary ceiling (0.97865) lies above. Unmodeled
   acceleration.

The instrument's n=500 fresh-seed census carries binomial noise of
roughly ±0.02–0.03 (Wilson 95 at these shares); regions 1–3 are wider
than that, so the map is noise-robust at its edges.

## Method note (a near-miss worth recording)

The first scratch implementation of the arms capped the phase index at
4 (copied from `_vh_share`'s hold-last loop), so the alternative-arm
branches NEVER EXECUTED and every arm "coincided" with the primary at
delta exactly 0.0 — a false `hazard forms are w8-irrelevant` claim,
caught before anything was committed because an exactly-zero float delta
across differently-parameterised ODE integrations is itself a red flag.
Guard pinned in tests: arms C and D must differ from A by more than the
band halfwidth (`test_arms_actually_differ_from_primary`). General
lesson: when a sensitivity probe returns exactly zero sensitivity,
first prove the perturbation actually reached the computation.

## Disposition

Docs + tool + tests only; no compiler, receipt, or gate changes; the
frozen instrument and the five-step collection chain are untouched.
Figure unaffected (the w8 point stays VERDICT PENDING; arms C/D are
interpretation aids, not drawn predictions).
