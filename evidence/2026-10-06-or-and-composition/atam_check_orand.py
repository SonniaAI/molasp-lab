"""Exhaustive aTAM (tau=2) producibility check for the OR-AND
composition builds (tick 20, SON-4763).  Self-contained; grid and BFS
inherited from evidence/2026-10-06-body-conjunction-builds.

Pre-registered criteria (designs/003 amendment, written before this
ran):

  G1 (composition)  BUILD1: every terminal decodes {p,q,r} with 3
      locked rows; BOTH variant paths realize (some terminal carries
      DAr&DBr, some carries Cr&Ur); no assembly mixes variants.
  G1-cut  seed surgery on p's fact: r's true glue producible in 0
      (expected over-collapse, mirroring tick 18 finding 3).
  G2 (OR rescue)  BUILD2: unique terminal decode {p,r} — the same
      deletion that killed r in designs/003 build 2 (pure AND) now
      survives via the unit rule; conjunctive-path glues q-t /
      q-t-done / and1_r producible in 0; DBr in no assembly.
  G3 (foundedness)  BUILD3: unique terminal {q}; p-t and r-t
      producible in 0 (both rules of r die with p).
  G4 (certificate)  BUILD4: unique terminal {p} != clingo stable
      {p,r} of P_OA_minus_q — the emit-time certificate fires; the
      static d3 closure check fires independently.
  d1/d2  via + AND discipline hold on all builds (d2 static: the
      conjunctive body literals q,p both south-read in r's row).
  d3 (new, OR discipline / compile-model closure)  the compiled
      predicted-true set must be closed and supported under the
      program's own rules: no rule with body inside the set may have
      its head predicted false (closure), every predicted-true atom
      is a fact or has a fully-supported rule (support).  W2's
      dropped-unit-rule compile violates closure via r :- p.

Inertness (unique-name rule): SP4, cap3, and1_r-done, unit1_r-done,
rf-relay, u-cutp each occur exactly once across tiles+seed of every
build using them.  r-t-done is DELIBERATELY not in that list: it is
the shared value output of the OR pair — inventory count 2 (DBr.N
and Ur.N), per-assembly count <= 1 (the two readers compete for the
same site).  That count-2 fingerprint IS the OR pair convention.
"""
import json
import os

from tiles_orand import (BUILDS, PROGRAMS, FACTS, RULES, PREDICTED, TAU,
                         FACE_DIR, OPPOSITE, glue_strength)

SITES = [(x, y) for y in (1, 2, 3) for x in (0, 1, 2, 3)]


def freeze(assembly):
    return frozenset(assembly.items())


def seed_assembly(build):
    return {(x, 0): "seed" + str(x) for x in range(4)}


def matched_strength(build, asm, site, tile_name):
    faces = build["tiles"][tile_name]
    total = 0
    for face, (dx, dy) in FACE_DIR.items():
        g1 = faces.get(face)
        if not g1:
            continue
        nx, ny = site[0] + dx, site[1] + dy
        if ny == 0 and (nx, 0) in build["seed"]:
            g2 = build["seed"][(nx, 0)]
        elif (nx, ny) in asm:
            g2 = build["tiles"][asm[(nx, ny)]].get(OPPOSITE[face])
        else:
            continue
        total += glue_strength(g1, g2)
    return total


def producible(build):
    seen = {freeze(seed_assembly(build))}
    frontier = [seed_assembly(build)]
    terminals = []
    while frontier:
        asm = frontier.pop()
        moves = 0
        for site in SITES:
            if site in asm:
                continue
            if not any((site[0] + dx, site[1] + dy) in asm
                       for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))):
                continue
            for tile in build["tiles"]:
                if matched_strength(build, asm, site, tile) >= TAU:
                    moves += 1
                    nxt = dict(asm)
                    nxt[site] = tile
                    key = freeze(nxt)
                    if key not in seen:
                        seen.add(key)
                        frontier.append(nxt)
        if moves == 0:
            terminals.append(asm)
    return seen, terminals


def decode(build, asm):
    true_atoms = []
    locked = 0
    for y, atom in build["rows"].items():
        lock = asm.get((3, y))
        if lock is not None:
            locked += 1
            if build["tiles"][lock]["W"].endswith("-t"):
                true_atoms.append(atom)
    return "".join(true_atoms), locked


def exposes_glue(build, seen, glue):
    for asm in seen:  # frozenset of ((x, y), tile) pairs
        for _pos, name in asm:
            if name.startswith("seed"):
                continue
            if any(v == glue for v in build["tiles"][name].values()):
                return True
    return False


def tile_in_any(build, seen, tile):
    for asm in seen:
        if any(name == tile for _pos, name in asm):
            return True
    return False


def clingo_models(program):
    try:
        import clingo
    except ImportError:
        return None
    ctl = clingo.Control()
    ctl.add("base", [], program)
    ctl.ground([("base", [])])
    models = []
    with ctl.solve(yield_=True) as handle:
        for m in handle:
            models.append(sorted(str(s) + "." for s in m.symbols(atoms=True)))
    return models


def via_discipline(build):
    violations = []
    for name, faces in build["tiles"].items():
        n = faces.get("N", "")
        if not n.endswith("-t-done"):
            continue
        witness = n[: -len("-t-done")]
        row_atom = build["rows"].get(build["row_of"].get(name))
        if row_atom == witness:
            continue
        if faces.get("S", "") == witness + "-t-done":
            continue
        violations.append((name, n, faces.get("S", "")))
    return violations


