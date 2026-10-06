"""designs/002 tile system — the 2-cycle witness `a. p :- q. q :- p.`

Program P:   fact a;  rules p :- q,  q :- p.
Stable model: {a}.  Supported-but-unstable: {a,p,q} (p "supported" by
q, q by p — pure circular support; clingo anchor: the semantics of this
program family is machine-checked in
../2026-10-06-clingo-crosscheck/).

Stage analysis (immediate-consequence fixpoint, the compile-time solve
the lowering reads its order from):
    stage 0: {a};  stage s+1: no new atoms (p needs q, q needs p).
    Least model {a}: a=true, p=false, q=false.  stage(p)=stage(q)=inf.

Row order (a linear extension of the stage order): row 1 = a (fact),
row 2 = p, row 3 = q.  The order cuts the cycle at the edge q -> p
(p's only rule body sits ABOVE its head): D2T's south glue `q-true` is
a unique name in the whole system — nothing below the p-row exposes a
q-true witness, so D2T has no strength-2 attachment path at any time.
The other cycle edge p -> q is WIRED (D3T.S = rd2t-done, p's true-done
glue, sits directly below) but transitively dead: rd2t-done is exposed
only by D2T, which is never producible.  The falsity chain anchors both
rows from below: D2F.S bonds row 1's true-done glue (a=true), D3F.S
bonds row 2's FALSE-done glue (p=false) — value-typed (v3 discipline,
designs/001 catalogue rule (a)), so the dead edge cannot ride p's false
row either: rd2t-done vs rd2f-done is strength 0.

Lemma this system makes executable (the designs/002 claim): a rule with
a false head dies in EITHER geometry — if the false body atom is above
the head, its true-glue is unexposed (the no-p mechanism); if it is
below, its row exposes only its false-done glue, which the head's
true-tile does not bond.  The cycle cannot fire at any position: the
level mapping is supplied by the row order, not by species count.

Tile types: 12 (+3 seed).  Glue alphabet: 26 names.  τ=2; spine glues
SP1/SP2/SP3 strength 2 and row-typed (v2.0 lesson), SP4 unique-name
inert cap.  aTAM τ=2 exhaustive check: atam_check_2cycle.py.
"""
FACE_DIR = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
DIRS = list(FACE_DIR.values())

STRENGTH = {("SP1", "SP1"): 2, ("SP2", "SP2"): 2, ("SP3", "SP3"): 2}

TILES = {
    # spine, row-typed, strength-2 chain
    "S1": {"S": "SP1", "E": "go1", "N": "SP2"},
    "S2": {"S": "SP2", "E": "go2", "N": "SP3"},
    "S3": {"S": "SP3", "E": "go3", "N": "SP4"},
    # row 1: atom a (fact) — value-typed exactly as designs/001 v3
    "D1T": {"W": "go1", "S": "f-a",       "E": "rd1t", "N": "rd1t-done"},
    "D1F": {"W": "go1", "S": "u-a",       "E": "rd1f", "N": "rd1f-done"},
    "L1":  {"W": "rd1t", "S": "base",     "N": "base2"},
    # row 2: atom p; only rule p :- q, q sits ABOVE → the CUT EDGE.
    # D2T's south glue q-true is a unique name: unexposed by construction.
    "D2T": {"W": "go2", "S": "q-true",    "E": "rd2t", "N": "rd2t-done"},
    "D2F": {"W": "go2", "S": "rd1t-done", "E": "rd2f", "N": "rd2f-done"},
    "L2":  {"W": "rd2f", "S": "base2",    "N": "base3"},
    # row 3: atom q; only rule q :- p, p sits BELOW → WIRED but
    # transitively dead: rd2t-done is exposed only by D2T (never
    # producible).  D3F bonds p's FALSE-done glue — the falsity chain.
    "D3T": {"W": "go3", "S": "rd2t-done", "E": "rd3t", "N": "rd3t-done"},
    "D3F": {"W": "go3", "S": "rd2f-done", "E": "rd3f", "N": "rd3f-done"},
    "L3":  {"W": "rd3f", "S": "base3",    "N": "cap3"},
}
SEED_N = {(0, 0): "SP1", (1, 0): "f-a", (2, 0): "base"}
SEED_TILES = {(0, 0): "seed0", (1, 0): "seed1", (2, 0): "seed2"}
SITES = [(0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2),
         (0, 3), (1, 3), (2, 3)]


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
