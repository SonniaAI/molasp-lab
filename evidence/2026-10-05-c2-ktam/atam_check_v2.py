"""Exhaustive aTAM (tau=2) producibility check for designs/001 v2.

Same BFS as atam_check.py, over the strength-2-spine construction in
tiles_v2.py. Claims to machine-check:
  1. The system grows (v1 did not -- its checker output is evidence/).
  2. D1F (a := false despite the fact) is never producible.
  3. D2T (the unfounded p := true) is never producible.
  4. Every terminal assembly decodes to {a}, the unique stable model.
"""
import json
from tiles_v2 import TILES, SEED_TILES, SITES, matched_strength, has_neighbour

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


if __name__ == "__main__":
    seen, terminals = producible()
    decodes = sorted(decode(t) for t in terminals)
    ever = lambda name: any(name in dict(a).values() for a in seen)
    out = {
        "producible_assemblies": len(seen),
        "terminal_assemblies": len(terminals),
        "terminal_decodes": decodes,
        "D1F_ever_producible": ever("D1F"),
        "D2T_ever_producible": ever("D2T"),
    }
    print(json.dumps(out, indent=2))
    assert len(terminals) >= 1 and decodes == ["a"] * len(terminals), "terminal claim violated"
    assert not ever("D1F") and not ever("D2T"), "wrong-tile producibility"
    print("aTAM v2 CHECK PASSED: system grows; every terminal assembly"
          " decodes to {a}; D1F and D2T never producible at tau=2.")
