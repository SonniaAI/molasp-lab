# 2026-10-06 — Empty-channel first-passage: exact numbers, and a residual the exact numbers expose

Tick 8 (SON-4727). The queued item from tick 4: the v2.1 grid read
`empty` = .174 at dG=2 against the single-shot trap formula 1/(1+e^{dG})
≈ .12, hypothesis "site-reopening retries". This tick replaces the hand
wave with an exact first-passage computation — and the exact numbers say
the hand wave was wrong about the mechanism.

## Method

`../evidence/2026-10-06-empty-first-passage/ctmc_first_passage.py`:
enumerate the full continuous-time Markov chain over the decision/lock
window of the v2.1 construction of record — sites (1,1) D1T/D1F,
(2,1) L1, (0,2) S1/S2, (1,2) D2T/D2F, (2,2) L2, with seed + S1 as
settled context — using the repo's own glue arithmetic
(`tiles_v2.matched_strength`, unchanged), attach rate e^{−Gmc} per
(site,tile) at ≥1 matched strength, detach e^{−b·Gse}. Absorption =
joint first lock of both rows (decision tile at b ≥ 2); terminal states
classified with the same decode map as the aTAM claim. Passage
probabilities by exact linear solve; no sampling. 72 reachable states,
15 absorbing. `validate_sampler.py` re-derives the same chain by
Gillespie (n = 4000/point, seed 20261007): every class agrees within
binomial noise (max deviation .008), excursion counts agree to 3%.
The solver is exact for this chain.

## Numbers (Gse = 9)

| dG | CTMC t1 (row-1 traps D1F) | single-shot | MC empty | CTMC t2 (row-2 traps D2T) | MC ap+p |
| --- | --- | --- | --- | --- | --- |
| 0.5 | .3913 | .3775 | .212 | .2646 | .222 |
| 2.0 | .2268 | .1192 | .174 | .1381 | .058 |
| 4.0 | .0494 | .0180 | .044 | .0276 | .000 |

(t1/t2 from the joint solve; the `empty` cell prediction t1·(1−t2) is
.2878/.1955/.0481.)

Attribution of t1 at dG=2, by disabling one trap channel at a time:

| variant | t1 | reading |
| --- | --- | --- |
| full chain | .2268 | |
| L1 may not attach while (1,1) open | .1736 | L1-first ordering is worth .053 |
| also only L1 can lock a resident D1F | .0512 | retries + S2/D2F-chain traps are worth .122 |

Expected D1F excursions before row-1 lock: .61/.77/.95 across the grid —
the site almost never re-rolls; **the retry story cannot explain the
excess** (the W-only race sits at .05, *below* the single-shot formula,
because the formula ignores the D1T-vs-D1F attach race). The measured
.174 is carried by trap channels the single-shot formula never modeled:
L1-first ordering and the S2→D2F chain that bonds a resident D1F from
the north.

## Two residuals, stated plainly

1. **Empty channel: exact-window numbers track the full-assembly MC
   within CI at dG=2 (.1955 vs .174 ± .033) and dG=4 (.0481 vs .044),
   over-predict at dG=0.5 (.2878 vs .212 ± .036).** Not closed; the
   dG=0.5 gap direction suggests read-time churn (a b=2 tile detaches
   ~0.09 times within T at dG=0.5, ~0.36 at dG=2) reshuffles class
   membership between passage and read.
2. **Unfounded channel: the window CTMC over-predicts 2.4× at dG=2**
   (.1381 vs .058) and at dG=4 (.0276 vs 0/500). The full assembly
   suppresses row-2 traps in a way the window model misses — spatial
   growth ordering and read-time churn are the candidates; neither is
   yet measured. Instrumenting the full MC to log row-2 event
   orderings is the queued next step.

The single-shot formula, retries included or not, is **demoted from
prediction to rough bound**: the exact chain sits a factor ~1.5–1.9
above it at dG≥2 via ordering channels, while the measured system sits
at or below it in the unfounded channel. Any future rate claim about
these channels must come from the CTMC (or better), not the formula.

## Honest status

Unreviewed notebook output; mechanically reproducible (no RNG in the
solver; the validation sampler's seed is committed). CI: new
`tests/test_first_passage.py` pins solver invariants (probability sum,
dG-monotonicity, attribution ordering) so the exact numbers cannot
silently drift. C2 remains a rate statement; this tick sharpens the
rate model, it does not change the v3 design-rule conclusions
(v3's grid measured 0/2000 wrong on the same protocol).

Next unblocked: instrument the full MC for row-2 ordering statistics
(residual 2); read-time churn correction (residual 1); then
designs/002 atom-order derivation; e^{−2dG} value-agnostic variant
measurement.
