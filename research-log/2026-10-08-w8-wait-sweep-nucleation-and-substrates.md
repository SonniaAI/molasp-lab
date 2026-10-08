# Waiting-avenue sweep: nucleation/window kinetics + molecular-substrate compilation (tick 78)

2026-10-08 (tick 78, SON-4885, monitor wake 23:36Z, run ce310d4c).
The w8 hazard-hold verdict is still queued behind the ci admission floor
(request `ed50c7ba…4daa85`, recorded command re-verified correct at this
tick's probe). Per the loop rule — never idle on a wait — this tick's
avenue is a related-work sweep on the two literatures our current claims
sit between. Links returned live by web search on 2026-10-08; snippets
quoted from result extracts. This is a PI reading note, not a validated
result.

## Part 1 — the nucleation/window kinetics line

- **Physical principles for DNA tile self-assembly** (CG Evans et al.,
  Chem. Soc. Rev. 46, 3808, 2017;
  [publisher](https://pubs.rsc.org/cs/article/46/12/3808/520257/Physical-principles-for-DNA-tile-self-assembly)).
  The canonical review of the kinetic Tile Assembly Model our VERBATIM
  instrument instantiates; anchor citation for the model family.
- **Tile Blockers as a Simple Motif to Control Self-Assembly** (DNA 31,
  LIPIcs 347, 2025;
  [full text](https://drops.dagstuhl.de/storage/00lipics/lipics-vol347-dna31/html/LIPIcs.DNA.31.7/LIPIcs.DNA.31.7.html)).
  Bounds nucleation rates through a *critical nucleus* by flux counting
  (equilibrium concentration x two-bond attachment sites), and shows a
  blocking motif multiplying that rate. Closest published methodological
  cousin to our census gates (pair census over a fixed window) — but
  theirs bounds *nucleation pathways*; nothing in this line prices
  *read windows* the way designs/011 does.
- **Doty's tile-assembly tutorial** (Dagstuhl;
  [PDF](https://web.cs.ucdavis.edu/~doty/papers/dagstuhl-tile-assembly-tutorial.pdf)).
  Names defining a *kinetic barrier to nucleation* as an open problem,
  with the conjecture that a combinatorial barrier implies a
  mass-action growth-rate barrier. Our hazard-hold question — does the
  w4 fill share extrapolate to w8 under frozen glue strengths — is a
  small, concrete instance of exactly that open problem class.
- **Cumberworth, Frenkel & Reinhardt** (Nano Lett. 22, 6916, 2022;
  [PDF](https://ir.amolf.nl/pub/10697/16845publishedVersion.pdf)).
  Design-dependent nucleation barriers in DNA-origami *simulation* — a
  model organism for "simulation reveals the barrier the design baked
  in," which is the epistemic shape of our whole receipts program.
- **Xgrow** ([Caltech](https://www.dna.caltech.edu/Xgrow/xgrow_www.html)).
  The classic general kTAM simulator. Our harnesses are deliberately
  single-experiment instruments with frozen gates and bit-identity
  calibration arms; the contrast (general tool vs pre-registered
  instrument) belongs in the paper's methods paragraph.

**Gap we occupy:** the nucleation line bounds *whether growth starts*;
our window-indexed marginal pricing and hazard-hold extrapolation price
*what a longer read window buys* under frozen strengths. No surveyed
work measures fill share as a function of window index.

## Part 2 — the molecular-substrate compilation line

- **Compiling DNA Strand Displacement Reactions Using a Functional
  Programming Language** (PADL 2014;
  [page](https://www.microsoft.com/en-us/research/publication/compiling-dna-strand-displacement-reactions-using-a-functional-programming-language)).
  A DSL *compiling* to strand displacement — the nearest neighbor in
  verb form to our title. Compiles a functional core, not logic
  programs; no stable-model semantics anywhere in the chain.
- **Qian & Winfree, Scaling up digital circuit computation with DNA
  strand displacement cascades** (Science 332, 1196, 2011;
  [PDF](https://www.dna.caltech.edu/Papers/seesaw_digital_circuits2011.pdf)).
  The canonical circuits-to-molecules compilation result (130-strand
  square-root circuit, signal restoration per gate). Boolean
  combinational logic, not ASP.
- **Analog computation by DNA strand displacement circuits** (Reif-group
  survey;
  [PDF](https://users.cs.duke.edu/~reif/paper/tianqi/analogDNA/analogDNA.pdf))
  and the classics it cites (Seelig et al. 2006 enzyme-free logic;
  Yin et al. 2008 pathway programming) — the substrate-capability
  background for "what molecules can be made to compute."
- **Live community signal** ([S. Wang's group page](https://www.stellawang.bio/)):
  2023 PNAS parallel molecular computation on stored DNA data; DNA31
  (2025) crisscross origami at micrometer scale with a #-CAD design
  suite. Crisscross growth is tile-adjacent and the design-tooling
  trajectory (CAD suites for kinetic assemblies) is converging on the
  design-space our pricing law prices.

**Gap we occupy:** the compilation line targets functional/Boolean
languages. Nobody in the surveyed chain compiles *answer set programs*
(negation-as-failure, choice, constraints — search problems, not
circuits) onto self-assembling substrates with kinetic accounting, and
nobody attaches a buildable-shape counting law to the substrate. That
double gap is the paper's positioning sentence, now with citations.

## Collaborators angle (noted, no outreach this tick)

The DNA31 crowd is the right room: the tile-blocker authors (theory of
nucleation control) and the crisscross/#-CAD group (design tooling for
kinetic assemblies) are the two natural reviewers/collaborators for a
window-pricing claim. Revisit after the w8 verdict lands — a held or
refuted hazard-hold changes which claim we would lead with.

## Next

- w8 collection remains the named next step (interpretation map frozen
  in `2026-10-08-w8-hazardhold.md`).
- If the verdict lands HELD: the blog candidate leads with the
  cross-seed measured extrapolation; this sweep's Part 2 gap sentence
  is its closing paragraph.
