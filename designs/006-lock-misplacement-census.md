# designs/006 — lock-tile off-channel placement census (the L*-class)

## Why

Tick 38 (strength-2 lock-read encoding, designs/005 (b)) FALSIFIED the
encoding as a mitigation and discovered a hazard class in the act: the
squatter population MIGRATES from V-value squatters to misplaced LOCK
tiles — L2@(3,3) 67/500, L3@(3,2) 43/500, L3@(3,2) 82/500 in the
Vp-missing arm, UNIT_ONLY worse 0.268 → 0.352 — riding the
site-agnostic strength-2 W read plus base relays
(`evidence/2026-10-07-strength2-lock/strength2.out`, K1/K2).

The census could not have warned about this class: every existing d4
layer filters by SITE class (lock sites only) or by substitution
probe. The misplaced locks sit at *other rows'* lock sites (and
potentially anywhere), bonding at b=1 through base relays and the W
read at family strength — present in the raw `off_channel` table,
surfaced by no layer, invisible in the tick-37 census verdict "all
lock squatters V-class" (G1). The tick-38 consequence, verbatim:
*d4 should flag lock-tile off-channel placements as a distinct hazard
class — invisible in the family census: base-relay b=1 only, dominant
the moment lock bonds are reinforced.*

## What lands

`molasp.offchannel.lock_misplacements(build, canon, strength=None,
bond_fn=None)` — the TILE-class view: every site (any class) where an
`L*` tile that is not the canonical occupant bonds ≥ 1 against the
canonical background. Channel record: `bond` (family arithmetic by
default; the tick-38 `matched_s2` for the strength-2 view), the
family-strength per-`faces` decomposition, and `w_read` — the W-face
channel is the face a reinforced lock read doubles. Attached to
`check_d4` as `lock_misplacements`, printed by `d4_report_lines`,
kinetic context quoted into `MEASURED_CONTEXT
["strength2_lock_misplacements"]`.

## Pre-registered gates (M1–M4; falsifiers fixed before the census
output was produced — registration commit precedes the receipt)

Views: BUILD1 (tiles_and, family scope) and UNIT_ONLY
(`compile_program`, "p. q. r :- p."), each at family arithmetic and
under the s2 bond rule (tick-38 `matched_s2`: any `L*` W read counts
2, any tile's E bond into a placed `L*` counts 2). MINIMAL ("p.") is
an emit-path control.

- **M1 CONSTRUCTION** (fam views): BUILD1_fam and UNIT_fam each have
  ≥ 1 L*-placement channel, and every channel bond == 1 (transient
  class only; consistent with G2's no-stable-solo reading).
  [falsified: any fam view empty, OR any fam channel bond ≥ 2]
- **M2 s2 RANK FLIP** (s2 views): in BUILD1_s2 and UNIT_s2, the
  kinetically-dominant channels L2@(3,3) and L3@(3,2) are present
  with bond ≥ 2 (the doubled W read is load-bearing in the census
  arithmetic), AND every non-L squatter at the lock sites stays
  bond ≤ 1 under the same s2 arithmetic — the static census then
  reproduces the measured migration ordering (locks over V-class).
  [falsified: either named channel missing or bond < 2, OR any
  non-L lock-site squatter ≥ 2]
- **M3 NO-NEW-PHYSICS** (all four views): every (site, tile) channel
  in the layer appears in that view's bond table with the identical
  total (`off_channel` at fam arithmetic; the `matched_s2` table for
  s2 views) — the layer adds classification, not channels.
  [falsified: any mismatch in any view]
- **M4 EMIT-PATH** (compile arms UNIT_ONLY, MINIMAL): the
  auto-attached `build["d4"]` carries `lock_misplacements` equal to
  `check_d4`'s (the compiler-facing path actually reports the class).
  [falsified: missing or differing on any arm]

## Honest boundaries, fixed in advance

- The census is SOLO (canonical background). The vacancy-enabled
  channel measured at L3@(3,2) 82/500 (Vp-missing arm, K2) needs the
  vacancy background and is OUTSIDE this layer's solo arithmetic —
  same bound as the one-site census everywhere; a vacancy-background
  probe is follow-up work, not claimed here.
- Census bonds are arithmetic, not rates. The M2 gate asks the static
  view to reproduce the migration ORDERING (which channels can gain),
  not the kinetic counts; the counts stay quoted context from the
  committed tick-38 receipt.
- Standing rule (tick 37 precedent): deterministic static enumeration,
  no cluster job. The receipt is the committed `.out`.

## (evaluation lands in the tick-39 collection commit)
