# 2026-10-13 w8 q0 position-weighting sensitivity (tick 115, SON-5146)

Date: 2026-10-13T18:00Z wake · SON-5146 · run 12435821 · posfresh request
bda50c6b STILL QUEUED (admission floor, "resource/owner limit"; idempotent
nonce molasp-w8-posfresh-t113 holds it). Never-idle avenue while the waiter
waits: make the tick-113 q0 caveat quantitative.

## Question

The family pool q0 = 1110/1499 = 0.7404937 (arms 3+5+7 = 375/500, 370/500,
365/499; receipt evidence/2026-10-09-w8-blockprobe/run.out sha256 fe7be746)
is built ONLY from first-position windows. If the position-decline account
is true, q0 estimates share(first), not the family mean, and every q0-based
gate inherits that bias. How big is the exposure, concretely, per instrument?

This is design arithmetic on committed counts — no simulation, no new seed
burns, no re-test of the frozen eight-window verdicts, no multiplicity
relitigation. Committed tool: `tools/w8_q0_sensitivity.py`; all numbers
below are its exact outputs, pinned in `tests/test_w8_q0_sensitivity.py`
(18 tests), and the exact binomial CDF is cross-checked against Fraction
arithmetic at n=20 inside the test.

## Model

Under a two-rate decline with first-vs-rest gap Δ and first-window family
weight w, the position-balanced family rate is q0 − Δ·(1−w). Anchors: the
tick-112 descriptive gap Δ = 0.780 − 1777/2499 = 0.0689156, and family
compositions from the actual lineages (posfresh blocks plan 10 windows each
→ w = 1/10; 5- and 2-window families as spread; a half-effect Δ/2 row).

## Numbers (exact, n=1000 low-gate; normal-approx census power)

Low gate = hotrepro-style one-sided "window reads low vs q0" test, exact
binomial, calibrated at q0: critical k = 717 (P(X≤717|q0) ≤ 0.05 <
P(X≤718|q0)). False-flag = P(trip | true family rate) for a fresh
non-first window.

| scenario | family rate | low-gate flag | census pwr (δ=.02, n=5000) |
| --- | ---: | ---: | ---: |
| window-noise (q0 stands) | 0.7404937 | 0.0500 | 0.7377 |
| decline Δ, w=1/10 | 0.6784697 | 0.9962 | 0.6901 |
| decline Δ, w=1/5 | 0.6853612 | 0.9863 | 0.6945 |
| decline Δ, w=1/2 | 0.7060359 | 0.7864 | 0.7089 |
| half-effect Δ/2, w=1/2 | 0.7232648 | 0.3402 | 0.7225 |

Wilson-95 on the pool itself: [0.71771, 0.76205] — the w=1/2 decline rate
0.7060 sits BELOW the interval's floor, i.e. the exposure is not covered by
the pool's own sampling error (plug-in SE 0.0113 ≪ bias 0.034).

## Reading

1. **One-sided low gates are fragile.** A fresh mid/late window tested
   against q0 trips the "low" gate 34–99% of the time under decline
   scenarios (vs 5% by construction under window-noise). Any future
   one-sided-below-q0 instrument must either wait for posfresh or carry a
   dual-null band.
2. **Census power is second-order.** The planned decisive census (exact
   conditional hypergeometric; normal approx here for planning only) loses
   0.7377 → 0.6901–0.7225 across scenarios — a ≤0.048 power shift, not a
   redesign trigger. The ladder's power plan may keep q0 as its null with a
   disclosed band.
3. **Standing recommendation until posfresh adjudicates:** q0-based
   one-sided-low gates use the band [q0 − Δ(1−w), q0] with w named from the
   actual family; two-sided consistency checks keep q0 with the caveat
   line. This is a recording convention, not a new claim.

## Boundaries

Descriptive robustness arithmetic only. The decline scenarios are
hypothetical states of the world anchored on a descriptive gap from the
same eight windows (tick-113 boundary: p there quantified extremity, not
independent confirmation); they are NOT evidence the decline is real, and
NOT_DETECTED from posfresh would collapse the band to the sampling interval.
Normal-approximation power rows are planning arithmetic, not the
confirmatory exact-conditional scan. No physical-replicate inference, no
wet-lab, no blog (not a milestone), no external contact, no
paper/preprint activity.

## Receipts

- Tool: tools/w8_q0_sensitivity.py (exact log-sum-exp binomial; Wilson;
  scenario table printer). Bug disclosed and fixed in-tick: a first draft
  used a hand-rolled incomplete-beta CDF that returned k=-1 at calibration;
  replaced by exact lgamma log-sum-exp, then verified against Fraction
  arithmetic (test_cdf_symmetric_case_against_direct_sum).
- Tests: tests/test_w8_q0_sensitivity.py — Ran 18 tests / OK.
- Full suite: see collection commit message (CI command identical).
- Next action unchanged: collect posfresh per the frozen branch map
  (SON-5144 comment, mechanical chain rehearsed at 6fe9ca4); this note's
  band applies to whatever gates the ladder redesign names.
