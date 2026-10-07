"""d4 — emit-time off-channel census (designs/004, lock-site integrity).

Given the emitted tile inventory, the seed, and the predicted
canonical assembly (one site per tile), enumerate every (site, tile)
pair with total bond >= 1 that is not the canonical occupant: the
misincorporation channels the no-mismatch kTAM actually exposes.
This is the compiler-facing lift of the tick-24 measurement code
(``evidence/2026-10-07-repair-mechanism/trap_census.py``, whose
published receipt this module's tests pin against).

Severity: WARNING, not fatal.  d2/d3 fire on wrong compiles; a
squatter is a kinetic hazard with measured dG dependence (→ 0 by
dG 4), not a semantic error.  The report therefore carries the
measured kinetic context (R4 squat decay, R3b repair rates, P2
dwell ratio) so a consumer can weigh the repairability trade —
value-glue sharing buys substitution repair (74.9–97%) at the cost
of lock squatters (31.4% blocked at dG 0.5) and the cross-row lock
misread (23/23 of the L3-arm false positives) — with numbers, not a
default nobody noticed.

Report shape (``check_d4``)::

    {
      "system": <build name>,
      "severity": "warning",
      "off_channel": {"x,y": {tile: bond, ...}, ...},
      "off_channel_sites_per_species": {tile: ["x,y", ...], ...},
      "lock_hazards": {"x,y": {tile: bond, ...}, ...},   # lock sites only
      "lock_hazards_stable": {...},    # subset with bond >= 2 (tau)
      "lock_hazards_transient": {...},  # subset with bond < 2
      "lock_pair_channels": {"stable": {...}, "transient": {...}},
                                     # deep-probe channels split at tau
      "lock_deep_probe": {"x,y": {west_tile: {tile: bond}}},
      "lock_misreads": {"x,y": {west_tile: {lock_tile: bond}}},
      "measured_context": {... quoted numbers + sources ...},
    }

``lock_misreads`` is the subset of the one-west-substitution deep
probe where the channel tile is itself a lock tile (the L2-style
cross-row misread: a lock reads any ``-t`` glue as TRUE regardless
of row).  The deep probe substitutes the west neighbour of each
lock site with every tile that bonds there before testing lock-site
channels — a bounded two-site search catching channels that need a
single background substitution.

The stable/transient split (tick 31, designs/004 follow-up): the
pre-registered row-scope kTAM sweep FALSIFIED the elimination
reading — under row scope every canonical-background lock hazard
is statically gone, yet reads still block at 0.144, carried by
b=1 channels (the west-substitution pair class, e.g. the D2T+Vp
mutual pair, and non-west-axis holds outside the probe).  The
census therefore reports the bond class of every hazard and the
pair-channel layer separately, quoting the measured context, so a
static ``lock_hazards {}`` can never again be read as kinetic
elimination.  ``pair_probe_bound`` records the west-bounded
coverage of the probe (DBr@(3,3), 72/500 under row scope, rides a
non-west axis and is invisible to it by construction).

Conventions (this geometry family, designs/001-003): the
canonical assembly is derived structurally per row — the spine
tile (no W glue) sits at x=0, the row-entry tile (``go{i}`` on W)
at x=1, the remaining via/conduit tile at x=2, and the lock tile
(named ``L*``, the lab's decode-reader convention) at x=3 — from
``row_of`` (``canonical_assembly``); lock sites follow the same
``L*`` convention.  Both canon and lock_sites can be supplied
explicitly for other conventions.
"""
from __future__ import annotations

FACE_DIR = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

# The four shared value-family glue suffixes (true and false) that
# row scope qualifies (tick 30; previously -t/-t-done only — the
# false-family lock squats survived, see apply_lock_glue_scope).
SHARED_VALUE_SUFFIXES = ("-t", "-t-done", "-f", "-f-done")

# designs/002 v2.0 row-typed-spine exemption: spine self-bonds are
# strength 2 (with strength-1 spines nothing attaches in row 1 at
# tau=2); all other matched glues are cooperative strength 1.
DEFAULT_STRENGTH = {("SP1", "SP1"): 2, ("SP2", "SP2"): 2, ("SP3", "SP3"): 2}

