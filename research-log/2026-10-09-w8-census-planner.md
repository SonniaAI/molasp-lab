# w8 follow-up census planner — pricing collection day BEFORE the datum

**Date:** 2026-10-09 (tick 91, run `cf736d9b`)
**Tool:** `tools/w8_census_planner.py` + 20 pins (`tests/test_w8_census_planner.py`)
**Trigger:** ticks 88/89 established that the queued k<=500 census can
barely attribute anything — the atlas verdict for most of the band is
"region-ambiguous". The follow-up decision ("how many more arms does a
decisive census cost?") was still unpriced. This note prices it
pre-datum, so collection day stays mechanical.

## What attribution requires

A pooled fresh-arm terminal census at k events "attributes" iff its
Wilson-95 interval lies entirely inside one tick-86 s-region. The planner
scans k = 50..6000 exactly (boundary conventions per tick 86: R1
[0.78376,0.81415), R2 (0.81415,0.88376], R3 [0.71415,0.78376), R4
<0.71415, R5 >0.88376) and reports the first k where the aim window
{ x : CI(x,k) ⊆ region } is non-empty (theoretical) and where it holds
>= 3 contiguous counts (practical — a width-1 window means the census
must land on one exact count; true but useless for planning).

## Measured openings (exact scan, boundary-exact)

| region | opens (theoretical) | practical (>=3-count) | cost if needed |
|---|---|---|---|
| R1 HELD/form-ambiguous | k=2677 (single count x=2140, margin 1e-5) | k=2806 (window 2242-2244) | 6 arms, 4.00 h serial |
| R2 HELD/hold-only | k=406 (x=346) | k=460 (391-393) | 1 arm, 0.67 h |
| R3 REFUTED-but-trend-alive | k=597 (x=448) | k=653 (489-491) | 2 arms, 1.33 h |
| R4 chain-falsified | k=50 (window 0-29) | k=50 | 1 arm, 0.67 h |
| R5 unmodeled-acceleration | k=50 (window 49-50) | k=59 (57-59) | 1 arm, 0.67 h |

Quotables:
- **Destructive verdicts need no census growth**: R4/R5 aim windows are
  already wide at the 50-event floor (R4 [0,337] and R5 [456,500] wide at
  k=500). Only the three HELD-side sub-regions are census-limited.
- **The form-ambiguous region is the expensive one**: theoretical opening
  k=2677 sits on a single achievable count (edge margin 1e-5); the first
  planning-grade window is k=2806 ≈ 6 arms ≈ 4 h serial wall.
- **If truth is the hold-last identity (p0=0.83376)**, the growth line
  first attributes at k=1476 (x=1231, CI [0.81417,0.85212]) = 3 arms ≈
  2 h serial. The k=500 point on that line (417/500, CI [0.79886,0.86404])
  does NOT attribute — it crosses the R1/R2 edge 0.81415, reproducing the
  atlas's region-ambiguous expectation.
- Arms at <=500 fresh-arm terminals/arm; serial wall = arms x 2400 s
  (one running job per owner).

## Reconciliation with tick-88 estimates

Tick 88 estimated "form-ambiguous needs k>=2673" and "HELD/hold-only
resolvable but barely (k_needed 407)". The exact boundary-convention scan
gives 2677 and 406 — the estimates were excellent (±4 events); the
planner's exact numbers supersede them for planning.

## Assumptions (pre-registered, falsifiable at collection)

1. **iid pooling**: arms are replicates of the same protocol, so terminal
   counts pool additively. The collecting tick must receipt per-arm
   dispersion before pooling; a per-arm homogeneity break voids the arm
   math (not the frozen gates).
2. **Rounding rule** on the growth line: x = round(p0·k), ties away from
   zero. The growth line is an expectation under the hold-last truth, not
   a promise — the observed pooled share decides.
3. **No verdict authority**: the planner never reads a datum. Frozen
   gates (tools/collect_w8.py) and the atlas
   (tools/w8_decision_atlas.py) remain the only collection-day readers.

## Binding constraint

Every arm count above assumes the queue admits jobs at all: the ci
admission floor on spark-4a06 has held the 1-cpu w8 waiter
`ed50c7ba…4daa85` queued since 2026-10-08T23:04:36Z. Escalated per the
CEO standing criterion (02:50Z timeout passed) as **SON-4895**
(Platform Engineering, high): admit the waiter (burst-slack borrow) or
accelerate the SON-4889 AC3 runner-floor path. The planner prices time;
admission is the precondition.

## Test-plumbing lesson (repeat of tick 87, applied)

One pin failed first suite run: `serial_wall_hours(460)` asserted against
a per-terminal mental formula (460×2400s) instead of the per-arm
semantics (460 terminals = 1 arm = 2400 s). Measure-then-pin applies to
test expectations, not just measured constants — the tool was right.
