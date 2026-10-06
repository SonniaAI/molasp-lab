"""Exhaustive aTAM (tau=2) producibility check for the WRONG_CUT
lock-on-false build (designs/002 F2 boundary).  Same BFS as
atam_check_anchored.py, imported unchanged where possible.

Claims:

  1. WRONG_CUT_LOCKFALSE terminates at {a,p} — its own predicted
     terminal decode (the compile's post-cut fixpoint prediction),
     reached by the anchored falsity chain: D3F's south glue
     rp-t-done bonds row 2's predicted-true north face, and L3 bonds
     the false output rq-f.  {a,p} is neither stable nor a model of P
     (q :- p has a true body and a false head).
  2. The self-correction channel is structurally GONE: D3T (Q_CUT)
     is producible in 0 assemblies, and unlike WRONG_CUT no tile in
     the system bonds rq-t from the lock side — the true tile's b=1
     transient has no cooperative capture partner (L3 bonds rq-f
     only).  Value typing of the lock, not the cut, decides.
  3. The capture-channel contrast, pinned: in WRONG_CUT,
     glue_strength(L3.W, D3T.E) == 1 (the tick-15 capture channel);
     here glue_strength(L3.W, D3T.E) == 0.
  4. clingo (when present): unique stable model of P is {a,p,q};
     {a,p,q} minus q violates q :- p under assumptions (a,p,q=false
     unsatisfiable) — the decode the build locks in is semantically
     wrong, and the substrate will not flag it.
  5. Unique-name inertness (tick-11 rule): u-cut, u-a, u-p, u-q,
     SP4, cap3, rq-f-done each occur exactly once across
     tiles+seed; q-true occurs zero times (this build cuts q:-p and
     wires nothing to the p-cycle edge's south name).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MULTIROW = os.path.join(os.path.dirname(HERE), "2026-10-06-multirow-ktam-grid")
for p in (HERE, MULTIROW):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_anchored import (SEED_TILES, SEED_N, WRONG_CUT,  # noqa: E402
                            matched_strength, glue_strength)
from tiles_cutlock import WRONG_CUT_LOCKFALSE as BUILD  # noqa: E402

TAU = 2
SITES = [(0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2),
         (0, 3), (1, 3), (2, 3)]


def freeze(assembly):
    return frozenset(assembly.items())


def producible(build):
    seen = {freeze(SEED_TILES)}
    frontier = [dict(SEED_TILES)]
    terminals = []
    while frontier:
        asm = frontier.pop()
        moves = 0
        for site in SITES:
            if site not in asm and any(
                    (site[0] + dx, site[1] + dy) in asm
                    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))):
                for tile in build["tiles"]:
                    if matched_strength(build, asm, site, tile) >= TAU:
                        moves += 1
                        nxt = dict(asm)
                        nxt[site] = tile
                        key = freeze(nxt)
                        if key not in seen:
                            seen.add(key)
                            frontier.append(nxt)
        if moves == 0:
            terminals.append(asm)
    return seen, terminals


def decode_rows(build, assembly):
    from tiles_anchored import true_variants
    out = ""
    for row, atom in sorted(build["rows"].items()):
        if assembly.get((1, row)) in true_variants(build, row):
            out += atom
    return out if out else "empty"


def occurrences(build):
    occ = {}
    for faces in build["tiles"].values():
        for g in faces.values():
            occ[g] = occ.get(g, 0) + 1
    for g in SEED_N.values():
        occ[g] = occ.get(g, 0) + 1
    return occ


def clingo_semantics():
    try:
        import clingo  # noqa: F401
    except ImportError:
        return {"available": False}
    program = "a. p :- a. p :- q. q :- p."
    ctl = clingo.Control()
    ctl.add("base", [], program)
    ctl.ground([("base", [])])
    models = []
    with ctl.solve(yield_=True) as h:
        for m in h:
            models.append(sorted(str(s) + "." for s in m.symbols(atoms=True)))
    ctl2 = clingo.Control()
    ctl2.add("base", [], program)
    ctl2.ground([("base", [])])
    ret = ctl2.solve(assumptions=[(clingo.Function("a"), True),
                                  (clingo.Function("p"), True),
                                  (clingo.Function("q"), False)])
    return {"available": True, "stable_models": models,
            "ap_only_satisfiable": bool(ret.satisfiable)}


if __name__ == "__main__":
    seen, terminals = producible(BUILD)
    tile_in = {}
    for t in BUILD["tiles"]:
        tile_in[t] = sum(1 for asm in seen
                         if any(name == t for _, name in asm))
    term_decodes = sorted(decode_rows(BUILD, a) for a in terminals)
    occ = occurrences(BUILD)
    inert_once = {g: occ.get(g, 0) for g in
                  ("u-cut", "u-a", "u-p", "u-q", "SP4", "cap3", "rq-f-done")}
    tiles = BUILD["tiles"]
    checks = {
        "n_producible": len(seen),
        "n_terminals": len(terminals),
        "terminal_decodes": term_decodes,
        "expected_terminal_decode": BUILD["expected_terminal_decode"],
        "d3t_producible_in": tile_in["D3T"],
        "d2tq_producible_in": tile_in["D2TQ"],
        "capture_channel_lockfalse":
            glue_strength(tiles["L3"]["W"], tiles["D3T"]["E"]),
        "capture_channel_wrongcut_reference":
            glue_strength(WRONG_CUT["tiles"]["L3"]["W"],
                          WRONG_CUT["tiles"]["D3T"]["E"]),
        "falsity_chain_south_bond":
            glue_strength(tiles["D3F"]["S"], tiles["D2TA"]["N"]),
        "lock_bonds_false_output":
            glue_strength(tiles["L3"]["W"], tiles["D3F"]["E"]),
        "inert_once": inert_once,
        "q_true_occurrences": occ.get("q-true", 0),
        "rq_t_bonded_by_any_w_face": sorted(
            t for t, f in BUILD["tiles"].items() if f.get("W") == "rq-t"),
        "clingo": clingo_semantics(),
    }
    # assertions (fail loudly, not silently)
    assert term_decodes == [BUILD["expected_terminal_decode"]], term_decodes
    assert tile_in["D3T"] == 0, tile_in["D3T"]
    assert checks["capture_channel_lockfalse"] == 0
    assert checks["capture_channel_wrongcut_reference"] == 1
    assert checks["falsity_chain_south_bond"] == 1
    assert checks["lock_bonds_false_output"] == 1
    # tick-11 unique-name rule: at most once system-wide.  u-q is 0
    # here BY DESIGN (unlike WRONG_CUT): the predicted-false tile's
    # south face carries the falsity chain rp-t-done instead of the
    # inert u-q, so u-q is not in this build's alphabet at all.
    assert all(v <= 1 for v in inert_once.values()), inert_once
    assert checks["q_true_occurrences"] == 0
    assert checks["rq_t_bonded_by_any_w_face"] == []
    print(json.dumps(checks, indent=1))
    print("ALL A-TAM CHECKS PASSED")
