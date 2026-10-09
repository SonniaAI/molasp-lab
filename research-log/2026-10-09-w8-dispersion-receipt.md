# w8 stage-3 per-arm dispersion receipt — pre-registered before the datum (tick 93)

Tick 93 (2026-10-09 ~05:15Z). This landing adopts the WIP left by the
failed run 89dbfc0f (openclaw_gateway_wait_error — harness wait
failure, not a content failure): the two files were re-verified against
their own live output (measure-then-pin discipline re-applied) before
committing, and the tick numbering was corrected to 93 (no tick 93
existed when the WIP was written; last landed commit was tick 92,
e176147).

## What this is

The tick-92 census policy (tools/w8_census_policy.py) fixed the
collection-day growth ladder mechanically and named a stage-3 receipt —
per-arm dispersion — without anything that produces it. This tick lands
the generator, still BEFORE any pooled w8 datum exists:

- `tools/w8_dispersion_receipt.py` — given per-arm census counts
  (x_i, k_i) (one arm = one queued 500-terminal census run), prints a
  dispersion receipt: per-arm p_hat_i, the pooled p_hat, a
  leave-one-out pooled p_hat per arm, and a two-sided EXACT binomial
  p-value per arm (point-probability method, log-space) testing each
  arm against the pool of the OTHER arms only. Leaving the tested arm
  out is deliberate: testing an arm against a pool that contains it
  would shrink its own surprise.
- Pre-registered mechanical rule (fixed before the datum):
  `POOLING_CONTESTED` iff min_i p_i < alpha (alpha = 0.05 default,
  fixed now); `POOLING_SUPPORTED` otherwise. No chi-square statistic —
  the ladder pools 2–6 arms, so an asymptotic dispersion statistic
  would be decoration; the exact per-arm tests carry the whole rule.
- Refusals: malformed arms, x outside [0,k], k<=0, fewer than 2 arms,
  alpha outside (0,1) — all exit 2 with REFUSED on stderr.

## Measured (canonical-lineage cross-checks, pinned in tests)

- Two-arm canonical pair `417:500 407:500`: pooled 0.824000;
  leave-one-out identities hold (each arm tested against the other
  only); exact two-sided p 2.747402e-01 / 2.294052e-01;
  min_exact_p 0.2294052 → POOLING_SUPPORTED. The two canonical
  census points from tick 88/91 do NOT contest pooling at alpha 0.05.
- Wild-arm control `417:500 417:500 250:500`: wild arm
  p = 3.030544e-66 vs the clean leave-one-out pool 0.834 → CONTESTED;
  the normal arms are themselves contested against the polluted pool
  (6.212780e-17) — the receipt detects the outlier from BOTH sides,
  which is the diagnostic we want at stage 3.
- Identical arms: p = 1.0 (whole mass), SUPPORTED.
- alpha is the whole rule: same min_exact_p at alpha 0.05/0.50 flips
  the verdict — pinned so nobody later "tunes" alpha quietly.

## Authority (unchanged)

NONE over the science. This tool adjudicates only the iid pooling
assumption behind the ladder arithmetic (tick-91 assumption 1). A
CONTESTED receipt voids the arm math and triggers the stage-3
escalation path with a recommended size — it never HELDs/REFUTEs the
substrate. The frozen collector (tools/collect_w8.py) and the atlas
(tools/w8_decision_atlas.py) remain the only collection-day verdict
surfaces.

Caveats pre-registered in the module docstring: arms are few, the
per-arm tests are not independent (they share one pool), no
multiplicity correction — alpha is a planning convention in the
tick-92 spirit.

## Queue state at landing (operational, not science)

Waiter ed50c7ba…4daa85 probed ~05:11Z: STILL QUEUED (reason verbatim:
ci admission floor; 1500m cpu must stay free on spark-4a06 for 2 x 500m
ci runner slots + listener/burst slack; age ~6.1h; command re-verified
in record). No resubmit. SON-4895 (PE escalation) is blocked on the
single operator step tracked on SON-4889 (restart deployment
cluster-job-queue in ns hx) — PE engaged substantively at 03:33–04:19Z
(path 1 rejected with reasons, path 2 AC3 probe executed); no duplicate
escalation fired this tick.

## Suite

Exact CI command `python3 -m unittest discover -s tests -v`:
`Ran 623 tests in 7.211s / OK (skipped=1)` = 613 + 10 new pins in
tests/test_w8_dispersion_receipt.py (all ten test names verified in the
verbose output per the collection-guard rule).
