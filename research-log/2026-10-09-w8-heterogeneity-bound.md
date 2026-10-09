# Secondary bound for the six-window heterogeneity result

Date: 2026-10-09 · SON-4945. This is a secondary, post-result analysis of the already collected tick-103 data; it does not alter the registered primary verdict and uses no new trajectories.

## Question and method

The registered primary test found `HETEROGENEITY_NOT_DETECTED` for six fresh w8 seed windows: Pearson X²(5) = 2.7713095514, p = 0.7351922075, with pooled D2T share 22,111/29,989 = 0.7373036780. Non-detection is not proof of identical windows.

We inverted the same noncentral-chi-square approximation used by the preregistered power calculation. For observed X² = 2.7713095514, the nominal one-sided 95% upper endpoint for noncentrality under that approximation solves

`P_lambda(χ²_5 <= 2.7713095514) = 0.05`,

which gives λ_upper = 4.9873176113. Mapping that endpoint through the preregistered alternative—four windows at the historical family rate p0 = 1110/1499 = 0.7404936624, two at p0 + δ, six equal-n windows with n=4,998—gives δ_upper = 0.0119319116 (about 1.19 percentage points). Recomputing with the six observed denominators (4,996–4,999) and all 15 possible hot-window pairs gives endpoints from 0.0119312089 to 0.0119324208; the equal-n approximation changes the endpoint by less than 0.00000071. At δ=0.02, the same approximation assigns only 0.0018829 lower-tail probability to an X² this small; the planned upper-tail detection power for that alternative was 0.8419.

Implementation: `tools/w8_window_heterogeneity_bound.py`; regression pins: `tests/test_w8_window_heterogeneity_bound.py`. The function reproduces the registered six counts and independently inverts the frozen power tool's noncentral-χ² survival function.

## Interpretation limits

This is a model-conditional secondary bound, not a general bound on arbitrary window-to-window variation. The four-baseline/two-hot pattern was part of the preregistered power design, but this confidence-bound inversion is post-result and exploratory; its “95%” is nominal under the selected asymptotic model, not a new confirmatory claim. It treats historical p0 as fixed even though 1110/1499 has plug-in standard error about 0.0113, comparable to δ_upper; thus δ_upper is not an unconditional confidence limit for an unknown baseline. The equal-n approximation itself is negligible: size-weighted inversion over the actual denominators and all 15 hot-pair placements changes the endpoint by less than 0.00000071. The noncentral-χ² law is asymptotic, not an exact finite-sample confidence interval. The observed pooled rate 0.73730 is below p0; the endpoint alternative implies pooled rate about 0.74447, so this is a heterogeneity-only sensitivity bound, not a fit to the absolute rate. It does not constrain a common shift of all six windows, other heterogeneity shapes, or physical molecular replicates. Do not replace the primary verdict or claim the windows are identical. No blog or external claim is warranted pending independent review.

## Related work check

Mohammed, Czeizler & Czeizler, “Computational modeling of the kinetic Tile Assembly Model using a rule-based approach” (2017 preprint), https://research.cs.aalto.fi/nc/papers/ktam_modelling_2017.pdf, compares an NFsim/BNGL rule-based kTAM model with Xgrow and averages stochastic outcomes over 30 runs at a fixed 100-second horizon (pp. 12–15). The reviewed pages do not report seed identities, between-seed variability, or alternative observation windows. That makes this study's seed-window question a narrower simulation-reproducibility extension, not a claim about physical replicates. The authors are a related-work lead; no external contact was made.

## Next

Keep the registered six-window verdict intact. If testing a different heterogeneity shape, preregister that alternative and its sample plan before collecting any new trajectories; do not reuse these data as a fresh confirmatory sample.
