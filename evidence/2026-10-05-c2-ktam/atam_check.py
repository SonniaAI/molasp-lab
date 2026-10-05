"""Exhaustive aTAM (tau=2) producibility check for designs/001.

BFS over producible assemblies from the seed; a tile may attach at an
empty site iff its summed matched glue strength against current
neighbours is >= tau = 2 (all glues strength 1). Terminal assemblies
have no legal attachment. Decodes every terminal assembly.

Expected (hand argument, to be machine-checked here):
  - D1F unproducible: south mismatches the fact glue; east bond alone
    gives strength 1 < 2 in every reachable configuration.
  - D2T unproducible: south glue matches nothing ('no-p'); only its east
    bond can match, strength 1 < 2.
  => every terminal assembly decodes to {a}: the aTAM-level statement of
     C2 for the witness, with zero reliance on kinetics.
"""
import json
from itertools import product
from ktam_mc import TILES, SEED_N, SEED_TILES, SITES, matched_strength, has_neighbour, FACE_DIR

TAU = 2

def freeze(assembly):
    return frozenset((s, t) for s, t in assembly.items() if s not in SEED_TILES)

def decode(assembly):
    a = {"D1T": True, "D1F": False}.get(assembly.get((0, 1)))
    p = {"D2T": True, "D2F": False}.get(assembly.get((0, 2)))
    l1 = assembly.get((1, 1)) == "L1"
    l2 = assembly.get((1, 2)) == "L2"
    if a is None or p is None or not (l1 and l2):
        return "partial"
    if a and p:
        return "ap"
    if a:
        return "a"
    if p:
        return "p"
    return "empty"

def producible_terminals():
    start = freeze(SEED_TILES)
    seen = {start}
    frontier = [dict(SEED_TILES)]
    terminals = []
    while frontier:
        asm = frontier.pop()
        moves = []
        for site in SITES:
            if site not in asm and has_neighbour(asm, site):
                for tile in TILES:
                    if matched_strength(asm, site, tile) >= TAU:
                        nxt = dict(asm)
                        nxt[site] = tile
                        key = freeze(nxt)
                        if key not in seen:
                            seen.add(key)
                            frontier.append(nxt)
                        moves.append((site, tile))
        if not moves:
            terminals.append(asm)
    return seen, terminals

if __name__ == "__main__":
    seen, terminals = producible_terminals()
    decodes = sorted(decode(t) for t in terminals)
    out = {
        "producible_assemblies": len(seen),
        "terminal_assemblies": len(terminals),
        "terminal_decodes": decodes,
        "D1F_ever_producible": any(t.get((0, 1)) == "D1F" for t in seen if (0, 1) in dict(t)),
        "D2T_ever_producible": any("D2T" in dict(t).values() for t in seen),
    }
    print(json.dumps(out, indent=2))
    assert out["terminal_decodes"] == ["a"], "aTAM claim violated"
    assert not out["D1F_ever_producible"] and not out["D2T_ever_producible"]
    print("aTAM CHECK PASSED: every terminal assembly decodes to {a};"
          " D1F and D2T are never producible at tau=2.")
