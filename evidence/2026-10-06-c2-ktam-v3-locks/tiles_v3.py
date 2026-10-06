"""v3 tile system for designs/001 — evidence-checking locks.

v2.1 flaw, measured 2026-10-06 (evidence/2026-10-06-c2-ktam-v2-window):
the locks are value-blind. L1's W=r1 bonds D1T's E=r1 and D1F's E=r1
alike; L2's W=r2 bonds D2F and D2T alike; and D2F's S=row1done bonds
D1T's N and D1F's N alike. So any sub-tau near-miss that survives until
a lock arrives becomes terminal: the unfounded channel tracks the same
~e^{-dG} trap level as the founded one (at dG=0.5 it EQUALS it).

v3 rule (designs/001 section "v3"): a lock must check the value it
locks. Value-type every glue that carries a decision value across a
tile boundary:
    D1T: E=rd1t, N=rd1t-done      D1F: E=rd1f, N=rd1f-done
    L1 : W=rd1t                    (bonds only D1T)
    D2F: S=rd1t-done, E=rd2f       D2T: E=rd2t (S=no-p unchanged)
    L2 : W=rd2f                    (bonds only D2F)
Note the N/S channel must be typed too: with a blind row1done, D2F
arriving above a transient D1F bonds W+S = 2 and locks the wrong value
with ONE coincidence — the e^{-2*dG} claim would silently fail on the
founded channel. With all three lock interfaces typed, locking a wrong
value requires two coincident sub-tau attachments: the wrong decision
tile (b=1) AND its locker reduced to a single bond (b=1).

Correct growth is unchanged: every correct assembly bond pattern is the
same two-strength-1 corner as v2.1, only glue names differ. aTAM
producibility is re-checked by atam_check_v3.py (the compiler emits the
check for every emitted tile set — this file is the second entry in
that habit).

Witness: a. p :- p.  Stable: {a}; supported-but-unstable: {a,p}.
"""
FACE_DIR = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
DIRS = list(FACE_DIR.values())

STRENGTH = {("SP1", "SP1"): 2, ("SP2", "SP2"): 2}

TILES = {
    # spine, row-typed (unchanged from v2.1)
    "S1": {"S": "SP1", "E": "go1", "N": "SP2"},
    "S2": {"S": "SP2", "E": "go2", "N": "SP3"},
    # row 1: atom a (fact present); E and N now carry the value
    "D1T": {"W": "go1", "S": "f-a",       "E": "rd1t", "N": "rd1t-done"},
    "D1F": {"W": "go1", "S": "u-a",       "E": "rd1f", "N": "rd1f-done"},
    "L1":  {"W": "rd1t", "S": "base",     "N": "base2"},
    # row 2: atom p (only rule is the unencodable self-loop p :- p)
    "D2T": {"W": "go2", "S": "no-p",      "E": "rd2t", "N": "topT"},
    "D2F": {"W": "go2", "S": "rd1t-done", "E": "rd2f", "N": "topF"},
    "L2":  {"W": "rd2f", "S": "base2",    "N": "cap2"},
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
