# 2026-10-13 w8 related-work scan — position-dependent decline in self-assembly kinetics vs the posfresh branch map

SON-5152 · run 7b68fdec · written while the posfresh probe (request
`bda50c6bf65bb5433500dc7c855593c39727eb0376154b985c5efb386f9a1d66`,
nonce molasp-w8-posfresh-t113) is STILL QUEUED on the admission floor.
Never-idle avenue: a literature scan that serves BOTH branches of the
frozen interpretation map. No gate, sample size, or branch condition
changes here — this note only annotates what each branch would mean.

## Anchors (search-snippet level — see honesty box)

1. **kTAM's constant-concentration assumption.** The kinetic Tile
   Assembly Model's standard statement carries "all monomers hold the
   same constant concentration" as assumption (1) (Winfree 1998 kTAM;
   restated in Patitz' 2013 review and the self-assembly.net wiki
   entry). Under that assumption, windows inside one seed block are
   statistically exchangeable — window position cannot carry rate
   structure. The w8 position-structure hypothesis is precisely a
   candidate violation of this exchangeability premise.
2. **Nucleation order stratifies growth via depletion.** Schulman &
   Winfree 2007 ("Synthesis of crystals with a programmable kinetic
   barrier to nucleation", PMC1986573): "the rate of monomer depletion
   increases quickly after nucleation because the number of growth
   sites on a crystal" grows. Earlier-nucleated structures consume
   shared monomer; later ones grow slower and complete less often.
   A decline of terminal pair share with window position is exactly
   the census-side signature this mechanism would print.
3. **Depletion is a first-class design concern.** Evans & Winfree 2017
   ("Physical principles for DNA tile self-assembly", Chem Soc Rev):
   seeded growth reduces tile depletion — depletion is treated as a
   physical principle to engineer around, not noise.
4. **Incomplete completion under depletion is a named failure mode.**
   DNA31 tile-blocker paper (LIPIcs vol 347): growth must be slow
   enough "to avoid monomer depletion before structures complete" —
   i.e., depletion-limited runs yield fewer terminal structures, the
   quantity our census counts.
5. **Concentration heterogeneity stratifies outcomes.** Chen & Kao 2011
   (concentration ∝ growth-error/time scaling; arXiv:1210.5786):
   tile-type concentration sets error and completion-time scaling.
   Our tick-115 finding — a pos-1-weighted q0 under-declares
   family-rate exposure by up to 0.062 — is the estimator-side analog.

## What each posfresh branch would mean against this literature

- **Branch B (POSITION_DECLINE_DETECTED)** — the pooled q0 stops being
  a parameter and becomes a trajectory average, exactly as the
  depletion literature reports growth-vs-time curves rather than one
  terminal rate. The stage-2 plan already retires pooled q0 in favor
  of (q_early, q_late). Natural two-parameter readout for the
  descriptive per-500 subwindow shares ALREADY frozen in the prereg:
  a depletion-front fit `q(pos) = q∞ + (q0 − q∞)·e^(−pos/λ)`.
  Curvature (not just the endpoint contrast) separates exponential
  saturation from linear drift — computable from frozen descriptives
  alone, no new substrate runs, no gate changes.
- **Branch A (POSITION_DECLINE_NOT_DETECTED)** — position coupling is
  bounded below MDE 0.040 (n=2000/group, virgin blocks): consistent
  with kTAM exchangeability at census scale. It does NOT refute
  depletion structure universally; the one-sided-low gate exposure is
  already covered by the dual-null band [q0 − Δ(1−w), q0].
- **The internal-contrast design itself** is the scan's sharpest
  confirmation: EARLY vs LATE inside ONE block separates
  position-indexed state (consumption-front-like coupling) from block
  provenance, the same maneuver the depletion literature uses to
  separate nucleation-order effects from tile-type effects. That is
  why posfresh is powered where tick-112's instrument was not.

## Gap this lab could own

None of the scanned literature reports within-block, position-indexed
terminal-share censuses for seed-blocked compilation-target substrates.
If Branch B fires, "depletion-aware census estimation" —
position-stratified q0 with a fitted front length λ, plus the
stratified-contrast MDE scaling (0.040/Δ_meas)² already in the stage-2
plan — is a self-contained methodological contribution.

## Honesty box

All five anchors are search-snippet-level reads (titles, abstracts,
snippets; URLs in this file are the fetched sources). No full-PDF
verification has been done. None is load-bearing for a frozen gate.
If Branch B fires and the depletion-front fit or any citation becomes
part of a design, figure, or post, verify the full PDFs first and
update this note.

## Sources

- Schulman & Winfree 2007 — https://pmc.ncbi.nlm.nih.gov/articles/PMC1986573
- Evans & Winfree 2017 — https://pubs.rsc.org/cs/article/46/12/3808/520257/Physical-principles-for-DNA-tile-self-assembly
- Tile Blockers (DNA 31) — https://drops.dagstuhl.de/storage/00lipics/lipics-vol347-dna31/html/LIPIcs.DNA.31.7/LIPIcs.DNA.31.7.html
- Chen & Kao concentration scaling — https://arxiv.org/html/1210.5786v1
- Patitz 2013 review (kTAM assumptions) — https://www.dna.caltech.edu/courses/cs191/paperscs191/patitz2013review_NatComp.pdf
- kTAM wiki (assumption statement) — http://self-assembly.net/wiki/index.php/Kinetic_Tile_Assembly_Model_(kTAM)
