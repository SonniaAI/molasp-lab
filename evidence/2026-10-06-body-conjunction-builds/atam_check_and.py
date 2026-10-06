"""Exhaustive aTAM (tau=2) producibility check for designs/003 — the
body-conjunction builds F1-F3 (tick 18, SON-4758).

Grid: 4 columns x 3 rows over a 4-wide seed.  BFS over all assemblies
reachable by strength >= tau attachments; a terminal is an assembly
with no legal move.  decode() reads the LOCK column: a row is TRUE iff
its lock tile bonds a `-t` value on W, FALSE iff `-f`, absent = dead.

Pre-registered criteria (designs/003, written tick 17 before any of
this ran):

  F1 (foundedness of the AND)
    - BUILD1: exactly one terminal, decoding {p,q,r};
    - re-run with p's fact deleted: r's true tiles producible in 0;
    - re-run with q's fact deleted: r's true tiles producible in 0.
  F2 (slot-A death)
    - BUILD2: unique terminal {p}; no tile exposing q-t / and1_r /
      r-t ever producible (build 2 has no slot-A tiles at all — the
      meaningful content is the unique false-locked terminal).
  F3 (certificate arm)
    - BUILD3: unique terminal {q,r}, a NON-model of P_AND-p (clingo:
      stable model is {q}); the BFS-vs-clingo certificate must fire.
      Static AND-discipline (d2) must also flag it: no south read of
      p anywhere in r's row.

Errata demolitions (as-written tables, machine-checked here):
  E1  BUILD1_RAW stalls at {p}: D2T.S=f-q matches nothing below.
  E2  BUILD3_RAW stalls at {q} — which IS the stable model of
      P_AND-p: the wrong compile escapes the semantic certificate by
      stalling.  Only the static discipline (d2) catches it.  This is
      why d2 is a compiler invariant, not a nicety.

Structural checks (designs/003 candidate invariants):
  d1 (via discipline): any tile exposing a witness glue <x>-t-done on
      N, where x is not the tile's own row atom, must read <x>-t-done
      on S (source stubs and fact decisions originate their OWN row's
      witness and are exempt by the row-atom test).
  d2 (AND discipline): for each predicted-TRUE atom with a non-empty
      positive body, every body literal's <x>-t-done appears as a
      south read among that row's tiles.
  unique-name inertness: SP4, cap3, rf-relay, w1-relay, pf-cap each
      occur exactly once across tiles+seed of the build using them.

clingo (5.8.0 on the pod) anchors the semantics of all three
programs; the certificate compares BFS decode vs clingo enumeration.

Writes the JSON receipt to atam_and.out next to this file.
"""
import json
import os

from tiles_and import BUILDS, PROGRAMS, TAU, FACE_DIR, OPPOSITE, glue_strength

SITES = [(x, y) for y in (1, 2, 3) for x in (0, 1, 2, 3)]


def freeze(assembly):
    return frozenset(assembly.items())


def seed_assembly(build):
    return {(x, 0): "seed" + str(x) for x in range(4)}


def matched_strength(build, asm, site, tile_name):
    """Total bond strength for tile_name at site given assembly asm
    (seed cells always present, exposing their north faces only)."""
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
    """TRUE atoms = rows whose lock (col 3) bonds a -t value."""
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
    """True iff any producible tile has `glue` on any face."""
    for asm in seen:
        for _pos, name in asm:
            if name.startswith("seed"):
                continue
            if any(v == glue for v in build["tiles"][name].values()):
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
    """d1: a tile exposing <x>-t-done on N for x not its own row atom
    must read <x>-t-done on S (it relays x's witness, so it must read
    it from the row below).  Tiles originating their own row atom's
    witness (fact decisions, reader slots, stubs) are exempt."""
    violations = []
    for name, faces in build["tiles"].items():
        n = faces.get("N", "")
        if not n.endswith("-t-done"):
            continue
        witness = n[: -len("-t-done")]
        row_atom = build["rows"].get(build["row_of"].get(name))
        if row_atom == witness:
            continue  # originates its own witness
        if faces.get("S", "") == witness + "-t-done":
            continue  # relay reads it below
        violations.append((name, n, faces.get("S", "")))
    return violations


