# Repair-mechanism study — how the substrate repairs, and why some
# deaths beat the living build (tick 24, SON-4778)

Card: SON-4778. Build and receipts: `../evidence/2026-10-07-repair-mechanism/`
(trap_census.py + trap_census.out, ktam_mc_trap.py, submit.out; the
kTAM receipt lands as trap_grid.out + queue receipt after collection).
Tests: `../tests/test_repair_mechanism.py`.

## Question

Tick 23's survey measured WHICH single-species deaths repair; two
mechanism items stayed open: (i) why V0p/Vp removals EXCEED build1
parity at dG 0.5 (1.25×/1.53×) — repair cannot make a system better
than itself, so something in build1 must be hurting it; (ii) the
L3-only falsifier channel (18/500 strict "pqr" with the lock species
absent) — what reads TRUE at a lock site whose species does not
exist?

## Static half (machine-checked, exhaustive glue arithmetic)

Off-channel census (trap_census.py): against the canonical assembly
background, every (site, tile) pair bonding b ≥ 1 that is not the
canonical occupant — the misincorporation channels the no-mismatch
kTAM exposes at rate k_f·e^-Gmc each.

1. **Exactly two species squat lock sites: Vp@(3,2) and V0p@(3,1)**
   (both b=1). These are the two exceeds-parity removals. DAr, L3
   and the spine tiles have ZERO off-channel sites — their glues
   are unique; spine sites (0,1..3) admit no squatter at all.
2. **Stable substitution repairs exist**: in Vp-missing, D2T bonds
   b=2 at (2,2) (south p-t-done + east q-t to L2.W — it re-exposes
   Vp's value glue for L2's west bond); in V0p-missing, D1T bonds
   b=2 at (2,1) (west p-t + east p-t — re-exposing L1's west
   partner). Substitution repair is not a rare coincidence: the
   value-typed glue families make the D/V tiles of a row partially
   interchangeable, so a sibling tile can fill a dead value site at
   full stability.
3. **The L3-misread channel is structural**: the lock deep probe
   (one west-neighbour substitution allowed) finds L2@(3,3) bonds
   b=1 iff (2,3) hosts Vp or D2T — anything exposing a q-t value
   glue on its east face. The strict decoder reads any "-t" W glue
   as TRUE regardless of row: a lock species' absence is masked by
   a foreign L-tile held by a squatter, and D2T enables it as well
   as Vp does (a channel the tick-23 narrative missed).
4. Correction to my own hand census: D1T DOES have off-channel
   sites ((2,1),(2,2), both value-glue-mediated); only DAr/L3/spine
   are single-site species. The machine beat the notebook again.

## Pre-registration (written before the kTAM job ran; queued as job
hxq-71568fa80ca466b4, request 71568fa80ca4…, nonce repair-mechanism-v1)

Instrument: protocol of record + read-time census of all 12
canonical sites per trajectory. 8 systems (build1 + the 7 non-DEAD
removals; tick-23 DEAD rows L1/L2/S1/S2/S3 excluded, L3 kept as the
misread arm), dG {0.5, 2, 4} (dG 7 starves everywhere; tick-23
numbers stand), n=500/point, 12,000 trajectories.

- R2 (trap-relief explains exceeds-parity): conditioned on no
  read-time lock squatter, strict "pqr" at dG 0.5 of build1 /
  V0p-missing / Vp-missing agree within 0.10 [gap ≥ 0.15].
- R3a: build1 non-pqr top squatters are Vp@(3,2), V0p@(3,1)
  [any other tile top-1].
- R3b: V0p-missing pqr terminals hold D1T@(2,1) and Vp-missing pqr
  terminals hold D2T@(2,2), each ≥ 50% [majority other/empty].
- R3c: L3-missing pqr terminals at dG 0.5 hold L2@(3,3) with
  Vp-or-D2T@(2,3) in ≥ 2/3 [L2 < 50%].
- R4: build1 lock-squat rate monotone down in dG; Vp-missing ratio
  < 1 by dG 4 (trap relief vanishes while the repair channel
  starves) [non-monotone, or ratio ≥ 1].

H-ladder (the refined law this would establish): a lock tile
survives its partner's death iff it retains a cooperative face pair
of its own — L2's base-chain ladder (S+N) makes Vp's death free;
L3's only pair is S+W, and W needs DBr, which is why DBr repairs
least. Repair is the norm not because the substrate is clever but
because value-glue families make tiles interchangeable; the price
of that interchangeability is the row-agnostic "-t" misread.

## kTAM half

**v1 run (job hxq-71568fa80ca466b4) failed post-simulation — harness
bug, not science.** All 12,000 trajectories simulated, then
aggregation crashed: `Counter.update(str-valued dict)` abuses
Python's empty-Counter fast path (a silent `dict.update` copy), then
string-concatenates counts (the receipt shows `"0,1": "S1S1..."`)
and only raises `TypeError` when a novel key meets an int.
Fixed to count `"site:tile"` pairs (comment in-source); receipt
kept as queue-result-v1-failed.txt. Resubmitted as v2 (job
hxq-7cb04524b6e6bb84, request 7cb04524b6e6bb…, nonce
repair-mechanism-v2).

**Partial v1 evidence (valid counters, census field garbage):**
- build1 dG 0.5/2/4: pqr 0.554/0.758/0.986; read-time lock-squat
  rate 0.314/0.118/0.000 (R4 monotonicity already visible, and the
  dG-4 zero is striking); pqr-and-blocked 9/3/0.
- Top squatters at dG 0.5: Vp@(3,2)=107, DBr@(3,3)=70, Vp@(3,3)=59,
  V0p@(3,1)=52 — **R3a confirmed early** (Vp top-1 at (3,2), V0p
  top-1 at (3,1)). New structural insight: the Vp@(3,2) squatter
  exposes N=p-t-done, and DBr rides it — Vp@(3,2)+DBr@(3,3) is a
  mutual b=2 squatter STACK (squatters stabilizing squatters),
  parallel to the tick-22 DBr+L3 repair trap.
- Vp-missing dG 0.5: pqr 0.864 (ratio 1.56, reproducing tick-23's
  1.53), vacancy occupied by D2T in 389/432 = 90% of strict-pqr
  terminals (L2 10%) — **R3b_Vp confirmed at 90%**, the b=2
  substitution channel from the static census. Blocked only 6.8%.
- Preliminary R2: conditional-on-clean pqr build1 0.781 vs Vp-missing
  0.927 — gap 0.146, under the 0.15 falsifier gate but not the
  0.10 target; trap relief explains most of the exceeds-parity gap,
  whether the residual 0.15 is noise or a second mechanism is
  exactly what v2's V0p/D1T/D2T arms decide.

Full verdicts R2-R4 land with the v2 receipt (trap_grid.out); the
receipt-pin tests activate then.

## Honest limits

Read-time census, not full history: "blocked at read" is a
lower bound on trap visitation. One geometry (4-column AND), one
build family, positive programs only; the ladder law is claimed for
this geometry until a second geometry tests it. dG 7 excluded (the
census instrument cannot see starved rows that tick 23 already
measured as 0).
