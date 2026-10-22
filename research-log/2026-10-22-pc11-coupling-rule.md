# 2026-10-22 — PC11 coupling rule derived from conduit geometry (tick 156)

**Status: lab note, machine-checked, not independently reviewed.**

Tick 155 mechanized the PC11 multiplicity partition (L3) as one
shared or-support bit and left the coupling unexplained: why do the
two free column tops `(1,n) ∈ {Cr, DAr}` and `(2,n) ∈ {Ur, DBr}`
never realize all four combinations? This tick derives the rule from
the emitted inventory alone — static glue arithmetic under
cooperative attachment at TAU = 2, honoring growth order — with the
census used only as a cross-check. `tools/pc11_coupling_rule.py`,
receipt `evidence/2026-10-22-pc11-coupling-rule/rule.json`
(sha256 `53daa0aa…108b`), pins in `tests/test_pc11_coupling_rule.py`.

## The rule, in three lemmas (all heights 5..12, the entire census range)

**L-east (body-identity glue).** The emitter names one conduit glue
per rule *body* of the or-supported head `r`: the conduit's east face
is `unit1_r` (unit body `{q2}`) resp. `and1_r` (AND body `{q2, s}`),
and that glue occurs **exactly twice** in the whole inventory — the
conduit's east face and its own reader's west face. The east–west
handshake across row n is therefore a body-identity match.

**L-west (the bit is free only at (1,n)).** Against the forced row-n
context — `S{n}`'s east `go_n` to the west, and the passthrough
re-type (`s` at row n−2) putting `s-t-done` on `Cq2`'s north face to
the south — *every* conduit reaches exactly TAU = 2 by west+south
(1+1). So the free choice lives only at (1,n), and the number of
admissible conduits equals the number of **live** bodies of `r`
(here 2; both live under the least model since `q2, s` are true).
The south bond is the semantic read by value typing: a false lo
emits `{lo}-t-done` nowhere, so its conduit would die at 1 < 2.

**L-coupling ((2,n) is a function of the bit).** At (2,n) the
available providers at attach time are south (`Uq2`'s north
`q2-t-done`, the hi chain link — strength exactly 1 for both
readers, again value-typed) and west (the chosen conduit's body
glue). No single face reaches 2 (`unit1_r`/`and1_r` are not spine
glues), so a west match is **necessary**; by L-east the only tile
whose west face matches is the chosen body's own reader. Growth
order closes the last escape: `L{n}` east of (2,n) needs *its* west
bond (south alone is 1 < 2), so it can never arrive first to supply
an east bond. Hence `admissible(2,n | bit) = {reader_bit}` — a
singleton. The two sites carry ONE choice, not two.

## Corollary (derived, not just measured)

The census fiber over a presence set is the number of live bodies k
of the or-head on corner ideals (k = 2 here), so

    assemblies(n) = |ideals(n)| + (k − 1) · |corner ideals(n)|

and the `(k−1)` multiplier is now the per-body glue handshake of
L-east/L-coupling — tick 155's `2^1` is `r`'s head multiplicity.
Cross-checked against the live census at every height 5..12: fiber
== 2 on all corner ideals, never 4, including the 13 both-site
corner ideals at n = 12; the two-term law lands exactly everywhere
(147/238/366/540/770/1067/1443/1911).

## Falsifiable prediction (recorded open)

A 3-body or-head should census at fiber k = 3 on its corner ideals —
never 2³ — because the reader is a *function* of the conduit glue,
not an independent second bit. Not yet measured; the natural
follow-up family (a second or-pair, or a 3-body head) is queued
next. This is also the last piece needed to collapse L3's empirical
content entirely: with the coupling rule in hand, the only measured
input left in the PC11 law is tick 155's tile-table forcing (Layer
2), which the same glue-arithmetic method should now attack.

Zero queue spend; docs + static analysis + census cross-check only.
