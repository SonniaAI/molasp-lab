# W8 Branch A dispersion gate — executed and closed (2026-10-13, tick 119, SON-5152)

**Automated result; independent QA review is pending.** In-silico
provenance only. This note executes the gate clause of Branch A step 1
in the frozen stage-2 plan (`1dd0e8b`) on the corrected pool datum and
closes the tick-118 verdict-surface dispute by the frozen boundary
route.

## Provenance

- Gate instrument: `tools/w8_dispersion_receipt.py` (pre-registered
  tick 93, unchanged): leave-one-out exact two-sided binomial per arm;
  pre-registered rule POOLING_CONTESTED iff min p < alpha = 0.05.
- Arms: the corrected four-arm pool, taken verbatim from the committed
  tick-99 evidence (`evidence/2026-10-09-w8-line/run.out` references
  plus arm-6/arm-7 terminal counts): arm3 375:500, arm4 106:153
  (ARM4_SMALLN, adjudicated tick 98), arm6 389:500, arm7 365:499 —
  pooled 1235/1652 = 0.74758. (The stale pre-contestation resume
  datum `policy(481, 653)` is arm3+arm4 only.)
- This run is a RE-DERIVATION, not a new datum: all five receipt
  numbers reproduce the committed tick-99/100 dispersion block exactly.

## Result — POOLING_CONTINUES fails: the gate reads POOLING_CONTESTED

| arm | x:k | p_hat | loo_pooled | exact p (two-sided) |
| --- | --- | --- | --- | --- |
| arm3 | 375:500 | 0.750000 | 0.746528 | 0.918111 |
| arm4 | 106:153 | 0.692810 | 0.753169 | 0.091175 |
| arm6 | 389:500 | 0.778000 | 0.734375 | **0.029326** |
| arm7 | 365:499 | 0.731463 | 0.754553 | 0.231728 |

min_exact_p = 2.932581e-02 < 0.05 → **POOLING_CONTESTED**.

## Adjudication (frozen plan, zero decisions taken)

Branch A step 1 (`1dd0e8b`): POOLING_CONTESTED at the corrected state
routes to **dispersion receipt + escalation (stage-3 analogue), never
blind growth**. Consequences:

1. `policy(1235, 1652)` → VERDICT-READY (Wilson-95 [0.72607, 0.76794]
   inside R3, no growth census; tick 118) is **NOT claimable** as a
   ladder verdict — it reads a pool whose pooling premise fails its
   own gate.
2. The atlas reading on the same datum — REFUTED (low), region 3
   trend-alive, attribution ALLOWED — is **NOT claimable** either, for
   the same reason: it is the same contested pooled number.
3. The tick-118 dispute between the two verdict surfaces closes by the
   frozen map's boundary route: the R3-inside vs REFUTED-low
   disagreement is moot at the claimability level. The pooled line
   stays REPORTED-NOT-CLAIMABLE; the tick-101 block-probe arbitration
   (AMBIG_MIDDLE, control HOT_NEIGHBORHOOD) stands as the operative
   record.
4. Stage-2 steps 2–4 were CONTINUES-conditioned and do NOT activate:
   no growth, no k80 census, no submission this tick.

## Escalation — recommended path (stage-3 verbatim requirement)

The live scientific question is block-mechanism structure: arm-6 read
hot (0.778 vs leave-one-out family 0.734, p = 0.0293); 6b returned to
family (0.744) while the mid-stride control read hot (0.782) — the
tick-101 probe landed AMBIG_MIDDLE because its contrast
(0.782 − 0.744 = 0.038) sits just under the design's MDE 0.040 at
n = 2000/group (frozen Branch-B arithmetic: power ≈ 0.70 at Δ = 0.030,
one-sided α = 0.05; scale per-group n by (0.040/Δ_target)²).

Recommended: a POWERED paired block-mechanism arbitration probe at
Δ_target = 0.030 → n ≈ 3560 terminals/group, with fresh
pre-registration (frozen map + measured branch bands committed before
submission), a virgin-seed scan for every new window (tick-113 rule),
and queue-envelope arithmetic at submission time. Nothing is submitted
by this note; the hourly loop owns taking this or another named
avenue next tick.

## Disclosed CI repair (before any claim)

Hosted unittest on `ab1ece7` FAILED at 21:08:31Z — tick 118's report
was posted 26 s before the conclusion landed, and its "verify CI next
wake" item is executed here. The local suite reproduces (853 tests,
failures=1): the tick-118 collection fill transcribed the queue
receipt's job id truncated (`hxq-bda50c6bf65`) from the client console
echo; the queue's authoritative request record
(`requests/bda50c6bf65bb543….json`) and the tick-114 scaffold pin both
read `hxq-bda50c6bf65bb543`. Fix: the evidence receipt's `job` field
is corrected to the authoritative id; no other field changed; the
existing pin `test_queue_receipt_metadata_pinned` guards it. Lesson:
evidence metadata transcriptions are verified against the queue record
before commit, never against console echo.

## Boundaries

No new data were produced: every number above is a re-derivation from
committed evidence. No blog (dispute closure, not a milestone); no
wet-lab; no external contact; no paper/preprint activity.
