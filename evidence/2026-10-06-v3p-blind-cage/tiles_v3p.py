"""v3p tile system for designs/001 — value-agnostic blind cage (tick 11).

Catalogue entry (b) as specified ("value-agnostic locks requiring two
independent bonds -> error ~e^{-2*dG}") is NOT realizable per-tile in
kTAM: a lock whose glues are value-blind bonds the wrong value with the
same strength as the correct one, so SOME closure is always a single
coincidence riding on the wrong tile's own sub-tau residency (~e^{-dG}).
The only fully value-agnostic alternative is to strip every
value-independent support bond so that EACH lock closure rides on
sub-tau residents — this file is that maximally-blind cage:

    D1T: W=go1, S=f-a, E=r1, N=row1done     (E/N value-BLIND now)
    D1F: W=go1, S=u-a, E=r1, N=row1done     (wrong tile: b=1 alone)
    L1 : W=r1,  S=cap1 (bonds NOTHING — seed bond stripped), N=base2
    D2F: W=go2, S=cap3 (bonds NOTHING — row coupling stripped), E=r2, N=topF
    D2T: W=go2, S=no-p, E=r2, N=topT        (wrong tile: b=1 alone)
    L2 : W=r2,  S=base2, N=cap2

Correct cage (all value-blind): D1T is the only tau-resident decision
tile (S=f-a bonds the seed); D2F/L1 are b=1 alone; L2 arrives at b=2
(W->D2F.E, S->L1.N) making D2F and L1 b=2 in turn. Correct growth
therefore pays a cooperative-overlap penalty (~e^{-2*dG} in rate at the
D2F^L1 overlap) that v2.1 and v3 do not. The wrong cage (D1F in place of
D1T, D2T in place of D2F) is the SAME arithmetic: it needs THREE sub-tau
windows to overlap (D1F, L1, D2F) plus the L2 arrival, so error scales
DEEPER than e^{-2*dG} — but only in lockstep with the correct-growth
penalty. The error/growth RATIO is the invariant; value-typing (v3) is
what breaks it. Measured aTAM (this file, run.out): the concession is total — the
stripped cage reaches exactly ONE tau=2 terminal, {seed, S1, S2, D1T},
decode "partial". The correct terminal {a} is itself unreachable (the
cage's remaining closures are mutually dependent b=1 transients), and
D1F/D2T attach 0 times. Unlike v3 (10 producible, 1 terminal {a}), the
blind cage loses aTAM-producible growth outright: correct growth
survives only kinetically, through sub-tau overlap windows.

Ratio arithmetic (prediction, MC queued): correct completion rides the
D2F(b=1) ^ L1(b=1) overlap + L2 arrival ~ e^{-2*dG} against D1T's
tau-residency; wrong completion additionally rides D1F's b=1 residency
~ e^{-3*dG}. Wrong/correct ~ e^{-dG} — the SAME ratio as v2.1
(wrong ~e^{-dG} against tau-direct correct growth). Value-agnostic
locking preserves the error/throughput ratio; only value-typing moves
it. Falsifier: an MC on this tile set showing wrong completions at or
above e^{-2*dG} while correct completion stays within e^{-dG} of v3's
rate would refute the lemma.

Witness: a. p :- p.  Stable {a}; supported-but-unstable {a,p}.
"""
import json

FACE_DIR = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
DIRS = list(FACE_DIR.values())
STRENGTH = {("SP1", "SP1"): 2, ("SP2", "SP2"): 2}

