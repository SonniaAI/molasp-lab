"""Exhaustive aTAM (tau=2) producibility check for designs/002 — the
2-cycle witness `a. p :- q. q :- p.` on the value-typed 3-row system in
tiles_2cycle.py.  Same BFS as atam_check_v2/v3.py.  Claims:

  1. The system grows.
  2. D1F (a := false despite the fact) is never producible.
  3. D2T (p := true; the CUT-EDGE tile, south glue `q-true` unique-name
     unexposed) is never producible.
  4. D3T (q := true; the WIRED tile, south glue rd2t-done exposed only
     by D2T) is never producible — transitive death.
  5. Every terminal assembly decodes to {a}, the unique stable model;
     the supported-but-unstable {a,p,q} has NO realizing assembly.

designs/002-specific structural claims:

  6. Unique-name inertness: `q-true` and `SP4` each appear exactly once
     across the whole system (tiles + seed) — an inert name cannot be
     an accidental witness (tick-11 lesson: count occurrences in the
     FULL system, not vs-all-other-glues).
  7. rd2t-done (the wired edge's witness glue) is exposed by exactly
     one tile face in the system — D2T's north — so its death is
     exactly D2T's death, nothing else's.
  8. Value-side glue pairs all strength 0 (v3 rule (a) carried across
     rows AND up the vertical channels): L1.W-vs-D1F.E, D2F.S-vs-D1F.N,
     L2.W-vs-D2T.E, D3T.S-vs-D2F.N (the dead edge cannot ride p's
     false row), D3F.S-vs-D2T.N, L3.W-vs-D3T.E.
  9. Wrong contexts keep strictly fewer bonds than correct contexts.
"""
import json
from tiles_2cycle import (TILES, SEED_TILES, SEED_N, SITES,
                          matched_strength, glue_strength, has_neighbour)

TAU = 2


def freeze(assembly):
    return frozenset((s, t) for s, t in assembly.items() if s not in SEED_TILES)


def decode(assembly):
    a = {"D1T": True, "D1F": False}.get(assembly.get((1, 1)))
    p = {"D2T": True, "D2F": False}.get(assembly.get((1, 2)))
    q = {"D3T": True, "D3F": False}.get(assembly.get((1, 3)))
    locked = (assembly.get((2, 1)) == "L1" and assembly.get((2, 2)) == "L2"
              and assembly.get((2, 3)) == "L3")
    spined = (assembly.get((0, 1)) == "S1" and assembly.get((0, 2)) == "S2"
              and assembly.get((0, 3)) == "S3")
    if a is None or p is None or q is None or not (locked and spined):
        return "partial"
    bits = ""
    bits += "a" if a else ""
    bits += "p" if p else ""
    bits += "q" if q else ""
    return bits if bits else "empty"


def producible():
    seen = {freeze(SEED_TILES)}
    frontier = [dict(SEED_TILES)]
    terminals = []
    while frontier:
        asm = frontier.pop()
        moves = 0
        for site in SITES:
            if site not in asm and has_neighbour(asm, site):
                for tile in TILES:
                    if matched_strength(asm, site, tile) >= TAU:
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


def glue_occurrences():
    occ = {}
    for t, faces in TILES.items():
        for g in faces.values():
            occ[g] = occ.get(g, 0) + 1
    for g in SEED_N.values():
        occ[g] = occ.get(g, 0) + 1
    return occ


def exposes_glue(glue):
    """Tiles whose NORTH face carries `glue` — the only faces a row
    above can read as a body witness (seed south faces aside)."""
    north = [t for t, faces in TILES.items() if faces.get("N") == glue]
    south = [t for t, faces in TILES.items() if faces.get("S") == glue]
    seed = [site for site, g in SEED_N.items() if g == glue]
    return {"north": north, "south": south, "seed": seed}


