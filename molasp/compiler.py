"""molasp compiler pass, v0.1 (tick 21).

Emits a 4-column (S|D|V|L) aTAM tile inventory for a ground positive
ASP program in the fragment covered by designs/001-003 and the tick-20
OR-AND composition:

  - facts `a.` and rules `h :- l1, ..., lb.` with b <= 2;
  - predicted-true set = the least model (computed here), or a caller
    override (a wrong-compile arm) which the d3 check must reject;
  - row order: topological (every body literal strictly below its
    head), tie-broken by first appearance in program text — the
    tick-14 order-falsifier discipline as an emit-time gate;
  - row 1 must be a TRUE fact (corpus invariant; deeper programs are
    mechanically emitted but their geometry is untested).

Emission policy (pinned tick 20, point 3): reader paths are
rule-local.  Dead variants are EMITTED with true-typed reads and
killed by value typing, never by omission.  Slot A (col 1) reads the
row-below atom's predicted-value done glue when that read is
non-semantic (conduits, false rows); semantic reads of the
adjacent-below literal happen at slot A (conjunctive variant), and
semantic reads of the via-carried row-1 witness at slot B (col 2).
The V column is a via: it relays the row-1 atom's value-done glue
northward unchanged (d1 discipline).

Emit-time checks (both fatal, both static):
  d2  dropped literals — the semantic reads of each emitted variant
      equal the rule's body set exactly;
  d3  compile-model closure/support — the predicted-true set is a
      supported model of the program (completeness: every rule live
      under the prediction has its head predicted; support: every
      predicted non-fact atom has a live rule).  This is the check
      that fired on the tick-20 wrong compile W2.
  d4  off-channel census (designs/004) — WARNING severity, attached
      to the emitted build as ``build["d4"]``: every (site, tile)
      misincorporation channel the inventory admits against the
      canonical assembly, lock-site hazards called out, measured
      kinetic context quoted.  Reports, never gates.

Output: a build dict in exactly the tiles_orand BUILDS shape
(name/rows/row_of/seed/tiles), so the existing aTAM BFS checkers
consume compiler output unchanged.  Structural parity with those
hand-built, machine-checked builds is pinned in
tests/test_compiler_v01.py; identical (seed, row_of, tiles) means
the identical assembly system, hence identical BFS verdicts.

Untested geometry raises UnsupportedGeometry rather than emitting a
guess: b >= 3 bodies, unit variants whose literal is not via-carried,
conjunctive variants whose literals are not (adjacent-below, row-1),
and programs needing > 1 derived row chain beyond the corpus shape
are refused loudly until a design pins them.
"""
from __future__ import annotations

from . import offchannel

FACE_DIR = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
TAU = 2
STRENGTH = {("SP1", "SP1"): 2, ("SP2", "SP2"): 2, ("SP3", "SP3"): 2}


class CompileError(Exception):
    """Fatal emit-time check failure (d2/d3) or bad input."""


class UnsupportedGeometry(CompileError):
    """Fragment/geometry the pass has no machine-checked design for."""


# ---------- parsing ------------------------------------------------------

def parse_program(text: str):
    """Parse `a.` facts and `h :- l1, l2.` rules (positive, ground).

    Returns (facts, rules, order) where rules maps head -> list of
    bodies (each a list of literals, source order) and order is the
    first-appearance order of atoms.
    """
    facts, rules, order = [], {}, []

    def see(atom):
        if atom not in order:
            order.append(atom)

    for stmt in text.replace("\n", " ").split("."):
        stmt = stmt.strip()
        if not stmt:
            continue
        if ":-" in stmt:
            head, body = stmt.split(":-", 1)
            head = head.strip()
            lits = [x.strip() for x in body.split(",") if x.strip()]
            if not head or not lits:
                raise CompileError(f"malformed rule: {stmt!r}")
            see(head)
            for lit in lits:
                see(lit)
            rules.setdefault(head, []).append(lits)
        else:
            head = stmt
            see(head)
            facts.append(head)
    return facts, rules, order


def least_model(facts, rules):
    """Least model by closure (the stable model of a positive program)."""
    model = set(facts)
    changed = True
    while changed:
        changed = False
        for head, bodies in rules.items():
            if head in model:
                continue
            if any(set(b) <= model for b in bodies):
                model.add(head)
                changed = True
    return model


