"""kTAM Gillespie MC for designs/001: tile lowering of `a. p :- p.`.

Witness program (c2-witness, 2026-10-05):  fact a. ; rule p :- p.
Stable model: {a}.  Supported-but-unstable: {a,p}.

Tile system (tau=2 abstraction, strength-1 glues), 2 columns x 2 rows
above a 2-tile seed. Growth is northward; each row has a Decision site
(col 0, decides the atom's value) and a Lock site (col 1, cooperatively
locks the row via W+S bonds). Value tiles carry the same north glue
("row1done") so the prefix is carried by tile identity, not glue
identity -- no later rule reads a's value, which is exactly the point
of this witness.

Seed (y=0):   x0 N-glue "f-a"   (fact a present -> only D1T south-matches)
              x1 N-glue "base"

Tile types:
  D1T  S=f-a    N=row1done E=r1      (a true; producible)
  D1F  S=u-a    N=row1done E=r1      (a false; south mismatch => trap only)
  L1   S=base   W=r1       N=base2   (locks row 1)
  D2T  S=no-p   N=topT     E=r2      (p true; NO south match by construction:
                                      the self-loop p :- p cannot be wired,
                                      support must arrive from below)
  D2F  S=row1done N=topF   E=r2      (p false; south-matches row 1)
  L2   S=base2  W=r2       N=cap2    (locks row 2)

Prediction: decodes {a,p} (unfounded) appear only via kinetic traps at
the single-tile error floor, same scale as the {}/D1F trap (positive
control: a founded error with identical geometry). No amplification term
exists for the unfounded state -- every trap is transient.

kTAM model: attach rate per (site, tile) = k_f*exp(-Gmc) if the tile has
>=1 matching glue against current neighbours (mismatch-attachments with 0
matched strength detach at k_f and are neglected -- Xgrow "no mismatch"
approximation, noted in the design doc). Detach rate = k_f*exp(-b*Gse)
with b = summed matched glue strength. k_f = 1/s. Assembly decoded at
fixed read time T.
"""
import math, random, json
from collections import Counter

random.seed(20261005)

FACE_DIR = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
DIRS = list(FACE_DIR.values())

TILES = {
    "D1T": {"S": "f-a",      "N": "row1done", "E": "r1"},
    "D1F": {"S": "u-a",      "N": "row1done", "E": "r1"},
    "L1":  {"S": "base",     "W": "r1",       "N": "base2"},
    "D2T": {"S": "no-p",     "N": "topT",     "E": "r2"},
    "D2F": {"S": "row1done", "N": "topF",     "E": "r2"},
    "L2":  {"S": "base2",    "W": "r2",       "N": "cap2"},
}
SEED_N = {(0, 0): "f-a", (1, 0): "base"}   # glue on each seed tile's N face
SEED_TILES = {(0, 0): "seed0", (1, 0): "seed1"}
SITES = [(0, 1), (1, 1), (0, 2), (1, 2)]


def exposed_glue(assembly, site, d):
    """Glue exposed towards `site` by whatever tile sits at site+d, else None."""
    nb = (site[0] + d[0], site[1] + d[1])
    if nb not in assembly:
        return None
    t = assembly[nb]
    if t.startswith("seed"):
        return SEED_N[nb] if d == FACE_DIR["S"] else None
    back = (-d[0], -d[1])
    for face, g in TILES[t].items():
        if FACE_DIR[face] == back:   # neighbour's face pointing at `site`
            return g
    return None


def matched_strength(assembly, site, tile):
    b = 0
    for face, g in TILES[tile].items():
        d = FACE_DIR[face]
        if exposed_glue(assembly, site, d) == g:
            b += 1
    return b


def has_neighbour(assembly, site):
    return any((site[0] + d[0], site[1] + d[1]) in assembly for d in DIRS)


def run_assembly(Gmc, Gse, T_read):
    rf = math.exp(-Gmc)
    assembly = dict(SEED_TILES)
    t = 0.0
    while True:
        events = []
        for site in SITES:
            if site in assembly:
                b = matched_strength(assembly, site, assembly[site])
                events.append((math.exp(-b * Gse), "detach", site))
            elif has_neighbour(assembly, site):
                for tile in TILES:
                    if matched_strength(assembly, site, tile) >= 1:
                        events.append((rf, "attach", (site, tile)))
        total = sum(r for r, _, _ in events)
        if total <= 0 or t > T_read:
            break
        t += random.expovariate(total)
        if t > T_read:
            break
        r = random.random() * total
        acc = 0.0
        for rate, kind, arg in events:
            acc += rate
            if acc >= r:
                if kind == "attach":
                    assembly[arg[0]] = arg[1]
                else:
                    del assembly[arg]
                break
    a = {"D1T": True, "D1F": False}.get(assembly.get((0, 1)))
    p = {"D2T": True, "D2F": False}.get(assembly.get((0, 2)))
    l1 = assembly.get((1, 1)) == "L1"
    l2 = assembly.get((1, 2)) == "L2"
    if a is None or p is None:
        return "unreadable"
    if not (l1 and l2):
        return "unlocked"
    if a and p:
        return "ap"
    if a:
        return "a"
    if p:
        return "p"
    return "empty"


def sweep():
    rows = []
    # Sweep 1: Gse sweep at fixed DeltaG = ln 2 (tau=2 fast-growth boundary).
    for Gse in (7.0, 9.0, 11.0, 13.0):
        Gmc = Gse - math.log(2)
        T_read = 400.0 * math.exp(Gse)
        n = 500
        c = Counter(run_assembly(Gmc, Gse, T_read) for _ in range(n))
        row = {"sweep": "Gse@dG=ln2", "Gse": Gse, "Gmc": round(Gmc, 3), "n": n,
               "T_read_s": round(T_read, 1),
               "decode": {k: c.get(k, 0) for k in ("a", "ap", "p", "empty", "unreadable", "unlocked")}}
        rows.append(row)
        print(json.dumps(row), flush=True)
    # Sweep 2: DeltaG sweep at fixed Gse = 9 -- error floor vs speed setting.
    for dG in (math.log(2), 2.0, 4.0, 6.0):
        Gse, Gmc = 9.0, 9.0 - dG
        T_read = 400.0 * math.exp(Gse)
        n = 500
        c = Counter(run_assembly(Gmc, Gse, T_read) for _ in range(n))
        row = {"sweep": "dG@Gse=9", "Gse": Gse, "Gmc": round(Gmc, 3), "n": n,
               "T_read_s": round(T_read, 1),
               "decode": {k: c.get(k, 0) for k in ("a", "ap", "p", "empty", "unreadable", "unlocked")}}
        rows.append(row)
        print(json.dumps(row), flush=True)
    return rows


if __name__ == "__main__":
    sweep()