# Measured kinetic context quoted verbatim into every report so the
# hazard severity is read against numbers, not vibes.  Sources are
# committed receipts; d4 itself is static arithmetic (non-goal:
# kinetics — designs/004).
MEASURED_CONTEXT = {
    "squat_blocked_rate_by_dG": {"0.5": 0.314, "2.0": 0.118, "4.0": 0.000},
    "substitution_repair_rates": {
        "D1T fills V0p vacancy": 0.749, "D2T fills Vp vacancy": 0.901,
        "V0p repairs D1T-missing": 0.94, "Vp repairs D2T-missing": 0.97},
    "lock_dwell_ratio_nonpqr_over_pqr": 4.5059,
    "row_scope_kinetics": {
        "read_lock_squat_blocked_dG0.5": 0.144,
        "surviving_lock_squats_of_500": {
            "Vp@(3,2)": 72, "DBr@(3,3)": 72, "V0p@(3,1)": 0},
        "stable_b2_repair_fill": 0.162,
        "b1_transient_equilibrium_occupancy": 0.38,
        "vertical_stack_read_block_dG0.5": 0.141,
        "vertical_stack_cooccurrence": "141/141 (Vp@(3,2)+DBr@(3,3), H3)",
        "relay_stack_stable_fill_dG0.5": 0.155,
        "relay_stack_b3_frac": 0.9871,
        "relay_stack_lb_any_frac": 0.0129,
        "family_refs": {"blocked": 0.27, "stable_repair_fill": 0.908,
                        "misread": 0.056},
    },
    "sources": [
        "evidence/2026-10-07-repair-mechanism/trap_grid.out (R3b, R4)",
        "evidence/2026-10-07-vp-residual/vp_residual.out (P2 dwell)",
        "evidence/2026-10-07-row-scope-ktam/row_scope.out (RS1-RS4)",
        "evidence/2026-10-07-recombination/recombination.out (H1-H4)",
    ],
}


def glue_strength(g1, g2, strength=None):
    """Bond strength of two opposing face glues (0 when either is
    blank or the names differ)."""
    if not g1 or not g2:
        return 0
    table = DEFAULT_STRENGTH if strength is None else strength
    if (g1, g2) in table:
        return table[(g1, g2)]
    return 1 if g1 == g2 else 0


def matched_strength(build, asm, site, tile_name, strength=None):
    """Total bond strength for ``tile_name`` at ``site`` given
    assembly ``asm`` (seed cells always present, exposing their
    north faces; sites at y=0 read the seed glue table directly)."""
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
        total += glue_strength(g1, g2, strength)
    return total


def canonical_assembly(build):
    """Derive the predicted canonical assembly (one site per tile)
    from ``row_of`` and the row structure: per row, the spine tile
    (no W glue) at x=0, the row-entry tile (``go{i}`` on W) at x=1,
    the remaining via/conduit tile at x=2, the lock tile (``L*``) at
    x=3.  Name-agnostic except for the ``L*`` lock convention, so
    slot-B readers with D-prefix names (e.g. DBr at x=2 in the AND
    builds) place correctly."""
    by_row = {}
    for tname, row in build["row_of"].items():
        by_row.setdefault(row, []).append(tname)
    canon = {}
    for row, tnames in sorted(by_row.items()):
        spine = [t for t in tnames if not build["tiles"][t].get("W")]
        entry = [t for t in tnames
                 if build["tiles"][t].get("W") == f"go{row}"]
        lock = [t for t in tnames if t.startswith("L")]
        via = [t for t in tnames
               if t not in spine and t not in entry and t not in lock]
        placed = {0: spine, 1: entry, 2: via, 3: lock}
        for x, bucket in placed.items():
            if len(bucket) != 1:
                raise ValueError(
                    f"row {row}: column {x} is not one-tile ({bucket}); "
                    "the designs/003 row structure does not hold — pass "
                    "canon explicitly")
            canon[(x, row)] = bucket[0]
    return canon


def infer_lock_sites(canon):
    """Lock sites = canonical occupants named ``L*`` (the decode
    readers; lab convention from designs/003)."""
    return tuple(sorted(s for s, t in canon.items() if t.startswith("L")))


def skey(site):
    return "%d,%d" % site


def off_channel(build, canon, strength=None):
    """The who-can-squat-where table: per site, every non-canonical
    inventory tile bonding >= 1 against the canonical background."""
    table = {}
    for site in sorted(canon):
        squatters = {}
        for tile in sorted(build["tiles"]):
            if tile == canon[site]:
                continue
            b = matched_strength(build, canon, site, tile, strength)
            if b >= 1:
                squatters[tile] = b
        if squatters:
            table[skey(site)] = squatters
    return table


