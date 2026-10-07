"""OR-AND parity corpus for compiler v0.1 (tick 46).

The compiler pass (molasp/compiler.py) pins structural parity with
the three hand-built, BFS-machine-checked builds of the tick-20
composition (tests/test_compiler_v01.py P1-P3).  That proves the
emitter against three points.  This module generalizes the *veri-
fication* (not the parity argument) to a systematic corpus: every
program shape the v0.1 fragment admits, each compiled and checked
by exhaustive aTAM (tau=2) producibility on the full 4 x n grid.

The parity claim, per corpus program: the compiled tile system's
terminal assemblies decode exactly the program's least model —
the compute-only C-claim for this fragment — with every dead
variant's reader glues absent from every producible assembly.

Corpus axes (each program names which axis it spans):

  rows n          2 (PC1), 3 (PC2-PC4), 4 (PC5-PC8, first
                  exhaustive 4-row BFS in the programme)
  OR multiplicity 1 body (PC1, PC5), duplicate-AND pair (PC6),
                  AND+unit (PC2, PC8), unit+unit+AND three-way
                  terminal contention (PC7)
  dead variants   dead AND over a false atom (PC3), both rules
                  dead / false terminal row (PC4)
  middle facts    none (PC1-PC4), two (PC5-PC8)

Refusal corpus (PR1-PR6): every shape outside the fragment that the
pass must refuse loudly, with the registered failure flavor.

Machinery is inherited unchanged from
evidence/2026-10-06-or-and-composition/atam_check_orand.py (BFS,
decode, seed-row handling); only the site grid generalizes from
y in 1..3 to y in 1..n.  Glue semantics (STRENGTH pairs = 2,
equal names = 1, else 0) copied from tiles_orand so this module
depends on nothing outside molasp/.
"""
from __future__ import annotations

import time

from .compiler import (  # noqa: F401 (re-exported for test pins)
    CompileError,
    UnsupportedGeometry,
    compile_program,
    least_model,
    parse_program,
)

TAU = 2
FACE_DIR = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
STRENGTH = {("SP1", "SP1"): 2, ("SP2", "SP2"): 2, ("SP3", "SP3"): 2,
            ("SP4", "SP4"): 2}


def glue_strength(g1, g2):
    if not g1 or not g2:
        return 0
    if (g1, g2) in STRENGTH:
        return STRENGTH[(g1, g2)]
    return 1 if g1 == g2 else 0


# ---- corpus ------------------------------------------------------------

# name -> (program text, expected least model, axis note)
CORPUS = {
    "PC1": ("p. r :- p.", {"p", "r"},
            "n=2, unit-only OR: the smallest admissible shape"),
    "PC2": ("p. q. r :- p, q. r :- p.", {"p", "q", "r"},
            "n=3, AND+unit (the tick-20 BUILD1 program, re-verified "
            "through the corpus path)"),
    "PC3": ("p. r :- p, q. r :- p.", {"p", "r"},
            "n=3, dead AND variant over predicted-false q (BUILD2 "
            "program): OR rescue + dead-reader absence"),
    "PC4": ("q. r :- p, q. r :- p.", {"q"},
            "n=3, both rules dead, false terminal row (BUILD3 "
            "program): full foundedness demolition"),
    "PC5": ("p. q. s. r :- p, s.", {"p", "q", "s", "r"},
            "n=4, AND over (row-3 fact, row-1 via) with two middle "
            "facts: first exhaustive 4-row BFS"),
    "PC6": ("p. q. s. r :- p, s. r :- p, s.", {"p", "q", "s", "r"},
            "n=4, duplicate-AND OR pair (and1_r/and2_r count-2 "
            "fingerprint on the conjunctive class)"),
    "PC7": ("p. q. s. r :- p. r :- p. r :- p, s.", {"p", "q", "s", "r"},
            "n=4, three-way terminal-row contention: two unit readers "
            "+ one AND pair compete for the V-column slot"),
    "PC8": ("p. q. s. r :- p, s. r :- p.", {"p", "q", "s", "r"},
            "n=4, AND+unit at four rows: does the BUILD1 shape "
            "generalize past n=3"),
    "PC9": ("p. q :- p. r :- q.", {"p", "q", "r"},
            "n=3, live two-link unit chain (designs/008 PC9, v0.2 "
            "stage 1): first intermediate derived row — G1/G2 "
            "relaxed, the chain truth relayed up the V column"),
}

