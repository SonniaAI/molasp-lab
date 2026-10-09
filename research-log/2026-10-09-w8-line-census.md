# w8 stage-1 line census — pre-registration (tick 99)

Date: 2026-10-09 · SON-4922 · run 1ad1c30a · harness + pins + this
note land together BEFORE the job is submitted; the collection
addendum is appended in the same tick.

## What and why

Tick 98's arm-5 pairwise arbitration (ARM4_SMALLN, 3-arm
dispersion receipt POOLING_SUPPORTED at min_exact_p 1.385823e-1)
restored the census ladder's pooling premise at arm level, making
the pooled line datum 481/653 claimable again.  The tick-92
census policy — recomputed on (481, 653) BEFORE this harness was
written — names the next step mechanically:

    first census: x=481 / k=653 -> Wilson-95 CI [0.70150, 0.76893]
      region-ambiguous (crosses an edge) -> stage-1 growth policy:
        line k=1524, x_line=1123, region R3
        practical window at line k: [1123, 1162]
        cost: 2 additional arm(s) x 2400 s; pooled census 4 arms total
      attribution probability AT the line census: 0.494
      P>=0.80 (stage-2 decisive census) at k=3090 (7 arms)

This tick grows the pooled datum with TWO full reserved-block arms
(the policy prices whole arms): arm-6 seeds 340261107+[0,500) and
arm-7 seeds 360261107+[0,500), both grep-verified never run (no
evidence/*/run.out outside this tick's directory contains either
seed; pinned mechanically in tests/test_w8_line.py).  Pooled k
becomes 653+500+500 = 1653 >= k_line 1524; the region reading is
recomputed at the OBSERVED pooled k at collection.  No region
constants live in the instrument (pre-registered: region
arithmetic belongs to the frozen atlas/policy tools only).

## Instrument identity

evidence/2026-10-09-w8-line/ktam_w8_line.py is VERBATIM
ktam_w8_arb5.py / ktam_w8_growth.py / ktam_w8_hazardhold.py:
same BUILD1 Vp-missing protocol, same s2 lock-read arithmetic,
same run_traj (DW9's function verbatim, RNG order unchanged),
same WIN_MULT=8 window, same CAL identity gate (367:131 at the
w4 mid-window census on DW9's own seeds — the next link of the
DW9 -> VH -> w8 -> growth -> arb5 -> here chain).  Arms 6 and 7
replace arm 5; everything else is identical except the docstring,
the added ARM5 reference constants, and the line-reading map
below.

The duplicated dispersion arithmetic is VERBATIM-proven by
identity: it reproduces the committed receipts exactly — tick-93
canonical (417:500, 407:500) min_exact_p 0.22940515642070108,
tick-93 wild (417:500, 250:500) 3.0305437299158517e-66, tick-98
3-arm 0.13858226897330395 (pinned in tests/test_w8_line.py
against both the module and the committed tool's own function).

## Pre-registered line reading (frozen before submission)

x6, x7 = per-arm terminal pair-census D2T counts over pair
denominators n6, n7 (non-pair terminals reported, not counted).
Dispersion = leave-one-out exact two-sided binomial tests over
the 4-arm set [(375,500), (106,153), (x6,n6), (x7,n7)],
alpha = 0.05.

  CAL_FAIL                -> VOID (instrument, not science)
  n6 < 50 or n7 < 50      -> NO_EVENTS (arm-level only; pooled
                             line not formed)
  min_exact_p < 0.05      -> POOLING_CONTESTED (pooled
                             attribution NOT claimable; next step
                             = block-mechanism probe, never blind
                             growth)
  else                    -> SUPPORTED_LINE: pooled (481+x6+x7,
                             653+n6+n7) is the claimable line
                             datum; the frozen atlas reads it at
                             collection — inside one region ->
                             VERDICT-READY (ladder stops);
                             ambiguous -> stage 2 named
                             mechanically by the policy tool from
                             the observed pooled phat.

Measured branch bands (pinned): (370, 370) -> SUPPORTED_LINE
(min_p 0.164736, pooled 1221/1653, Wilson-95 [0.71694, 0.75927]);
(250, 450) -> POOLING_CONTESTED (1.24645e-53); (390, 380) ->
POOLING_CONTESTED (0.0454933) — honest note: the 4-arm
leave-one-out receipt has MORE power than tick-98's 3-arm one, so
moderately-high arm pairs can fire; SUPPORTED_LINE requires
genuine arm-level consistency, and the map is exhaustive with no
default arm.

## Collection-day chain (zero decisions)

result -> tools/import_queue_result.py -> harness VERDICTS
cross-check -> committed dispersion tool on the real 4 arms
(cross-checked against the duplicate) -> census policy recomputed
at the observed pooled (x, k) -> atlas reading -> if SUPPORTED
and ambiguous, stage-2 census named by the policy tool; if
CONTESTED, block-mechanism probe next (tick-98 account-B path).

## Honest boundaries

- P(attr) at the line census is 0.494 under phat=0.73660: an
  ambiguous second datum is the EXPECTED half of outcomes and is
  pre-registered as informative (tick-92), not protocol failure.
- The pairwise design of tick 98 adjudicated the observed arm-4
  gap; block effects <~0.03 in rate remain undetectable by this
  design (tick-98 boundary carried forward unchanged).
- Arm-4 stays in the pooled set as adjudicated (ARM4_SMALLN);
  its n=153 weight is inside the leave-one-out arithmetic.

## Collection addendum (tick 100 adoption)

Provenance: tick-99's run (SON-4922, run 1ad1c30a) submitted the job,
imported the result (11:24:25Z), and died before committing; Paperclip
auto-blocked the card at 11:27Z.  This tick (SON-4928, run 6609530a)
adopted the untracked run.out/import manifest, refetched the queue
receipt (job hxq-3a5d1727ee308bd8, nonce molasp-w8-line-t99,
11:22:50Z -> 11:23:31Z, exit 0, run.out sha256 fe7be746...4e9325
byte-identical to the imported blob) and executed the frozen
collection chain with the committed tools.  Nothing was re-run.

- CAL: CAL_OK exact (367:131 mid-w4; the DW9 -> VH -> w8 -> growth
  -> arb5 -> line identity chain holds a fifth queued run).
- arm-6 = 340261107+[0,500): x6 = 389, n6 = 500, share 0.778,
  Wilson-95 [0.73953, 0.81223].  Pairwise: p3 = 0.163 (consistent),
  p4 = 2.37e-5 (arm-4, expected — adjudicated small-n), p5 = 0.0528
  (marginal, above alpha).
- arm-7 = 360261107+[0,500): x7 = 365, n7 = 499 (one non-pair
  terminal excluded per pre-reg), share 0.73146,
  Wilson-95 [0.69092, 0.76847].  Pairwise: consistent with all three
  reference arms.
- Dispersion (committed tool, cross-check EXACT vs the duplicate:
  min_exact_p 2.932581e-02, per-arm [0.918111, 0.091175, 0.029326,
  0.231728]) -> POOLING_CONTESTED.  Driver: arm-6's 0.778 vs its
  leave-one-out pool 0.734375 (p = 0.0293).  Recorded context the
  pre-reg anticipated: the 4-arm leave-one-out receipt has more power
  than tick-98's 3-arm one, and under iid the family-wise firing
  probability of four correlated alpha-0.05 tests is ~15-20%, so a
  single 0.0293 is not by itself evidence of block structure — the
  block-mechanism probe arbitrates, exactly as tick-98's arm-5
  arbitrated arm-4.
- Pooled line (REPORTED, NOT CLAIMABLE per the frozen branch):
  1235/1652 = 0.74758, Wilson-95 [0.72607, 0.76794].  Policy/atlas
  readings recorded for the record only: VERDICT-READY (CI inside
  R3), REFUTED (low), region 3 trend-alive, attribution ALLOWED —
  direction identical to tick-96's REFUTED, so no prior verdict is
  at stake; the pooled attribution is withheld because the
  dispersion receipt contests the pooling premise, and the frozen
  branch map says probe, never blind growth.
- Branch taken: POOLING_CONTESTED -> next step = block-mechanism
  probe (this tick, pre-registered before submission).

Card: SON-4922 closed as finished-by-adoption (collection landed by
this tick); SON-4928 carries the tick-100 report.