def lock_deep_probe(build, canon, lock_sites, strength=None):
    """Channels at each lock site allowing one WEST-neighbour
    substitution of the canonical background: per lock site,
    {west_substitute: {lock-site tile: bond}} for bonds >= 1 by any
    tile other than the canonical lock tile (any channel when the
    canonical lock tile is absent from the inventory)."""
    out = {}
    for lock in sorted(lock_sites):
        west = (lock[0] - 1, lock[1])
        if west not in canon:
            continue
        west_canon = canon[west]
        west_options = []
        if west_canon in build["tiles"]:
            west_options.append(west_canon)
        for tile in sorted(build["tiles"]):
            if tile == west_canon:
                continue
            if matched_strength(build, canon, west, tile, strength) >= 1:
                west_options.append(tile)
        found = {}
        for wtile in west_options:
            bg = dict(canon)
            bg[west] = wtile
            channels = {}
            for tile in sorted(build["tiles"]):
                if tile == canon[lock]:
                    continue
                b = matched_strength(build, bg, lock, tile, strength)
                if b >= 1:
                    channels[tile] = b
            if channels:
                found[wtile] = channels
        if found:
            out[skey(lock)] = found
    return out


def lock_misreads_from(probe):
    """Subset of the deep probe where the lock-site channel tile is
    itself a lock tile — the cross-row misread class (a lock reads
    any ``-t`` glue on W as TRUE, regardless of row).  Deep-probe
    channels already exclude the canonical lock tile, so every
    ``L*`` channel here is a WRONG-row lock sitting at a lock site."""
    out = {}
    for site, wests in probe.items():
        for west, channels in wests.items():
            mis = {t: b for t, b in channels.items() if t.startswith("L")}
            if mis:
                out.setdefault(site, {})[west] = mis
    return out


def split_lock_hazards(hazards, tau=2):
    """The bond-class split of a lock-hazard table (tick 31,
    designs/004 follow-up): ``stable`` holds at bond >= tau —
    on-site squatters that survive read-out by arithmetic; the
    rest is the ``transient`` layer — single-bond holds at
    equilibrium ~0.38 occupancy at the protocol point, the class
    that carried the measured 0.144 row-scope read-block after
    every static hazard died."""
    stable, transient = {}, {}
    for site, squatters in hazards.items():
        for tile, b in squatters.items():
            tgt = stable if b >= tau else transient
            tgt.setdefault(site, {})[tile] = b
    return {"stable": stable, "transient": transient}


def split_pair_channels(probe, tau=2):
    """The deep probe split at tau: substitution-ENABLED lock-site
    channels by bond class.  This is the layer that survives glue
    qualification — under row scope the only static survivor class
    is here ({west D2T -> Vp@(3,2)} at b=1, the smoke-predicted
    mutual pair, measured 72/500), and the stable b=2 recombination
    channel (0.162 repair fill) is this table's b>=2 face."""
    stable, transient = {}, {}
    for site, wests in probe.items():
        for west, channels in wests.items():
            for tile, b in channels.items():
                tgt = stable if b >= tau else transient
                tgt.setdefault(site, {}).setdefault(west, {})[tile] = b
    return {"stable": stable, "transient": transient}


def vertical_lock_stacks(build, canon, lock_sites, strength=None):
    """Two-site cooperative channels in the lock column (tick 33/34,
    the VERTICAL LOCK-STACK class): pairs of squatters at vertically
    adjacent lock sites that bond EACH OTHER, so each is held in the
    other's presence even when every single-site bond against the
    canonical background is zero — invisible to the one-site census.
    This is the class that carried the measured row-scope read-block
    (Vp@(3,2) + DBr@(3,3): 141/141 of blocked terminals,
    recombination.out H3; west D2T co-stacks but is not
    load-bearing).  Per adjacent lock-site pair, records every
    mutually-supporting pair with its solo bonds (against the pure
    canonical background — the one-site census view) and in-stack
    totals, so ``solo == 0`` channels read as cooperative-only."""
    locks = set(lock_sites)
    out = {}
    for lo in sorted(lock_sites):
        hi = (lo[0], lo[1] + 1)
        if hi not in locks or hi not in canon:
            continue
        pairs = {}
        for t1 in sorted(build["tiles"]):
            if t1 == canon[lo]:
                continue
            for t2 in sorted(build["tiles"]):
                if t2 == canon[hi]:
                    continue
                bmut = glue_strength(build["tiles"][t1].get("N"),
                                     build["tiles"][t2].get("S"), strength)
                if bmut < 1:
                    continue
                a1 = dict(canon)
                a1[hi] = t2
                b1 = matched_strength(build, a1, lo, t1, strength)
                a2 = dict(canon)
                a2[lo] = t1
                b2 = matched_strength(build, a2, hi, t2, strength)
                if b1 < 1 or b2 < 1:
                    continue
                pairs[f"{t1}+{t2}"] = {
                    "b_mutual_vertical": bmut,
                    "b_lower_in_stack": b1,
                    "b_upper_in_stack": b2,
                    "b_lower_solo": matched_strength(
                        build, canon, lo, t1, strength),
                    "b_upper_solo": matched_strength(
                        build, canon, hi, t2, strength),
                }
        if pairs:
            out[f"{skey(lo)}|{skey(hi)}"] = pairs
    return out


