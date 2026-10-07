# 2026-10-07 — Recombination mechanism of the row-scope survivors (tick 33)

Run: SON-4778 tick 33 (run 53083909). Pre-registration commit
`3fa1b4a` (pushed before submission); job `hxq-e38ad7f3d5f377b9`,
request `e38ad7f3d5f377b9345dd9f376f49208508e0e8af2a6fb724369808a0404b957`,
archive blob `4684430d9030cd7d0a7a60717a74b736b8a9c1821a5365bb38f99fb94a78d67a`
(= sha256 of the tarball built from HEAD `3fa1b4a`), image
paperclip-test, 1 core / 1 GiB / 3600 s, executed on spark-4a06 in
27 s, exit 0, image verified. Receipt: `queue-receipt.json`; raw
output: `recombination.out` (this directory).

## Question

Tick 31 falsified the row-scope elimination reading: the read-block
survives at 0.144 and STABLE (b>=2) D2T repair of the Vp vacancy
survives at 0.162 over all terminals (family: 0.908) — with no
history in the instrument. Tick 33 asks the mechanism question: is
the surviving channel cooperative recombination — the n=8 tick-30
smoke's D2T+Vp mutual pair — or a solo/intrinsic hold the static
census under-counted?

## Instrument

4 arms (BUILD1 x {family,row} x {plain,Vp-missing}), n=1000/arm at
dG 0.5, protocol of record (Gse 9, Gmc 9.5, T_read 400 e^Gmc,
no-mismatch kTAM, per-run RNG), fresh seed base 100261107 stride
2e7. Per-trajectory history: first passages (D2T@(2,2); any
non-L2@(3,2); Vp@(3,2)), t_stab (first moment D2T@(2,2) reaches
matched b>=2) with partner snapshot, cumulative stable dwell, and
read-time per-partner bond decomposition by neighbour removal
(partner contribution = matched b minus b recomputed without that
partner; load-bearing = removal drops the hold below b=2).

Pre-registered gates H1/H1b/H1c/H2/H3/H4 with falsifiers are in the
script header at `3fa1b4a` (also the job's first output line).

## Machine verdicts (final line of the receipt)

- **H4 CALIBRATED** — row_build1 blocked 0.141 (ref 0.144, dev
  0.003), row_Vp stable fill 0.155 (ref 0.162, dev 0.007),
  family_build1 blocked 0.273 (ref 0.27, dev 0.003); secondary
  family_Vp stable fill 0.886 vs 0.908 (dev 0.022). All
  interpretable.
- **H1 FALSIFIED (lb_any 0.0129, n=155)** — the row_Vp stable
  channel is NOT a 2-bond mutual pair with a single load-bearing
  partner. b22 histogram: {2: 2, 3: 153} — 98.7% of stable holds
  are THREE-bond stacks: N->DAr (squatter @2,3, 153/155) +
  S->V0p (canonical vertical relay @2,1, 155/155) + W->S2
  (squatter @1,2, 155/155). Removing any single partner leaves
  b=2: the hold is 2-of-3 REDUNDANT, so no partner is
  individually load-bearing (the two b=2 leftovers carry the
  0.0129).
- **H1b CONFIRMED (lb_noncanon 0.0485, n=886)** — family_Vp
  stable holds are canonical-bonded: 711/886 are the classic b=2
  holds E->L2 (711) + S->V0p (668); 170 reach b=4 by ADDING the
  same N/W relays, as luxury not necessity.
- **H1c FALSIFIED as gated (0.0129)** — but the descriptive
  partner table shows the squatter relays DAr and S2 participate
  in 153/155 and 155/155 holds respectively; they are
  non-essential singly, essential jointly. The registered gate
  (single load-bearing non-canonical partner) was the wrong
  operationalization of "squatter-mediated"; the receipt's full
  table carries the truth.
- **H2 NO_EVENTS (n_pair=0)** — in row Vp-missing, (3,2) is never
  squatted at all (ever_noncanon32 = 0.000 over 1000): with Vp
  absent and row scope killing every other lock-W match, the
  smoke's D2T+Vp pair is structurally unavailable in this arm.
  The surviving channel re-routed to the N/S/W relay stack.
- **H3 FALSIFIED as gated (0/141), refined in truth** — the row
  read-block (141/1000 = 0.141) is the **Vp@(3,2)+DBr@(3,3)
  vertical lock stack**: 141/141 co-occurrence (and V0p@(3,1)
  zero, reproducing tick 31). D2T@(2,2) co-resides stable in
  142/1000 as its own b=3/4 stack, E-bonded to Vp in 141/142 —
  but removing D2T leaves Vp bonded to DBr, so the west pair is
  not load-bearing for the block (mutual_pair_link 0). Tick 32's
  static reading "the read-block IS the {west D2T -> Vp} pair
  class" is kinetically refined: the load-bearing pair is the
  VERTICAL stack; D2T is a co-stacked west neighbour.

## Findings

1. **The row-scope repair channel is a redundant cooperative
   stack, not a pair.** One canonical vertical relay (S->V0p,
   row-scope-qualified on both faces) plus two squatter relays
   (N->DAr on DBr's site, W->S2 on D2T's own site), any two of
   which hold the tile. Notably E->L2 — a bond of the FAMILY
   channel — appears in ZERO row_Vp stable holds: row scope kills
   it (D2T's east glue is value-family shared), which is exactly
   why the census read "repair bonds 2->1" and why the channel
   had to recombine to survive.
2. **The row read-block and the row repair channel are the same
   geometry.** The blocked class is a cooperative stack around
   the (2,2)/(3,2)/(3,3) junction: DBr@(3,3) over Vp@(3,2) over
   the D2T relay stack west. 141/1000 exactly; no other squatter
   class fires.
3. **Redundancy is why the knob failed.** Row scope killed every
   canonical single bond it aimed at (E->L2: 0/155; V0p@(3,1)
   squat: 0/141) yet both channels survive by recombining three
   b=1 relays. "Static elimination is not kinetic elimination"
   (tick 31/32) now has its mechanism: 2-of-3 redundancy is
   invisible to a per-bond census.
4. **Speed (reported, unregistered):** row stacks stabilize early
   (mean t_stab 2.4e4 vs family 1.2e5 — the b=3 relay stack
   nucleates ~5x faster than the canonical 2-bond hold), and once
   stable, persist to read (dwell ~5.3e6 ~ T_read).

## Consequences

- designs/004: refinement note appended — d4's pair-channel
  report should add (a) the vertical lock stack class
  {Vp@(3,2) N<->DBr@(3,3)} and (b) the relay-stack class around
  the substitution vacancy; the measured row-scope context gains
  stable-fill 0.155 with 98.7% b=3 composition. Implementation of
  the wording/report update is the next tick's d4 task.
- The honest family-vs-row trade at dG 0.5 gains a column:
  stable-repair channel *composition* — family {canonical
  2-bond 80%, canonical 4-bond 19%} vs row {redundant 3-bond
  relay stack 99%}.

## Open

- Does the relay stack survive dG growth the way the family
  channel starves (tick-24 R4)? A dG sweep of the stack channel
  is the natural next pre-registration.
- Blog candidate (genuine milestone): "redundancy is why the knob
  failed" — pair-hazard models under-call cooperative stacking.
