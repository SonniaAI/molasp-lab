# W8 powered paired block-mechanism arbitration probe — pre-registered before submission (2026-10-13, tick 120, SON-5152)

**Automated pre-registration; independent QA review is pending.** In-silico
provenance only. This note executes the tick-119 escalation
(`research-log/2026-10-13-w8-branchA-dispersion-gate.md`) verbatim: a
POWERED paired block-mechanism arbitration probe at delta_target = 0.030
with fresh pre-registration (frozen map + power stated before
submission), a virgin-seed scan for every new window (tick-113 rule),
and queue-envelope arithmetic at submission time. Nothing is submitted
by this note; the queue request follows only after this file, the
harness, and the pins are committed and pushed.

## Lineage (all numbers from committed receipts)

- Tick 99 line census: arm-6 `340261107+[0,500)` = 389/500 = 0.778;
  four-arm dispersion POOLING_CONTESTED (min_exact_p 0.0293258, driver
  arm-6). Re-derived and confirmed tick 119 at the corrected arms
  (arm3 375:500, arm4 106:153, arm6 389:500, arm7 365:499).
- Tick 101 block probe (n=500/group): arm6b `340261107+[500,1000)` =
  372/500 = 0.744 (family-consistent, qF6 0.8785); gap control
  `350261107+[0,500)` = 391/500 = 0.782 (qF8 0.0363 →
  HOT_NEIGHBORHOOD). Branch AMBIG_MIDDLE: contrast +0.038 sits just
  under the design MDE 0.040.
- Hotrepro (tick 111, n≈1000/group fresh continuations): A-fresh
  `340261107+[1000,2000)` = 691/999 = 0.6917; B-fresh
  `350261107+[500,1500)` = 714/1000 = 0.7140. Contrast +0.0223, SAME
  direction. Pooled over both ticks: GAP 1105/1500 = 0.73667 vs A6
  1063/1499 = 0.70914 (delta +0.02753). Post-hoc pooling, recorded as
  motivation only — never a gate.
- Tick 118 posfresh (virgin blocks 560/580×261107): no position
  decline; window-noise unrefuted there. Tick 119: both pooled verdict
  readings on the contested four-arm pool are unclaimable; pooled line
  REPORTED-NOT-CLAIMABLE; ladder PAUSED.

## The accounts this probe arbitrates (stated before any datum)

- **A (window noise):** both hot readings (arm-6 0.778, gap control
  0.782) were window-level fluctuations; fresh continuations of the
  same two blocks do not differ persistently. Prediction: one-sided
  Fisher p > 0.05 at this power.
- **B (block mechanism):** the gap block (base 350261107) runs
  persistently elevated relative to arm-6's block (base 340261107).
  Prediction: share(GAP) > share(A6), p ≤ 0.05.

## Design (frozen)

- GAP group: seeds `350261107 + 1500 + i`, i ∈ [0,3560); fresh range
  [1500,5060); windows w1 [1500,3280), w2 [3280,5060), 1780 seeds each.
- A6 group: seeds `340261107 + 2000 + i`, i ∈ [0,3560); fresh range
  [2000,5560); windows w1 [2000,3780), w2 [3780,5560).
