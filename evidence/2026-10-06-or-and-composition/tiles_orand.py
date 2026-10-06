"""designs/003 honest-limit item 3 — the OR-AND composition builds,
machine-check arm (tick 20, SON-4763).

An atom with k rules where one body is conjunctive: does designs/002's
OR pair convention (k TRUE variants sharing value outputs) compose
with designs/003's sequential-gating AND?

Program family (positive, unique stable model = least model):
    P_OA      = `p.  q.  r :- p, q.  r :- p.`   stable {p,q,r}
    P_OA-q    = `p.       r :- p, q.  r :- p.`  stable {p,r}
    P_OA-p    = `q.       r :- p, q.  r :- p.`  stable {q}

r is the OR-AND atom: rule 1 body {p,q} (conjunctive), rule 2 body
{p} (unit).  Logically r <=> p, so:
  - deleting q's fact must NOT kill r (the unit rule rescues the
    dead AND slot — the discriminator against designs/003 build 2,
    where the same deletion terminates at {p});
  - deleting p's fact must kill r (both rules read p).

Geometry: 4 columns S | D | V | L, rows y=1..3 over a 4-wide seed,
inherited unchanged from designs/003.  Row r carries TWO variant
reader paths sharing the value outputs r-t / r-t-done and the lock
L3:
  conjunctive variant (rule r :- p,q):
    DAr  (col 1)  W=go3, S=q-t-done, E=and1_r   — slot A reads the
             highest-row body literal q directly;
    DBr  (col 2)  W=and1_r, S=p-t-done, E=r-t   — slot B reads the
             via-carried witness p.  designs/003 build 1 unchanged.
  unit variant (rule r :- p):
    Cr   (col 1)  W=go3, S=<row-below predicted-value done>,
             E=unit1_r  — a CONDUIT: relays the spine across slot A;
             its south read is the row-below predicted-value glue
             (chain discipline, as D3F in designs/003 build 2), NOT a
             semantic read of q;
    Ur   (col 2)  W=unit1_r, S=p-t-done, E=r-t, N=r-t-done — the
             semantic read of p happens here, at the V column, one
             slot later than the unit-reader of designs/002 (there
             the single body literal was the directly-below row; here
             p is two rows down, so its witness only surfaces at the
             via's north face).

Hybrid exclusion is by glue identity: and1_r != unit1_r, so DAr+Ur
and Cr+DBr mispair at strength 1 and never attach at tau=2.

Builds:
  BUILD1   P_OA, rows p<q<r, all predicted true.  Both variant paths
           live; terminals: one per variant, SAME decode {p,q,r}.
  BUILD2   P_OA-q, rows p<q<r; q false, r true.  The conjunctive
           variant is emitted but value-dead (q-t-done never exposed);
           the unit variant's conduit is typed S=q-f-done (row-below
           predicted-value).  Terminal {p,r} = the OR RESCUE.
  BUILD3   P_OA-p, rows q<p<r; q true, p and r false.  Both r-rules
           dead (no p-t anywhere).  Terminal {q}.
  BUILD4   W2 wrong compile of P_OA-q: the miscompiling solver's
           model is {p} (r wrongly false), so it drops BOTH reader
           variants and emits r's false chain.  Terminal {p} != the
           real stable model {p,r}: the BFS-vs-clingo certificate
           fires; the static d3 closure check fires independently
           (r :- p has p in the solver's own model).
  cut_p_fact(BUILD1)  seed-surgery arm for the over-collapse note.
"""
FACE_DIR = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
TAU = 2
STRENGTH = {("SP1", "SP1"): 2, ("SP2", "SP2"): 2, ("SP3", "SP3"): 2}

SITES = [(x, y) for y in (1, 2, 3) for x in (0, 1, 2, 3)]

SPINE = {
    "S1": {"S": "SP1", "E": "go1", "N": "SP2"},
    "S2": {"S": "SP2", "E": "go2", "N": "SP3"},
    "S3": {"S": "SP3", "E": "go3", "N": "SP4"},
}

