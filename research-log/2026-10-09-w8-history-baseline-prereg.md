# Pre-registration: w8 contrast bound without historical-baseline exchangeability

Date: 2026-10-09 · SON-4949. This post-result sensitivity analysis reuses the tick-103 six-window counts; it will collect no new trajectories and will not revise the registered omnibus verdict.

## Question and model

Tick 106's profile-score analysis pools the historical family count (1110/1499) with the four candidate cold windows. Test the narrower robustness question: what is the two-hot rate-difference endpoint if the historical baseline is allowed to have its own unrelated rate?

For each candidate hot pair H among the six current windows, model three groups:

- historical count: Binomial(1499, p_hist), with p_hist unconstrained relative to current windows;
- four current cold windows pooled: Binomial(n_c, p_c);
- two current hot windows pooled: Binomial(n_h, p_c + δ).

The historical likelihood factorizes through its own nuisance p_hist. Therefore it contributes no information to δ when historical/current exchangeability is removed; inference uses only the current cold and hot aggregates. The remaining model still assumes a common p_c across the four current cold windows and a common p_c+δ across the selected pair.

## Frozen analysis

For each of the 15 hot-pair assignments, aggregate the four non-hot current arms and the two hot arms from the committed `OBSERVED_ARMS` counts. Apply the existing constrained-binomial profile efficient-score inversion at z=1.6448536269514722. Report all assignment endpoints, their minimum and maximum, the hot pair attaining the maximum, and the absolute difference between that maximum and tick 106's pooled-history envelope (0.013672878393).

This is a nominal asymptotic score sensitivity, not an exact finite-sample confidence bound. No hot pair may be omitted or selected to narrow the reported maximum. The historical 1110/1499 count must not enter either current-group aggregate.

## Validation and interpretation

- Verify the source arms match the six committed counts and denominators.
- Verify exactly 15 distinct hot pairs are analyzed and that every returned endpoint inverts to z=-1.6448536269514722 within numerical tolerance.
- Pin the minimum, maximum, maximum-pair identity, and comparison with tick 106 in unittest discovery.
- If the endpoint moves, report this only as sensitivity to historical/current-baseline pooling under the specified two-hot model. Do not update `HETEROGENEITY_NOT_DETECTED`, claim arbitrary six-window homogeneity, or generalize to physical molecular replicates.
- No new trajectories, cluster job, blog, external contact, wet-lab step, or paper/preprint submission is authorized by this analysis.