def vacancy_relay_stacks(build, canon, strength=None, min_contacts=2):
    """Cooperative vacancy-repair channels (tick 33/34, the VACANCY
    RELAY-STACK class): non-canonical fillers whose hold at a site is
    relayed through a FAN of neighbour contacts — direct canonical
    bonds plus mutually-supporting squatter relays at adjacent sites.
    This enumerates the redundancy that single-load-bearing analysis
    misses: the measured row-scope repair channel is a 2-of-3 relay
    stack D2T@(2,2) N->DAr + S->V0p + W->S2 (153/155 holds at b=3,
    lb_any 0.0129 — recombination.out H1), so no single partner is
    load-bearing and the channel survives killing any one bond class.
    A filler enters the report when it has at least one squatter
    relay AND at least ``min_contacts`` contact axes; its
    ``solo_total_bond`` (pure-canonical-background arithmetic, the
    repair_bonds view) separates family-style stable-by-arithmetic
    fills (solo >= tau) from cooperative-only ones (solo < tau)."""
    out = {}
    for v in sorted(canon):
        fillers = {}
        for f in sorted(build["tiles"]):
            if f == canon[v]:
                continue
            contacts = {}
            n_squatter_axes = 0
            for face, (dx, dy) in FACE_DIR.items():
                u = (v[0] + dx, v[1] + dy)
                if u not in canon:
                    continue
                g1 = build["tiles"][f].get(face)
                if not g1:
                    continue
                axis = {}
                if glue_strength(g1, build["tiles"][canon[u]].get(
                        OPPOSITE[face]), strength) >= 1:
                    axis["canonical"] = canon[u]
                relays = [t for t in sorted(build["tiles"])
                          if t != canon[u]
                          and glue_strength(
                              g1, build["tiles"][t].get(OPPOSITE[face]),
                              strength) >= 1]
                if relays:
                    axis["squatter_relays"] = relays
                    n_squatter_axes += 1
                if axis:
                    contacts[face] = axis
            if contacts and n_squatter_axes >= 1 \
                    and len(contacts) >= min_contacts:
                fillers[f] = {
                    "contacts": contacts,
                    "n_relay_contacts": len(contacts),
                    "n_squatter_relay_axes": n_squatter_axes,
                    "solo_total_bond": matched_strength(
                        build, canon, v, f, strength),
                }
        if fillers:
            out[skey(v)] = fillers
    return out


def check_d4(build, canon=None, *, lock_sites=None, strength=None):
    """Emit-time off-channel census (d4).  WARNING severity: returns
    the report; never gates emission (designs/004 A3)."""
    if canon is None:
        canon = canonical_assembly(build)
    if lock_sites is None:
        lock_sites = infer_lock_sites(canon)
    oc = off_channel(build, canon, strength)
    per_species = {}
    for site, squatters in oc.items():
        for tile in squatters:
            per_species.setdefault(tile, []).append(site)
    probe = lock_deep_probe(build, canon, lock_sites, strength)
    hazards = {s: sq for s, sq in oc.items()
               if s in {skey(l) for l in lock_sites}}
    haz_split = split_lock_hazards(hazards)
    stacks = vertical_lock_stacks(build, canon, lock_sites, strength)
    relays = vacancy_relay_stacks(build, canon, strength)
    report = {
        "system": build.get("name", "<unnamed>"),
        "severity": "warning",
        "off_channel": oc,
        "off_channel_sites_per_species": {
            t: sorted(s) for t, s in sorted(per_species.items())},
        "lock_hazards": hazards,
        "lock_hazards_stable": haz_split["stable"],
        "lock_hazards_transient": haz_split["transient"],
        "lock_deep_probe": probe,
        "lock_pair_channels": split_pair_channels(probe),
        "lock_stack_channels": stacks,
        "vacancy_relay_stacks": relays,
        "pair_probe_bound": (
            "one-west-substitution bounded: channels riding N/S/E "
            "substitutions are outside the probe (measured example: "
            "DBr@(3,3) survives row scope at 72/500, row_scope.out RS1)"),
        "lock_misreads": lock_misreads_from(probe),
        "measured_context": MEASURED_CONTEXT,
    }
    return report


