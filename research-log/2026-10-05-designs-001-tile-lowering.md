# 2026-10-05 - designs/001: the witness lowered to tiles, two flaws caught, one window found

Tick 3 of the loop (SON-4709). Deliverable: `designs/001` — the C2
witness `a. p :- p.` lowered to a τ=2 tile system, machine-checked at
the aTAM level, plus first kTAM numbers and the identification of the
regime where they mean anything.

## What landed

- **`evidence/2026-10-05-c2-ktam/`** — `atam_check.py` (v1),
  `tiles_v2.py` + `atam_check_v2.py` (v2.1 construction of record),
  `ktam_mc.py` + `run.out` (v1-geometry kTAM MC, 2 sweeps × 4 settings ×
  500 runs).
- **`designs/001-tile-lowering-witness.md`** — the construction, the two
  flaws, the numbers, the slow-growth window, falsification criteria.

## Results, with numbers

1. **v1 never grows at τ=2.** The exhaustive producibility BFS returned
   1 producible assembly (the seed) and 0 legal moves: a decision tile
   whose only initial bond is south strength-1 cannot bootstrap a row.
   The checker earned its keep before any kTAM number could be trusted.
2. **v2.0 grew into dead ends.** Shared spine glue made S2 legal at row
   1, where it exposes `go2` instead of `go1`; 3 of 4 terminal
   assemblies were partial. Fix: row-indexed spine glues (v2.1).
3. **v2.1 passes cleanly:** 10 producible assemblies, **unique terminal
   assembly decoding {a}** — the stable model — with `D1F` (fact
   ignoring) and `D2T` (unfounded p) producible in zero reachable
   states. The self-loop `p :- p` cannot fire because its body cannot
   sit below its head in the growth order. C2 holds in the error-free
   abstraction, machine-checked, at the smallest instance.
4. **kTAM (v1 geometry, honestly labelled a strength-1-locking regime):**
   unfounded decodes `{a,p}` and `{p}`: **0 / 4000** (CI₉₅ upper bound
   ~7.5×10⁻⁴); founded value error `empty`: 72–102 / 500, **flat in both
   Gse (7→13 at ΔG=ln2) and ΔG (ln2→6 at Gse=9)** — it is an order race
   at formation (single-bond lock seeding), not a kinetic error rate.

## The finding that matters

Near-miss trapping ≈ 1/(1+e^{−ΔG}) with ΔG = Gse − Gmc is O(1) whenever
Gmc ≥ Gse. Every kTAM point we (and mostly everyone) call "fast growth"
sits in that regime. Error suppression needs the **slow-growth window
Gse < Gmc < 2Gse**: strength-2 corner attachments still win against
detachment (e^{−2Gse} < r_f) while strength-1 near-misses lose. That
window is the C2 kTAM experiment, and it is now specified with a
prediction: `empty` falls ~exponentially in Gmc − Gse across the window,
`{a,p}` stays at the transient floor.

## What failed

Both v1 and v2.0 (above). Also: Xgrow is not in the pod and not in the
approved cluster images, so the simulator is in-house (Gillespie,
no-mismatch approximation — stated in the design doc). The clingo
cross-check of the witness partitions is still owed to the first
cluster tick.

## Next (unblocked)

1. kTAM MC on v2.1 across the slow-growth window (Gse=9; Gmc ∈ {9.5, 11,
   13, 16}) — the prediction above is falsifiable as written.
2. First cluster tick: clingo cross-check of the five witness programs
   (fastlas/reflas images), plus the window sweep at N=5000 if local
   runtime binds.
3. designs/002: multi-atom positive recursion (the `go`-typing here
   hard-codes the atom order; a compiler pass must derive it).