TILES = {
    "S1":  {"S": "SP1", "E": "go1", "N": "SP2"},
    "S2":  {"S": "SP2", "E": "go2", "N": "SP3"},
    "D1T": {"W": "go1", "S": "f-a", "E": "r1", "N": "row1done"},
    "D1F": {"W": "go1", "S": "u-a", "E": "r1", "N": "row1done"},
    "L1":  {"W": "r1", "S": "cap1", "N": "base2"},
    "D2F": {"W": "go2", "S": "cap3", "E": "r2", "N": "topF"},
    "D2T": {"W": "go2", "S": "no-p", "E": "r2", "N": "topT"},
    "L2":  {"W": "r2", "S": "base2", "N": "cap2"},
}
SEED_N = {(0, 0): "SP1", (1, 0): "f-a", (2, 0): "base"}
SEED_TILES = {(0, 0): "seed0", (1, 0): "seed1", (2, 0): "seed2"}
SITES = [(0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)]


def exposed_glue(assembly, site, d):
    nb = (site[0] + d[0], site[1] + d[1])
    if nb not in assembly:
        return None
    t = assembly[nb]
    if t.startswith("seed"):
        return SEED_N[nb] if d == FACE_DIR["S"] else None
    back = (-d[0], -d[1])
    for face, g in TILES[t].items():
        if FACE_DIR[face] == back:
            return g
    return None


def glue_strength(g, exp):
    if (g, exp) in STRENGTH:
        return STRENGTH[(g, exp)]
    if (exp, g) in STRENGTH:
        return STRENGTH[(exp, g)]
    return 1 if g == exp else 0


def matched_strength(assembly, site, tile):
    b = 0
    for face, g in TILES[tile].items():
        exp = exposed_glue(assembly, site, FACE_DIR[face])
        if exp is not None:
            b += glue_strength(g, exp)
    return b


def has_neighbour(assembly, site):
    return any((site[0] + d[0], site[1] + d[1]) in assembly for d in DIRS)


def decode(assembly):
    vals = set(assembly.values())
    a = "D1T" in vals
    p = "D2T" in vals
    complete = all(s in assembly for s in SITES)
    if complete and a and not p:
        return "a"
    if complete and a and p:
        return "ap"
    if complete and p:
        return "p"
    if complete:
        return "empty"
    return "partial"


def enumerate_aTAM(tau=2):
    """Exhaustive BFS over tau-stable assemblies from the seed.

    States are (site -> tile) dicts, keyed by sorted item tuples so the
    visited set branches on tile identity, not just occupancy.
    """
    start = dict(SEED_TILES)
    key0 = tuple(sorted(start.items()))
    seen = {key0}
    frontier = [start]
    terminals = []
    max_b = {t: 0 for t in ("D1F", "D2T")}
    while frontier:
        assembly = frontier.pop()
        grew = False
        for site in SITES:
            if site in assembly or not has_neighbour(assembly, site):
                continue
            for tile in TILES:
                b = matched_strength(assembly, site, tile)
                if b >= tau:
                    if tile in max_b:
                        max_b[tile] = max(max_b[tile], b)
                    nxt = dict(assembly)
                    nxt[site] = tile
                    key = tuple(sorted(nxt.items()))
                    if key not in seen:
                        seen.add(key)
                        frontier.append(nxt)
                    grew = True
        if not grew:
            terminals.append(assembly)
    return terminals, max_b


def main():
    terminals, max_b = enumerate_aTAM(tau=2)
    from collections import Counter
    decodes = Counter(decode(a) for a in terminals)
    wrong_terminals = [a for a in terminals if decode(a) in ("ap", "p", "empty")]
    report = {
        "tile_count": len(TILES) + len(SEED_TILES),
        "producible_states_note": "BFS over tau=2 attachments from seed",
        "terminals": len(terminals),
        "terminal_decodes": dict(decodes),
        "wrong_terminals": len(wrong_terminals),
        "max_b_of_wrong_tiles_in_producible": max_b,
        "v3_contrast": "v3: D1F/D2T producible in 0/10 assemblies, wrong terminal 0",
    }
    print(json.dumps(report, indent=2))
    for a in terminals:
        print(json.dumps({"decode": decode(a), "assembly": {str(k): v for k, v in sorted(a.items())}}))


if __name__ == "__main__":
    main()
