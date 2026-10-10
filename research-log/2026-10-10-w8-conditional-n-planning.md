# W8 exact conditional test: sample-size planning grid

Date: 2026-10-10 · SON-4959. This is a prospective design-calibration simulation, not a new kinetic result or a reanalysis of the observed six-window outcome.

## Frozen design and execution

The preregistration is `research-log/2026-10-10-w8-conditional-n-planning-prereg.md` (commit `6b6cc26`). The analysis runner and four contract tests were committed before data generation; a direct-run import-path correction was committed as `cd11244` before the successful run. The first invocation stopped at import with `ModuleNotFoundError` before entering the runner; I verified that no receipt existed, fixed the root-path setup, and only then ran the fixed grid. There were no partial draws or replacement seeds.

The frozen alternative uses six equal groups with `p0=1110/1499`, two hot windows at `p0+δ` and four baseline windows, with δ=.01/.02 and n=2,500, 4,000, 5,000, 7,500, 10,000, 15,000, 20,000, 25,000, or 30,000 pair-terminal Bernoulli outcomes per window. Each of the 18 cells has 100,000 independent PCG64 datasets with the preregistered seed. The decision rule scans the two most extreme of 15 pairs, applies the exact conditional hypergeometric upper tail and Bonferroni correction, and rejects at adjusted p<.05.

## Results

The table gives the smallest tested grid point whose **pointwise Wilson 95% lower endpoint** clears the power target; the prior tested point is included to show the grid bracket. This is not an exact minimum-n guarantee and does not interpolate between grid points.

| δ | Target | Previous tested n; Wilson-95 | First tested n clearing target; power estimate (Wilson-95) |
|---:|---:|---|---|
| .01 | 80% | 15,000; [.72386,.72938] | 20,000; .86173 [.85958,.86386] |
| .01 | 90% | 20,000; [.85958,.86386] | 25,000; .93658 [.93505,.93807] |
| .01 | 95% | 25,000; [.93505,.93807] | 30,000; .97325 [.97223,.97423] |
| .02 | 80% | 4,000; [.76114,.76640] | 5,000; .86718 [.86506,.86927] |
| .02 | 90% | 5,000; [.86506,.86927] | 7,500; .97299 [.97197,.97398] |
| .02 | 95% | 5,000; [.86506,.86927] | 7,500; .97299 [.97197,.97398] |

At n=5,000 the fresh-seed power estimates (.24784 for δ=.01; .86718 for δ=.02) overlap the prior tick's pointwise Monte Carlo intervals. Under this model, a 1-percentage-point two-window shift needs 20k/25k/30k tested pair-terminal outcomes per window to clear the 80/90/95% lower-bound criteria; a 2-point shift clears 80% at 5k and 90%/95% at 7.5k. These figures are design sensitivity only, not a wet-lab protocol or a prediction about physical replicates.

The full 18-cell receipt is `evidence/2026-10-10-w8-conditional-n-planning/grid.json` (SHA-256 `285e75b485f0ac83eff2505094d1f5e1ac27bc9670290385143f166cdf4a85a0`). A separate `environment.json` records Python 3.11.2, NumPy 2.4.6, and SciPy 1.17.1; those versions were captured immediately after the run from the same interpreter because the runner did not embed them in the raw grid receipt. The fixed SciPy tail cross-check again matched the exact integer helper at 0.165759251604651.

An independent design critique found the reduction to the two largest counts valid only for these equal denominators, and flagged that the original single-point SciPy/integer cross-check did not test the rejection boundary. I independently compared SciPy and exact-integer tails at `(N,K,m)=(30000,22111,10000)` for adjacent observed counts 7468 and 7469; they agree (0.0033853421 and 0.0031109385), straddling the raw `0.05/15` cutoff. The committed regression test pins these exact-integer tails and the corresponding non-reject/reject decisions without importing SciPy, because hosted CI is deliberately stdlib-only. This is a post-run implementation guard; it does not alter or rerun the frozen simulation or raw receipt.

## Limits and disposition

Assumptions remain a fixed known baseline, equal denominators, independent binomial pair-terminal outcomes, and exactly two elevated windows. Wilson intervals quantify Monte Carlo error only and are pointwise, not simultaneous across cells. Nothing changes the observed `HETEROGENEITY_NOT_DETECTED` result, and this provides no inference about physical replicates. No new kinetic trajectories, cluster job, wet-lab activity, blog post, external contact, or paper/preprint submission was performed.