def and_discipline(build, bodies):
    """d2: every positive body literal of a predicted-TRUE atom
    appears as a south read among that row's tiles (decision slots
    and conduits; locks/stubs contribute base faces that never match
    a witness pattern)."""
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


def main():
    report = {"tau": TAU, "checks": {}}
    ck = report["checks"]

    ck["clingo"] = {name: clingo_models(prog) for name, prog in PROGRAMS.items()}

    # ---- F1 -------------------------------------------------------
    b = BUILDS["build1"]
    seen, terms = producible(b)
    ck["F1_build1"] = {
        "assemblies": len(seen), "terminals": len(terms),
        "decodes": [decode(b, t)[0] for t in terms],
        "locked_rows": [decode(b, t)[1] for t in terms],
        "r_true_glue_producible": exposes_glue(b, seen, "r-t"),
    }
    for arm in ("build1_cutp", "build1_cutq"):
        b = BUILDS[arm]
        s2, t2 = producible(b)
        ck["F1_" + arm] = {
            "assemblies": len(s2), "terminals": len(t2),
            "decodes": sorted({decode(b, t)[0] for t in t2}),
            "r_true_glue_producible": exposes_glue(b, s2, "r-t"),
            "and1_r_producible": exposes_glue(b, s2, "and1_r"),
        }

    # ---- F2 -------------------------------------------------------
    b = BUILDS["build2"]
    seen2, terms2 = producible(b)
    ck["F2_build2"] = {
        "assemblies": len(seen2), "terminals": len(terms2),
        "decodes": [decode(b, t)[0] for t in terms2],
        "locked_rows": [decode(b, t)[1] for t in terms2],
        "q_t_producible": exposes_glue(b, seen2, "q-t"),
        "and1_r_producible": exposes_glue(b, seen2, "and1_r"),
        "r_t_producible": exposes_glue(b, seen2, "r-t"),
    }

    # ---- F3 -------------------------------------------------------
    b = BUILDS["build3"]
    seen3, terms3 = producible(b)
    dec3 = [decode(b, t)[0] for t in terms3]
    stable = ck["clingo"]["P_AND_minus_p"]
    stable_str = "".join(sorted(a.rstrip(".") for a in stable[0])) if stable else None
    ck["F3_build3"] = {
        "assemblies": len(seen3), "terminals": len(terms3),
        "decodes": dec3,
        "clingo_stable": stable,
        "certificate_fires": sorted(set(dec3)) != [stable_str],
    }
    ck["F3_d2_static"] = {"violations": and_discipline(b, {"r": ["p", "q"]})}

    # ---- errata demolitions ----------------------------------------
    for key, label in (("build1_raw", "E1"), ("build3_raw", "E2")):
        b = BUILDS[key]
        s, t = producible(b)
        ck[label + "_" + key] = {
            "assemblies": len(s), "terminals": len(t),
            "decodes": sorted({decode(b, x)[0] for x in t}),
        }

    # ---- d1 structural ----------------------------------------------
    ck["d1_via_discipline"] = {n: via_discipline(b) for n, b in BUILDS.items()}

    # ---- d2 on the CORRECT build must hold ---------------------------
    ck["d2_build1"] = {"violations": and_discipline(BUILDS["build1"],
                                                    {"r": ["p", "q"]})}

    # ---- unique-name inertness ----------------------------------------
    # w1-relay is NOT in this list: it is a load-bearing relay channel
    # (exposed once by F+, read once by Fp), not an inert name.
    names = ["SP4", "cap3", "rf-relay", "pf-cap", "u-cutp"]
    inert = {}
    for name, b in BUILDS.items():
        occ = {}
        for faces in b["tiles"].values():
            for g in faces.values():
                occ[g] = occ.get(g, 0) + 1
        for g in b["seed"].values():
            occ[g] = occ.get(g, 0) + 1
        inert[name] = {n: occ.get(n, 0) for n in names}
    ck["inertness"] = inert

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atam_and.out")
    with open(out, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    print(json.dumps(report, indent=1, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
