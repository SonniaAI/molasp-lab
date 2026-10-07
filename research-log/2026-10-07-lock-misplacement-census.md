# Lock-tile off-channel placement census — designs/006, tick 39

Pre-registration `1570193` (gates M1–M4, designs/006) landed before
the census ran. Receipt:
`evidence/2026-10-07-lock-misplacement-census/lock_misplacement_census.out`
(deterministic static enumeration; standing rule, no cluster job).
Machine verdicts: **M1 CONFIRMED, M2 FALSIFIED as registered, M3
CONFIRMED, M4 CONFIRMED.**

## What the new layer is

`molasp.offchannel.lock_misplacements` — the TILE-class view of the
census: every site (any class) where an `L*` lock tile that is not
the canonical occupant bonds ≥ 1 against the canonical background,
with per-face decomposition and the `w_read` flag (the face a
strength-reinforced lock read doubles). Attached to `check_d4`,
printed by `d4_report_lines`, kinetic context quoted into
`MEASURED_CONTEXT["strength2_lock_misplacements"]` (tick-38 counts:
L2@(3,3) 67, L3@(3,2) 43, 82 Vp-arm, of 500).

## Verdicts

- **M1 CONFIRMED — the solo class exists and is transient**: BUILD1
  and UNIT_ONLY each carry exactly two solo L*-placement channels,
  both bond 1, both W-read carried — but NOT at lock sites: they are
  the VIA-SITE placements `L1@(2,1)` and `L2@(2,2)` (a lock reading
  the via tile's E glue off its own row).
- **M2 FALSIFIED as registered — and the falsification is the
  finding**: the kinetically-dominant channels `L2@(3,3)` /
  `L3@(3,2)` carry **zero solo bond** in every view, under family
  AND s2 arithmetic (named channels null). They are
  one-substitution-ENABLED, not solo: the existing west-substitution
  pair layer catches them at bond 1 — `L2@(3,3)` fires via west `D2T`
  or `Vp`, `L3@(3,2)` via west `DBr` (and `L2@(3,1)` via `Vp`;
  pinned in tests). The M2 clauses that DID hold: the via-site solo
  class doubles to **stable bond 2** under s2 (L1@2,1, L2@2,2 —
  `w_read` channels), and non-L lock-site squatters never gain
  (`nonl_lock_site_max_bond` 1 in all views) — at lock sites only
  locks can gain under the s2 rule, by construction.
- **M3 CONFIRMED**: zero mismatches in all four views — the layer is
  a pure relabeling of the bond tables, classification not channels.
- **M4 CONFIRMED**: `compile_program`'s auto-attached `build["d4"]`
  carries the layer on UNIT_ONLY and MINIMAL, byte-equal to
  `check_d4`'s report.

## Interpretation

The instrument picture after tick 38 + this tick: the
L*-misplacement hazard splits into **two census layers**. The SOLO
class is via-site lock placements (W-read carried, b=1 transient at
family strength, stable b=2 the moment lock reads are reinforced —
this is a channel the kinetic squatter tables never tabulated,
because they counted lock sites only). The DOMINANT kinetic class is
lock-site lock misplacements, which need one background substitution
and therefore live in the pair layer (`lock_misreads`), invisible to
any solo arithmetic. Dominance ordering between the layers is
kinetic, not arithmetic — the census flags both; the rates stay
quoted measurement.

Principle (fourth sibling, same family as ticks 31/35/38): the
misplaced-lock hazard is carried by the glue AND by the background —
no solo-bond reading of an inventory prices it.

## Consequences

- The tick-38 consequence is delivered: the emit-time d4 census now
  flags lock-tile off-channel placements as a first-class hazard
  class, with the s2-doubling face marked; future encodings price
  against BOTH the V-classes and this class via
  `lock_misplacements` + `lock_misreads` together.
- Forward hypothesis (testable, next MC pre-registration): under the
  s2 encoding the census predicts STABLE via-site lock placements
  (bond 2) at (2,1)/(2,2) — an MC arm that tabulates via-site lock
  occupancy should see them rise against family; the tick-38 runs
  did not count that site class.
- Follow-up instrument gap (named, not claimed): the Vp-arm channel
  measured at `L3@(3,2)` 82/500 is vacancy-enabled — outside the
  solo census AND outside the west-bounded probe (same bound as
  RS1's `DBr@(3,3)`); a vacancy-background probe is the honest next
  extension.

## Honest boundaries

Census bonds are arithmetic, not rates; two systems (BUILD1,
UNIT_ONLY); the 82-channel is not covered by any current layer and
is not claimed to be; no new kinetic measurements this tick.
