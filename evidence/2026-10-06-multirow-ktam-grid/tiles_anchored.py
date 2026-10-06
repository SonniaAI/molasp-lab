"""designs/002 order falsifier — the anchored cycle
`a.  p :- a.  p :- q.  q :- p.`  (OR construction)

Program P:   fact a;  rules p :- a,  p :- q,  q :- p.
Semantics (positive program, unique stable model = least model):
    stage 0: {a};  stage 1: {a,p} (p :- a fires);  stage 2: {a,p,q}.
Stable model {a,p,q} — machine-checked against real clingo in
atam_check_anchored.py (module available on the pod, tick 7 lesson).

The OR construction (the new piece this build adds to designs/002):
an atom with k defining rules gets k TRUE-variant tiles sharing value
outputs (E = <atom>-t, N = <atom>-t-done); a variant is live only if
its rule's body row sits directly below with its own true-done glue
exposed.  Here p has two variants: the ANCHOR p :- a (live) and the
cycle edge p :- q (cut: q sits above, so its witness can never be
adjacent to p's south face).

Three builds are defined, one per falsifier arm:

  CORRECT     rows a<p<q, cut edge p:-q (the body-above-head edge).
              Predicted unique terminal decode: {a,p,q} (the stable
              model) — the OR anchor fires, the wired edge q:-p
              reads p's true-done from directly below.
  WRONG_CUT   rows a<p<q but the cut placed the wrong way round
              (q:-p cut, p:-q nominally wired by name).  Predicted
              unique terminal decode {a,p}: q's only support is
              severed while p stays anchored — a wrong-but-terminal
              decode that is neither stable nor even a model of P.
  WRONG_ROWS  rows a<q<p (a non-stage order), name-typed wiring.
              Predicted unique terminal decode {a}: the anchor edge
              p:-a dies too — a's true-done glue is never adjacent to
              p's south face with q's row in between.  Losing the
              order loses the anchor itself; the decode collapses to
              the stable model of the program WITHOUT the anchor rule.

designs/002 criterion 4: if any wrong build still decoded {a,p,q},
stage order would NOT be load-bearing.  Measured outcome in
atam_anchored.out / designs/002.

Tile types: 13 (+3 seed) per build.  Glue alphabet: 27 names.
tau=2; spine SP1/SP2/SP3 strength 2, row-typed (v2.0 lesson); SP4
unique-name inert cap.  Value typing per v3 rule (a): done-glues
carry the atom's value, lock tiles bond only the predicted value's
output.  Inert names (u-a, u-p, u-q, q-true, u-cut, SP4, cap3) each
appear exactly once system-wide (tick-11 inertness rule).
"""
FACE_DIR = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
DIRS = list(FACE_DIR.values())

STRENGTH = {("SP1", "SP1"): 2, ("SP2", "SP2"): 2, ("SP3", "SP3"): 2}

SEED_N = {(0, 0): "SP1", (1, 0): "f-a", (2, 0): "base"}
SEED_TILES = {(0, 0): "seed0", (1, 0): "seed1", (2, 0): "seed2"}
SITES = [(0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2),
         (0, 3), (1, 3), (2, 3)]

SPINE = {
    "S1": {"S": "SP1", "E": "go1", "N": "SP2"},
    "S2": {"S": "SP2", "E": "go2", "N": "SP3"},
    "S3": {"S": "SP3", "E": "go3", "N": "SP4"},
}
ROW_A = {  # atom a: fact, predicted TRUE
    "D1T": {"W": "go1", "S": "f-a",      "E": "ra-t", "N": "ra-t-done"},
    "D1F": {"W": "go1", "S": "u-a",      "E": "ra-f", "N": "ra-f-done"},
    "L1":  {"W": "ra-t", "S": "base",    "N": "base2"},
}

# p's OR pair: two TRUE variants sharing value outputs (E/N); the
# south glue alone decides which rule each variant encodes.
P_ANCHOR = {"W": "go2", "S": "ra-t-done", "E": "rp-t", "N": "rp-t-done"}
P_CYCLE_CUT = {"W": "go2", "S": "q-true",     "E": "rp-t", "N": "rp-t-done"}
P_CYCLE_WIRED = {"W": "go2", "S": "rq-t-done", "E": "rp-t", "N": "rp-t-done"}
P_FALSE = {"W": "go2", "S": "u-p", "E": "rp-f", "N": "rp-f-done"}
L_P = {"W": "rp-t", "S": "base2", "N": "base3"}

Q_WIRED = {"W": "go3", "S": "rp-t-done", "E": "rq-t", "N": "rq-t-done"}
Q_CUT = {"W": "go3", "S": "u-cut",       "E": "rq-t", "N": "rq-t-done"}
Q_FALSE = {"W": "go3", "S": "u-q", "E": "rq-f", "N": "rq-f-done"}
L_Q = {"W": "rq-t", "S": "base3", "N": "cap3"}