def d4_report_lines(report):
    """Human-readable warning block for the emit log."""
    lines = [f"d4 off-channel census ({report['system']}) — "
             f"severity {report['severity']} (kinetic hazard, not a "
             "semantic error; does not gate emission)"]
    for site, sq in sorted(report["lock_hazards_stable"].items()):
        for tile, b in sorted(sq.items()):
            lines.append(f"  lock hazard (stable, b>=2): {tile} squats "
                         f"{site} at bond {b}")
    for site, sq in sorted(report["lock_hazards_transient"].items()):
        for tile, b in sorted(sq.items()):
            lines.append(f"  lock hazard (b=1 transient): {tile} squats "
                         f"{site} at bond {b} — equilibrium ~0.38 at the "
                         "protocol point; not eliminated by glue "
                         "qualification")
    for cls, label in (("transient", "b=1"), ("stable", "b>=2")):
        for site, wests in sorted(report["lock_pair_channels"][cls].items()):
            for west, chans in sorted(wests.items()):
                for tile, b in sorted(chans.items()):
                    lines.append(f"  pair channel ({label}): {tile} at "
                                 f"{site} (bond {b}) via west substitution "
                                 f"{west} — substitution-enabled; measured "
                                 "row-scope read-block 0.144 (RS1)")
    for pair_key, pairs in sorted(report["lock_stack_channels"].items()):
        for pair, b in sorted(pairs.items()):
            coop = (b["b_lower_solo"] == 0 or b["b_upper_solo"] == 0)
            if not coop:
                continue
            lines.append(
                f"  vertical lock stack: {pair} at {pair_key} "
                f"(mutual N-S bond {b['b_mutual_vertical']}, in-stack "
                f"b {b['b_lower_in_stack']}/{b['b_upper_in_stack']}, "
                f"solo {b['b_lower_solo']}/{b['b_upper_solo']}"
                + (" — cooperative-only: invisible to the one-site "
                   "census; measured row read-block 0.141 rides "
                   "this class (recombination.out H3)" if coop else "")
                + ")")
    for site, fillers in sorted(report["vacancy_relay_stacks"].items()):
        for filler, fan in sorted(fillers.items()):
            if fan["n_relay_contacts"] < 3 \
                    and fan["n_squatter_relay_axes"] < 2:
                continue
            dirs = ", ".join(
                f"{face}->" + "+".join(
                    ([v["canonical"]] if "canonical" in v else [])
                    + v.get("squatter_relays", []))
                for face, v in sorted(fan["contacts"].items()))
            lines.append(
                f"  vacancy relay stack: {filler} at {site} — "
                f"{fan['n_relay_contacts']} contact axes ({dirs}); "
                f"solo total bond {fan['solo_total_bond']}. "
                "Redundant fan: single-load-bearing analysis does not "
                "apply (measured row repair 0.155 at 98.7% b=3, "
                "lb_any 0.0129 — recombination.out H1)")
    for site, wests in sorted(report["lock_misreads"].items()):
        for west, mis in sorted(wests.items()):
            for tile, b in sorted(mis.items()):
                lines.append(f"  lock misread: {tile} at {site} (bond {b}) "
                             f"via west substitution {west}")
    ctx = report["measured_context"]
    lines.append(
        "  measured context: lock-squat block rate "
        + " -> ".join(f"{v} (dG {k})" for k, v in
                      sorted(ctx["squat_blocked_rate_by_dG"].items(),
                             key=lambda kv: float(kv[0])))
        + f"; substitution repair "
        + "/".join(str(v) for v in
                   ctx["substitution_repair_rates"].values())
        + f"; non-pqr lock dwell {ctx['lock_dwell_ratio_nonpqr_over_pqr']}x "
          "pqr — pick the read window against these numbers")
    return lines


# ---------- lock_glue_scope knob (designs/004) ---------------------------