def check_d3(predicted: set, facts, rules):
    """d3: predicted must be a supported model of the program."""
    predicted = set(predicted)
    fact_set = set(facts)
    if not fact_set <= predicted:
        raise CompileError(
            f"d3 completeness: facts {sorted(fact_set - predicted)} "
            "must be predicted true")
    for head, bodies in rules.items():
        live = any(set(b) <= predicted for b in bodies)
        if live and head not in predicted:
            raise CompileError(
                f"d3 completeness: rule for {head!r} is live under the "
                "predicted model but its head is predicted false")
    for atom in sorted(predicted - fact_set):
        if not any(set(b) <= predicted for b in rules.get(atom, [])):
            raise CompileError(
                f"d3 support: predicted-true {atom!r} has no live rule")


# ---------- row order ----------------------------------------------------

def row_order(facts, rules, order, predicted):
    """Topological order, body atoms strictly below heads, first-
    appearance tie-break.  Row 1 must be a predicted-true fact."""
    deps = {}
    for head, bodies in rules.items():
        deps.setdefault(head, set()).update(
            lit for b in bodies for lit in b)
    placed, rows = [], {}
    remaining = list(order)
    while remaining:
        ready = [a for a in remaining
                 if not (deps.get(a, set()) & set(remaining))]
        if not ready:
            raise CompileError(
                f"row order: dependency cycle among {remaining}; the "
                "tick-14 order falsifier applies — reorder or widen")
        # first-appearance tie-break: `remaining` keeps source order
        nxt = ready[0]
        remaining.remove(nxt)
        placed.append(nxt)
    for i, atom in enumerate(placed, start=1):
        rows[i] = atom
    if placed[0] not in set(facts) or placed[0] not in predicted:
        raise UnsupportedGeometry(
            f"row-1 atom {placed[0]!r} must be a predicted-true fact "
            "(corpus invariant; untested below-true geometry refused)")
    return rows


# ---------- emission -----------------------------------------------------

