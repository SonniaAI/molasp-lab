# 2026-10-22 — PC11 fiber mechanics: L3 is one shared or-support bit (tick 155, SON-5152)

## What this tick answers

Tick 154 reduced the PC11 contention law
`assemblies(n) = C(n+4,4) + C(n+2,2)` to L3 — the multiplicity
partition (fiber 1 off corner ideals, fiber 2 on corner ideals) —
and left L3 machine-verified only. This tick mechanizes L3: the
whole fiber structure over the ideal set is **one binary choice**,
and a closed-form **canonical section** reproduces the census fiber
exactly at every censusable height.

## The three layers of the mechanism

1. **Static rule inventory** (from `parse_program`, no census): the
   decorated PC11 program has derived heads `q2` (1 rule) and `r`
   (2 rules, bodies `{q2, s}` and `{q2}`). The only or-supported
   atom is `r`; both of its rule supports are contained in every
   corner ideal, so both conduits are live exactly where `r` is
   demanded (corner ideals, by tick 153's C1).

2. **Forced tile table** (measured element-wise at every height,
   then written closed-form in `forced_tile`): every site's tile is
   a pure function of `(n, site)` — `S<y>` in column 0, `D<y>T`
   transports then `Cq2` in column 1, `V0p`/`V<y>p` then `Uq2` in
   column 2, `L<y>` in column 3 — except exactly the two column
   tops: `(1,n) ∈ {Cr, DAr}` and `(2,n) ∈ {Ur, DBr}`.

3. **One shared bit, not two** (`section`, the key check): the
   canonical section `section(n, ideal, bit)` assigns `bit 0 =
   Cr/Ur`, `bit 1 = DAr/DBr` across BOTH column tops jointly and
   reproduces the census fiber exactly: unique assembly on
   non-corner ideals; the two bit-orbits on corner ideals; fiber 2,
   never 4, even when both free sites are present (the choices are
   coupled — one compiler-level selection shared by the
   column-top pair). This is stronger than tick 153's
   diff-restriction: the second reading is *exactly* the bit-flip
   of the first, site by site.

So L3's empirical content shrinks to: "the compiler realizes the
or-supported atom as a single bit shared across the or-support
pair," and the law becomes
`assemblies(n) = |ideals(n)| + (2^1 − 1)·|corner ideals(n)|` with
the `2^1` now traceable to the head multiplicity of `r`.

## New height and family boundary

- **n = 12** was never censused before this tick. Pinned from the
  closed form first (presence 1820, contended 91, assemblies 1911),
  confirmed live, section verified element-wise there too.
- **The decorative lineage caps at height 12**: the 7-letter
  decorative alphabet (`tuvwxyz`) over the 5-row anchor saturates —
  `program_for(13) == program_for(12)` exactly. The census range of
  this lineage is 5..12, and the section is now verified across the
  **entire** census range, eight consecutive heights (147, 238,
  366, 540, 770, 1067, 1443, 1911). Extending past 12 requires
  extending the decorative alphabet (a family decision, not a
  census limit).

## What remains open

- The compiler-level *coupling rule* — WHY the two column tops
  share one selection (fiber 2, not 4) — is now pinned element-wise
  at every censusable height but not yet derived from the conduit
  geometry in `molasp.compiler`. That is the recorded next step.
- Whether the bit-section structure survives a second or-supported
  atom (two or-support pairs ⇒ two bits ⇒ fiber 4?) is the natural
  follow-up experiment; no such family has been censused yet.

## Artifacts

- Tool: `tools/pc11_fiber_mechanics.py` (stdlib-only,
  deterministic, no RNG; census-backed).
- Receipt:
  `evidence/2026-10-22-pc11-fiber-mechanics/mechanics.json`
  sha256 `940668cda9ad47ea1e5a7d8ec39d0848abe39c473d11dc4515d401f66c10d926`.
- Pins: `tests/test_pc11_fiber_mechanics.py` (8 tests; every
  receipt scalar re-derived live, hash + byte stability).

Zero queue spend; docs + census only. Nothing here is a validated
result until independently reviewed.
