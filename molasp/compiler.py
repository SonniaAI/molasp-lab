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
guess: b >= 3 bodies, unit variants whose literal is neither
via-carried (row-1) nor an adjacent-below derived row, conjunctive
variants whose literals are not (adjacent-below fact, row-1 via),
OR/AND bodies or a second derived row at a non-terminal row, and
non-adjacent chain reads are refused loudly until a design pins
them.  Legal unit-chain links (designs/008 stage 1: at most one
intermediate derived row, single unit body) are emitted: the
intermediate reader relays its atom's truth-typed t-done glue up the
V column (the chain link), and the D column carries each row's
value/variant done glue northward.
"""
from __future__ import annotations

import re

from . import offchannel

FACE_DIR = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
TAU = 2

# designs/010 §10.3 class closure rule (stage 7): the row-typed-spine
# exemption of designs/002 v2.0 is a CLASS property, not a finite
# enumeration — every same-name SPi<->SPi spine self-bond (i >= 1; the
# emitter mints SP{i} per row) carries strength 2, and every other
# matched pair keeps the cooperative fallback 1.  This is the ONE
# predicate; parity.py and offchannel.py consume it, and their
# divergent SP1-3 / SP1-4 enumerated tables are deleted (unification,
# designs/010 §10.4-1).  Strictly SP<digits> names (the emitter's own
# shape), so no non-spine glue can ride the closure silently.
_SPINE_GLUE_RE = re.compile(r"SP[1-9][0-9]*")


def glue_strength(g1, g2):
    """Bond strength of two opposing face glues: 0 when either is
    blank or the names differ; 2 for spine self-bonds (class closure,
    designs/010 §10.3); 1 for every other matched pair."""
    if not g1 or not g2:
        return 0
    if g1 == g2:
        return 2 if _SPINE_GLUE_RE.fullmatch(g1) else 1
    return 0


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

    # v0.2 stage 1 (designs/008): northward column glues.  The D
    # column exposes each row's value (fact rows) or variant-conduit
    # (derived rows) done glue; the V column relays the row-1 via
    # until an intermediate derived row replaces it with its own
    # truth-typed t-done glue — the chain link a reader above reads.
    d_north = {1: f"{a1}-{'t' if a1 in predicted else 'f'}-done"}
    v_north = {1: via}
    intermediate_rows = []

    # designs/009 §9.2 consumer-aware lookahead: when the row above
    # a predicted-true intermediate derived row reads that atom as
    # the hi literal of an AND body, the conduit's N face re-types
    # from the conduit glue (unit1_{a}-done) to the passthrough of
    # the row-below D-column value, and d_north carries that same
    # passthrough north.  Unit-consumer rows (PC9/PC10) never fire
    # this and keep the stage-1 layout byte-identically.
    passthrough_rows = set()
    for k in range(2, n):
        consumer = rows[k + 1]
        if consumer not in predicted:
            continue
        for body in rules.get(consumer, []):
            if len(body) == 2:
                b_hi, _b_lo = sorted(body,
                                     key=lambda x: -row_of_atom[x])
                if b_hi == rows[k]:
                    passthrough_rows.add(k)

    # rows 2..n
    for i in range(2, n + 1):
        a = rows[i]
        below = rows[i - 1]
        below_done = f"{below}-{'t' if below in predicted else 'f'}-done"
        below_d = d_north[i - 1]   # D-column glue the row below exposes
        below_v = v_north[i - 1]   # V-column glue (via or chain link)
        emit(f"S{i}", {"S": f"SP{i}", "E": f"go{i}", "N": f"SP{i + 1}"}, i)

        if a in predicted:
            bodies = rules.get(a, [])
            intermediate = bool(bodies) and i != n
            if intermediate:
                if len(bodies) > 1:
                    raise UnsupportedGeometry(
                        f"rule atom {a!r} at non-terminal row {i} with "
                        f"{len(bodies)} bodies: OR at an intermediate "
                        "derived row needs a northward truth-OR relay "
                        "(each variant conduit exposes its own glue); "
                        "untested (designs/008 stage 1 admits single-"
                        "body chains)")
                if any(len(b) >= 2 for b in bodies):
                    raise UnsupportedGeometry(
                        f"rule atom {a!r} at non-terminal row {i}: AND "
                        "at an intermediate derived row is untested "
                        "(designs/008 stage 1 admits unit-body chains "
                        "only)")
                if intermediate_rows:
                    raise UnsupportedGeometry(
                        f"chain depth > 2 at row {i}: a second "
                        "intermediate derived row is unexamined geometry "
                        "(designs/008 §6 boundary)")
            if not bodies:                     # fact true at row >= 2
                if i == n:
                    raise UnsupportedGeometry(
                        f"fact-true {a!r} at terminal row: no corpus "
                        "build pins a terminal V tile (refused)")
                emit(f"D{i}T", {"W": f"go{i}", "S": below_d,
                                "E": f"{a}-t", "N": f"{a}-t-done"}, i)
                emit(f"V{i}{a1}", {"W": f"{a}-t", "E": f"{a}-t",
                                   "S": below_v, "N": below_v}, i)
                d_north[i] = f"{a}-t-done"
                v_north[i] = below_v
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
                        if row_of_atom[hi] != i - 1 or (
                                row_of_atom[lo] != 1
                                and row_of_atom[lo] != i - 2):
                            raise UnsupportedGeometry(
                                f"conjunctive variant of {a!r}: literals "
                                f"must sit at (adjacent-below, row-1 via), "
                                f"got rows "
                                f"{(row_of_atom[hi], row_of_atom[lo])}")
                        derived_hi = hi in rules
                        if derived_hi and row_of_atom[lo] != i - 2:
                            # gate A positional arm (designs/009 §9.2/
                            # §9.3): a derived adjacent-below hi is
                            # read as the chain link, with the lo at
                            # the positional i-2 D-column passthrough.
                            raise UnsupportedGeometry(
                                f"conjunctive variant of {a!r}: adjacent-"
                                f"below literal {hi!r} is a derived row "
                                "— the designs/009 §9.2 Option II arm "
                                "reads it as the chain link with the lo "
                                f"at the positional i-2 passthrough; lo "
                                f"{lo!r} at row {row_of_atom[lo]} is not "
                                "the passthrough row (the row-1 via arm "
                                "is fact-hi only)")
                        if not derived_hi and row_of_atom[lo] != 1:
                            raise UnsupportedGeometry(
                                f"conjunctive variant of {a!r}: literals "
                                f"must sit at (adjacent-below, row-1 via), "
                                f"got rows "
                                f"{(row_of_atom[hi], row_of_atom[lo])}")
                        if not derived_hi and below_v != via:
                            raise UnsupportedGeometry(
                                f"conjunctive variant of {a!r}: row-1 via "
                                f"relay suspended below row {i} (a derived "
                                "row occupies the V column); untested "
                                "(designs/008 stage 1)")
                        if derived_hi:
                            # designs/009 §9.2 reader-order swap: the
                            # lo reader at x=1 south-reads the re-typed
                            # passthrough by value typing (false lo →
                            # f-done against a t-done read, bond 0);
                            # the hi reader at x=2 south-reads the
                            # UNCHANGED stage-1 chain link.
                            emit(f"D{chr(65)}{a}" if and_no == 1 else
                                 f"D{chr(65)}{a}{and_no}",
                                 {"W": f"go{i}", "S": f"{lo}-t-done",
                                  "E": vj, "N": f"{vj}-done"}, i)
                            emit(f"D{chr(66)}{a}" if and_no == 1 else
                                 f"D{chr(66)}{a}{and_no}",
                                 {"W": vj, "S": f"{hi}-t-done",
                                  "E": f"{a}-t",
                                  "N": f"{a}-t-done"}, i)
                        else:
                            emit(f"D{chr(65)}{a}" if and_no == 1 else
                                 f"D{chr(65)}{a}{and_no}",
                                 {"W": f"go{i}", "S": f"{hi}-t-done",
                                 "E": vj, "N": f"{vj}-done"}, i)
                            emit(f"D{chr(66)}{a}" if and_no == 1 else
                                 f"D{chr(66)}{a}{and_no}",
                                 {"W": vj, "S": f"{lo}-t-done",
                                 "E": f"{a}-t",
                                 "N": f"{a}-t-done"}, i)
                        reads = {hi, lo}
                    else:                        # unit variant (b == 1)
                        lit = body[0]
                        if row_of_atom[lit] == 1:
                            if below_v != via:
                                raise UnsupportedGeometry(
                                    f"unit variant of {a!r}: row-1 via "
                                    f"relay suspended below row {i} (a "
                                    "derived row occupies the V column); "
                                    "untested (designs/008 stage 1)")
                        elif lit == below and lit in rules:
                            pass   # chain link (designs/008 stage 1):
                            # the reader's true-typed {lit}-t-done read
                            # is carried by the derived row below — it
                            # realizes iff that atom is true, so dead
                            # links stay dead by value typing.
                        elif lit in rules:
                            raise UnsupportedGeometry(
                                f"unit variant of {a!r}: chain literal "
                                f"{lit!r} at row {row_of_atom[lit]} is "
                                "non-adjacent (must sit directly below "
                                "its reader); untested geometry")
                        else:
                            raise UnsupportedGeometry(
                                f"unit variant of {a!r}: literal {lit!r} "
                                "not via-carried (row-1) nor an adjacent-"
                                "below derived row; direct-below FACT "
                                "readers are a designs/002 geometry, "
                                "unwired in v0.2 stage 1")
                        cnames = (f"C{a}", f"U{a}") if unit_no == 1 else \
                                 (f"C{a}{unit_no}", f"U{a}{unit_no}")
                        conduit_n = (below_d if i in passthrough_rows
                                     else f"{vj}-done")
                        emit(cnames[0],
                             {"W": f"go{i}", "S": below_d, "E": vj,
                              "N": conduit_n}, i)          # conduit
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
            if intermediate:
                intermediate_rows.append(i)
                d_north[i] = (below_d if i in passthrough_rows
                              else f"unit1_{a}-done")
                v_north[i] = f"{a}-t-done"
        else:                                   # predicted false
            emit(f"D{i}F{a}", {"W": f"go{i}", "S": below_d,
                               "E": f"{a}-f", "N": f"{a}-f-done"}, i)
            lock_n = f"cap{n}" if i == n else f"base{i + 1}"
            if i == n:                          # terminal: inert cap
                emit(f"F{a}", {"W": f"{a}-f", "E": f"{a}-f",
                               "S": below_v, "N": "rf-relay"}, i)
                emit(f"L{i}f{a}", {"W": f"{a}-f", "S": f"base{i}",
                                  "N": lock_n}, i)
                if a in rules:                  # designs/008 stage 3:
                    # terminal dead-reader emission — same proof as
                    # stage 2: least-model support kills every body
                    # of a predicted-false head, so a unit body's
                    # reader has zero matchable faces (S reads
                    # {lit}-t-done for a false literal, emitted
                    # nowhere; W is the vj conduit glue, which the
                    # false basis emits nowhere; 1 per face < TAU 2,
                    # stacked dead readers mutually give 1 each).
                    # PC4/PC10's dead links become EMITTED machinery
                    # whose absence from every assembly BFS-proves.
                    # Stage 4: AND bodies emit the READER half only
                    # (the DB-shaped tile).  The conduit half stays
                    # unemitted: its S face reads {hi}-t-done, which
                    # is LIVE whenever hi is true (a false head's
                    # AND body needs only one dead conjunct), so the
                    # conduit could become producible and change the
                    # assembly set.  The reader's never-realizes is
                    # glue arithmetic: W = the vj conduit glue
                    # and{and_no}_{a}, unique to this body and
                    # exposed nowhere (no true variant of a false
                    # head exists); S reads {lo}-t-done, bonding at
                    # most 1 (a true lo's basis, or stacked dead
                    # readers).  Max 1 < TAU 2 (PC4's and1_r).
                    and_no = unit_no = 0
                    for body in rules[a]:
                        if len(body) > 2:
                            raise UnsupportedGeometry(
                                f"body width {len(body)} for false "
                                f"head {a!r} (row {i}): dead-reader "
                                "emission pins unit and AND bodies "
                                "only; slot widening untested "
                                "(designs/003 honest limit; false-head "
                                "side closed by designs/008 stage 5)")
                        if len(body) == 1:
                            unit_no += 1
                            vj = f"unit{unit_no}_{a}"
                            emit(f"UD{i}{a}" if unit_no == 1 else
                                 f"UD{i}{a}{unit_no}",
                                 {"W": vj, "S": f"{body[0]}-t-done",
                                  "E": f"{a}-t", "N": f"{a}-t-done"}, i)
                        elif len(body) == 2:
                            and_no += 1
                            hi, lo = sorted(
                                body, key=lambda x: -row_of_atom[x])
                            derived_lit = (hi if hi in rules
                                           else lo if lo in rules
                                           else None)
                            if (row_of_atom[hi] != i - 1
                                    or (derived_lit is not None
                                        and row_of_atom[derived_lit]
                                        != i - 1)):
                                # gate A union, false-head side
                                # (designs/009 §9.3): the dead reader
                                # is emitted machinery, but only for
                                # the AND shape the design pins — the
                                # hi (or derived) literal adjacent-
                                # below, the fact lo at the row-1 via
                                # or the positional i-2 passthrough.
                                raise UnsupportedGeometry(
                                    f"conjunctive variant of false head "
                                    f"{a!r} (row {i}): gate A union "
                                    "(designs/009 §9.3) runs for false "
                                    "heads too — accepted placements "
                                    "are hi adjacent-below (i-1) with lo "
                                    "at the row-1 via (fact hi) or the "
                                    "positional i-2 passthrough "
                                    f"(derived hi); got rows "
                                    f"(hi {row_of_atom[hi]}, lo "
                                    f"{row_of_atom[lo]}, derived "
                                    f"{row_of_atom.get(derived_lit)})")
                            vj = f"and{and_no}_{a}"
                            emit(f"AD{i}{a}" if and_no == 1 else
                                 f"AD{i}{a}{and_no}",
                                 {"W": vj, "S": f"{lo}-t-done",
                                  "E": f"{a}-t", "N": f"{a}-t-done"}, i)
            else:                               # relay the V column north
                emit(f"V{i}{a1}", {"W": f"{a}-f", "E": f"{a}-f",
                                   "S": below_v, "N": below_v}, i)
                emit(f"L{i}", {"W": f"{a}-f", "S": f"base{i}",
                               "N": lock_n}, i)
                if a in rules:                  # designs/008 stage 2:
                    # explicit dead-reader emission.  Least-model
                    # support guarantees every body of a false head
                    # is dead, so a unit body's reader can never
                    # realize: its S face reads {lit}-t-done, which a
                    # false literal emits nowhere, and its W face is
                    # the vj conduit glue, which the false basis
                    # emits nowhere.  With match strength 1 < TAU 2
                    # per face the tile has zero matchable faces
                    # (stacked dead readers mutually give 1 each), so
                    # the dead link is EMITTED machinery whose absence
                    # from every assembly BFS-proves — not vacuous
                    # non-emission.  The terminal false row emits the
                    # same readers (stage 3).  Stage 4: AND bodies
                    # emit the READER half only, same proof — W is
                    # the vj conduit glue and{and_no}_{a}, unique to
                    # the body and exposed nowhere; S reads
                    # {lo}-t-done at strength <= 1 (a true lo's basis
                    # or stacked dead readers).  The conduit half
                    # stays unemitted: its S face reads {hi}-t-done,
                    # live whenever hi is true (a false head's AND
                    # body needs only one dead conjunct), risking a
                    # producible dead conduit.  Width > 2: refused
                    # (designs/008 stage 5: the silent-acceptance
                    # boundary of false heads is closed on both the
                    # terminal and non-terminal sides).
                    and_no = unit_no = 0
                    for body in rules[a]:
                        if len(body) > 2:
                            raise UnsupportedGeometry(
                                f"body width {len(body)} for false "
                                f"head {a!r} (row {i}): dead-reader "
                                "emission pins unit and AND bodies "
                                "only; slot widening untested "
                                "(designs/003 honest limit; false-head "
                                "side closed by designs/008 stage 5)")
                        if len(body) == 1:
                            unit_no += 1
                            vj = f"unit{unit_no}_{a}"
                            emit(f"UD{i}{a}" if unit_no == 1 else
                                 f"UD{i}{a}{unit_no}",
                                 {"W": vj, "S": f"{body[0]}-t-done",
                                  "E": f"{a}-t", "N": f"{a}-t-done"}, i)
                        elif len(body) == 2:
                            and_no += 1
                            hi, lo = sorted(
                                body, key=lambda x: -row_of_atom[x])
                            derived_lit = (hi if hi in rules
                                           else lo if lo in rules
                                           else None)
                            if (row_of_atom[hi] != i - 1
                                    or (derived_lit is not None
                                        and row_of_atom[derived_lit]
                                        != i - 1)):
                                # gate A union, false-head side
                                # (designs/009 §9.3): same accepted
                                # placements as the true-head arm.
                                raise UnsupportedGeometry(
                                    f"conjunctive variant of false head "
                                    f"{a!r} (row {i}): gate A union "
                                    "(designs/009 §9.3) runs for false "
                                    "heads too — accepted placements "
                                    "are hi adjacent-below (i-1) with lo "
                                    "at the row-1 via (fact hi) or the "
                                    "positional i-2 passthrough "
                                    f"(derived hi); got rows "
                                    f"(hi {row_of_atom[hi]}, lo "
                                    f"{row_of_atom[lo]}, derived "
                                    f"{row_of_atom.get(derived_lit)})")
                            vj = f"and{and_no}_{a}"
                            emit(f"AD{i}{a}" if and_no == 1 else
                                 f"AD{i}{a}{and_no}",
                                 {"W": vj, "S": f"{lo}-t-done",
                                  "E": f"{a}-t", "N": f"{a}-t-done"}, i)
                d_north[i] = f"{a}-f-done"
                v_north[i] = below_v

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
