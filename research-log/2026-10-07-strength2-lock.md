# Strength-2 lock-read encoding — priced and falsified (tick 38, 2026-10-07)

Designs/005 deferred item (b): the first **kinetic lever at fixed bond
identity** (R1 contrast: renames change identity, strength changes
kinetics). Pre-registration 63d12d9 (gates K1–K8 fixed before any MC
ran; n=8 smoke caught three instrument defects first — dropped `dg`
argument, missing-species canon inheritance, `is_vp` name predicate).
Job hxq-2791e8805defef75 (nonce strength2-v1, request
2791e8805defef754…c1122, paperclip-test, 1 core / 1 GiB / 3600 s,
archive blob 9c7e7a52…c4ae5e = sha256 of the committed-HEAD tarball),
exit 0 in ~22 s on spark-4a06. Receipt:
`evidence/2026-10-07-strength2-lock/strength2.out` (8 arms, n=500,
seed base 160261107 stride 2e7) + `queue-receipt.json`; pins in
`tests/test_strength2.py`.

## The encoding

A lock tile's W-face glue pair counts 2 instead of 1, on both
evaluation sides (the lock's own W bond and any tile's E bond into a
placed lock) — site-agnostic and structural (any `L*` W read). Value
relays, done glues, base relays and squatter bonds stay strength 1;
both measured hazard classes keep their intrinsic bonds.

## Verdicts (machine line, verbatim)

K1 FALSIFIED · K2 FALSIFIED · K3 FALSIFIED · K4 INCONCLUSIVE ·
K5 CONFIRMED · K6 FALSIFIED · K7 FALSIFIED · K8 CONFIRMED

## The numbers

| arm | blocked | strict | fill | top squatters (count/500) |
|---|---|---|---|---|
| fam_b1 dG0.5 | 0.308 | 0.568 | — | Vp@3,2 123, V0p@3,1 75, Vp@3,3 77, DBr@3,3 56 |
| s2_b1 dG0.5 | 0.314 | 0.492 | — | **L2@3,3 67, L3@3,2 43**, Vp@3,2 49, V0p@3,1 27 |
| fam_b1_Vp | 0.068 | 0.862 | **0.904** | V0p@3,1 12, DBr@3,3 21 |
| s2_b1_Vp | 0.216 | 0.678 | **0.412** | **L3@3,2 82**, L1@3,2 8 |
| s2_b1 dG2 | 0.146 | 0.716 | — | L2@3,3 56, L3@3,2 14 |
| s2_b1_Vp dG2 | 0.046 | 0.880 | 0.464 | L3@3,2 16 |
| fam_unit | 0.268 | 0.570 | — | V2p@3,2 103, Ur@3,3 47, V0p@3,1 49 |
| s2_unit | 0.352 | 0.442 | — | **L2@3,3 83, L3@3,2 44**, V2p@3,2 41 |

Calibration (K5 CONFIRMED): fam_b1 blocked 0.308 (ref 0.27, dev
0.038 ≤ 0.05); fam_b1_Vp fill 0.904 (ref 0.908, dev 0.004 ≤ 0.05).
The falsifications are interpretable — no protocol drift.

## What happened

- **K8 CONFIRMED — the encoding does exactly what it mechanically
  promises**: median first-passage of L2@(3,2) drops 25097 → 21444
  (~15% faster lock capture; the W bond alone now holds at b=2).
- **K1 FALSIFIED — and the mechanism is the finding**: the read-block
  does not drop (0.314 vs 0.308); the **squatter class migrates**.
  The V-class value squatters (Vp@3,2 123→49, V0p@3,1 75→27) and the
  lo-read Vp+DBr stack (co-occurrence among blocked 0.305→0.096, K3
  FALSIFIED) give way to **misplaced lock tiles** — L2@3,3 (67),
  L3@3,2 (43), L1@3,2 — riding the same site-agnostic strength-2 W
  read the encoding grants to every `L*` tile, plus the base-relay
  vertical chain. Strengthening the canonical read strengthens the
  same bonds wherever they can form.
- **K2 FALSIFIED — the repair channel collapses**: Vp-missing stable
  D2T fill 0.904 → 0.412. In that arm the dominant squatter is
  L3@3,2 (82/500) sitting on the vacancy's east lock site, starving
  the fill's E→lock bond (L3's W reads r-t, not q-t — the doubled
  bond never engages for the substituting tile).
- **K7 FALSIFIED — corpus-general**: UNIT_ONLY gets *worse* under s2
  (0.268 → 0.352) with the identical misplaced-lock signature
  (L2@3,3 83, L3@3,2 44). The failure mode is constructional, like
  the hazard classes it fails to remove (tick 37).
- **K6 FALSIFIED — dG does not rescue it**: blocked starves with dG
  (0.314→0.146) but the s2 fill *rises* (0.412→0.464) — the wrong
  direction for a mitigation knob.
- **K4 INCONCLUSIVE**: strict-pqr 0.492 (gate ≥0.55, falsifier ≤0.45)
  — mild yield degradation, inside the inconclusive band.

## Interpretation (post-hoc reading of the receipt; per-class bond
decomposition was not instrumented — label stands)

**Kinetic reinforcement is not hazard elimination.** The arc now has
three sibling principles: (i) static elimination is not kinetic
elimination (tick 31); (ii) renames are structurally blind to
displaced-pair recombination (R1, tick 35); (iii) strength
reinforcement is blind to displaced placement — the lever strengthens
the canonical channel and the off-channel uses of the same glue
indiscriminately. The duality (repairability ⇄ squattability as one
property of value-glue sharing) survives its first non-rename knob:
the hazard is carried by the glue, not by the tile.

Honest boundaries: L*-misplacement mechanism is observed at read time
(counts above) with a structural hypothesis (site-agnostic W read +
base-relay vertical nucleation), not per-bond decomposed; the dwell
metric (squat32 mean 1.10e6 s2 vs 1.39e6 fam) is reported but the
b=1 equilibrium comparison was not re-derived for the new class; dG
grid covers 0.5/2.0 only on BUILD1 arms.

## Consequences

- designs/005 (b) is **evaluated and closed as a failed mitigation**:
  the compiler-guidance line (d4 census + both hazard classes) remains
  the only lever with a measured win; kinetic lock reinforcement joins
  renames in the priced-out set. Future encoding work must price
  against BOTH the V-classes and the L-misplacement class this study
  discovered.
- d4 note: the census should flag lock-tile off-channel *placements*
  (L* at non-own lock sites) as a distinct hazard class — they were
  invisible in the family census because they bond only via base
  relays at b=1, and become dominant the moment lock bonds are
  reinforced.
