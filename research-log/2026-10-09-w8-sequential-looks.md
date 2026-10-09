# w8 sequential-look error map — pre-registered BEFORE the datum

Tick 94, 2026-10-09 (queued falsifier `ed50c7ba…4daa85`).
Tool: `tools/w8_sequential_looks.py` · pins:
`tests/test_w8_sequential_looks.py` (13).

## The gap this closes

The tick-92 census policy froze a **staged** collection ladder — stop
when a pooled census attributes, otherwise buy more terminals (500 →
k_line 1442 → k80 2895). Tick 88 priced verdict-flip risk at a
**single** look; tick 93's dispersion receipt explicitly carried "no
multiplicity correction" as a caveat. Nobody had receipted what
data-dependent stopping does to the *procedure's* final-verdict error
rate. That is this receipt, fixed before any pooled datum exists.

## Model (pre-registered assumptions, falsifiable at collection)

- **A1** iid arms at a common true share (tick-91 assumption 1; a
  tick-93 `POOLING_CONTESTED` receipt voids the ladder to stage 3).
- **A2** canonical committed prices k1=500 → k_line=1442 → k80=2895;
  realized k_line/k80 are phat-dependent — the pinned sensitivity
  (k_line 1342/1542 at the primary) shows the error map is flat under
  plausible movement.
- **A3** verdict-ready == the atlas attribution rule (Wilson-95
  entirely inside one tick-86 region, frozen `contained`/EPS);
  a stage-3 stop publishes NO verdict and is scored safe.
- **A4** error == procedure stops verdict-ready and the frozen
  Fraction-exact gate verdict is wrong against the truth
  (false-HELD / false-REFUTED).
- Wilson/regions imported **structurally** from the tick-91 planner;
  gate constants receipt-duplicated from the collector/tick-88.

## The map (verbatim tool output)

```
truth    insid stop1   stop2   stop3   stage3  falseHELD falseREFU err_seq  err_1look infl
0.71415  N     0.0274  0.0441  0.0304  0.8981  5.908e-13 0.000e+00 5.908e-13 2.373e-04 0.000
0.76415  N     0.0000  0.4294  0.3173  0.2532  3.047e-06 0.000e+00 3.047e-06 1.604e-01 0.000
0.77376  N     0.0000  0.1525  0.1498  0.6977  2.277e-04 0.000e+00 2.277e-04 3.134e-01 0.001
0.78376  Y     0.0001  0.0258  0.0236  0.9505  0.000e+00 4.257e-02 4.257e-02 4.794e-01 0.089
0.79376  Y     0.0006  0.0020  0.0425  0.9549  0.000e+00 2.281e-03 2.281e-03 2.737e-01 0.008
0.81415  Y     0.0125  0.0230  0.0234  0.9411  0.000e+00 5.036e-07 5.036e-07 3.868e-02 0.000
0.83376  Y     0.0811  0.4335  0.3035  0.1819  0.000e+00 2.940e-07 2.940e-07 2.618e-03 0.000
0.87376  Y     0.0589  0.1962  0.1962  0.5487  0.000e+00 5.254e-03 5.254e-03 2.704e-01 0.019
0.88376  Y     0.0410  0.0399  0.0303  0.8888  0.000e+00 5.637e-02 5.637e-02 5.282e-01 0.107
0.89376  N     0.1057  0.1449  0.1996  0.5497  3.223e-03 0.000e+00 3.223e-03 2.152e-01 0.015
```

## Readings (pre-registered)

1. **Optional stopping does not inflate error here — it deflates it,
   at every truth on the grid.** The ambiguity gate is a conservative
   filter: the point estimates that would mis-verdict sit at gate
   edges, where the Wilson-95 straddles a region boundary and the
   ladder refuses to stop. Worst-case staged error is at the exact
   gate edges (4.26% at 0.78376, 5.64% at 0.88376) — a 9–10× cut
   against the single-look 47.9%/52.8%. At the primary 0.83376 the
   staged error is 2.9e-07; at the trend arm 0.76415 it is 3.0e-06
   against a single-look 16.0% false-HELD.
2. **The price is verdict scarcity at edge truths.** The procedure
   buys error control by escalating instead of verdicting: stage-3
   probability 0.95 at the floor edge, 0.89 at the ceiling and at
   0.71415, versus 0.18 at the primary. Expected collection-day
   prose near any boundary is "stage-3, dispersion receipt,
   escalate" — that is the instrument working, not failing (tick-92
   pre-registered expected collection days ≈ 2.0 under the same
   planning discipline).
3. **Tick-93's "no multiplicity correction" caveat is now quantified:
   across up to three data-dependent looks, total inflation is
   bounded by the single-look map itself (infl < 1 everywhere).**
4. **Identity cross-checks pass on all four tick-88 probes** (0.01
   outside floor 31.3%, 0.01 inside floor 27.4%, 0.01 inside ceiling
   27.0%, 0.01 outside ceiling 21.5%) — pinned in the tests.

## Authority

Pooling-assumption and planning arithmetic only. Zero verdict
authority: `tools/collect_w8.py` and `tools/w8_decision_atlas.py`
remain the only collection-day verdict surfaces; the frozen gates are
untouched.

## Suite

Exact CI command `python3 -m unittest discover -s tests`:
`Ran 636 tests in 7.708s / OK (skipped=1)` = 623 + 13 new pins.

## Queue state at landing (operational, not science)

Waiter `ed50c7ba…4daa85` probed ~05:19Z: STILL QUEUED (~6.2 h; reason
verbatim: `queued: ci admission floor; 1500m cpu must stay free on
spark-4a06 for 2 x 500m ci runner slots + listener/burst slack` — the
old floor text, consistent with the controller restart on SON-4889
not yet executed). No resubmit. SON-4895 last substantive PE update
04:19Z: patch live + byte-pin verified, single remaining step is the
operator restart (`kubectl -n hx rollout restart
deployment/cluster-job-queue`, owner adrozdov) — answered and fully
evidenced, so no re-request fired this tick (the ≥1 h re-request rule
targets an *unanswered* request).
