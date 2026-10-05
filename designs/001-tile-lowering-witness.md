# Design 001 — Tile lowering of the C2 witness `a. p :- p.`

Status: v2.1 machine-checked at τ=2 (aTAM); kTAM run pending on v2.1.
Date opened/closed: 2026-10-05. Evidence: `../evidence/2026-10-05-c2-ktam/`.

## Goal

Compile the C2 witness program (fact `a.`; self-loop `p :- p.`; stable
model `{a}`; supported-but-unstable `{a,p}`) to a seeded tile system at
τ=2 such that terminal assemblies decode only to stable models, with the
self-loop structurally unencodable — support must arrive from below in
the growth order or not at all. This is the geometry-supplies-the-level-
mapping claim (paper, branch (c)) made executable at the smallest scale.

## Construction of record (v2.1)

3 columns × 2 rows above a 3-tile seed. Strength-2 row-typed spine glues
`SP1/SP2` at column 0; strength-1 decision/lock glues elsewhere.

```
row2:  [S2: S=SP2,E=go2,N=SP3] [D2F: W=go2,S=row1done,E=r2,N=topF] [L2: W=r2,S=base2]
row1:  [S1: S=SP1,E=go1,N=SP2] [D1T: W=go1,S=f-a,E=r1,N=row1done]  [L1: W=r1,S=base]
seed:  N-glues: SP1 | f-a | base          (the f-a glue IS the fact a.)
```

D-tile variants not shown are the wrong tiles: `D1F` (S=`u-a`, mismatch
with the fact glue) and `D2T` (S=`no-p` — nothing exposes `no-p`, because
the only rule deriving p is `p :- p`, which cannot be wired: its body
atom sits in the same row as its head, and no glue from row 2 exists
before row 2 grows). 8 tile types + 3 seed tiles; |Σ| = O(1) in the
search, as the resource table demands.

**Machine-checked (exhaustive producibility BFS, `atam_check_v2.py`):**
10 producible assemblies, **1 terminal assembly**, decoding `{a}`;
`D1F` and `D2T` are producible in **0** of the 10 reachable states.

## Two flaws caught on the way (kept as evidence — this is why checks run)

- **v1 never grows at τ=2** (`atam_check.py`, `atam.out`): the decision
  tile's only initial bond is its south glue, strength 1 < 2; its east
  lock partner does not exist yet. Bootstrapping a row requires either a
  strength-2 spine or a two-present-neighbour corner. v1's kTAM runs
  (`ktam_mc.py`, `run.out`) therefore measured a *strength-1 transient
  locking* growth mode, not a τ=2 system — see numbers below, labelled
  as such.
- **v2.0 had interchangeable spine tiles** (`S2` legal at row 1 via the
  shared `SP` glue): it exposes `go2` where row 1 needs `go1`, and the
  assembly dies as a partial terminal (3 of 4 terminals were dead ends).
  Fix: row-indexed spine glues. Cheap here; the same class of bug in a
  10³-tile set is why the compiler must emit the producibility check.

## kTAM results (v1 geometry, strength-1-locking regime — honest label)

Gillespie MC, k_f = 1 s⁻¹, mismatch-attachments neglected (Xgrow
"no-mismatch" approximation), read at fixed T. n = 500 per point.
`Gse@dG=ln2` sweep (Gse ∈ {7,9,11,13}) and `dG@Gse=9` sweep
(Gmc ∈ {8.307, 7, 5, 3}) — `evidence/.../run.out`:

- Decode `{a}` (stable): 398–428 / 500 everywhere.
- Decode `{a,p}` (unfounded): **0 / 4000**. 95% CI upper bound ≈ 7.5×10⁻⁴
  (rule of three). Same for `{p}`: 0 / 4000.
- Decode `empty` (founded value error: a lost to the D1F near-miss):
  72–102 / 500, **flat in both Gse and ΔG** — an order race at formation
  (lock tile seeds from a single south bond, then accepts the wrong
  value tile), not a kinetic error rate. In v1 the wrong value tile is
  lockable from above (`row1done` pairs with D2F's south regardless of
  value), so the founded error persists; D2T has no upper locking
  partner at this height, so the unfounded state is transient-only —
  ≥250× separation, but construction-dependent, not yet a theorem.

## What this does and does not establish

Established: at τ=2, the lowering is correct by exhaustive check — the
self-loop cannot fire because its body cannot be positioned below its
head, and the wrong tiles have no strength-2 attachment path. That is C2
in the error-free abstraction, machine-checked.

Not established: C2 in kTAM. The near-miss trap probability for a
strength-1 tile that must be locked by a partner arriving at rate
r_f = e^{−Gmc} against detachment e^{−Gse} is ≈ 1/(1+e^{−ΔG}) with
ΔG = Gse − Gmc — O(1) whenever Gmc ≥ Gse. Error suppression requires the
**slow-growth window Gse < Gmc < 2Gse**, where growth still proceeds
(strength-2 corner attachments detach at e^{−2Gse} < r_f) but near-miss
trapping falls like e^{−(Gmc−Gse)}. Next experiment: kTAM on v2.1 across
the window at Gse = 9, Gmc ∈ {9.5, 11, 13, 16}; prediction — `empty`
falls roughly exponentially with Gmc−Gse, `{a,p}` stays at the transient
floor. Refutes the design if `empty` does not fall, or if `{a,p}` rises
above it.

## Falsification criteria for the design itself

1. A producible path to `D2T` (or `D1F`) at τ=2 in v2.1 — the BFS says
   none exists; attack the BFS or the glue table.
2. kTAM on v2.1 in the window producing unfounded decodes above the
   transient-occupancy floor.
3. An instance where the row order cannot realise a strict level mapping
   the program needs (positive recursion through many atoms) — that is
   designs/002 territory: the row-typing here hard-codes order a < p.
