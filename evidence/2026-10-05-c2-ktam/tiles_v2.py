"""v2 tile system for designs/001 (fixes the v1 bootstrap flaw).

v1 flaw, caught by atam_check.py: at tau=2 nothing ever attaches -- the
decision tile's only initial bond is its south glue (strength 1) because
its east lock partner does not exist yet. v1's kTAM "growth" was
entirely strength-1 transient locking, which is the order-race error
channel itself, so v1 kTAM numbers measure that regime, not a tau=2
system. Kept as evidence; not the construction of record.

v2 fix: a vertical spine at column 0 carrying a STRENGTH-2 glue ("SP").
Spine tiles attach alone (south bond strength 2, tau-legal) and expose a
strength-1 east glue "go-i". Decision tiles now attach into a south+west
corner: west = spine (1), south = value input (1) -> 2. Locks likewise
(W+S). Strict level mapping: a decision tile at row i can only ever bond
to its own row's spine and the previous row's decision output -- support
arrives from below or not at all.

Strength-2 glues are standard aTAM (glue strength is a function of the
glue pair); kTAM equivalent: spine bond counts b=2 in exp(-b*Gse).

Witness: a. p :- p.   Stable: {a}; supported-but-unstable: {a,p}.
Sites: rows 1-2 x cols 0-2. Seed is a 3-wide row at y=0.
"""
FACE_DIR = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
DIRS = list(FACE_DIR.values())

# glue pair -> strength (default 1); row-indexed so spine tiles are not
# interchangeable across rows (S2 at row 1 was a real dead end in v2.0)
STRENGTH = {("SP1", "SP1"): 2, ("SP2", "SP2"): 2}

TILES = {
    # spine, row-typed
    "S1": {"S": "SP1", "E": "go1", "N": "SP2"},
    "S2": {"S": "SP2", "E": "go2", "N": "SP3"},
    # row 1: atom a (fact present)
    "D1T": {"W": "go1", "S": "f-a",      "E": "r1", "N": "row1done"},
    "D1F": {"W": "go1", "S": "u-a",      "E": "r1", "N": "row1done"},
    "L1":  {"W": "r1",  "S": "base",     "N": "base2"},
    # row 2: atom p (only rule is the unencodable self-loop p :- p)
    "D2T": {"W": "go2", "S": "no-p",     "E": "r2", "N": "topT"},
    "D2F": {"W": "go2", "S": "row1done", "E": "r2", "N": "topF"},
    "L2":  {"W": "r2",  "S": "base2",    "N": "cap2"},
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