# name -> (program text, expected exception class name, message
# fragment, optional predicted override) — every out-of-fragment
# shape refuses loudly, no guessing.  PR6 needs the override: d3
# support fires on the caller's wrong-compile prediction, not on
# the (correctly smaller) least model.
REFUSALS = {
    "PR1": ("p. q. s. r :- p, q.", "UnsupportedGeometry",
            "conjunctive variant", None,
            "AND hi at non-adjacent row 2"),
    "PR2": ("p. q.", "UnsupportedGeometry",
            "terminal", None,
            "fact-true at the terminal row"),
    "PR3": ("p. q :- p. s. r :- q.", "UnsupportedGeometry",
            "non-adjacent", None,
            "chain literal two+ rows below its reader (the v0.2 "
            "stage-1 split of the old rule-atom-below-terminal "
            "refusal, which is now legal chain geometry)"),
    "PR4": ("p. q. r :- q.", "UnsupportedGeometry",
            "via-carried", None,
            "unit literal not at row 1 (adjacent-below FACT readers "
            "stay a designs/002 geometry)"),
    "PR5": ("p. q. s. r :- p, q, s.", "UnsupportedGeometry",
            "slot widening", None,
            "body width 3"),
    "PR6": ("p. r :- p, q.", "CompileError",
            "d3 support", {"p", "r"},
            "underivable predicted-true atom (wrong-compile arm)"),
    "PR7": ("p. z. q :- p. q :- p. r :- q.", "UnsupportedGeometry",
            "truth-OR relay", None,
            "OR at an intermediate derived row (v0.2 stage 1 admits "
            "single-body chains only)"),
    "PR8": ("p. q :- p. r :- q. s :- r.", "UnsupportedGeometry",
            "chain depth", None,
            "second intermediate derived row (designs/008 §6 "
            "boundary: chain length 2 only)"),
    "PR9": ("p. q. s. q2 :- p. r :- q2, s. r :- q2.",
            "UnsupportedGeometry", "row-1 via", None,
            "designs/008 PC11: AND lo-literal at row 3, not the "
            "row-1 via (still refused in v0.2 stage 1)"),
    "PR10": ("p. s. q2 :- p. r :- q2, p.", "UnsupportedGeometry",
             "derived row", None,
             "AND conduit over an adjacent-below DERIVED row would "
             "read its variant glue, not a truth-typed value"),
}


# ---- BFS machinery (generalized from atam_check_orand) -----------------

def sites_for(build):
    n = len(build["rows"])
    return [(x, y) for y in range(1, n + 1) for x in range(4)]


def _freeze(assembly):
    return frozenset(assembly.items())


def seed_assembly(build):
    return {(x, 0): "seed" + str(x) for x in range(4)
            if (x, 0) in build["seed"]}


def _matched_strength(build, asm, site, tile_name):
    faces = build["tiles"][tile_name]
    total = 0
    for face, (dx, dy) in FACE_DIR.items():
        g1 = faces.get(face)
        if not g1:
            continue
        nx, ny = site[0] + dx, site[1] + dy
        if ny == 0 and (nx, 0) in build["seed"]:
            g2 = build["seed"][(nx, 0)]
        elif (nx, ny) in asm:
            g2 = build["tiles"][asm[(nx, ny)]].get(OPPOSITE[face])
        else:
            continue
        total += glue_strength(g1, g2)
    return total


def producible(build):
    """Exhaustive tau=2 BFS from the seed; returns (seen, terminals)."""
    seen = {_freeze(seed_assembly(build))}
    frontier = [seed_assembly(build)]
    terminals = []
    while frontier:
        asm = frontier.pop()
        moves = 0
        for site in sites_for(build):
            if site in asm:
                continue
            if not any((site[0] + dx, site[1] + dy) in asm
                       for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))):
                continue
            for tile in build["tiles"]:
                if _matched_strength(build, asm, site, tile) >= TAU:
                    moves += 1
                    nxt = dict(asm)
                    nxt[site] = tile
                    key = _freeze(nxt)
                    if key not in seen:
                        seen.add(key)
                        frontier.append(nxt)
        if moves == 0:
            terminals.append(asm)
    return seen, terminals


