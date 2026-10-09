# w8 block-mechanism probe — pre-registration (tick 100)

Date: 2026-10-09 · SON-4928 · run 6609530a · harness + pins + this
note land together BEFORE the job is submitted; the collection
addendum is appended by the tick that runs it.

## What and why

Tick 99's line census (adopted and landed by this tick, commit
e878f05) returned POOLING_CONTESTED: arm-6 (340261107+[0,500)) read
389/500 = 0.778 while arm-7 read 365/499 = 0.73146, and the
pre-registered 4-arm leave-one-out receipt fired at min_exact_p
2.932581e-02 (driver: arm-6 vs its LOO pool 0.734375).  The frozen
branch map withholds the pooled line datum 1235/1652 and names the
next step: a block-mechanism probe, never blind growth.

The probe arbitrates two accounts, stated before any datum:

- **Account A (window noise):** arm-6's elevation is one window's
  binomial fluctuation.  Under iid the family-wise firing
  probability of four correlated alpha-0.05 LOO tests is ~15-20%,
  and 0.0293 is exactly the kind of minimum such a family produces.
  Prediction: an adjacent window in the SAME seed block returns to
  the family mean (arms 3+5+7 pooled: 1110/1499 = 0.74049).
- **Account B (block structure):** the 340261107 block runs hot as
  a block.  Prediction: the adjacent window stays high (~0.778).

## Discriminating arms (both never run; grep-pinned in tests)

- **ARM6B** seeds 340261607 + i, i in [0,500) — arm 6's OWN block,
  the NEXT 500-seed window [500,1000).  Same block, fresh window:
  separates block-level from window-level.
- **ARM8** seeds 350261107 + i, i in [0,500) — the never-used
  mid-stride gap (BASE + 6.5 strides).  Any-window control: does an
  arbitrary unaligned window behave like the family?

Reference set fixed from committed receipts: arm-6 (389,500) from
run.out sha256 fe7be746; family pool (1110,1499) = arms 3+5+7, the
full-n arms only — arm-4 (106,153) stays excluded per tick-98's
ARM4_SMALLN adjudication.

## Instrument identity

evidence/2026-10-09-w8-blockprobe/ktam_w8_blockprobe.py is VERBATIM
ktam_w8_line.py: the import block is byte-identical, and the
simulation core (matched_s2 / run_traj / mid_class / census) plus
the pure arithmetic (logpmf / exact_two_sided_p / dispersion_min_p /
wilson) are spliced verbatim from the committed harness (the splice
was diff-audited in-run; retyped drafts of the pure functions were
caught differing and replaced).  CAL unchanged: 260261107 must read
exactly 367:131 at the w4 mid-window census — the next link of the
DW9 -> VH -> w8 -> growth -> arb5 -> line -> here chain.  Arms 6B
and 8 replace arms 6 and 7; everything else differs only in
docstring, reference constants, and the reading map.  The
duplicated exact-test arithmetic is pinned by identity against the
tick-93/98/99 receipts AND against the live committed tool
w8_dispersion_receipt (tests/test_w8_blockprobe.py).

## Pre-registered probe reading (frozen before submission)

x6b, x8 = per-arm terminal pair-census D2T counts; n6b = D2T+L2,
n8 = D2T+L2 (pair terminals only, non-pair reported not counted).

    q6  = exact_two_sided_p(n6b, 389/500, x6b)     same-block consistency
    qF6 = exact_two_sided_p(n6b, 1110/1499, x6b)   family consistency
    qF8 = exact_two_sided_p(n8,  1110/1499, x8)    control vs family
    alpha = 0.05 (fixed before the datum)

Branch map (mechanical, exhaustive, no default arm):

    CAL_FAIL                -> VOID (instrument, not science)
    n6b < 50 or n8 < 50     -> NO_EVENTS
    q6 >= a and qF6 < a     -> BLOCK_STRUCTURE   (6b reproduces arm-6's
                              elevation: block-level heterogeneity;
                              cross-block pooling structurally unsafe;
                              census-ladder pooling premise downgraded)
    qF6 >= a and q6 < a     -> WINDOW_NOISE      (6b returns to family;
                              pooling premise restored at family level)
    q6 >= a and qF6 >= a    -> AMBIG_MIDDLE      (consistent with both:
                              underpowered; both accounts stand)
    q6 < a and qF6 < a      -> OUTSIDE_BOTH      (neither account
                              predicted it; per-window heavy tails
                              recorded, no account promoted)

Control reading (recorded, never overrides the primary map):
qF8 < a -> HOT_NEIGHBORHOOD if x8/n8 > 0.74049, COLD_NEIGHBORHOOD
if below; else FAMILY_CONSISTENT.  The collection-day chain weighs
it WITH the primary branch.

Descriptive (labelled, no gates): per-arm Wilson-95; pairwise exact
tests of 6b and 8 vs arms 3/5/6/7 individually; 6-arm LOO
dispersion over [(375,500),(370,500),(389,500),(365,499),(x6b,n6b),
(x8,n8)].

