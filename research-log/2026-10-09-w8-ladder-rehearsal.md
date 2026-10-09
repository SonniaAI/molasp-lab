# w8 LADDER rehearsal — drilling the growth-ladder decision chain before the datum

Tick 95 (SON-4908, run f68c60f5) — 2026-10-09 ~06:20Z.

## What was drilled and why

Tick 90 rehearsed the five-step RESULT chain (`import_queue_result` ->
`collect_w8` -> `apply_w8_receipt` -> atlas) on synthetic frames. The
growth tools built AFTER that rehearsal — tick 91 planner, tick 92 census
policy, tick 93 dispersion receipt, tick 94 sequential-look error map —
had never been executed as a decision chain. `tools/w8_ladder_rehearsal.py`
drives the REAL `tools/w8_census_policy.py` `policy()` /
`collection_report()` on synthetic first-arm censuses (k1=500 fresh-arm
terminals) at seven pre-named truths, and checks the mechanical stage
naming against expectations committed in the tick-86/88/91/92/94 receipts
BEFORE this rehearsal ran.

## Rehearsal table (measured, deterministic)

```
truth            x1   mode                 k_line arms +add wall_h  Wilson-95
primary          417  grow                  1442    3    2  1.33  [0.79886,0.86404]
floor_edge       392  escalate_dispersion      -    -    -     -  [0.74584,0.81783]
ceiling_edge     442  escalate_dispersion      -    -    -     -  [0.85296,0.90919]
trend            382  grow                  1634    4    3  2.00  [0.72486,0.79912]
chain_falsified  325  verdict_ready            -    -    -     -  [0.60719,0.69052]
unmodeled        475  verdict_ready            -    -    -     -  [0.92723,0.96591]
edge_pointing    407  escalate_dispersion      -    -    -     -  [0.77755,0.84567]
```

7/7 truths match the committed expectations; exit 0.

## Findings

1. **The tick-92 receipt reproduces exactly at the primary**: 417/500 ->
   grow, k_line 1442 (theoretical opening also 1442), region R2, practical
   window (1203, 1250), x_line 1203, 3 pooled arms (+2 additional), 1.33 h
   wall. The ladder has not drifted against its own landed record.
2. **New number (recorded, not fixed)**: the trend arm's mechanical ladder
   answer is k_line=1634 (region R3, window (1203,1248), 4 arms, +3,
   2.00 h; P(attr) at line 0.497, expected collection days 2.0 under
   p=0.764; stage-2 P>=0.80 census k=3430, 7 arms, 4.67 h) — NOT the
   tick-91 planner's R3 regional minimum k=653. The two tools answer
   different pre-registered questions: the planner prices per-region
   minimum k; the policy scans for the FIRST k whose >=3-count practical
   window contains the point-estimate line x=round(phat*k). They agree at
   the primary and differ at the trend arm. Both receipts stand; on
   collection day the POLICY is the growth authority (it is the mechanical
   ladder), and this divergence is now receipted so it cannot be misread
   as drift.
3. **Edge truths hit stage-3 directly at k1=500** (floor_edge 392/500,
   ceiling_edge 442/500, edge_pointing 407/500): the ladder's mechanical
   counterpart of tick-94's verdict-scarcity finding. Near any boundary
   the expected collection-day prose is "stage-3: dispersion receipt +
   escalation with recommended path" — and the tool's report prints the
   outside-cap extrapolation (tick-92: k_ext ~ 25.8M at p-hat=0.814) and
   the "never stage 4" rule verbatim.
4. **Destructive verdicts need no growth, mechanically**: chain_falsified
   325/500 -> verdict_ready R4; unmodeled 475/500 -> verdict_ready R5;
   both carry growth=None. Tick-91's census-pricing finding is now drilled
   as ladder behavior, not just priced.

## Authority

Planning/policy arithmetic only. The rehearsal NEVER verdicts a real
datum: it does not import the frozen collector (`tools/collect_w8.py`)
or the atlas; collection-day verdict surfaces remain exactly those two.
Refusal contracts (k1 below the MIN_EVENTS floor, x1 out of range) raise
ValueError, pinned.

## Suite

Exact CI command `python3 -m unittest discover -s tests`:
`Ran 648 tests in 8.276s / OK (skipped=1)` = 636 + 12 new pins in
`tests/test_w8_ladder_rehearsal.py` (all twelve names present in verbose
discovery output).

## Queue state at landing (operational, not science)

Waiter `ed50c7ba…4daa85` probed 06:12Z: STILL QUEUED (~7.1 h; reason
verbatim: `queued: ci admission floor; 1500m cpu must stay free on
spark-4a06 for 2 x 500m ci runner slots + listener/burst slack`). No
resubmit. SON-4895: PE engaged substantively (patch live, byte-pin
verified 04:19Z); the single remaining step is the operator restart on
SON-4889 (owner adrozdov) — answered and evidenced, so no re-request
fired (the >=1 h rule targets unanswered requests).
