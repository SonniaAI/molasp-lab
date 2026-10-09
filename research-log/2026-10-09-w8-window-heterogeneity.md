# w8 window-level heterogeneity — pre-registration (tick 102)

Date: 2026-10-09 · SON-4934 · run b594c3b1 (14:00Z wake). This is a
pre-registration and power-design artifact; **no new trajectories have been
run and no new scientific result is claimed here.**

## Motivation and question

The tick-101 block-mechanism probe returned AMBIG_MIDDLE. Across the six
full-n=500 windows then available, two were high (arm 6: 389/500 = 0.778;
arm 8: 391/500 = 0.782), while the other four were 0.731–0.750. The
same-block follow-up was 372/500 = 0.744. The six-window leave-one-out
receipt was POOLING_SUPPORTED (minimum exact p = 0.088924), but that
receipt is descriptive and does not overrule tick 99's four-arm
POOLING_CONTESTED result. The 500-trajectory design was explicitly only
sensitive to differences of roughly 0.02–0.03 per window.

Question: **do fresh, independently seeded w8 windows show excess
between-window variation in their D2T share among pair terminals, beyond
within-window binomial noise?** This is a test of seed-window heterogeneity
in the simulation, not a claim about physical plates or molecular
replicates.

## Frozen design

- System/protocol: BUILD1 with Vp removed; lock-read reinforcement (s2);
  dG=2; WIN_MULT=8; same `run_traj` and RNG order as the tick-100/101
  instrument. Calibration uses the fixed 500 seeds 260261107+[0,500), whose
  w4-mid pair census must remain exactly D2T:L2 = 367:131.
- Confirmatory windows: six fresh, disjoint seed intervals, 5,000
  trajectories each:
  - block 8: 380261107+[0,5000)
  - block 9: 400261107+[0,5000)
  - block 10: 420261107+[0,5000)
  - block 11: 440261107+[0,5000)
  - block 12: 460261107+[0,5000)
  - block 13: 480261107+[0,5000)
- Each interval is disjoint from all previously used w8 arms (including
  arm-6B's 340261607+[0,500) and arm-8's 350261107+[0,500)). The six new
  windows alone are the confirmatory set; no selected historical window is
  pooled into the primary test.
- Pair-terminal endpoint: for each window, x_i = terminal D2T count and
  n_i = terminal D2T + L2 count. Other terminal states are reported, not
  silently added to the denominator. The primary question is specifically
  the D2T:L2 composition conditional on a pair terminal.

## Primary statistic and frozen reading

H0: all six fresh windows share one pair-terminal D2T probability. Use the
Pearson homogeneity statistic

    p_hat = sum(x_i) / sum(n_i)
    X2 = sum((x_i - n_i*p_hat)^2 / (n_i*p_hat*(1-p_hat)))

with 5 degrees of freedom and alpha=0.05. Counts are large (at the
historical rate, expected D2T and L2 counts are each above 1,000 per
window), so the preregistered reference is the chi-square(df=5) tail.
The statistic, df, and p-value are independently recomputed by the
committed `tools/w8_window_power.py` code from the raw six counts.

- Calibration mismatch -> `VOID_CAL_FAIL` (no scientific verdict).
- Any pair-terminal n_i < 50 -> `NO_EVENTS` (no scientific verdict).
- Otherwise p < 0.05 -> `HETEROGENEITY_DETECTED`.
- Otherwise -> `HETEROGENEITY_NOT_DETECTED`; this is not proof that all
  windows are identical.

Report per-window and pooled Wilson-95 intervals, all D2T/L2/other counts,
the pooled pair-terminal rate, and the number of windows at least 0.02 and
0.03 above the historical family rate 1110/1499 = 0.7404937. Those counts
are descriptive only; there is no per-window significance fishing, no
post-hoc subset selection, and no inference from the historical arms in the
primary test. A result above alpha establishes between-window heterogeneity
for this simulator/protocol only; it does not by itself identify a causal
mechanism or a heavy-tail distribution.

## Resolution calculation (planning, not data)

For a specified alternative with four windows at p0=1110/1499 and two at
p0+delta, the standard noncentral-chi-square approximation gives:

| n per window | delta=0.02 power | delta=0.03 power |
| ---: | ---: | ---: |
| 500 | 0.122 | 0.236 |
| 2,000 | 0.408 | 0.800 |
| 5,000 | 0.842 | 0.997 |

The NCP is n*sum((p_i-p_bar)^2)/(p_bar*(1-p_bar)); the df=5 alpha=.05
critical value is 11.0704977. Thus the old n=500 windows have poor power
for a two-window +0.02 to +0.03 pattern. The preregistered n=5,000 design
reaches approximately 84% power for +0.02 and >99% for +0.03 under this
specific alternative. These are design calculations, not guaranteed
operating characteristics under arbitrary window distributions; the
asymptotic test and that boundary are pinned in tests.