Measured branch bands, pinned in tests (n6b = n8 = 500, x8 = 370):
x6b 300 -> OUTSIDE_BOTH; 355 -> WINDOW_NOISE; 375 -> AMBIG_MIDDLE;
390 -> BLOCK_STRUCTURE; 410 -> OUTSIDE_BOTH.  Control bands at
x6b = 389: x8 330 -> COLD_NEIGHBORHOOD; 370, 385 ->
FAMILY_CONSISTENT.  Honest note: an exact 6b reproduction of arm-6
(x6b = 389) reads AMBIG_MIDDLE, not BLOCK_STRUCTURE — family
consistency at n=500 only fails below ~0.059, so BLOCK_STRUCTURE
requires 6b to sit at or above arm-6's own elevation.  The map is
exhaustive over x6b in [300,450] step 5 (pinned).

## Collection-day chain (zero decisions)

result -> tools/import_queue_result.py -> harness VERDICTS
cross-check -> committed dispersion tool cross-check on the real
6-arm set -> branch map reading -> blog ONLY if BLOCK_STRUCTURE
lands (a demolition of the ladder's pooling premise would be a
genuine milestone; WINDOW_NOISE and AMBIG_MIDDLE are dispute
resolutions, not milestones).

## Honest boundaries

- Two fresh arms are two more tests; the primary map is exhaustive
  over the (q6, qF6) sign pattern and the control is a recorded
  label, so no unplanned comparison can be promoted post hoc.
- AMBIG_MIDDLE is a real outcome, not protocol failure.
- This probe adjudicates the OBSERVED arm-6 elevation only; block
  effects smaller than ~0.02-0.03 in rate remain undetectable at
  n=500 per arm (tick-98 boundary carried forward).
- Submission is deliberately deferred to the next tick (tick-99
  adoption consumed this tick's box); the pre-registration above is
  complete and frozen — the next tick submits, collects, and
  appends the addendum with zero design decisions.

## Collection addendum (tick 101, SON-4931, run e77d144a)

Job hxq-3a6099bef8caf34b (paperclip-test, 1 cpu / 1 Gi / 2400 s;
admitted 13:04:04Z, finished 13:04:44Z, exit 0; run.out sha256
99a093bb).  Disclosure: first attempt hxq-73b32c3a5f17ffce failed on
a command-path error (archive mounts at /work/source, command ran
relative to /work -> file not found, exit 2, no data consumed);
resubmitted with the `source/` prefix on the byte-identical archive
blob e07ab8f0.  Infrastructure fix only — arms, seeds, and the
frozen reading map untouched.

**CAL: 260261107 reads exactly 367:131** at the w4 mid-window census —
the DW9 -> VH -> w8 -> growth -> arb5 -> line -> blockprobe identity
chain holds on its sixth queued run.  Verdicts cross-check: q6, qF6,
qF8 and the branch/control labels were recomputed independently from
the raw counts in this run and match the harness exactly.

**Datum.**

| arm | census | share | Wilson-95 | test |
| --- | --- | --- | --- | --- |
| ARM6B (6's block, next window) | 372:500 | 0.744 | [0.70399, 0.78029] | q6 0.07557, qF6 0.87852 |
| ARM8 (mid-stride control) | 391:500 | 0.782 | [0.74373, 0.81597] | qF8 0.03634 |

**Branch: AMBIG_MIDDLE** (q6 >= a AND qF6 >= a; frozen map, no
default).  **Control: HOT_NEIGHBORHOOD** (qF8 < a with x8/n8 above
the family mean) — recorded WITH the primary branch per the frozen
chain; it never overrides it.

Reading, weighed exactly as pre-registered:

- 6b, arm-6's own block and the adjacent window, returned to the
  family mean (0.744 vs family 0.74049; qF6 0.879) and is only
  marginally consistent with arm-6's own elevation (q6 0.0756 —
  above alpha, inside AMBIG, nowhere near a reproduction).
- The never-used mid-stride control window read 0.782 — as hot as
  arm-6 itself (qF8 0.0363).  An arbitrary unaligned window can
  read hot.
- Together: the elevation phenomenon is not reproduced within block
  340261107's next window, and it is not specific to that block
  either.  Both pre-registered accounts stand; the probe is
  underpowered to separate them, exactly what AMBIG_MIDDLE means.
  The pre-registered honest note that x6b = 389 would have read
  AMBIG_MIDDLE (not BLOCK_STRUCTURE) was never exercised: 6b did not
  sit at arm-6's elevation.

**Descriptive (labelled, no gates):** the 6-arm LOO dispersion over
[(375,500),(370,500),(389,500),(365,499),(372,500),(391,500)] reads
min_exact_p 8.892422e-02 -> POOLING_SUPPORTED, cross-checked EXACT
against the committed w8_dispersion_receipt tool.  Per the frozen
boundaries this cannot be promoted post hoc: the tick-99 4-arm
CONTESTED receipt stands, and the pooled line datum 1235/1652 stays
REPORTED-NOT-CLAIMABLE.

**Zero design decisions taken.**  No blog (AMBIG_MIDDLE is a dispute
resolution, not a milestone).  The next instrument is the next
tick's pre-registration, now with these numbers in hand: window-level
heavy tails (two hot windows out of six full-n windows) and the
~0.02-0.03 rate-resolution boundary are the facts any successor
instrument must engage.
