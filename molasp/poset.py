"""Attach-grammar poset engine (tick 66, SON-4861).

Derives, from a compiled build's face grammar alone, the per-site
attachment grammar whose well-founded sets are conjectured (and
then measured) to equal the BFS assembly presence sets.

Definitions (all from `producible`'s own strength rule — TAU=2,
glue_strength as in compiler.py, seed row a constant):

- occupant map: site -> set of tile names the BFS ever placed
  there (measured, not assumed).
- minimal support set of (site, name): a minimal set of NON-SEED
  neighbour sites whose combined bond strengths with `name` reach
  TAU (seed-row glues are constants, never requirements).  All
  four directions count — a north or east neighbour can in
  principle supply a cooperative bond.  When a neighbour site is
  contended (several possible names) the minimal sets are computed
  for every name combination and kept as alternatives (a
  presence-level over-approximation the probe must answer for).
- grammar class of a site: "and" (one name, exactly one minimal
  support set), "or-support" (>= 2 minimal sets — local strength
  admits several attachment routes), "contended-shared" /
  "contended-split" (>= 2 names ever placed there).
- well-founded set: a set S such that every member has SOME
  minimal support set inside S along some admissible linear
  order — enumerated as the least family containing the empty set
  and closed under "add s when some name at s has some minimal
  support set already inside".

Tick-65's poset law is the special case where every site is "and":
well-founded sets are then exactly the ideals of the requirement
DAG, and for the 4-column geometry those ideals are the nested
height vectors counted by C(n+4,4).  The v1 corpus probe measured
that local or-support is the NORM (north-bond alternatives), so
the corpus-wide law must be stated at the well-founded level,
where unreachable local options (a site held only via a north
neighbour that itself needs the site) never materialise.
"""
from __future__ import annotations

from itertools import combinations, product

from .compiler import TAU, glue_strength
from .parity import FACE_DIR, OPPOSITE, producible  # noqa: F401 (re-export)

def occupants_of(seen):
    """site -> set of tile names the BFS ever placed there (y>=1)."""
    occ = {}
    for asm in seen:
        for pos, name in asm:
            if pos[1] >= 1:
                occ.setdefault(pos, set()).add(name)
    return occ

def presence_sets(seen):
    """Assemblies as frozensets of non-seed sites (the seed-only
    assembly maps to the empty set)."""
    return {frozenset(pos for pos, _name in asm if pos[1] >= 1)
            for asm in seen}

def _terms(build, site, name, occ):
    """Bond terms of `name` at `site`: constant seed strength plus
    (neighbour_site, possible_strengths) for occupied non-seed
    neighbours (one strength per possible neighbour name)."""
    faces = build["tiles"][name]
    const = 0
    var = []  # (nbr_site, frozenset(strengths))
    for face, (dx, dy) in FACE_DIR.items():
        g1 = faces.get(face)
        if not g1:
            continue
        nbr = (site[0] + dx, site[1] + dy)
        if nbr[1] == 0 and nbr in build["seed"]:
            const += glue_strength(g1, build["seed"][nbr])
        elif nbr in occ:
            strengths = frozenset(
                glue_strength(g1, build["tiles"][n2].get(OPPOSITE[face]))
                for n2 in occ[nbr])
            if strengths:
                var.append((nbr, strengths))
    return const, var

def minimal_supports(build, site, name, occ):
    """All minimal non-seed support sets of (site, name), pooled
    over every contended-neighbour name combination."""
    const, var = _terms(build, site, name, occ)
    sites = [s for s, _st in var]
    pooled = set()
    for combo in product(*[sorted(st) for _s, st in var]):
        strength = dict(zip(sites, combo))
        supports = set()
        for r in range(len(sites) + 1):
            for sub in combinations(sites, r):
                if const + sum(strength[s] for s in sub) >= TAU:
                    supports.add(frozenset(sub))
        pooled |= {s for s in supports
                   if not any(s2 < s for s2 in supports)}
    return frozenset(pooled)

def grammar(build, seen):
    """(supports, classes, occ): supports[site][name] = frozenset
    of minimal support frozensets; per-site grammar class; the
    occupant map."""
    occ = occupants_of(seen)
    supports, classes = {}, {}
    for site, names in occ.items():
        per_name = {name: minimal_supports(build, site, name, occ)
                    for name in names}
        supports[site] = per_name
        if len(names) > 1:
            first = per_name[next(iter(names))]
            classes[site] = ("contended-shared"
                             if all(s == first for s in per_name.values())
                             else "contended-split")
        elif len(next(iter(per_name.values()))) == 1:
            classes[site] = "and"
        else:
            classes[site] = "or-support"
    return supports, classes, occ

def _addable(supports, site, current):
    """Some name at `site` has some minimal support set inside
    `current`."""
    return any(ms <= current
               for name_supp in supports[site].values()
               for ms in name_supp)

def well_founded_sets(supports):
    """All well-founded sets: least family containing the empty
    set and closed under adding an addable site."""
    memo = set()
    def visit(current):
        key = frozenset(current)
        if key in memo:
            return
        memo.add(key)
        for site in supports:
            if site not in current and _addable(supports, site, current):
                visit(current | {site})
    visit(frozenset())
    return memo

def requirement_dag(supports):
    """site -> its unique minimal support set; only meaningful for
    sites of class "and" (the tick-65 case).  Raises ValueError if
    any site is not unique-support."""
    dag = {}
    for site, per_name in supports.items():
        if len(per_name) != 1:
            raise ValueError(f"contended site {site} has no unique support")
        supp = next(iter(per_name.values()))
        if len(supp) != 1:
            raise ValueError(f"or-support site {site} has no unique support")
        dag[site] = next(iter(supp))
    return dag

def ideals_of(dag):
    """All downward-closed sets (order ideals) of the requirement
    DAG, enumerated by DFS from the empty set."""
    memo = set()
    def visit(current):
        key = frozenset(current)
        if key in memo:
            return
        memo.add(key)
        for site, req in dag.items():
            if site not in current and req <= current:
                visit(current | {site})
    visit(frozenset())
    return memo
