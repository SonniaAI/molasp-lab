"""designs/003 body conjunction — the AND builds, machine-checked arm.

Program family (positive, unique stable model = least model):
    P_AND   = `p.  q.  r :- p, q.`      stable {p,q,r}
    P_AND-q = `p.  r :- p, q.`          stable {p}
    P_AND-p = `q.  r :- p, q.`          stable {q}

Geometry: 4 columns S | D | V | L (x=0..3), rows y=1..3 above a
4-wide seed (y=0).  Column V is one-role-per-row: source stub
(row p) / witness via (row q) / second decision slot D^B_r (row r).
All cooperative glues strength 1; spine SP1/SP2/SP3 strength 2
(designs/002 v2.0 row-typed-spine lesson — the design 003 text says
"all glues strength 1", but with a strength-1 spine NOTHING attaches
in row 1 at tau=2; the spine exemption is inherited from designs/001
and is recorded as erratum E0 in designs/003).

Two build-table errata found by this very machine check (the design
was derivation-only at tick 17) and corrected here:

  E1 (BUILD1): D2T.S was written `f-q` (the row-1 fact convention).
    Nothing below site (1,2) ever exposes f-q — D1T.N is p-t-done —
    so the as-written build stalls at decode {p} and FAILS its own
    F1 prediction.  Corrected: D2T.S = p-t-done.  A fact above row 1
    south-reads the row-below done glue (chain discipline), exactly
    as the design's own Build 2 false tiles already do (D2F.S =
    p-t-done).  Side finding, recorded in the log: with chain
    discipline, deleting p's fact kills q's fact tile too — fact
    deletion is NOT modular in this geometry, and the tile path
    cannot distinguish `q.` from `q :- p` when q's row sits directly
    above p's row (a compile-time-only distinction).

  E2 (BUILD3): F+.S was written `vb3` ("base south face, no witness
    read").  vb3 matches nothing below site (2,2) — V0q.N is
    q-t-done — so the as-written W1 wrong compile stalls at decode
    {q}, which IS the stable model: a wrong compile that escapes the
    certificate by stalling and masquerading as correct.  Corrected:
    F+.S = q-t-done (the conduit bonds the channel below it; the
    dropped-literal wrongness is unchanged — no tile in r's row
    reads p).  The corrected build realizes the pre-registered F3
    arm: terminal {q,r}, a non-model, certificate fires.

Builds defined:
  BUILD1       P_AND, rows p<q<r, all true (corrected D2T).
  BUILD1_RAW   P_AND exactly as the design table stands (S=f-q).
  BUILD2       P_AND-q, rows p<q<r (q,r false; falsity chains).
  BUILD3       P_AND-p W1 dropped-literal wrong compile, rows q<r<p
               (corrected F+).
  BUILD3_RAW   BUILD3 exactly as the design table stands (S=vb3).
  cut_p_fact() / cut_q_fact() return build variants for the F1
  re-runs (p's seed fact replaced by an inert glue; D2T removed).
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

# ---- shared row-p / row-q fragments -------------------------------
ROW_P_TILES = {  # fact p, predicted TRUE (unchanged across builds)
    "D1T":  {"W": "go1", "S": "f-p",  "E": "p-t", "N": "p-t-done"},
    "V0p":  {"W": "p-t", "E": "p-t",  "S": "vb1", "N": "p-t-done"},
    "L1":   {"W": "p-t", "S": "base1", "N": "base2"},
}
ROW_Q_TILES = {  # fact q, predicted TRUE (BUILD1/BUILD3)
    "D1Tq": {"W": "go1", "S": "f-q",  "E": "q-t", "N": "q-t-done"},
    "V0q":  {"W": "q-t", "E": "q-t",  "S": "vb1", "N": "q-t-done"},
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


# ---- BUILD 1: P_AND, rows p<q<r, all true --------------------------
BUILD1 = {
    "name": "P_AND_corrected",
    "rows": {1: "p", 2: "q", 3: "r"},
    "row_of": {"S1": 1, "D1T": 1, "V0p": 1, "L1": 1,
               "S2": 2, "D2T": 2, "Vp": 2, "L2": 2,
               "S3": 3, "DAr": 3, "DBr": 3, "L3": 3},
    "seed": dict(SEED_P),
    "tiles": {
        **SPINE, **ROW_P_TILES,
        # erratum E1: S = p-t-done (as written: f-q -> stalls at {p})
        "D2T":  {"W": "go2", "S": "p-t-done", "E": "q-t", "N": "q-t-done"},
        "Vp":   {"W": "q-t", "E": "q-t", "S": "p-t-done", "N": "p-t-done"},
        "L2":   {"W": "q-t", "S": "base2", "N": "base3"},
        "DAr":  {"W": "go3", "S": "q-t-done", "E": "and1_r", "N": "and1_r-done"},
        "DBr":  {"W": "and1_r", "S": "p-t-done", "E": "r-t", "N": "r-t-done"},
        "L3":   {"W": "r-t", "S": "base3", "N": "cap3"},
    },
}

BUILD1_RAW = {
    "name": "P_AND_as_written",
    "rows": {1: "p", 2: "q", 3: "r"},
    "row_of": dict(BUILD1["row_of"]),
    "seed": dict(SEED_P),
    "tiles": {
        **SPINE, **ROW_P_TILES,
        "D2T":  {"W": "go2", "S": "f-q", "E": "q-t", "N": "q-t-done"},
        "Vp":   {"W": "q-t", "E": "q-t", "S": "p-t-done", "N": "p-t-done"},
        "L2":   {"W": "q-t", "S": "base2", "N": "base3"},
        "DAr":  {"W": "go3", "S": "q-t-done", "E": "and1_r", "N": "and1_r-done"},
        "DBr":  {"W": "and1_r", "S": "p-t-done", "E": "r-t", "N": "r-t-done"},
        "L3":   {"W": "r-t", "S": "base3", "N": "cap3"},
    },
}


# ---- BUILD 2: P_AND-q, rows p<q<r, q and r false --------------------
BUILD2 = {
    "name": "P_AND_minus_q",
    "rows": {1: "p", 2: "q", 3: "r"},
    "row_of": {"S1": 1, "D1T": 1, "V0p": 1, "L1": 1,
               "S2": 2, "D2F": 2, "Vp": 2, "L2": 2,
               "S3": 3, "D3F": 3, "Fr": 3, "L3": 3},
    "seed": dict(SEED_P),
    "tiles": {
        **SPINE, **ROW_P_TILES,
        "D2F":  {"W": "go2", "S": "p-t-done", "E": "q-f", "N": "q-f-done"},
        "Vp":   {"W": "q-f", "E": "q-f", "S": "p-t-done", "N": "p-t-done"},
        "L2":   {"W": "q-f", "S": "base2", "N": "base3"},
        "D3F":  {"W": "go3", "S": "q-f-done", "E": "r-f", "N": "r-f-done"},
        "Fr":   {"W": "r-f", "E": "r-f", "S": "p-t-done", "N": "rf-relay"},
        "L3":   {"W": "r-f", "S": "base3", "N": "cap3"},
    },
}

# ---- BUILD 3: W1 dropped-literal wrong compile of P_AND-p -----------
# rows q<r<p; solver wrongly predicts r TRUE and drops literal p.
BUILD3 = {
    "name": "W1_dropped_literal_corrected",
    "rows": {1: "q", 2: "r", 3: "p"},
    "row_of": {"S1": 1, "D1Tq": 1, "V0q": 1, "L1q": 1,
               "S2": 2, "DAr": 2, "Fplus": 2, "L2": 2,
               "S3": 3, "D3Fp": 3, "Fp": 3, "L3": 3},
    "seed": dict(SEED_Q),
    "tiles": {
        **SPINE, **ROW_Q_TILES,
        "DAr":  {"W": "go2", "S": "q-t-done", "E": "r-t", "N": "r-t-done"},
        # erratum E2: S = q-t-done (as written: vb3 -> stalls, and the
        # stall masquerades as the correct decode {q})
        "Fplus": {"W": "r-t", "E": "r-t", "S": "q-t-done", "N": "w1-relay"},
        "L2":   {"W": "r-t", "S": "base2", "N": "base3"},
        "D3Fp": {"W": "go3", "S": "r-t-done", "E": "p-f", "N": "p-f-done"},
        "Fp":   {"W": "p-f", "E": "p-f", "S": "w1-relay", "N": "pf-cap"},
        "L3":   {"W": "p-f", "S": "base3", "N": "cap3"},
    },
}

BUILD3_RAW = {
    "name": "W1_dropped_literal_as_written",
    "rows": {1: "q", 2: "r", 3: "p"},
    "row_of": dict(BUILD3["row_of"]),
    "seed": dict(SEED_Q),
    "tiles": {
        **SPINE, **ROW_Q_TILES,
        "DAr":  {"W": "go2", "S": "q-t-done", "E": "r-t", "N": "r-t-done"},
        "Fplus": {"W": "r-t", "E": "r-t", "S": "vb3", "N": "w1-relay"},
        "L2":   {"W": "r-t", "S": "base2", "N": "base3"},
        "D3Fp": {"W": "go3", "S": "r-t-done", "E": "p-f", "N": "p-f-done"},
        "Fp":   {"W": "p-f", "E": "p-f", "S": "w1-relay", "N": "pf-cap"},
        "L3":   {"W": "p-f", "S": "base3", "N": "cap3"},
    },
}


# ---- F1 re-run variants --------------------------------------------
def cut_p_fact(build):
    """Replace p's seed fact glue with an inert unique name."""
    out = {k: (dict(v) if k == "tiles" else dict(v) if k == "seed" else v)
           for k, v in build.items()}
    out["name"] = build["name"] + "+cut_p_fact"
    out["seed"] = dict(build["seed"])
    out["seed"][(1, 0)] = "u-cutp"
    return out


def cut_q_fact(build):
    """Remove q's fact tile from the inventory (its facticity lives in
    D2T for BUILD1; there is no seed slot for a row-2 fact)."""
    out = dict(build)
    out["name"] = build["name"] + "+cut_q_fact"
    out["tiles"] = {k: v for k, v in build["tiles"].items() if k != "D2T"}
    out["row_of"] = {k: v for k, v in build["row_of"].items() if k != "D2T"}
    return out


BUILDS = {
    "build1": BUILD1, "build1_raw": BUILD1_RAW,
    "build2": BUILD2,
    "build3": BUILD3, "build3_raw": BUILD3_RAW,
    "build1_cutp": cut_p_fact(BUILD1),
    "build1_cutq": cut_q_fact(BUILD1),
}

# Programs for the clingo semantic anchor.
PROGRAMS = {
    "P_AND": "p. q. r :- p, q.",
    "P_AND_minus_q": "p. r :- p, q.",
    "P_AND_minus_p": "q. r :- p, q.",
}