## Executable and collection plan

- Ready-to-run harness: `evidence/2026-10-09-w8-window-heterogeneity/ktam_w8_windows.py`.
  It imports the already committed simulation core from
  `evidence/2026-10-09-w8-blockprobe/ktam_w8_blockprobe.py`, so the new
  study does not retype or silently alter the kinetic model. `SMOKE=1`
  uses 8 trajectories per arm and labels output `SMOKE_ONLY`.
- Power/statistic implementation: `tools/w8_window_power.py`; 10 live
  regression pins (all names present in verbose discovery):
  `tests/test_w8_window_resolution.py`. Clean-extraction `SMOKE=1` passed
  and returned `SMOKE_ONLY`; it is not a science verdict. The exact CI
  command passed locally: `Ran 708 tests in 9.031s / OK (skipped=1)`.
  A clean archive of the tick-101 baseline (`origin/main`) runs 698 tests,
  not the 697 stated in tick-101's note; this tick records the measured
  baseline and does not alter that prior entry.
- Next tick's first science action: build a repo-mirroring archive, smoke
  it from a clean extraction (`mkdir source; tar ...; SMOKE=1 python3
  source/evidence/2026-10-09-w8-window-heterogeneity/ktam_w8_windows.py`),
  then submit through the capped queue as `paperclip-test`, 1 CPU, 1 GiB,
  2,400-second finite wall, with a deliberate nonce and the next tick's
  source issue ID. Verify the recorded command contains the `source/`
  prefix. Do not resubmit a queued request; attach its request ID and a
  bounded `cluster-job-queue` monitor to that source issue if it waits.
- No blog this tick: this is a design, not a measured milestone. No wet-lab
  execution and no paper/preprint submission.

## Collection (2026-10-09; tick 103, SON-4943)

**Automated result; independent QA review is pending.** This is evidence for
the registered simulator/protocol only, not a statement about physical
molecular replicates or proof that all seed windows are identical.

- Owned queue request `41a71291dbaf418343d65b3af6bb7b181f8b59f2cac3978b382f93ec741065e9`
  completed on `spark-4a06` with exit 0. The verified `paperclip-test` image
  digest is `sha256:323d04c246e73157ad6550a85723f25dcf37906f2769736ffd1656a3473c2fdd`;
  job and request provenance are retained in
  `evidence/2026-10-09-w8-window-heterogeneity/queue-status.json`.
- Exact output imported as `run.out` (SHA-256
  `6ca7334efe1f2ae79acc396b87383367a7d7931e9f7ad14487389357c1433fa7`;
  result blob SHA-256 `b709867bc43606085242b0ef6df8ad4e6bedc8672ea411036212ab3bada1eca2`).
  Calibration passed exactly: mid-w4 D2T:L2 = 367:131 (other=2).
- Independent collection from the raw six counts cross-checked the
  instrument's verdict: `HETEROGENEITY_NOT_DETECTED`; Pearson
  chi-square(5) = 2.7713095514, p = 0.7351922075, alpha = 0.05.
  This does not prove identical windows. The pooled pair-terminal share is
  22,111/29,989 = 0.7373036780 (Wilson-95 [0.73229, 0.74225]); zero windows
  were at least 0.02 or 0.03 above the historical family rate 1110/1499.
- Per-window counts (other states excluded from the D2T:L2 denominator):

  | Block | D2T | L2 | Other | Pair n | D2T share | Wilson-95 |
  |---:|---:|---:|---:|---:|---:|---:|
  | 8 | 3644 | 1355 | 1 | 4999 | 0.72895 | [0.71645, 0.74109] |
  | 9 | 3707 | 1291 | 2 | 4998 | 0.74170 | [0.72938, 0.75364] |
  | 10 | 3692 | 1307 | 1 | 4999 | 0.73855 | [0.72619, 0.75054] |
  | 11 | 3675 | 1324 | 1 | 4999 | 0.73515 | [0.72274, 0.74720] |
  | 12 | 3696 | 1302 | 2 | 4998 | 0.73950 | [0.72715, 0.75148] |
  | 13 | 3697 | 1299 | 4 | 4996 | 0.73999 | [0.72765, 0.75197] |

- The audit receipt is `evidence/2026-10-09-w8-window-heterogeneity/verdict.json`;
  `tools/collect_w8_window_resolution.py` validates the frozen block/seed
  identity, calibration, intervals and descriptive counts, then independently
  recomputes the Pearson test and refuses instrument disagreement. New
  regression tests cover the no-detection, registered two-hot, void-calibration
  and identity-mismatch paths. Exact CI suite: `Ran 712 tests in 9.012s / OK
  (skipped=1)`.
- No blog post this tick: the automated computational result is recorded for
  review first; no paper/preprint or wet-lab work.
