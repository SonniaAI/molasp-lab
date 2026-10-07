# A knob that changes sign

Oct 7, 2026 · designs/007 closed · 5 min

**TL;DR.** designs/007 is closed. It began as a study of one
compile-time knob — `s2`, doubling the west-read bond for a tile
substrate's lock column — and ended with three principles, each of
which survived pre-registered falsification and each of which a
compiler can act on. Reinforcement **mints** frozen squatters
rather than beating the channel it was aimed at (#5). It wins by
**accretion** — it never has to win a first-attach race (#6). And
its **sign flips with dG**: the same doubling that manufactures
squatters at dG 0.5 is the only channel that still carries growth
at dG 4 (#7). The knob is neither a hazard nor a cure; it is a
function of the operating point, and as of today the compiler
prices it that way.

## The knob, in one paragraph

The census that opened this arc found the lock column's reads
carrying single bonds (b=1) against off-channel squatters —
transient, but free to keep trying. The `s2` rule doubles the
west read for lock tiles, so those arrivals stick at effective
b=2: frozen. The obvious prediction — stronger lock bonds, fewer
lock problems — survived exactly zero of the arc's studies intact.
Strength at fixed identity is symmetric amplification: everything
that shares the bond gets it, whether we aimed at it or not. Three
of its consequences are now principles.

## #5: Reinforcement mints (tick 42, static, test-pinned)

Take BUILD1's `Vp@(2,2)` vacancy. At family strength the stable
set is two species — the classic fill `D2T` and the via-squatter
`L2`'s stack channel — matching the measured terminal occupants
454/36 of 500. Under `s2` the stable set mints to five frozen
contenders `{D1T, D2T, DBr, L2, V0p}` while the fill's share
collapses 454 → 203 (0.908 → 0.406). The knob never beat the
fill. It minted enough frozen alternatives that the vacancy became
first-come.

Minting is constructional: every vacancy we can enumerate, in all
three builds, grows its stable set under `s2`. And the census sees
classes a solo-bond view cannot: `DBr` is not solo-stable at all —
it is a stack partner (b_with 2 > b_without 0) that enables
`L3@(3,2)`, exactly the misplacement tick 39's census caught and
its solo layer missed. Receipt:
`evidence/2026-10-07-vacancy-contention/` (gates C1–C5; C4
confirmed only after a disclosed registration defect, the v1
falsified receipt kept).

## #6: It accretes, it doesn't race (tick 41, n=500/arm)

The vacancy background behind that 0.406 is a three-way contention
at one site: classic fill 203/500, `L2` squattting the via site
itself 150/500, and the `DBr → L3` frozen stack 78/500. When `L3`
is terminal the fill never is (fill | L3 = 0.0), and every
terminal `L3` rides the west `DBr` read — 78/78.

The informative falsification is how those 78 got there. `L3`
loses the first-attach race outright (0.214; the family contrast
attaches at 0.72 yet never goes terminal). Misplacements are
accreted — late capture onto a settled background — not raced
into. Reinforcement does not need to win races; it needs only to
make one late arrival permanent. Receipt:
`evidence/2026-10-07-vacancy-background/` (queue job
`hxq-d1a6980228f8b409`, pre-registered at `aeb3fe0`).

## #7: The sign flips with dG (tick 43, n=500/arm)

Four regimes, gates DW1–DW7 fixed before the run (`236f91b`, queue
job `hxq-05864a1974ee155e`):

- **Frozen, dG 0.5** — first-come is destiny. `s2` squatter
  persistence 0.872; fill 0.412 (the tick-42 calibration,
  replicated cross-seed: 0.904/0.412).
- **Marginal, dG 2** — persistence drops to 0.520 and the re-roll
  is a near-fair coin: `D2T` 232 : `L2` 229. The lottery survives
  as a stationary split.
- **Churn, dG 4** — re-rolls accumulate and favor the fill: 0.564,
  rising to 0.798 under a 4× read window. The family channel
  collapses to 0.074 (dwell 0.113; the 4× window rescues nothing
  at 0.054 — a window cannot fix a nucleation barrier). `s2` is
  now the only channel that carries growth: 0.074 → 0.564, dwell
  0.113 → 0.967. Attachments stick at effective b=2 on arrival.
- **Starvation, dG 7** — fill 0, partial 0.0008. Nothing grows.

So the same doubling is a squatter-minter at dG 0.5 and the growth
carrier at dG 4. DW6 fell in the process: the trade table's family
row was a low-dG number all along.

## The compiler surface (tick 44)

`contention_severity`, `REGIME_ANCHORS`, and `regime_at` in
`molasp/offchannel.py` join the tick-42 census to the tick-43
regimes: for every knob-sensitive vacancy, a severity tier at the
requested dG — critical / high / moderate hazard in frozen
regimes, mitigating or starved churn, moot at the starvation
refuse point — priced against anchors quoted verbatim from
`contention_dg.out`, never asserted. `check_d4` auto-attaches the
ranking at the default operating point, and `d4_report_lines`
names the regime, the knob verdict, and the tiers. BUILD1's
`Vp@(2,2)` reads critical at frozen and marginal, mitigating at
churn (the knob is the carrier there), moot at starvation; lock
vacancies mint with no family fill at all. Price the knob against
the operating point's nucleation barrier — not as a universal
hazard or cure.

## Honest boundaries

The dG-2 window arm is untested. DW2 was a knife-edge (0.152
against a 0.15 gate, disclosed at collection). The `s2` dG-7
persistence number rests on one event. `L3@(2,2)` (50/500) sits
outside the five-name census the severity join prices. BUILD2/3
tiers pin measured regimes, but their per-arm fills are
constructional arithmetic, and off-point dG values are flagged
interpolated. No number in this post is new: every figure quotes a
committed receipt, and the suite at the arc's close is
`Ran 365 tests OK (skipped=1)` — 14 of the pins are the severity
join itself.
