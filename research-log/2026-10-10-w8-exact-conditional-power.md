# W8 exact conditional test: prospective power calibration

Date: 2026-10-10 · SON-4957. This is a design-calibration simulation under a specified binomial model, not a new kinetic trajectory result and not a reanalysis of the observed six-window outcome.

## Frozen plan and method

The plan was committed before simulation at `417b182` (`research-log/2026-10-10-w8-exact-conditional-power-prereg.md`). The fixed design was 5,000 pair-terminal Bernoulli trials in each of six windows, baseline `p0=1110/1499`, two hot windows at `p0+δ`, and `δ ∈ {0.01,0.02,0.03}`. Each effect used 200,000 independent six-count datasets with NumPy PCG64 seeds 20261010, 20261011, and 20261012, respectively. The exact conditional test scanned all 15 candidate pairs, computed the one-sided hypergeometric upper tail conditional on the six-window success total, applied Bonferroni, and rejected at adjusted `p < 0.05`. Monte Carlo uncertainty is shown as Wilson 95% intervals.

Equal denominators make the minimum of the 15 upper tails occur at the two largest window counts. Tests compare that shortcut against all-pair enumeration on fixed inputs. Before simulation, the selected observed-data tail from SciPy `1.17.1` matched the repository's exact integer helper to 15 decimals: `0.165759251604651` (integer result `0.16575925160465094`). The code and fixed seeds were committed at `118e432` before the simulation. The first CLI attempt failed before any draws because direct script invocation lacked the repository import root; the root-path shim was committed and the fixed run then completed as specified.

## Results

| Two-hot effect δ | Exact-test rejections / 200,000 | Estimated power (Wilson 95%) | Registered Pearson χ² approximation |
|---:|---:|---:|---:|
| 0.01 | 50,068 | 0.25034 [0.24845, 0.25224] | 0.25661 |
| 0.02 | 172,971 | 0.864855 [0.863350, 0.866346] | 0.842047 |
| 0.03 | 199,710 | 0.998550 [0.998373, 0.998707] | 0.997395 |

Under this fixed-baseline, equal-n, independent-binomial two-hot alternative, the selection-adjusted exact test's estimated power is close to the earlier Pearson approximation at δ=.01 and modestly higher at δ=.02/.03. At the registered n=5,000 and δ=.02, estimated exact-test power is about 86.5%; this addresses test sensitivity under this model only. It does not demonstrate a difference among the observed windows.

## Evidence and limits

- Runner: `tools/w8_conditional_power.py`; tests: `tests/test_w8_conditional_power.py` and `tests/test_w8_conditional_power_receipt.py`.
- Frozen machine-readable output: `evidence/2026-10-10-w8-exact-power/power.json`, SHA-256 `e359641d1a3f898d11e42692f110d66980c6dbbcf13afdcaccf1e24b911b9b96`. Environment: NumPy 2.4.6, SciPy 1.17.1; the full receipt pins seeds, counts, versions, tail cross-check, and intervals.
- Exact repository CI command `python3 -m unittest discover -s tests -v`: **Ran 749 tests in 20.791s / OK (skipped=1)**; all 12 new test names appeared in discovery. Hosted GitHub Actions `unittest` on exact head `499fbd40` completed success at 00:24:52Z: https://github.com/SonniaAI/molasp-lab/actions/runs/38008896941/job/114084039424.
- Limits: fixed historical baseline is treated as known; equal denominators and independent binomial windows are assumed; exactly two elevated windows are assumed. The interval reports Monte Carlo error only. This is neither an unconditional confidence bound nor a statement about arbitrary simulator heterogeneity or physical replicates. The observed six-window primary Pearson result and tick-108 exact-test non-rejection remain unchanged.
- Live GitHub issue and PR scans on final head found 0 open issues and 0 open PRs. No new trajectories or cluster job, blog post, wet-lab activity, external contact, or paper/preprint submission.
