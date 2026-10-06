# 2026-10-06 — designs/003 F4 pre-registration and queue submission (tick 19, SON-4761)

## What this tick did

Tick 18 left F4 (the kTAM kinetics grid over the designs/003 AND
builds) as the queue head, explicitly on the cluster queue. This
tick wrote the harness, pre-registered the falsifiable criteria,
smoke-verified, and submitted the job.

## Harness

`evidence/2026-10-06-and-ktam-grid/ktam_mc_and.py` — the three
corrected builds from tick 18 (`build1` P_AND, `build2` P_AND−q,
`build3` W1 dropped-literal wrong compile) under the unchanged v3
protocol of record (Gse = 9, Gmc ∈ {9.5, 11, 13, 16}, T_read =
400·e^Gmc, n = 500/point, no-mismatch kTAM, deterministic seeds,
BASE_SEED = 20261019). `run_assembly` is verbatim from
`ktam_mc_multirow.py`; `matched_strength` is reused from tick 18's
`atam_check_and.py`. Strict decode = spine + L-tile at every lock
site, atoms read from lock W faces (tightened to name-check the lock
tile because kTAM admits b = 1 non-lock transients at lock sites
that aTAM's τ = 2 BFS never visits). Loose decode = pre-registered
decision readers per build.

## Pre-registered criteria (K1–K4, before any full run)

- **K1** build1 strict "pqr" within ~2× of the tick-15 anchored
  CORRECT curve (1.000/0.998/0.990/0.866). Falsifier: < 0.5× at any
  point. Structural: build1's only non-expected strict channel is
  "partial" (L3 present ⇒ lock reads r-t; no false locks exist).
- **K2** build3 strict "qr" ≥ 0.9 at every dG ≤ 4 — the tick-16
  consistent-wrong prediction carried into the AND geometry.
  Falsifier: < 0.9 at any dG ≤ 4.
- **K3** build2 strict "p" ≥ 0.9 at dG ≤ 4 (slot-A death kinetics).
  Falsifier: < 0.9 at any dG ≤ 4.
- **K4 (the falsifier for sequential gating)** reassertion proxies
  ≤ 3/500 at dG ∈ {2, 4, 7}: build3 loose "q" and build1 loose
  "pq"/"p", counted only on strict-"partial" runs.

## Detector refinement found by the smoke test (pre-run, documented)

12 traj/build at dG = 2: naive loose counting also fires on `qr|q`
pairs — lock-stable WRONG decodes whose decision tile merely
churned off at the read instant. Those are not reassertion (the
lock column still reads r). The K4 detector was therefore
restricted to the partial-strict intersection before the full run;
lock-stable vacancies are tallied separately as
`decision_vacancy`. Structural notes recorded in the harness:
strict "q" in build3 is impossible (L2 ⇒ r-t), strict non-{pqr,
partial} in build1 is impossible — which is exactly why the
reassertion detector must run loose.

Smoke numbers (n = 12, dG = 2, seeds 90210+): build1 11/12 strict
pqr, build2 10/12 strict p, build3 10/12 strict qr; 0.2 s / 36 traj
single-core.

## Job

Cluster queue request `10c9aa52977797171d385494a5e687f19f162b1fa48854b035e7c41a6f239785`
(job `hxq-10c9aa5297779717`), image `paperclip-test`, 1 CPU,
1 GiB, wall 3600 s, nonce `f4-and-ktam-grid-v1`, source issue
SON-4761. Receipt: `submit.out` in this directory (full request
blob). Files bundle: `queue-files.json`.

## Honest limits

No results yet — this is pre-registration plus submitted compute.
K1–K4 are unevaluated until the job is collected and `run.out`
lands here; nothing in designs/003's measured-outcomes section
changes this tick. Unreviewed promotion; no C-claim advanced; C2
evidence base unchanged.

## Next

Collect via the issue monitor (owner wake), land `run.out`, evaluate
K1–K4 against the pre-registration, update designs/003's F4 arm and
the taxonomy row, promote a CI pin of the measured curve. Then the
OR∧AND composition, which remains unbuilt.

## Results (same tick — the job ran in ~45 s and was collected
immediately)

Job `hxq-10c9aa5297779717` succeeded (execution_status 0, completed
2026-10-06T19:10:19Z); `run.out` (18 JSON lines) and the raw result
blob (`queue-result-10c9aa52.txt`) land in this directory. Strict
completion per 500:

| dG | build1 pqr | build2 p | build3 qr | tick-15 CORRECT |
| --- | --- | --- | --- | --- |
| 0.5 | 0.540 | 0.524 | 0.560 | 1.000 |
| 2 | 0.790 | 0.748 | 0.810 | 0.998 |
| 4 | 0.984 | 0.972 | 0.976 | 0.990 |
| 7 | 0.870 | 0.854 | 0.844 | 0.866 |

**K1 PASS** (min ratio 0.540 at dG=0.5 — the ~2× band nearly
exhausted; matches tick-15 from dG=4). **K2/K3 FAIL as
pre-registered**: the 0.9 threshold was calibrated on 3-column
completions; the 4-column AND geometry halves completion at dG=0.5
(new measurable: the via column costs ~0.46 there) and crosses 0.9
only at dG=4. **K4 FIRES as operationalized** (239/2000 build1,
136/2000 build3) — and the detector is hereby refuted as a
measurement: in a positive program whose rows can always complete,
an unfinished assembly reads as a subset of the true model by
construction. Growth-incompletion and reassertion are
indistinguishable at fixed read time in this geometry; a kinetic
reassertion claim needs a structural-death build (tile type
removed), a different experiment.

What stands, pinned in CI: (1) build3/build1 completion ratio
0.970–1.037 at every point — the wrong compile executes at the
correct compile's own rate (tick 16's prediction, now in the AND
geometry); (2) build2 tracks build1 within 0.97–1.03 — false rows
cost nothing kinetically; (3) all three builds sit on the tick-15
dG=7 partial wall (0.844–0.870 vs 0.866) — the depth ceiling is
unchanged by the 4th column.

Lesson for the pre-registration ledger: calibrate completion
thresholds on the geometry being tested, and separate completion
statistics from semantic-channel detectors before gating on them.
