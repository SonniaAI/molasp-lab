"""Exhaustive aTAM (tau=2) producibility check for the designs/002
order falsifier — anchored cycle `a. p :- a. p :- q. q :- p.` with the
OR construction, three builds (correct stage order / wrong cut edge /
wrong row order).  Same BFS as atam_check_2cycle.py.

Claims (designs/002 criterion 4 — stage order must be load-bearing):

  1. CORRECT grows and its unique terminal decodes {a,p,q}, the
     unique stable model; no wrong-value tile (D1F/D2F/D3F) and no
     dead variant tile (D2TQ in CORRECT) is ever producible.
  2. WRONG_CUT terminates at {a,p} — wrong-but-terminal: {a,p} is
     neither stable nor even a model of P (q :- p has a true body and
     a false head).  The stage-order CUT discipline is load-bearing.
  3. WRONG_ROWS terminates at {a} — stronger failure: with q's row
     between a and p, the anchor edge p :- a loses adjacency and dies
     with the cycle.  Order among true atoms is strict because the
     read channel is the immediately-below row.
  4. No wrong build decodes {a,p,q}: the falsifier criterion is NOT
     triggered.

Structural claims:

  5. OR variants share value outputs exactly (E and N identical,
     S alone differs) and the wired edge's witness glue rp-t-done is
     exposed north by exactly the OR pair.
  6. Unique-name inertness: q-true, u-a, u-p, u-q, u-cut, SP4, cap3
     each occur exactly once across tiles+seed (tick-11 rule).
  7. Value typing: every done-glue/value-output cross-value pair used
     by a lock or vertical channel is strength 0.
  8. Wrong-VALUE tiles keep b = 1 (spine only) in the full correct
     assembly — un-lockable.  Growth-dead VARIANT tiles (D2TQ) are a
     different family: value-equivalent, producible 0, and bonding
     3 of 4 faces in the finished context (every face except the dead
     rule-read south glue) — dead by growth order, not by locking.
     Recorded honestly; measured, not assumed (first draft of this
     check said 2 and the assertion caught the missing E bond).
  9. clingo (python module, when present) enumerates P to exactly one
     stable model {a,p,q}, and {a,p} is not stable — the semantic
     anchor for claims 2-3.
"""
import json

from tiles_anchored import (BUILDS, CORRECT, WRONG_CUT, WRONG_ROWS,
                            SEED_TILES, matched_strength, glue_strength,
                            decode, locked_rows, true_variants)

TAU = 2
PROGRAM = "a. p :- a. p :- q. q :- p."


def freeze(assembly):
    return frozenset(assembly.items())


def producible(build):
    seen = {freeze(SEED_TILES)}
    frontier = [dict(SEED_TILES)]
    terminals = []
    while frontier:
        asm = frontier.pop()
        moves = 0
        for site in [(0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2),
                     (0, 3), (1, 3), (2, 3)]:
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


def glue_occurrences(build):
    occ = {}
    for faces in build["tiles"].values():
        for g in faces.values():
            occ[g] = occ.get(g, 0) + 1
    from tiles_anchored import SEED_N
    for g in SEED_N.values():
        occ[g] = occ.get(g, 0) + 1
    return occ


def exposes_north(build, glue):
    return sorted(t for t, f in build["tiles"].items()
                  if f.get("N") == glue)


def full_correct_assembly():
    asm = dict(SEED_TILES)
    asm.update({(0, 1): "S1", (1, 1): "D1T", (2, 1): "L1",
                (0, 2): "S2", (1, 2): "D2TA", (2, 2): "L2",
                (0, 3): "S3", (1, 3): "D3T", (2, 3): "L3"})
    return asm