def value_blind_bonds():
    pairs = {
        "L1.W_rd1t_vs_D1F.E_rd1f": glue_strength("rd1t", "rd1f"),
        "D2F.S_rd1t-done_vs_D1F.N_rd1f-done":
            glue_strength("rd1t-done", "rd1f-done"),
        "L2.W_rd2f_vs_D2T.E_rd2t": glue_strength("rd2f", "rd2t"),
        "D3T.S_rd2t-done_vs_D2F.N_rd2f-done":
            glue_strength("rd2t-done", "rd2f-done"),
        "D3F.S_rd2f-done_vs_D2T.N_rd2t-done":
            glue_strength("rd2f-done", "rd2t-done"),
        "L3.W_rd3f_vs_D3T.E_rd3t": glue_strength("rd3f", "rd3t"),
    }
    contexts = []

    def ctx_row1():
        base = dict(SEED_TILES); base[(0, 1)] = "S1"
        w = dict(base); w[(1, 1)] = "D1F"
        c = dict(base); c[(1, 1)] = "D1T"
        contexts.append(("L1_total_D1F", matched_strength(w, (2, 1), "L1"),
                         "L1_total_D1T", matched_strength(c, (2, 1), "L1")))

    def ctx_row2():
        base = dict(SEED_TILES)
        base.update({(0, 1): "S1", (1, 1): "D1T", (0, 2): "S2"})
        w = dict(base); w[(1, 1)] = "D1F"
        c = dict(base)
        contexts.append(("D2F_total_above_D1F", matched_strength(w, (1, 2), "D2F"),
                         "D2F_total_above_D1T", matched_strength(c, (1, 2), "D2F")))
        w2 = dict(base); base2 = dict(base); base2[(1, 1)] = "D1T"
        w2[(1, 2)] = "D2T"; c2 = dict(base2); c2[(1, 2)] = "D2F"
        contexts.append(("L2_total_D2T", matched_strength(w2, (2, 2), "L2"),
                         "L2_total_D2F", matched_strength(c2, (2, 2), "L2")))

    def ctx_row3():
        base = dict(SEED_TILES)
        base.update({(0, 1): "S1", (1, 1): "D1T", (2, 1): "L1",
                     (0, 2): "S2", (1, 2): "D2F", (2, 2): "L2",
                     (0, 3): "S3"})
        w = dict(base); w[(1, 2)] = "D2T"
        c = dict(base)
        contexts.append(("D3F_total_above_D2T", matched_strength(w, (1, 3), "D3F"),
                         "D3F_total_above_D2F", matched_strength(c, (1, 3), "D3F")))
        w2 = dict(base); w2[(1, 3)] = "D3T"
        c2 = dict(base); c2[(1, 3)] = "D3F"
        contexts.append(("L3_total_D3T", matched_strength(w2, (2, 3), "L3"),
                         "L3_total_D3F", matched_strength(c2, (2, 3), "L3")))

    ctx_row1(); ctx_row2(); ctx_row3()
    return {"pair_strengths": pairs, "context_totals": contexts}


if __name__ == "__main__":
    seen, terminals = producible()
    decodes = sorted(decode(t) for t in terminals)
    ever = lambda name: any(name in dict(a).values() for a in seen)
    occ = glue_occurrences()
    out = {
        "producible_assemblies": len(seen),
        "terminal_assemblies": len(terminals),
        "terminal_decodes": decodes,
        "D1F_ever_producible": ever("D1F"),
        "D2T_ever_producible": ever("D2T"),
        "D3T_ever_producible": ever("D3T"),
        "unique_name_glues": {g: occ[g] for g in ("q-true", "SP4")},
        "rd2t-done_exposed_by": exposes_glue("rd2t-done"),
        "value_blind_bond_strengths": value_blind_bonds(),
    }
    print(json.dumps(out, indent=2, default=str))
    assert len(terminals) >= 1 and decodes == ["a"] * len(terminals), \
        "terminal claim violated"
    assert not ever("D1F") and not ever("D2T") and not ever("D3T"), \
        "wrong-tile producibility"
    assert occ["q-true"] == 1 and occ["SP4"] == 1, "unique-name inertness"
    assert exposes_glue("rd2t-done")["north"] == ["D2T"] and \
        not exposes_glue("rd2t-done")["seed"], "wired-edge witness exposure"
    blind = value_blind_bonds()
    assert all(b == 0 for b in blind["pair_strengths"].values()), \
        "a lock or vertical channel still bonds a wrong value"
    for wrong_key, wrong_b, correct_key, correct_b in blind["context_totals"]:
        assert wrong_b < correct_b, f"{wrong_key} not value-limited ({wrong_b})"
    print("aTAM 2cycle CHECK PASSED: system grows; unique terminal decodes"
          " {a}; D1F/D2T/D3T never producible at tau=2; q-true and SP4"
          " unique-name inert; rd2t-done exposed only by the never-producible"
          " D2T (transitive death); no value-side glue bonds a wrong value.")
