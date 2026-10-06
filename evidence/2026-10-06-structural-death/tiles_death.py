"""designs/003 structural-death build — tick 22 (SON-4773).

K4's honest successor (tick 19, designs/003 F4 note): in an
always-completable positive program, growth-incompletion reads as a
subset of the true model by construction, so "kinetic reassertion of
the true model" is unmeasurable at a fixed read time. The clean
instrument is a build in which the true-model completion is
STRUCTURALLY forbidden: remove one species from the correct build's
inventory (a synthesis-time missing-strand error model — nothing is
recompiled, so d2/d3 are silent by construction) and ask whether the
kinetics rebuilds the true-model readout anyway through b=1
transients.

The dead build: BUILD1 (P_AND `p. q. r :- p, q.`, errata E1/E2
applied) minus the single tile species DAr (r's slot-A reader).
Consequences, by glue arithmetic (verified by exhaustive BFS in
atam_death.py):
  - site (1,3) is permanently vacant: the only tiles reading
    q-t-done (S) or go3 (W) at that site was DAr;
  - DBr can never attach at tau=2 (S=p-t-done bonds Vp.N at
    strength 1; its W partner and1_r is never exposed);
  - L3 can never attach at tau=2 (S=base3 bonds L2.N at strength 1;
    its W partner r-t is never exposed);
  - so the aTAM terminal is rows 1-2 complete + spine S3, reading
    {p,q} on the lock column with row 3 dead-but-vacant.

Semantic anchor: {p,q} is the stable model of `p. q.` — the program
with r's rule dropped. Species-death reaches the dropped-rule MODEL
without re-layout: the recompile (build2-style false chains) and the
absence (vacant row) are different substrates for the same solver
answer, and they read differently at the lock column.

kTAM is where the two separate: DBr and L3 each retain a b=1 south
bond and can attach transiently, and once BOTH sit in row 3 they
mutually stabilize (DBr.E=r-t bonds L3.W=r-t — each reaches b=2).
The pre-registered question is whether that pair rebuilds the full
true-model strict decode — see ktam_mc_death.py.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIBLING = os.path.join(os.path.dirname(HERE),
                       "2026-10-06-body-conjunction-builds")
for p in (HERE, SIBLING):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_and import BUILD1  # noqa: E402

DEAD_SPECIES = "DAr"


def build_missing_species(build, species):
    """Return `build` with one tile species removed from the
    inventory (synthesis-time absence; nothing else is touched)."""
    out = {
        "name": build["name"] + "_missing_" + species,
        "rows": dict(build["rows"]),
        "row_of": {k: v for k, v in build["row_of"].items()
                   if k != species},
        "seed": dict(build["seed"]),
        "tiles": {k: dict(v) for k, v in build["tiles"].items()
                  if k != species},
    }
    return out


BUILD_DEAD = build_missing_species(BUILD1, DEAD_SPECIES)

# Programs for the clingo semantic anchor of the death experiment.
PROGRAMS = {
    "P_AND": "p. q. r :- p, q.",
    "P_AND_dead_semantics": "p. q.",
}