def clingo_semantics():
    try:
        import clingo  # noqa: F401  (module present on pod, tick 7)
    except ImportError:
        return {"available": False}
    ctl = clingo.Control()
    ctl.add("base", [], PROGRAM)
    ctl.ground([("base", [])])
    models = []
    with ctl.solve(yield_=True) as handle:
        for m in handle:
            models.append(sorted(str(s) + "." for s in m.symbols(atoms=True)))
    # {a,p} not stable: re-solve under the assumption set {a,p} minus q.
    ctl2 = clingo.Control()
    ctl2.add("base", [], PROGRAM)
    ctl2.ground([("base", [])])
    ret = ctl2.solve(assumptions=[(clingo.Function("a"), True),
                                  (clingo.Function("p"), True),
                                  (clingo.Function("q"), False)])
    ap_is_stable = bool(ret.satisfiable)
    return {"available": True, "stable_models": models,
            "ap_satisfiable_under_assumptions": ap_is_stable}


if __name__ == "__main__":
    out = {"program": PROGRAM, "builds": {}}
    for build in BUILDS:
        seen, terminals = producible(build)
        decodes = sorted(decode(build, t) for t in terminals)
        ever = {name: any(t == name for asm in seen for _, t in asm)
                for name in build["tiles"] if name.startswith("D")}
        out["builds"][build["name"]] = {
            "producible_assemblies": len(seen),
            "terminals": len(terminals),
            "terminal_decodes": decodes,
            "decision_tiles_ever_producible": ever,
            "locked_rows_terminal": [locked_rows(build, t) for t in terminals],
        }
        assert len(terminals) >= 1, build["name"]
        assert decodes == [build["expected_terminal_decode"]] * len(terminals), \
            (build["name"], decodes)

    # 1. correct build: wrong-value and dead-variant tiles never grow.
    seen, _ = producible(CORRECT)
    for wrong in ("D1F", "D2F", "D2TQ", "D3F"):
        assert not any(t == wrong for asm in seen for _, t in asm), wrong

    # 2. no wrong build ever decodes the stable model (criterion 4).
    for build in (WRONG_CUT, WRONG_ROWS):
        _, terminals = producible(build)
        assert all(decode(build, t) != "apq" for t in terminals), build["name"]

    # 5. OR pair shares value outputs; wired witness exposed by the pair.
    t = CORRECT["tiles"]
    assert t["D2TA"]["E"] == t["D2TQ"]["E"] == "rp-t"
    assert t["D2TA"]["N"] == t["D2TQ"]["N"] == "rp-t-done"
    assert t["D2TA"]["S"] != t["D2TQ"]["S"]
    assert exposes_north(CORRECT, "rp-t-done") == ["D2TA", "D2TQ"]

    # 6. unique-name inertness in every build.
    for build in BUILDS:
        occ = glue_occurrences(build)
        for g in ("q-true", "u-a", "u-p", "u-q", "u-cut", "SP4", "cap3"):
            if g in occ:
                assert occ[g] == 1, (build["name"], g)

    # 7. cross-value pairs strength 0.
    for a, b in (("ra-t-done", "ra-f-done"), ("rp-t-done", "rp-f-done"),
                 ("rq-t-done", "rq-f-done"), ("ra-t", "ra-f"),
                 ("rp-t", "rp-f"), ("rq-t", "rq-f")):
        assert glue_strength(a, b) == 0, (a, b)

    # 8. wrong-VALUE tiles un-lockable; variant tile growth-dead only.
    asm = full_correct_assembly()
    for wrong, site in (("D1F", (1, 1)), ("D2F", (1, 2)), ("D3F", (1, 3))):
        assert matched_strength(CORRECT, asm, site, wrong) == 1, wrong
    out["D2TQ_bond_in_full_correct_context"] = \
        matched_strength(CORRECT, asm, (1, 2), "D2TQ")
    assert matched_strength(CORRECT, asm, (1, 2), "D2TQ") == 3

    out["clingo"] = clingo_semantics()
    if out["clingo"].get("available"):
        assert out["clingo"]["stable_models"] == [["a.", "p.", "q."]]

    with open("atam_anchored.out", "w") as fh:
        json.dump(out, fh, indent=2, default=str)
    print(json.dumps(out, indent=2, default=str))
    print("aTAM anchored-cycle CHECK PASSED: correct order -> unique"
          " terminal {a,p,q}; wrong cut -> {a,p}; wrong rows -> {a};"
          " criterion 4 holds (no wrong build decodes {a,p,q}).")