ROW_P_TILES = {  # fact p, predicted TRUE (builds 1, 2, 4)
    "D1T": {"W": "go1", "S": "f-p", "E": "p-t", "N": "p-t-done"},
    "V0p": {"W": "p-t", "E": "p-t", "S": "vb1", "N": "p-t-done"},
    "L1":  {"W": "p-t", "S": "base1", "N": "base2"},
}
ROW_Q_TILES = {  # fact q, predicted TRUE (build 3)
    "D1Tq": {"W": "go1", "S": "f-q", "E": "q-t", "N": "q-t-done"},
    "V0q":  {"W": "q-t", "E": "q-t", "S": "vb1", "N": "q-t-done"},
    "L1q":  {"W": "q-t", "S": "base1", "N": "base2"},
}

SEED_P = {(0, 0): "SP1", (1, 0): "f-p", (2, 0): "vb1", (3, 0): "base1"}
SEED_Q = {(0, 0): "SP1", (1, 0): "f-q", (2, 0): "vb1", (3, 0): "base1"}


def glue_strength(g1, g2):
    if not g1 or not g2:
        return 0
    if (g1, g2) in STRENGTH:
        return STRENGTH[(g1, g2)]
    return 1 if g1 == g2 else 0


# ---- BUILD 1: P_OA, rows p<q<r, all true ---------------------------
BUILD1 = {
    "name": "P_OA_correct",
    "rows": {1: "p", 2: "q", 3: "r"},
    "row_of": {"S1": 1, "D1T": 1, "V0p": 1, "L1": 1,
               "S2": 2, "D2T": 2, "Vp": 2, "L2": 2,
               "S3": 3, "DAr": 3, "DBr": 3, "Cr": 3, "Ur": 3, "L3": 3},
    "seed": dict(SEED_P),
    "tiles": {
        **SPINE, **ROW_P_TILES,
        "D2T": {"W": "go2", "S": "p-t-done", "E": "q-t", "N": "q-t-done"},
        "Vp":  {"W": "q-t", "E": "q-t", "S": "p-t-done", "N": "p-t-done"},
        "L2":  {"W": "q-t", "S": "base2", "N": "base3"},
        # conjunctive variant (designs/003 build 1, unchanged)
        "DAr": {"W": "go3", "S": "q-t-done", "E": "and1_r", "N": "and1_r-done"},
        "DBr": {"W": "and1_r", "S": "p-t-done", "E": "r-t", "N": "r-t-done"},
        # unit variant: conduit + reader, sharing L3 and r-t(-done)
        "Cr":  {"W": "go3", "S": "q-t-done", "E": "unit1_r", "N": "unit1_r-done"},
        "Ur":  {"W": "unit1_r", "S": "p-t-done", "E": "r-t", "N": "r-t-done"},
        "L3":  {"W": "r-t", "S": "base3", "N": "cap3"},
    },
}

# ---- BUILD 2: P_OA-q, rows p<q<r; q false, r TRUE (OR rescue) ------
BUILD2 = {
    "name": "P_OA_minus_q",
    "rows": {1: "p", 2: "q", 3: "r"},
    "row_of": {"S1": 1, "D1T": 1, "V0p": 1, "L1": 1,
               "S2": 2, "D2F": 2, "Vp": 2, "L2": 2,
               "S3": 3, "DAr": 3, "DBr": 3, "Cr2": 3, "Ur": 3, "L3": 3},
    "seed": dict(SEED_P),
    "tiles": {
        **SPINE, **ROW_P_TILES,
        "D2F": {"W": "go2", "S": "p-t-done", "E": "q-f", "N": "q-f-done"},
        "Vp":  {"W": "q-f", "E": "q-f", "S": "p-t-done", "N": "p-t-done"},
        "L2":  {"W": "q-f", "S": "base2", "N": "base3"},
        # conjunctive variant: emitted (rule-local emission) but
        # value-dead — q-t-done is never exposed by a false q.
        "DAr": {"W": "go3", "S": "q-t-done", "E": "and1_r", "N": "and1_r-done"},
        "DBr": {"W": "and1_r", "S": "p-t-done", "E": "r-t", "N": "r-t-done"},
        # unit variant: conduit typed by the row-below PREDICTED value
        "Cr2": {"W": "go3", "S": "q-f-done", "E": "unit1_r", "N": "unit1_r-done"},
        "Ur":  {"W": "unit1_r", "S": "p-t-done", "E": "r-t", "N": "r-t-done"},
        "L3":  {"W": "r-t", "S": "base3", "N": "cap3"},
    },
}