def compile_program(text: str, predicted=None, name=None):
    """Compile program text to a build dict (tiles_orand BUILDS shape)."""
    facts, rules, order = parse_program(text)
    predicted = least_model(facts, rules) if predicted is None else set(predicted)
    check_d3(predicted, facts, rules)          # d3 (fatal on wrong models)
    rows = row_order(facts, rules, order, predicted)
    n = len(rows)
    row_of_atom = {a: i for i, a in rows.items()}

    tiles, row_of = {}, {}
    a1 = rows[1]                               # row-1 atom (fact, true)
    via = f"{a1}-{'t' if a1 in predicted else 'f'}-done"   # V-column relay

    def emit(tname, faces, row):
        if tname in tiles:
            raise CompileError(f"tile name collision: {tname}")
        tiles[tname] = faces
        row_of[tname] = row

    # seed + row 1 (fact row)
    emit("S1", {"S": "SP1", "E": "go1", "N": "SP2"}, 1)
    emit("D1T", {"W": "go1", "S": f"f-{a1}", "E": f"{a1}-t",
                 "N": f"{a1}-t-done"}, 1)
    emit(f"V0{a1}", {"W": f"{a1}-t", "E": f"{a1}-t", "S": "vb1",
                     "N": f"{a1}-t-done"}, 1)
    emit("L1", {"W": f"{a1}-t", "S": "base1", "N": "base2"}, 1)
    seed = {(0, 0): "SP1", (1, 0): f"f-{a1}", (2, 0): "vb1", (3, 0): "base1"}

    # rows 2..n
    for i in range(2, n + 1):
        a = rows[i]
        below = rows[i - 1]
        below_done = f"{below}-{'t' if below in predicted else 'f'}-done"
        emit(f"S{i}", {"S": f"SP{i}", "E": f"go{i}", "N": f"SP{i + 1}"}, i)

        if a in predicted:
            bodies = rules.get(a, [])
            if i != n and bodies:
                raise UnsupportedGeometry(
                    f"rule atom {a!r} at non-terminal row {i}: variant "
                    "readers occupy the via column; multi-derived-row "
                    "chains are untested geometry")
            if not bodies:                     # fact true at row >= 2
                if i == n:
                    raise UnsupportedGeometry(
                        f"fact-true {a!r} at terminal row: no corpus "
                        "build pins a terminal V tile (refused)")
                emit(f"D{i}T", {"W": f"go{i}", "S": below_done,
                                "E": f"{a}-t", "N": f"{a}-t-done"}, i)
                emit(f"V{i}{a1}", {"W": f"{a}-t", "E": f"{a}-t", "S": via,
                                  "N": via}, i)
            else:
                and_no, unit_no = 0, 0
                for j, body in enumerate(bodies):
                    if len(body) >= 2:
                        and_no += 1
                        vj = f"and{and_no}_{a}"
                    else:
                        unit_no += 1
                        vj = f"unit{unit_no}_{a}"
                    reads = set()
                    if len(body) > 2:
                        raise UnsupportedGeometry(
                            f"body width {len(body)} for {a!r}: slot "
                            "widening untested (designs/003 honest limit)")
                    if len(body) == 2:
                        hi, lo = sorted(body, key=lambda x: -row_of_atom[x])
                        if row_of_atom[hi] != i - 1 or row_of_atom[lo] != 1:
                            raise UnsupportedGeometry(
                                f"conjunctive variant of {a!r}: literals "
                                f"must sit at (adjacent-below, row-1 via), "
                                f"got rows "
                                f"{(row_of_atom[hi], row_of_atom[lo])}")
                        emit(f"D{chr(65)}{a}" if and_no == 1 else
                             f"D{chr(65)}{a}{and_no}",
                             {"W": f"go{i}", "S": f"{hi}-t-done",
                              "E": vj, "N": f"{vj}-done"}, i)
                        emit(f"D{chr(66)}{a}" if and_no == 1 else
                             f"D{chr(66)}{a}{and_no}",
                             {"W": vj, "S": f"{lo}-t-done", "E": f"{a}-t",
                              "N": f"{a}-t-done"}, i)
                        reads = {hi, lo}
                    else:                        # unit variant (b == 1)
                        lit = body[0]
                        if row_of_atom[lit] != 1:
                            raise UnsupportedGeometry(
                                f"unit variant of {a!r}: literal {lit!r} "
                                "not via-carried (row-1); direct-below unit "
                                "readers are a designs/002 geometry, "
                                "unwired in v0.1")
                        cnames = (f"C{a}", f"U{a}") if unit_no == 1 else \
                                 (f"C{a}{unit_no}", f"U{a}{unit_no}")
                        emit(cnames[0],
                             {"W": f"go{i}", "S": below_done, "E": vj,
                              "N": f"{vj}-done"}, i)          # conduit
                        emit(cnames[1],
                             {"W": vj, "S": f"{lit}-t-done", "E": f"{a}-t",
                              "N": f"{a}-t-done"}, i)         # reader
                        reads = {lit}
                    if reads != set(body):      # d2: dropped literals
                        raise CompileError(
                            f"d2: variant {j} of {a!r} reads {sorted(reads)} "
                            f"but body is {sorted(set(body))}")
            lock_n = f"cap{n}" if i == n else f"base{i + 1}"
            emit(f"L{i}", {"W": f"{a}-t", "S": f"base{i}", "N": lock_n}, i)
        else:                                   # predicted false
            emit(f"D{i}F{a}", {"W": f"go{i}", "S": below_done,
                               "E": f"{a}-f", "N": f"{a}-f-done"}, i)
            lock_n = f"cap{n}" if i == n else f"base{i + 1}"
            if i == n:                          # terminal: inert cap
                emit(f"F{a}", {"W": f"{a}-f", "E": f"{a}-f", "S": via,
                               "N": "rf-relay"}, i)
                emit(f"L{i}f{a}", {"W": f"{a}-f", "S": f"base{i}",
                                  "N": lock_n}, i)
            else:                               # relay the via north
                emit(f"V{i}{a1}", {"W": f"{a}-f", "E": f"{a}-f", "S": via,
                                  "N": via}, i)
                emit(f"L{i}", {"W": f"{a}-f", "S": f"base{i}",
                               "N": lock_n}, i)

    build = {
        "name": name or "compiled",
        "rows": rows,
        "row_of": row_of,
        "seed": seed,
        "tiles": tiles,
        "predicted": predicted,
        "program": text,
    }
    # d4 off-channel census (designs/004): WARNING severity — a
    # squatter is a kinetic hazard, not a semantic error, so this
    # reports and never gates.  A d4 failure records itself instead
    # of blocking emission (A3: d2/d3 behaviour unchanged).
    try:
        build["d4"] = offchannel.check_d4(build)
    except Exception as exc:                      # noqa: BLE001
        build["d4"] = {"severity": "error",
                       "detail": f"d4 census failed: {exc}"}
    return build


def structural_signature(build):
    """Name-normalized view: assembly depends only on (rows, seed,
    per-row face-glue multisets), not on hand tile names."""
    per_row = {}
    for tname, row in build["row_of"].items():
        per_row.setdefault(row, []).append(
            tuple(sorted(build["tiles"][tname].items())))
    return (dict(build["rows"]), dict(build["seed"]),
            {r: sorted(v) for r, v in sorted(per_row.items())})
