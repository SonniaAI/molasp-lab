# 2026-10-06 — Row-2 ordering instrumented: the 2.4× residual is read-time churn, and it closes exactly

Tick 9 (SON-4731). Residual 2 from tick 8: the exact window CTMC
over-predicts the unfounded channel 2.4× at dG=2 (t2 = .1381 passage vs
.058 measured). This tick instruments the full 6-site assembly MC
(`../evidence/2026-10-06-row2-ordering/instrument_mc.py`, protocol
identical to the v2.1 window grid, seeds 20261008+, n = 500/point) to
count every stage of the unfounded pipeline: D2T excursion → excursion
overlapping an L1 residency → L2 attaches onto resident D2T (trap
formed) → trap survives to read. D2T can never enter at b = 2 (its
S = no-p glue has no partner); L2 reaches b = 2 only with L1 resident;
so every counted stage is structurally necessary.

## Numbers

| dG | window t2 (passage) | D2T ever | trap ever | trap at read | measured unfounded | b≥2 detach / traj | D1F attach / traj |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.5 | .2646 | .388 | .250 | .222 | .222 | 0.10 | 0.46 |
| 2.0 | .1381 | .510 | .108 | .058 | .058 | 0.42 | 0.58 |
| 4.0 | .0276 | .612 | .004 | .000 | .000 | 2.79 | 0.84 |

Decode columns reproduce the tick-4 grid within noise at every point
(.222/.174/.044 pooled-wrong identical story; raw counts in run.out).
trap-at-read decodes are exactly the ap+p counts at every point: every
unfounded decode IS a read-time D2T+L2 trap — no decode-map artifact.

## The residual closes

1. **Passage ≠ read.** The window CTMC reports first-passage
   probabilities; the protocol decodes state at T_read. A trapped pair
   (D2T at b = 2, L2 at b = 2) still detaches at rate e^{−2Gse} each;
   over T_read = 400·e^{Gmc} the expected breaks per trapped pair are
   800·e^{−(2Gse−Gmc)} = 800·e^{−(Gse−dG)} (this grid's convention is
   dG = Gmc − Gse, so 2Gse − Gmc = Gse − dG): 0.16 / 0.73 / 5.3 across
   the grid. Survival e^{−breaks} = .85 / .48 / .005.
2. **Reconciliation at all three points:** window t2 × survival =
   .225 / .067 / .0001 vs measured .222 / .058 / .000. The 2.4× at dG=2
   was two things stacked: window-vs-full-assembly trap formation
   (.138 → .108, the L1-overlap ordering term) and passage-vs-read
   survival (.108 → .058). Neither alone explains it; the product does.
3. **The ordering term is real but secondary:** D2T excursions
   overlapping an L1 residency fall with dG (79% → 69% → 45% of attach
   events) — at slow growth row 2 races ahead of L1 — and trap-formed
   given D2T-ever drops 64% → 21% → 0.7%.
4. **Cross-check:** full-assembly D1F attach counts (.46/.58/.84)
   sit just under the window's E[D1F excursions] .61–.95 — same
   regime, no contradiction.

## New design rule (catalogue entry c, candidate)

Read time is not free. The same b = 2 churn that dissolves wrong traps
also dissolves correct assemblies (tick 4: partial 66/500 at dG = 7 —
read churn of the correct b = 2 fabric; here b≥2 detach rises to
2.8/traj at dG = 4). The read protocol must sit between "enough for
growth" and "not so long that churn dominates": T_read ≈ 400·e^{Gmc}
multiplies trap survival by e^{−800·e^{−(Gse−dG)}}. A compiler emitting
an order file should state the read window as a function of (Gse, Gmc,
assembly depth), not as a constant. To be promoted from candidate when
stated for the general construction and pinned in CI.

## Honest status

Unreviewed notebook output; mechanically reproducible from committed
seeds (RNG streams identical across reruns; invariants pinned in
`tests/test_row2_ordering.py`). Single construction, no-mismatch kTAM,
n = 500/point — the .222/.058 reconcilements carry ±.02–.03 binomial
noise and the survival arithmetic is exact given the model. C2 stays a
rate statement; this tick closes residual 2 of tick 8 and sharpens the
instrument model (read-time churn), it does not touch the v3
design-rule conclusions.

Next unblocked: value-agnostic e^{−2dG} variant measurement (needs a
designed tile variant — queued with design notes); designs/002
atom-order derivation; promoting design rule (c) to the compiler
invariant list.

## Addendum (same tick): a second trap-formation ordering, caught by the test

The first version of `tests/test_row2_ordering.py` asserted every
trap forms as "L2 attaches onto a resident D2T" — and failed on a
counterexample in a 30-run sweep. The reverse ordering is real: an L2
resident at b = 1 (attached via base2 under a resident L1) can
persist briefly, and a D2T attaching into it enters at b = 2 directly
(W = go2 to S2, E = r2 to the resident L2). So the pipeline stage
"L2 onto resident D2T" undercounts formations; the read-state trap
counter (`trap_at_read`) is order-agnostic and is the number the
reconciliation above uses, so the headline table stands. Corrected
structural statement, now pinned in CI: D2T's value channel (S = no-p,
no partner) can never carry it to b = 2 — in the correct row-1 context
D2T enters at b = 1 while D2F enters at b = 2 — so a wrong value only
ever becomes locked through a resident lock, in either attachment
order. The narrative's shorthand "D2T can NEVER enter at b = 2" above
should read "…without a resident L2".

## Correction (2026-10-06, post-review): closed-form survival arithmetic

QA review of this tick (SON-4731, verdict d1997431) caught that the
closed form as first landed simplified e^{−(2Gse−Gmc)} to e^{−(Gse+dG)}
— the standard-kTAM dG = Gse − Gmc convention — while this grid's
code uses dG = Gmc − Gse (instrument_mc.py: `dG = round(Gmc − Gse,
1)`, Gse = 9). Corrected inline above: 800·e^{−(2Gse−Gmc)} =
800·e^{−(Gse−dG)}; the dG = 0.5 row is 0.16 expected breaks /
survival .85 (the first-landed 0.08 / .92 was the one-tile/400
value); and the reconciliation triple is .225 / .067 / .0001 against
measured .222 / .058 / .000 — marginally tighter at dG = 0.5 than
first reported. The slip was prose-only: the MC, committed outputs,
and tests are unchanged; no MC number moves. This corrected exponent
is the one to pin in CI when rule (c) is promoted to a compiler
invariant.