def decode(build, asm):
    """Lock-column decode: (true-atom set, locked-row count)."""
    true_atoms, locked = set(), 0
    for y, atom in build["rows"].items():
        lock = asm.get((3, y))
        if lock is not None:
            locked += 1
            if build["tiles"][lock]["W"].endswith("-t"):
                true_atoms.add(atom)
    return true_atoms, locked


def dead_variant_glues(build):
    """vj channel glues of variants whose body is not satisfied by
    the predicted model (the dead paths that must never realize).
    designs/008 stage 2: every derived row reports, not just the
    terminal head — an intermediate false head's dead link is now
    emitted machinery (the UD reader tile reads exactly this vj
    glue on its W face), so its absence is checked, not assumed."""
    facts, rules, _order = parse_program(build["program"])
    predicted = set(build["predicted"])
    dead = set()
    for _row, head in sorted(build["rows"].items()):
        if head not in rules:
            continue
        and_no = unit_no = 0
        for body in rules[head]:
            if len(body) >= 2:
                and_no += 1
                vj = f"and{and_no}_{head}"
            else:
                unit_no += 1
                vj = f"unit{unit_no}_{head}"
            if not set(body) <= predicted:
                dead.add(vj)
    return dead


def assembly_exposes(build, seen, glue):
    for asm in seen:
        for _pos, name in asm:
            if name.startswith("seed"):
                continue
            if glue in build["tiles"][name].values():
                return True
    return False


# ---- report ------------------------------------------------------------

def check_program(name, program, expected_model):
    """Compile + BFS-verify one corpus program.  Returns a verdict
    dict; `ok` is the conjunction of every registered pin."""
    t0 = time.perf_counter()
    build = compile_program(program, name=name)
    compile_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    seen, terminals = producible(build)
    bfs_s = time.perf_counter() - t0
    decodes = {frozenset(decode(build, a)[0]) for a in terminals}
    n = len(build["rows"])
    full_locks = all(decode(build, a)[1] == n for a in terminals)
    dead = dead_variant_glues(build)
    dead_absent = {g: not assembly_exposes(build, seen, g)
                   for g in sorted(dead)}
    ok = (build["predicted"] == set(expected_model)
          and len(decodes) == 1
          and next(iter(decodes)) == set(expected_model)
          and full_locks
          and all(dead_absent.values()))
    return {
        "name": name,
        "ok": ok,
        "predicted": sorted(build["predicted"]),
        "expected": sorted(expected_model),
        "n_rows": n,
        "tiles": len(build["tiles"]),
        "assemblies": len(seen),
        "terminals": len(terminals),
        "terminal_decodes": sorted(sorted(d) for d in decodes),
        "full_locks": full_locks,
        "dead_variant_glues": sorted(dead),
        "dead_glues_absent": dead_absent,
        "seconds_compile": round(compile_s, 3),
        "seconds_bfs": round(bfs_s, 3),
        "d4_severity": build.get("d4", {}).get("severity"),
    }


def check_refusal(name, program, exc_name, fragment, predicted=None):
    try:
        compile_program(program, name=name, predicted=predicted)
    except Exception as exc:  # noqa: BLE001 — the point of the test
        return {"name": name, "ok": type(exc).__name__ == exc_name
                and fragment in str(exc),
                "raised": type(exc).__name__, "message": str(exc)[:160]}
    return {"name": name, "ok": False, "raised": None,
            "message": "compiled without refusing"}


def corpus_report():
    results = [check_program(k, v[0], v[1]) for k, v in CORPUS.items()]
    refusals = [check_refusal(k, v[0], v[1], v[2], v[3])
                for k, v in REFUSALS.items()]
    return {"corpus": results, "refusals": refusals,
            "all_ok": all(r["ok"] for r in results + refusals)}