CORRECT = {
    "name": "correct_stage_order",
    "rows": {1: "a", 2: "p", 3: "q"},
    "tiles": {
        **SPINE, **ROW_A,
        "D2TA": dict(P_ANCHOR), "D2TQ": dict(P_CYCLE_CUT),
        "D2F": dict(P_FALSE), "L2": dict(L_P),
        "D3T": dict(Q_WIRED), "D3F": dict(Q_FALSE), "L3": dict(L_Q),
    },
    "true_tiles": {1: "D1T", 2: "D2TA", 3: "D3T"},
    "expected_terminal_decode": "apq",
}

WRONG_CUT = {
    "name": "wrong_cut_edge",
    "rows": {1: "a", 2: "p", 3: "q"},
    "tiles": {
        **SPINE, **ROW_A,
        "D2TA": dict(P_ANCHOR), "D2TQ": dict(P_CYCLE_WIRED),
        "D2F": dict(P_FALSE), "L2": dict(L_P),
        "D3T": dict(Q_CUT), "D3F": dict(Q_FALSE), "L3": dict(L_Q),
    },
    "true_tiles": {1: "D1T", 2: "D2TA", 3: "D3T"},
    "expected_terminal_decode": "ap",
}

WRONG_ROWS = {
    "name": "wrong_row_order",
    "rows": {1: "a", 2: "q", 3: "p"},
    "tiles": {
        **SPINE, **ROW_A,
        # row 2 = q; its only rule q :- p has its body ABOVE the head:
        # name-typed south glue rp-t-done can never be adjacent.
        "D2T": {"W": "go2", "S": "rp-t-done", "E": "rq-t", "N": "rq-t-done"},
        "D2F": dict(Q_FALSE), "L2": dict(L_Q),
        # row 3 = p; the anchor p :- a reads ra-t-done BY NAME, but a's
        # row is not adjacent (q's row sits between) — the anchor dies.
        "D3TA": {"W": "go3", "S": "ra-t-done", "E": "rp-t", "N": "rp-t-done"},
        "D3TQ": dict(P_CYCLE_WIRED), "D3F": dict(P_FALSE), "L3": dict(L_P),
    },
    "true_tiles": {1: "D1T", 2: "D2T", 3: "D3TA"},
    "expected_terminal_decode": "a",
}

BUILDS = [CORRECT, WRONG_CUT, WRONG_ROWS]


def exposed_glue(build, assembly, site, d):
    nb = (site[0] + d[0], site[1] + d[1])
    if nb not in assembly:
        return None
    t = assembly[nb]
    tiles = build["tiles"]
    if t.startswith("seed"):
        return SEED_N[nb] if d == FACE_DIR["S"] else None
    back = (-d[0], -d[1])
    for face, g in tiles[t].items():
        if FACE_DIR[face] == back:
            return g
    return None


def glue_strength(g, exp):
    if (g, exp) in STRENGTH:
        return STRENGTH[(g, exp)]
    if (exp, g) in STRENGTH:
        return STRENGTH[(exp, g)]
    return 1 if g == exp else 0


def matched_strength(build, assembly, site, tile):
    b = 0
    for face, g in build["tiles"][tile].items():
        exp = exposed_glue(build, assembly, site, FACE_DIR[face])
        if exp is not None:
            b += glue_strength(g, exp)
    return b


def has_neighbour(assembly, site):
    return any((site[0] + d[0], site[1] + d[1]) in assembly for d in DIRS)


def decode(build, assembly):
    """Atoms whose TRUE tile sits in their row's decision site; empty
    or false rows read false.  Row assignment is per-build."""
    out = ""
    for row, atom in sorted(build["rows"].items()):
        if assembly.get((1, row)) in true_variants(build, row):
            out += atom
    return out if out else "empty"


def _true_tile_in_row(build, row):
    atom = build["rows"][row]
    prefix = "D%d" % row
    cands = [n for n in build["tiles"]
             if n.startswith(prefix) and "F" not in n and n != "S%d" % row]
    # rows may carry several true variants (OR) — any of them decodes
    # the atom true (they share value outputs by construction).
    for c in cands:
        if build["tiles"][c].get("E") == "r%s-t" % atom:
            return c
    return None


def true_variants(build, row):
    prefix = "D%d" % row
    return sorted(n for n in build["tiles"]
                  if n.startswith(prefix) and "F" not in n
                  and build["tiles"][n].get("E") == "r%s-t" % build["rows"][row])


def locked_rows(build, assembly):
    n = 0
    for row in (1, 2, 3):
        if assembly.get((0, row)) == "S%d" % row and \
                assembly.get((2, row)) == "L%d" % row and \
                assembly.get((1, row)) is not None:
            n += 1
    return n