- Pairing: window index matched across groups (same position within
  each group's fresh range). PRIMARY pools windows within group —
  Fisher support is fine-grained at these n (no structural floor,
  unlike tick-112 P1); the pairing surfaces in matched-window
  descriptives.
- CAL: `260261107+[0,500)` unchanged; mid-window pair census must be
  EXACTLY D2T 367 : L2 131 (10th consecutive identity run when it
  lands). Mismatch → VOID.
- PRIMARY: pooled GAP vs pooled A6 terminal pair census, Fisher exact
  one-sided, H1 share(GAP) > share(A6), alpha = 0.05.
- Branch map (exhaustive, mechanical, no default):
  CAL_FAIL → VOID; min pair-n < 3400 → NO_EVENTS; p ≤ 0.05 →
  BLOCK_MECHANISM_SUPPORTED; p > 0.05 → BLOCK_MECHANISM_NOT_DETECTED.
- Consequences pre-registered: SUPPORTED → persistent between-block
  elevation stands; pooling across stride/half-stride blocks
  structurally unsafe; family estimates go per-block; ladder iid-
  pooling premise downgraded (blog only after independent review).
  NOT_DETECTED → the twice-observed direction does not survive a
  powered test; window-noise stands as the operating account for BOTH
  hot readings; tick-101 AMBIG resolves to noise-at-power; four-arm
  POOLING_CONTESTED stays operative (pooled line
  REPORTED-NOT-CLAIMABLE); ladder stays PAUSED pending the next
  pre-registered step.

## Power (stated BEFORE submission)

Normal approximation, one-sided alpha = 0.05, p̄ ≈ 0.745 (family
0.7405, observed windows 0.69–0.78), n = 3560/group:

- SE(diff) = sqrt(2 × 0.745 × 0.255 / 3560) = 0.010332
- MDE at 90% power = (1.645 + 1.2816) × SE = 0.03024 ≈ 0.030
- power at Δ 0.030 ≈ 0.896; at 0.038 (tick-101 realized) ≈ 0.979;
  at 0.0223 (hotrepro realized) ≈ 0.696.
- n derivation, frozen rule: 2000 × (0.040/0.030)² = 3555.6 → 3560.
- Pair-n: terminal 'other' ≤ 0.5% in every committed w8 window →
  expected pair-n ≥ ~3542; floor 3400 carries ~4.5% headroom.

## Seed-scan record (tick-113 rule, executed this tick before commit)

Burned map for the two blocks, from committed evidence: block
340261107 offsets {0, 500, 1000} (arm6, arm6b, A-fresh); block
350261107 offsets {0, 500} (arm8, B-fresh). Full-tree numeric
range-scan over evidence/ tools/ tests/ molasp/ research-log/ log/
designs/ blog/ for every literal in [350262607, 350266666] ∪
[340263107, 340266666] (the fresh windows, all offsets): **zero
hits**. The suite pins this (`test_no_prior_run_out_contains_probe_seeds`
is the enforced backstop; it excludes this probe's own evidence dir).

## Queue-envelope arithmetic (at submission)

Measured throughput from the posfresh receipt: ~4500 terminals in
~102 s ≈ 44 seeds/s on paperclip-test 1cpu/1Gi. This probe: 3560 × 2
+ 500 CAL = 7620 seeds ≈ 173 s ≪ 2400 s wall. Envelope: paperclip-test,
1 cpu, 1 GiB, 2400 s — identical to the posfresh envelope.

## SMOKE disclosure

One clean-extraction SMOKE run (8 trajectories per window, 16/group,
SMOKE_ONLY label, never a verdict surface) is executed locally before
submission, tick-113 precedent. It consumes the first 8 seeds of each
of the four windows; the queued job runs the full windows
(deterministic core — identical outcomes for repeated seeds).

## Collection-time duties (next wake, mechanical)

1. `job_queue.py result --owner <agent-id> <request-id>` → import with
   EXPLICIT `--request` (tick-114 lesson); brace-extract run.out.
2. Read the FROZEN branch here — never re-derive the map.
3. Fill the queue receipt (house style, `collected` stays null) from
   the queue's authoritative record, never console echo (tick-119
   lesson: verify the job id against the request record).
4. Run the FULL suite with the receipt + run.out present (tick-111
   lesson); if the reserved-seed guards in test_w8_line /
   test_w8_blockprobe trip on this probe's receipt metadata, whitelist
   it as metadata-only in THIS tick, never weaken the duplicate-burn
   protection.
5. Collection commit + push; report on SON-5152; then the frozen
   consequences above.

## Boundaries

Direction frozen: GAP > A6; a realized reverse difference surfaces in
descriptives only — no post-hoc flip. Two blocks do not certify the
lattice. In silico kTAM simulation only; no wet-lab; no
physical-replicate or chemical-performance claim; no paper/preprint
activity; no blog until a reviewed finding exists.
