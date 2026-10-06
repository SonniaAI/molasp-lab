"""Exhaustive aTAM (tau=2) producibility check for designs/001 v3.

Identical BFS to atam_check_v2.py, over the value-typed (evidence-
checking-lock) tile set in tiles_v3.py. The v3 glue renaming must not
disturb the aTAM guarantee: correct growth still uses the same
strength-1+strength-1 corners, wrong tiles still have no strength-2
attachment path. Claims to machine-check:
  1. The system grows.
  2. D1F (a := false despite the fact) is never producible.
  3. D2T (the unfounded p := true) is never producible.
  4. Every terminal assembly decodes to {a}, the unique stable model.
Plus the v3-specific regression claims:
  5. No lock bonds a wrong value's glue at any strength: L1 vs D1F's
     east/north, L2 vs D2T's east, D2F vs D1F's north — all strength 0.
"""
import json
from tiles_v3 import TILES, SEED_TILES, SITES, matched_strength, has_neighbour

TAU = 2


def freeze(assembly):
    return frozenset((s, t) for s, t in assembly.items() if s not in SEED_TILES)


def decode(assembly):
    a = {"D1T": True, "D1F": False}.get(assembly.get((1, 1)))
    p = {"D2T": True, "D2F": False}.get(assembly.get((1, 2)))
    locked = assembly.get((2, 1)) == "L1" and assembly.get((2, 2)) == "L2"
    spined = assembly.get((0, 1)) == "S1" and assembly.get((0, 2)) == "S2"
    if a is None or p is None or not (locked and spined):
        return "partial"
    if a and p:
        return "ap"
    if a:
        return "a"
    if p:
        return "p"
    return "empty"


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


def value_blind_bonds():
    """v2.1 allowed each lock to bond a wrong value's glue (strength 1 on
    the value-side face). v3 must not. Reports (a) the value-side glue-pair
    strengths directly, and (b) matched_strength of the lock in wrong vs
    correct context: wrong must be strictly lower — the residue is the
    structural seed/spine bond only. (First version of this test asserted
    total strength == 0 in the wrong context and failed on the structural
    bond — the checker caught its own mis-specified test; fixed.)"""
    from tiles_v3 import glue_strength
    pairs = {
        "L1.W_rd1t_vs_D1F.E_rd1f": glue_strength("rd1t", "rd1f"),
        "D2F.S_rd1t-done_vs_D1F.N_rd1f-done": glue_strength("rd1t-done", "rd1f-done"),
        "L2.W_rd2f_vs_D2T.E_rd2t": glue_strength("rd2f", "rd2t"),
    }
    contexts = []
    # L1 east of D1F vs east of D1T (S=base bond present in both)
    base = dict(SEED_TILES); base[(0, 1)] = "S1"
    w = dict(base); w[(1, 1)] = "D1F"
    c = dict(base); c[(1, 1)] = "D1T"
    contexts.append(("L1_total_D1F", matched_strength(w, (2, 1), "L1"),
                     "L1_total_D1T", matched_strength(c, (2, 1), "L1")))
    # D2F above D1F vs above D1T (W=go2 bond present in both)
    base = dict(SEED_TILES); base[(0, 1)] = "S1"; base[(0, 2)] = "S2"
    w = dict(base); w[(1, 1)] = "D1F"
    c = dict(base); c[(1, 1)] = "D1T"
    contexts.append(("D2F_total_above_D1F", matched_strength(w, (1, 2), "D2F"),
                     "D2F_total_above_D1T", matched_strength(c, (1, 2), "D2F")))
    # L2 east of D2T vs east of D2F (S=base2 bond present in both)
    base = dict(SEED_TILES); base[(0, 1)] = "S1"; base[(0, 2)] = "S2"
    base[(1, 1)] = "D1T"; base[(2, 1)] = "L1"
    w = dict(base); w[(1, 2)] = "D2T"
    c = dict(base); c[(1, 2)] = "D2F"
    contexts.append(("L2_total_D2T", matched_strength(w, (2, 2), "L2"),
                     "L2_total_D2F", matched_strength(c, (2, 2), "L2")))
    return {"pair_strengths": pairs, "context_totals": contexts}


if __name__ == "__main__":
    seen, terminals = producible()
    decodes = sorted(decode(t) for t in terminals)
    ever = lambda name: any(name in dict(a).values() for a in seen)
    blind = value_blind_bonds()
    out = {
        "producible_assemblies": len(seen),
        "terminal_assemblies": len(terminals),
        "terminal_decodes": decodes,
        "D1F_ever_producible": ever("D1F"),
        "D2T_ever_producible": ever("D2T"),
        "value_blind_bond_strengths": dict(blind),
    }
    print(json.dumps(out, indent=2))
    assert len(terminals) >= 1 and decodes == ["a"] * len(terminals), "terminal claim violated"
    assert not ever("D1F") and not ever("D2T"), "wrong-tile producibility"
    assert all(b == 0 for b in blind["pair_strengths"].values()), \
        "a lock's value-side glue still bonds a wrong value"
    for wrong_key, wrong_b, correct_key, correct_b in blind["context_totals"]:
        assert wrong_b < correct_b, f"{wrong_key} not value-limited ({wrong_b})"
    print("aTAM v3 CHECK PASSED: system grows; every terminal assembly decodes"
          " to {a}; D1F and D2T never producible at tau=2; no lock's value-side"
          " glue bonds a wrong value (wrong contexts keep only structural"
          " bonds, strictly fewer than correct contexts).")