def apply_lock_glue_scope(build, scope="family", canon=None):
    """Return a copy of ``build`` under the ``lock_glue_scope`` knob
    (designs/004).  ``family`` (the emitted default) returns the
    build unchanged: value glues (``{atom}-t`` / ``{atom}-t-done``)
    are shared across a row's tiles, buying substitution repair
    (74.9-97% measured) at the cost of lock squatters and the
    cross-row lock misread.  ``row`` qualifies the shared
    value-family bonds per canonical row so the lock column no
    longer reads the propagation family:

    - lock-read bonds (west via E <-> lock W) become ``{g}-lk{i}``
      for the lock's row ``i`` — the canonical read survives, the
      V.W-vs-V.E squat (same glue on both via faces) does not;
    - canonical vertical relay bonds on value glues become
      ``{g}-lk{i+1}`` for the row pair they span — the relay
      survives, the cross-row substitution holds that ride it do
      not.

    Every rename touches a canonical bond on BOTH faces, so the
    canonical assembly's bond profile is unchanged by construction;
    what breaks is every OFF-channel use of the same bonds — squat,
    misread enabler, and substitution repair together (designs/004:
    all three are the same bonds).  Not a free fix: the repair
    channel dies with the hazards (measured trade in
    ``lock_glue_scope_reports``).

    The qualified families are ALL four shared value-family
    suffixes — true and false (``-t`` / ``-t-done`` / ``-f`` /
    ``-f-done``, tick 30).  The tick-29 rule covered the true
    families only, which left the false-family lock squats alive
    (BUILD3 ``Fp@(3,3)``, whose row reads its lock off ``p-f``;
    BUILD2 ``Vp@(3,2)`` / ``Fr@(3,3)``) — an honest boundary that
    is now closed: those squats ride the same row-shared family
    bonds and die under the same qualification.  The remaining
    boundary is glue CLASS, not family: non-value glues (spine,
    ``go*`` entries, caps, ``and*`` relays, ``w*`` relays) are
    never qualified — no hazard in the current inventories rides
    them at a lock site.
    """
    import copy
    if scope == "family":
        return copy.deepcopy(build)
    if scope != "row":
        raise ValueError(
            f"lock_glue_scope must be 'family' or 'row', got {scope!r}")
    if canon is None:
        canon = canonical_assembly(build)
    new = copy.deepcopy(build)
    tiles = new["tiles"]

    def value_family(g):
        return g.endswith(SHARED_VALUE_SUFFIXES)

    renames = []
    for (x, y) in sorted(canon):
        t = canon[(x, y)]
        east = canon.get((x + 1, y))
        if east is not None and east.startswith("L"):
            g = tiles[t].get("E")
            if g and g == tiles[east].get("W") and value_family(g):
                ng = f"{g}-lk{y}"
                renames += [(t, "E", ng), (east, "W", ng)]
        north = canon.get((x, y + 1))
        if north is not None:
            g = tiles[t].get("N")
            if g and g == tiles[north].get("S") and value_family(g):
                ng = f"{g}-lk{y + 1}"
                renames += [(t, "N", ng), (north, "S", ng)]
    for t, face, ng in renames:
        tiles[t][face] = ng
    return new


def lock_glue_scope_reports(build, canon=None):
    """d4 under both glue-family scopes — the emit-time view of the
    repairability trade (designs/004): ``family`` buys substitution
    repair and pays in lock squatters + the cross-row misread;
    ``row`` kills both hazard classes and the repair channel with
    them.  Also carries ``repair_bonds``: the static bond strength
    of the two census substitution tiles at their vacancy sites
    under each scope (the repair channel's stable-b=2 arithmetic,
    same bonds the census measures)."""
    if canon is None:
        canon = canonical_assembly(build)
    row_build = apply_lock_glue_scope(build, "row", canon)
    fam_rep = check_d4(build, canon)
    row_rep = check_d4(row_build, canon)

    def repair_bonds(b):
        # the two census substitution pairs (tick 24): D1T fills the
        # V0p vacancy at (2,1), D2T the Vp vacancy at (2,2) — skipped
        # for inventories without those tiles (e.g. wrong compiles).
        pairs = (("D1T", (2, 1)), ("D2T", (2, 2)))
        return {t: matched_strength(b, canon, s, t)
                for t, s in pairs if t in b["tiles"]}

    return {
        "family": fam_rep,
        "row": row_rep,
        "row_build": row_build,
        "repair_bonds": {
            "family": repair_bonds(build), "row": repair_bonds(row_build)},
    }