# ---- BUILD 3: P_OA-p, rows q<p<r; q true, p and r false ------------
BUILD3 = {
    "name": "P_OA_minus_p",
    "rows": {1: "q", 2: "p", 3: "r"},
    "row_of": {"S1": 1, "D1Tq": 1, "V0q": 1, "L1q": 1,
               "S2": 2, "D2Fp": 2, "Vq": 2, "L2p": 2,
               "S3": 3, "D3Fr": 3, "Fr": 3, "L3r": 3},
    "seed": dict(SEED_Q),
    "tiles": {
        **SPINE, **ROW_Q_TILES,
        "D2Fp": {"W": "go2", "S": "q-t-done", "E": "p-f", "N": "p-f-done"},
        "Vq":   {"W": "p-f", "E": "p-f", "S": "q-t-done", "N": "q-t-done"},
        "L2p":  {"W": "p-f", "S": "base2", "N": "base3"},
        "D3Fr": {"W": "go3", "S": "p-f-done", "E": "r-f", "N": "r-f-done"},
        "Fr":   {"W": "r-f", "E": "r-f", "S": "q-t-done", "N": "rf-relay"},
        "L3r":  {"W": "r-f", "S": "base3", "N": "cap3"},
    },
}

# ---- BUILD 4: W2 wrong compile of P_OA-q (solver model {p}) --------
BUILD4 = {
    "name": "W2_dropped_unit_rule",
    "rows": {1: "p", 2: "q", 3: "r"},
    "row_of": {"S1": 1, "D1T": 1, "V0p": 1, "L1": 1,
               "S2": 2, "D2F": 2, "Vp": 2, "L2": 2,
               "S3": 3, "D3F": 3, "Fr": 3, "L3f": 3},
    "seed": dict(SEED_P),
    "tiles": {
        **SPINE, **ROW_P_TILES,
        "D2F": {"W": "go2", "S": "p-t-done", "E": "q-f", "N": "q-f-done"},
        "Vp":  {"W": "q-f", "E": "q-f", "S": "p-t-done", "N": "p-t-done"},
        "L2":  {"W": "q-f", "S": "base2", "N": "base3"},
        # r predicted FALSE by the miscompiling solver: both reader
        # variants dropped, false chain emitted instead.
        "D3F": {"W": "go3", "S": "q-f-done", "E": "r-f", "N": "r-f-done"},
        "Fr":  {"W": "r-f", "E": "r-f", "S": "p-t-done", "N": "rf-relay"},
        "L3f": {"W": "r-f", "S": "base3", "N": "cap3"},
    },
}


def cut_p_fact(build):
    """Replace p's seed fact glue with an inert unique name."""
    out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in build.items()}
    out["name"] = build["name"] + "+cut_p_fact"
    out["seed"] = dict(build["seed"])
    out["seed"][(1, 0)] = "u-cutp"
    return out


BUILDS = {
    "build1": BUILD1,
    "build2": BUILD2,
    "build3": BUILD3,
    "build4": BUILD4,
    "build1_cutp": cut_p_fact(BUILD1),
}

PROGRAMS = {
    "P_OA": "p. q. r :- p, q. r :- p.",
    "P_OA_minus_q": "p. r :- p, q. r :- p.",
    "P_OA_minus_p": "q. r :- p, q. r :- p.",
}

# Rule structure for the static closure/support check (d3).  Facts
# carry empty bodies; only r has rules.
FACTS = ["p", "q"]
RULES = {"r": [["p", "q"], ["p"]]}

# Predicted-true sets as compiled into each build (locks typed -t).
PREDICTED = {
    "build1": {"p", "q", "r"},
    "build2": {"p", "r"},
    "build3": {"q"},
    "build4": {"p"},
    "build1_cutp": {"p", "q", "r"},  # seed surgery, not a re-compile
}