def and_discipline(build, bodies):
    violations = []
    for y, atom in build["rows"].items():
        if atom not in bodies:
            continue
        south_reads = [f.get("S", "") for n, f in build["tiles"].items()
                       if build["row_of"].get(n) == y]
        for lit in bodies[atom]:
            if lit + "-t-done" not in south_reads:
                violations.append((atom, lit, south_reads))
    return violations


def closure_support(true_set, facts, rules):
    """d3: the compiled predicted-true set must be a supported model
    of the program (closure: no live rule with a predicted-false
    head; support: every non-fact predicted-true atom has a fully
    in-set rule body)."""
    violations = []
    for h, bodies in rules.items():
        for body in bodies:
            if set(body) <= true_set and h not in true_set:
                violations.append(("closure", h, body))
    for a in sorted(true_set):
        if a in facts:
            continue
        if not any(set(b) <= true_set for b in rules.get(a, [])):
            violations.append(("support", a))
    return violations


def glue_counts(build):
    occ = {}
    for faces in build["tiles"].values():
        for g in faces.values():
            occ[g] = occ.get(g, 0) + 1
    for g in build["seed"].values():
        occ[g] = occ.get(g, 0) + 1
    return occ


def stable_str(models):
    return "".join(sorted(a.rstrip(".") for a in models[0])) if models else None


def main():
    report = {"tau": TAU, "checks": {}}
    ck = report["checks"]

    ck["clingo"] = {name: clingo_models(prog) for name, prog in PROGRAMS.items()}

    # ---- G1 -------------------------------------------------------
    b = BUILDS["build1"]
    seen, terms = producible(b)
    conj = [t for t in terms if "DAr" in t.values()]
    unit = [t for t in terms if "Cr" in t.values()]
    ck["G1_build1"] = {
        "assemblies": len(seen), "terminals": len(terms),
        "decodes": [decode(b, t)[0] for t in terms],
        "locked_rows": [decode(b, t)[1] for t in terms],
        "terminals_with_conj_variant": len(conj),
        "terminals_with_unit_variant": len(unit),
        "hybrid_assemblies": sum(
            1 for a in seen
            if ({n for _p, n in a} & {"DAr", "DBr"}
                and {n for _p, n in a} & {"Cr", "Ur"})),
        "shared_output_inventory_count": glue_counts(b).get("r-t-done"),
    }

    # ---- G1-cut (seed surgery) ------------------------------------
    b = BUILDS["build1_cutp"]
    s2, t2 = producible(b)
    ck["G1_cutp"] = {
        "assemblies": len(s2), "terminals": len(t2),
        "decodes": sorted({decode(b, t)[0] for t in t2}),
        "r_true_glue_producible": exposes_glue(b, s2, "r-t"),
    }

    # ---- G2 (OR rescue) -------------------------------------------
    b = BUILDS["build2"]
    seen2, terms2 = producible(b)
    ck["G2_build2"] = {
        "assemblies": len(seen2), "terminals": len(terms2),
        "decodes": [decode(b, t)[0] for t in terms2],
        "locked_rows": [decode(b, t)[1] for t in terms2],
        "q_t_producible": exposes_glue(b, seen2, "q-t"),
        "q_t_done_producible": exposes_glue(b, seen2, "q-t-done"),
        "and1_r_producible": exposes_glue(b, seen2, "and1_r"),
        "DBr_in_any_assembly": tile_in_any(b, seen2, "DBr"),
    }

    # ---- G3 -------------------------------------------------------
    b = BUILDS["build3"]
    seen3, terms3 = producible(b)
    ck["G3_build3"] = {
        "assemblies": len(seen3), "terminals": len(terms3),
        "decodes": [decode(b, t)[0] for t in terms3],
        "locked_rows": [decode(b, t)[1] for t in terms3],
        "p_t_producible": exposes_glue(b, seen3, "p-t"),
        "r_t_producible": exposes_glue(b, seen3, "r-t"),
    }

    # ---- G4 (certificate) -----------------------------------------
    b = BUILDS["build4"]
    seen4, terms4 = producible(b)
    dec4 = [decode(b, t)[0] for t in terms4]
    stable = stable_str(ck["clingo"]["P_OA_minus_q"])
    ck["G4_build4"] = {
        "assemblies": len(seen4), "terminals": len(terms4),
        "decodes": dec4,
        "clingo_stable_P_OA_minus_q": stable,
        "certificate_fires": sorted(set(dec4)) != [stable],
    }

    # ---- d1 / d2 / d3 ----------------------------------------------
    ck["d1_via_discipline"] = {n: via_discipline(b) for n, b in BUILDS.items()}
    ck["d2_conj_body"] = {
        n: (and_discipline(b, {"r": ["p", "q"]})
            if "r" in PREDICTED[n] else "n/a_r_predicted_false")
        for n, b in BUILDS.items() if "r" in b["rows"].values()}
    ck["d3_closure_support"] = {
        n: closure_support(set(PREDICTED[n]), FACTS, RULES)
        for n in BUILDS}

    # ---- inertness --------------------------------------------------
    names = ["SP4", "cap3", "and1_r-done", "unit1_r-done", "rf-relay", "u-cutp"]
    ck["inertness"] = {n: {g: glue_counts(b).get(g, 0) for g in names}
                       for n, b in BUILDS.items()}

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atam_orand.out")
    with open(out, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    print(json.dumps(report, indent=1, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
