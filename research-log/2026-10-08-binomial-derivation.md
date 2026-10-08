# 2026-10-08 — C(n+4,4) derived: the assembly poset is the 4×n box (tick 65)

Card: SON-4859 (hourly loop, tick 65). Receipt verbatim:
`evidence/2026-10-08-binomial-derivation/probe.out` (probe at HEAD
b651e40, JSON-lines, timings included). Predictions D1–D4 frozen in
the probe docstring before anything ran; probe code needed two fixes
before the first BFS executed (KeyError on the n=4 anchor program,
then a frozen-assembly iteration type) — fixed with predictions
unchanged, noted here for the record.

## 1. Question

Tick 64 measured assemblies == C(n+4,4) at n=4..9 and left it "an
observation, not a theorem". Why 4-combinations of n+4 — and does
the fit survive n=10..12?

## 2. Derivation (from the face tables, before running)

The decorative-fact family builds have exactly 4 tiles per row,
one per site, in four column classes (n=6 build dumped as evidence
in §5). With `glue_strength` = {SPi/SPi: 2 (class closure,
designs/010 §10.3); other matched pair: 1; mismatched/blank: 0}
and TAU = 2, the attach grammar is:

| column | tiles | needs | why |
|---|---|---|---|
| 0 | S_i | (0,i−1) only | S-face SPi/SPi = 2 alone |
| 1 | D_iT / Cq2 / DAr | (1,i−1) + (0,i) | below 1 + west go_i 1 |
| 2 | V0p / V* / Uq2 / DBr | (2,i−1) + (1,i) | below 1 + west 1; the local S+E option needs (3,i), which needs (2,i) — pruned by reachability, not local strength |
| 3 | L_i | (3,i−1) + (2,i) | below base-chain 1 + west 1 |

So every reachable assembly is column-contiguous (each site needs
its below-neighbor) and row-left-justified ((3,i) ⇒ (2,i) ⇒ (1,i)
⇒ (0,i)). Assemblies ↔ column height vectors

    n ≥ h0 ≥ h1 ≥ h2 ≥ h3 ≥ 0

— partitions inside a 4×n box — classically counted by C(n+4,4)
(border lattice paths / stars-and-bars). That is *why* the fit is
quartic: the enumerator's state space is a 4-dimensional simplex
slice, one dimension per column class, not per row.

## 3. Machine check (both directions, exhaustive)

For each n the probe compared the BFS `seen` set against the
explicit ideal set:

- **D2** assemblies ↔ shapes bijectively (every site occupied by
  exactly ONE tile name across all 1820 assemblies at n=12 — no
  variant or cross-site fill anywhere).
- **D3** every reached shape IS an ideal (set inclusion).
- **D4** every ideal is reached (set inclusion, other direction —
  this is the step a local-strength argument cannot give; the BFS
  is the oracle).
- **D1** |seen| == C(n+4,4).

All hold at n=4..12; tick-64 anchors 70/126/210/330/495/715
reproduced exactly before any new row was trusted.

| n | assemblies | C(n+4,4) | terminals | s |
|---|---|---|---|---|
| 4 | 70 | 70 | 1 | 0.021 |
| 9 | 715 | 715 | 1 | 0.277 |
| 10 | 1001 | 1001 | 1 | 0.407 |
| 11 | 1365 | 1365 | 1 | 0.577 |
| 12 | 1820 | 1820 | 1 | 0.811 |

(n=5..8 in the receipt; rows 5–8 omitted here for brevity.)

## 4. Status of the claim

Upgraded: from "empirical closed form" to **derived for this
family**: face-table grammar (§2) + exhaustive both-direction set
equality at n=4..12 (§3). What remains hand-waved is the grammar
table itself — it is read off the compiler's emitted faces (stable,
pinned by the corpus) rather than proved from the compiler source.
A compiler change that emits different faces breaks D2/D3/D4 loudly
(the pins below). Scope unchanged from §10.7: one family, one
geometry (AND-over-derived with unit via, decorative facts). Other
geometries (e.g. PR13-dead's dead cascade) have different counts
(210 at n=6 per tick 62 — same binomial there; PR13-dead shares
the grammar) — extending the poset argument to the whole compiling
corpus is a next-tick candidate, not claimed here.

## 5. Evidence

- Receipt: `evidence/2026-10-08-binomial-derivation/probe.out`
  (JSON-lines, head b651e40, per-n D1–D4 booleans + timings).
- The n=6 face dump used for §2 is reproducible via
  `molasp.compiler.compile_program` on the n=6 program (24 tiles,
  4 column classes as tabled).
- Pins: `tests/test_binomial_ideals.py` — set equality D3+D4 and
  bijectivity D2 re-derived live at n=4..8 (BFS ~0.5 s total);
  n=9..12 pinned as EMPIRICAL constants (identity arithmetic on
  measured values, labeled — a build change that breaks the fit
  fails loudly at n≤8 already).

Nothing here is a validated result until independently reviewed.
