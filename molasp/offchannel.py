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
      "lock_misplacements": {"x,y": {lock_tile: {"bond": int,
                     "faces": {face: bond}, "w_read": bool}}},
                                  # lock tiles at non-own sites (ANY
                                  # site class) — the tile-class view
                                  # (tick 39, designs/006)
      "vacancy_contention": {species: {"x,y": {tile: {
                     "classes": [...], "bond": {knob: int},
                     "faces": {face: bond}, "w_read": bool,
                     "enables": {"L@x,y": {knob: {"b_with": int,
                                               "b_without": int}}},
                     "stable_under": [knob, ...]}}}},
                                  # per-species vacancy backgrounds,
                                  # contenders priced under every knob
                                  # (tick 42, designs/007 consequence)
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

import math

FACE_DIR = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

# The four shared value-family glue suffixes (true and false) that
# row scope qualifies (tick 30; previously -t/-t-done only — the
# false-family lock squats survived, see apply_lock_glue_scope).
SHARED_VALUE_SUFFIXES = ("-t", "-t-done", "-f", "-f-done")

# designs/002 v2.0 row-typed-spine exemption, as the designs/010
# §10.3 class closure rule (stage 7): spine self-bonds SPi<->SPi are
# strength 2 for every i >= 1 (with strength-1 spines nothing
# attaches in row 1 at tau=2); all other matched glues are
# cooperative strength 1.  The ONE predicate lives in compiler.py and
# is consumed below; the former enumerated DEFAULT_STRENGTH (SP1-3
# only — the live row-4 divergence) is deleted (§10.4-1).

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
    "strength2_lock_misplacements": {
        "s2_b1": {"L1@(3,2)": 5, "L2@(3,3)": 67, "L3@(3,2)": 43},
        "s2_b1_Vp_arm": {"L3@(3,2)": 82},
        "s2_unit": {"L1@(3,2)": 3, "L2@(3,3)": 83, "L3@(3,2)": 44},
        "fam_refs": {"L2@(3,3)": 10, "unit_L2@(3,3)": 12},
        "note": "terminal squatter counts /500: the misplaced-lock "
                "class is minor at family strength and dominant "
                "under the strength-2 lock read (K1/K2 FALSIFIED "
                "as mitigation, tick 38)",
    },
    "vacancy_contention": {
        "s2_west_site_terminal_occupants_of_500": {
            "D2T": 203, "L2": 150, "DBr": 78, "L3": 54,
            "D1T": 6, "S2": 4},
        "fill_frac": {"family": 0.908, "s2": 0.406},
        "fill_given_L3_present": 0.0,
        "fill_given_L3_absent": 0.481,
        "L3_west_match": "78/78 DBr",
        "race_L3_first_frac": 0.214,
        "note": "tick-41 s2 Vp-missing arm: the vacancy's west site "
                "is three-way first-come contention (fill / via-squat "
                "/ reader stack) — price reinforcement knobs against "
                "the whole set (designs/007 consequence)",
    },
    "sources": [
        "evidence/2026-10-07-repair-mechanism/trap_grid.out (R3b, R4)",
        "evidence/2026-10-07-vp-residual/vp_residual.out (P2 dwell)",
        "evidence/2026-10-07-row-scope-ktam/row_scope.out (RS1-RS4)",
        "evidence/2026-10-07-recombination/recombination.out (H1-H4)",
        "evidence/2026-10-07-strength2-lock/strength2.out "
        "(K1/K2 terminal squatter tables)",
    ],
}


def glue_strength(g1, g2, strength=None):
    """Bond strength of two opposing face glues (0 when either is
    blank or the names differ).  Default: the compiler's class
    closure predicate (designs/010 §10.3).  An explicit ``strength``
    table still overrides per call (kinetic-sweep hypothesis
    tables)."""
    if strength is None:
        from .compiler import glue_strength as _closure
        return _closure(g1, g2)
    if not g1 or not g2:
        return 0
    if (g1, g2) in strength:
        return strength[(g1, g2)]
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


def lock_misplacements(build, canon, strength=None, bond_fn=None):
    """Lock-tile off-channel PLACEMENTS (tick 39, designs/006): the
    TILE-class view of the census — every site (any site class)
    where a lock tile (``L*``) that is not the canonical occupant
    bonds >= 1 against the canonical background.

    This is the class the strength-2 falsification discovered (tick
    38): at family strength the misplaced locks ride base relays
    and the W read at b=1 — present in ``off_channel`` but surfaced
    by no lock layer, because every existing layer filters by SITE
    class (lock sites only) or by substitution probe; the family
    census therefore read "all V-class squatters" (G1) while the
    L*-placements waited on the glue.  The moment lock bonds are
    reinforced they dominate (measured: L2@(3,3) 67/500, L3@(3,2)
    43/500, 82/500 in the Vp arm — strength2.out K1/K2).

    Channel record: ``bond`` is the total under the caller's
    arithmetic — ``bond_fn=None`` gives the family-strength census
    bond; pass the tick-38 ``matched_s2`` for the strength-2 view
    (any ``L*`` W read doubled).  ``faces`` is always the
    family-strength per-face decomposition, and ``w_read`` flags
    the W-face channel — the face a strength-reinforced lock read
    doubles, i.e. exactly the channels that gain under s2.
    Sites keyed ``x,y`` like every census layer."""
    out = {}
    for site in sorted(canon):
        placements = {}
        for tile in sorted(build["tiles"]):
            if not tile.startswith("L") or tile == canon[site]:
                continue
            fam_faces = {}
            for face, (dx, dy) in FACE_DIR.items():
                g1 = build["tiles"][tile].get(face)
                if not g1:
                    continue
                nx, ny = site[0] + dx, site[1] + dy
                if ny == 0 and (nx, 0) in build["seed"]:
                    g2 = build["seed"][(nx, 0)]
                elif (nx, ny) in canon:
                    g2 = build["tiles"][canon[(nx, ny)]].get(
                        OPPOSITE[face])
                else:
                    continue
                b_face = glue_strength(g1, g2, strength)
                if b_face:
                    fam_faces[face] = b_face
            if bond_fn is not None:
                total = bond_fn(build, canon, site, tile)
            else:
                total = sum(fam_faces.values())
            if total >= 1:
                placements[tile] = {
                    "bond": total,
                    "faces": fam_faces,
                    "w_read": fam_faces.get("W", 0) >= 1,
                }
        if placements:
            out[skey(site)] = placements
    return out


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


def matched_s2(build, asm, site, tile_name):
    """Family matched strength with the lock-read bond doubled —
    the tick-38 strength-2 rule, verbatim (promoted from the
    evidence scripts to the census module tick 42, so knob pricing
    lives beside the family arithmetic): a lock's W read into a
    matching E glue bonds twice; dually a non-lock tile's E read
    into a lock's matching W glue bonds twice."""
    b = matched_strength(build, asm, site, tile_name)
    faces = build["tiles"][tile_name]
    if tile_name.startswith("L"):
        g1 = faces.get("W")
        nb = (site[0] - 1, site[1])
        if nb[1] == 0 and nb in build["seed"]:
            g2 = build["seed"][nb]
        elif nb in asm:
            g2 = build["tiles"][asm[nb]].get("E")
        else:
            g2 = None
        if g1 and g2 and g1 == g2:
            b += 1
    else:
        g1 = faces.get("E")
        nb = (site[0] + 1, site[1])
        if nb in asm and str(asm[nb]).startswith("L"):
            g2 = build["tiles"][asm[nb]].get("W")
            if g1 and g2 and g1 == g2:
                b += 1
    return b


def vacancy_contention(build, canon=None, strength=None, bond_fns=None):
    """Full vacancy contention sets, priced per knob (tick 42 — the
    designs/007 design consequence: a lock-reinforcement knob must
    be priced against the FULL contention set of the affected
    vacancy — fill, via-site lock squat, reader stack — not against
    one hazard class).

    Species-death view: for every species S (one at a time), S is
    removed from the inventory, its canonical sites are empty, and
    the canonical map is otherwise kept (the tick-22/23 background).
    At each of S's sites every remaining tile is a CONTENDER when it
    has a family bond face, a per-knob own bond, or an enabling
    stack (below).  Contender classes:

    - ``fill`` — non-lock substitution fill (the repair channel;
      the measured D2T@(2,2) b=2 substitution, tick 24);
    - ``via_squatter`` / ``lock_squatter`` — a lock tile at the
      vacancy; ``via_squatter`` carries the W-read flag (doubles
      under s2 — the tick-39/40 solo class, L2@(2,2) measured);
    - ``stack_partner`` — the contender's presence at the vacancy
      lets a lock at a NEIGHBOURING site reach tau (load-bearing
      pair: b_with >= 2 > b_without under some knob), the
      cooperative channel a solo-bond census cannot price (measured:
      DBr@(2,2) enables frozen L3@(3,2); 78/78 of terminal L3 ride
      it, vacancy_bg.out VB2).

    ``bond`` carries the contender's own bond under every knob in
    ``bond_fns`` (default {"family": None, "s2": matched_s2}; the
    family entry is the plain per-face sum); ``stable_under`` lists
    the knobs under which the contender is stable — own bond >= 2
    OR any enabled stack at b_with >= 2.  The pricing story the
    layer pins (BUILD1, Vp removed, site 2,2): at family strength
    ONE contender is stable (the D2T fill, b=2 — measured fill
    0.908); under s2 THREE are stable at once (D2T unchanged, L2
    w_read 1->2, DBr via the L3 stack) — first-come contention,
    measured fill collapse 0.904 -> 0.406 (VB1/VB3).

    Adversaries that need a SECOND vacancy event are out of scope
    (single-species backgrounds only); multi-site species skip
    self-vacancy neighbours when probing enabled stacks."""
    if canon is None:
        canon = canonical_assembly(build)
    if bond_fns is None:
        bond_fns = {"family": None, "s2": matched_s2}
    species_sites = {}
    for site, tile in canon.items():
        species_sites.setdefault(tile, []).append(site)
    out = {}
    for sp in sorted(species_sites):
        bld = dict(build)
        bld["tiles"] = {t: g for t, g in build["tiles"].items()
                        if t != sp}
        bg = {s: t for s, t in canon.items() if t != sp}
        own_vacancies = set(species_sites[sp])
        sp_rec = {}
        for v in sorted(species_sites[sp]):
            contenders = {}
            for tile in sorted(bld["tiles"]):
                faces_fam = {}
                for face, (dx, dy) in FACE_DIR.items():
                    g1 = bld["tiles"][tile].get(face)
                    if not g1:
                        continue
                    nx, ny = v[0] + dx, v[1] + dy
                    if ny == 0 and (nx, 0) in build["seed"]:
                        g2 = build["seed"][(nx, 0)]
                    elif (nx, ny) in bg:
                        g2 = bld["tiles"][bg[(nx, ny)]].get(
                            OPPOSITE[face])
                    else:
                        continue
                    b_face = glue_strength(g1, g2, strength)
                    if b_face:
                        faces_fam[face] = b_face
                bonds = {}
                for knob, fn in sorted(bond_fns.items()):
                    bonds[knob] = (fn(bld, bg, v, tile) if fn
                                   else sum(faces_fam.values()))
                enables = {}
                for face, (dx, dy) in sorted(FACE_DIR.items()):
                    u = (v[0] + dx, v[1] + dy)
                    if u == v or u in own_vacancies:
                        continue
                    g_t = bld["tiles"][tile].get(face)
                    if not g_t:
                        continue
                    for lock in sorted(bld["tiles"]):
                        if not lock.startswith("L"):
                            continue
                        g_l = bld["tiles"][lock].get(OPPOSITE[face])
                        if not g_l or glue_strength(
                                g_t, g_l, strength) < 1:
                            continue
                        asm_with = dict(bg)
                        asm_with[v] = tile
                        rec = {}
                        for knob, fn in sorted(bond_fns.items()):
                            if fn is None:
                                b_with = matched_strength(
                                    bld, asm_with, u, lock, strength)
                                b_without = matched_strength(
                                    bld, bg, u, lock, strength)
                            else:
                                b_with = fn(bld, asm_with, u, lock)
                                b_without = fn(bld, bg, u, lock)
                            rec[knob] = {"b_with": b_with,
                                         "b_without": b_without}
                        if any(r["b_with"] >= 2 and r["b_without"] < 2
                               for r in rec.values()):
                            enables[f"{lock}@{skey(u)}"] = rec
                if not (faces_fam or enables
                        or any(bonds.values())):
                    continue
                classes = []
                w_read = faces_fam.get("W", 0) >= 1
                if tile.startswith("L"):
                    classes.append("via_squatter" if w_read
                                   else "lock_squatter")
                else:
                    classes.append("fill")
                if enables:
                    classes.append("stack_partner")
                stable = [k for k, b in sorted(bonds.items())
                          if b >= 2]
                for rec in enables.values():
                    for knob, r in rec.items():
                        if r["b_with"] >= 2 and knob not in stable:
                            stable.append(knob)
                contenders[tile] = {
                    "classes": classes,
                    "bond": bonds,
                    "faces": faces_fam,
                    "w_read": w_read,
                    "enables": enables,
                    "stable_under": sorted(stable),
                }
            if contenders:
                sp_rec[skey(v)] = contenders
        if sp_rec:
            out[sp] = sp_rec
    return out


# Tick-43 dG/read-window sweep anchors (contention_dg.out, n=500/arm,
# BUILD1 Vp-missing arm at site 2,2; quoted at .out precision).  The
# severity layer prices the static contention census against these
# MEASURED regimes — no number below is asserted, all are pinned in
# tests/test_contention_severity.py.
REGIME_ANCHORS = {
    "frozen": {"dg": 0.5, "family_fill": 0.904, "knob_fill": 0.412,
               "family_persist": 0.542, "knob_persist": 0.872,
               "site_dwell": 0.994,
               "source": "contention_dg.out fam_dg0.5/s2_dg0.5"},
    "marginal": {"dg": 2.0, "family_fill": 0.97, "knob_fill": 0.464,
                 "family_persist": 0.088, "knob_persist": 0.52,
                 "reroll_split": "D2T 232 : L2 229",
                 "source": "contention_dg.out fam_dg2/s2_dg2"},
    "churn": {"dg": 4.0, "family_fill": 0.074, "knob_fill": 0.564,
              "family_dwell": 0.113, "knob_dwell": 0.967,
              "family_partial": 0.633,
              "win4_family_fill": 0.054, "win4_knob_fill": 0.798,
              "source": "contention_dg.out fam_dg4/s2_dg4(/_win4)"},
    "starvation": {"dg": 7.0, "family_fill": 0.0, "knob_fill": 0.0,
                   "partial": 0.0008, "persist_n": 1,
                   "source": "contention_dg.out s2_dg7"},
}
# Regime boundaries are midpoints of the measured points 0.5/2/4/7;
# every dg off a measured point is priced by nearest regime and
# flagged interpolated (honest-boundary discipline, tick 43).
REGIME_BOUNDS = [(1.0, "frozen"), (3.0, "marginal"), (6.0, "churn"),
                 (None, "starvation")]
KNOB_VERDICTS = {
    "frozen": "hazard", "marginal": "hazard",
    "churn": "mitigation", "starvation": "moot",
}
DEFAULT_DG = 0.5   # the protocol point; check_d4 prices at it


def regime_at(dg):
    """Map a dG operating point to its measured regime.

    Returns ``(regime, interpolated)`` — ``interpolated`` is True
    off the four measured points (0.5 / 2 / 4 / 7), where the
    pricing rests on the nearest regime, not a measurement.
    """
    dg = float(dg)
    interpolated = not any(
        abs(dg - a["dg"]) < 1e-9 for a in REGIME_ANCHORS.values())
    for bound, regime in REGIME_BOUNDS:
        if bound is None or dg < bound:
            return regime, interpolated
    return "starvation", interpolated


def contention_severity(build, dg=None, canon=None, strength=None,
                        bond_fns=None):
    """Compiler-facing severity ranking of knob-sensitive vacancies
    WITH the dG axis (tick 44 — the designs/007 closure).

    The tick-42 census priced vacancies at one operating point;
    tick-43 resolved the trade table on dG.  This layer joins them:
    for every knob-sensitive vacancy (a site whose contender set
    changes stability between knobs) it emits a severity TIER at
    the requested dG, priced against the measured regime anchors
    (REGIME_ANCHORS — never asserted, always quoted).

    Tiers, by regime (see designs/007 closure section for the full
    derivation):

    - frozen/marginal: ``critical`` — the knob mints frozen
      contenders AND a family-stable fill exists (measured BUILD1
      Vp@2,2: fill 0.904 -> 0.412); ``high`` — knob mints but no
      family fill (first-come among squatters; lock/spine
      vacancies, 0 -> 3-6 frozen contenders); ``moderate`` — no
      minting, only w_read doubling of an already-family-stable
      squatter; ``low`` otherwise.
    - churn: ``mitigating`` — the knob is the growth carrier
      (family floor collapses, 0.074 vs 0.564; principle #7: the
      knob's sign flips with dG); ``starved`` — family-stable
      contenders exist but none survive the knob (b=1 nucleation
      cannot reach its partner at dwell 0.113).
    - starvation: ``moot`` for everything — nothing grows (fill
      0, partial 0.0008, persist rests on 1 event); the compile
      should refuse the operating point, not price it.

    Static arithmetic over the census + measured anchors; no
    kinetics are asserted here (tick-37 rule — the numbers come
    from contention_dg.out, pinned in tests).
    """
    dg = DEFAULT_DG if dg is None else dg
    regime, interpolated = regime_at(dg)
    vc = vacancy_contention(build, canon, strength, bond_fns)
    vacancies = {}
    for sp in sorted(vc):
        for site, contenders in sorted(vc[sp].items()):
            fam_stable = sorted(
                t for t, c in contenders.items()
                if "family" in c["stable_under"])
            s2_stable = sorted(
                t for t, c in contenders.items()
                if "s2" in c["stable_under"])
            minted = sorted(set(s2_stable) - set(fam_stable))
            fill_fam = [t for t in fam_stable
                        if "fill" in contenders[t]["classes"]]
            if not minted and not fam_stable:
                tier = "low"
            elif regime in ("frozen", "marginal"):
                if minted and fill_fam:
                    tier = "critical"
                elif minted:
                    tier = "high"
                elif any(contenders[t]["w_read"]
                         for t, c in contenders.items()
                         if t in fam_stable):
                    tier = "moderate"
                else:
                    tier = "low"
            elif regime == "churn":
                if s2_stable:
                    tier = "mitigating"
                elif fam_stable:
                    tier = "starved"
                else:
                    tier = "low"
            else:   # starvation
                tier = "moot"
            note = {
                "critical": "knob mints frozen contenders over a "
                            "family-stable fill (measured 0.904->0.412)",
                "high": "knob mints frozen contenders; no family fill "
                        "(first-come among squatters)",
                "moderate": "w_read doubling of an already-stable "
                            "squatter only",
                "mitigating": "knob is the growth carrier at this dG "
                              "(family floor 0.074 vs knob 0.564)",
                "starved": "family-only contenders: b=1 nucleation "
                           "starves at dwell 0.113",
                "moot": "nothing grows at this dG (fill 0, partial "
                        "0.0008) — refuse the operating point",
                "low": "no knob-sensitive stable contender",
            }[tier]
            vacancies.setdefault(sp, {})[site] = {
                "tier": tier,
                "family_stable": fam_stable,
                "s2_stable": s2_stable,
                "minted": minted,
                "note": note,
            }
    result = {
        "dg": dg,
        "regime": regime,
        "interpolated": interpolated,
        "knob_verdict": KNOB_VERDICTS[regime],
        "anchors": REGIME_ANCHORS[regime],
        "vacancies": vacancies,
        "boundary_notes": [
            "read-window axis: dG-2 arm MEASURED (DW9->VH arc; "+
            "evidence/2026-10-07-dg2win-l3vac, evidence/2026-10-08-*): "+
            "4x window tilts the split 367:131 (share 0.737) via a "+
            "vanishing-hazard ratchet (fill detach hazard 4.05e-7 -> "+
            "5.35e-9 by phase 2; forward-integrated share dev 0.0035 "+
            "held-out, 0.0254 fresh)",
            "MARGINAL tier is window-indexed in its honest form; "+
            "pricing severity at one fixed window (the check_d4 "+
            "default) is a labelled choice, not a silent default",
            "starvation persist rests on persist_n=1 (single event)",
            "L3@(2,2) (54/500) sits outside the tick-42 five-name "
            "census; priced as measured, not enumerated",
            "dg off the measured points 0.5/2/4/7 is nearest-regime "
            "pricing (interpolated=true)",
        ],
    }
    if regime == "marginal":
        # designs/011: the MARGINAL tier is window-indexed — emit the
        # measured/validated window curve with the pricing
        result["window_pricing"] = marginal_window_pricing()
    return result


# ---------- window-indexed MARGINAL pricing (designs/011) ----------

# VH-ratchet basis, quoted verbatim from the receipts (never asserted
# here — pins live in tests/test_window_pricing.py).  Fit arm: BUILD1
# Vp-missing, site (2,2), dG=2, s2, read grid 4x400*e^Gmc with Gmc
# 9.5, seeds [0,500) of the DW9/DW10/VH identity chain.  Hazards are
# PHASE-INDEXED on the fit grid: phase i covers the i-th quarter of
# the 4x window; the forward integration starts at the 1/4-window
# snapshot, so phases 2-4 are what it consumes.
VH_BASIS = {
    "arm": "BUILD1 Vp-missing, site (2,2), dG=2, s2, window grid "
           "w x 400 e^Gmc, Gmc 9.5",
    "sources": ["evidence/2026-10-08-vh-ratchet/run.out",
                "evidence/2026-10-07-dg2win-l3vac/run.out (DW9-DW11)",
                "evidence/2026-10-06-contention-dg (tick-43 anchors)"],
    "quarter": 400.0 * math.exp(9.5),   # one w1 window == grid quarter
    "lam": 0.00013237187264826007,      # pooled attach rate (fit)
    "p": {"D2T": 0.2624466571834993,    # pooled attach odds (fit)
           "L2": 0.24182076813655762,
           "O": 0.4957325746799431},
    "d_o": 2.689564148010662e-06,       # O churn (whole-window pool)
    "haz_d2t": {1: 4.04664078990303e-07, 2: 5.348122115210481e-09,
                 3: 0.0, 4: 1.0321999558539198e-09},
    "haz_l2": {1: 2.1705866990530424e-07, 2: 1.5280356180070675e-07,
                3: 6.806295950100927e-08, 4: 4.359141414272266e-08},
    "v0": [0.0, 0.448, 0.488, 0.064],   # 1/4-window snapshot (E,D2T,L2,O)
    "share_pred_w4_receipt": 0.7413549690850645,  # VH2/VH3 validated
    "homo_pi_receipt": 0.7123954307622163,        # window-blind
}                                                   # stationary

# Measured window curve on the fit seeds — window w means read time
# w x 400 e^Gmc.  The DW10 snapshot fracs 0.25/0.5/0.75 of the 4x
# window ARE the w1/w2/w3 read points; w4 is the DW9 terminal census.
WINDOW_MEASURED = {
    1: {"d2t": 232, "l2": 229,
        "source": "DW10 snap 0.25 == tick-43 s2_dg2 (232:229)"},
    2: {"d2t": 318, "l2": 174, "source": "DW10 snap 0.5"},
    3: {"d2t": 348, "l2": 146, "source": "DW10 snap 0.75"},
    4: {"d2t": 367, "l2": 131,
        "source": "DW9 terminal 367:131(:2)"},
}
FROZEN_QUOTE = {
    "persist": 0.826, "window": 4,
    "source": "DW11: frozen-squatter persistence is window-immune",
}

_WINDOW_TIERS = ((0.55, "contested"), (0.75, "ratchet-tilting"),
                 (None, "ratchet-tilted"))


def window_tier(share):
    """Label a fill share on the MARGINAL window curve.

    ``contested`` below 0.55 (the near-fair attach-coin regime — the
    fill is NOT reliable), ``ratchet-tilting`` 0.55-0.75 (the ratchet
    has engaged but the squatter holds 25-35%), ``ratchet-tilted``
    from 0.75 (fill-dominant).  The thresholds are labelled choices
    on a measured curve, not derived constants (designs/011)."""
    for bound, label in _WINDOW_TIERS:
        if bound is None or share < bound:
            return label
    return _WINDOW_TIERS[-1][1]


def _mat_mul(A, B):
    n = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(n))
             for j in range(n)] for i in range(n)]


def _expm4(Q, dt):
    """Matrix exponential — scaling-and-squaring + uniformization,
    pure python (the VH construction, tick 70; E starts at ZERO
    because the k=0 series term supplies e^{-mu h} I itself —
    starting from I doubles the identity component).  Validated
    against the 2-state closed form in tests."""
    n = len(Q)
    mu = max(-Q[i][i] for i in range(n))
    x = mu * dt
    m = 0
    while x > 0.25:
        x /= 2.0
        m += 1
    h = dt / (2 ** m)
    P = [[(1.0 + Q[i][i] / mu) if i == j else Q[i][j] / mu
          for j in range(n)] for i in range(n)]
    E = [[0.0] * n for _ in range(n)]
    term = math.exp(-mu * h)
    Pv = [[(1.0 if i == j else 0.0) for j in range(n)]
          for i in range(n)]   # P^k, starts at P^0 = I
    for k in range(0, 200):
        for i in range(n):
            for j in range(n):
                E[i][j] += term * Pv[i][j]
        if term < 1e-20 and k > mu * h + 20:
            break
        term = term * (mu * h) / (k + 1)
        Pv = _mat_mul(Pv, P)
    for _ in range(m):
        E = _mat_mul(E, E)
    for i in range(n):
        s = sum(E[i])
        assert abs(s - 1.0) < 1e-6, "expm row sum %.12f" % s
    return E


def _build_Q(d_d2t, d_l2):
    """The 4-state chain (E, D2T, L2, O): attach E->s at
    ``lam * p_s``; phase-dependent detach for the pair states;
    whole-window O churn."""
    b = VH_BASIS
    lam, p, d_o = b["lam"], b["p"], b["d_o"]
    return [
        [-lam, lam * p["D2T"], lam * p["L2"], lam * p["O"]],
        [d_d2t, -d_d2t, 0.0, 0.0],
        [d_l2, 0.0, -d_l2, 0.0],
        [d_o, 0.0, 0.0, -d_o],
    ]


def _vh_share(window_mult, haz_d2t=None):
    """Chain pair-share D2T/(D2T+L2) at read window ``window_mult``
    (multiples of 400 e^Gmc).  Integrates the fit-grid phases from
    the w1 snapshot: phase 2 covers w1->w2, phase 3 w2->w3, phase 4
    w3->w4; beyond w4 the LAST fit-phase hazards are held
    (extrapolation — designs/011 P3).  ``haz_d2t`` substitutes the
    D2T hazard table (sensitivity arms only — receipts stay
    authoritative in VH_BASIS)."""
    if window_mult < 1:
        raise ValueError("the chain starts at the w1 snapshot")
    if haz_d2t is None:
        haz_d2t = VH_BASIS["haz_d2t"]
    v = list(VH_BASIS["v0"])
    for step in range(int(round(window_mult)) - 1):
        phi = min(2 + step, 4)
        E = _expm4(_build_Q(haz_d2t[phi],
                            VH_BASIS["haz_l2"][phi]),
                   VH_BASIS["quarter"])
        v = [sum(v[i] * E[i][j] for i in range(4)) for j in range(4)]
    return v[1] / (v[1] + v[2])


def marginal_window_pricing(windows=(1, 2, 3, 4, 8)):
    """Window-indexed pricing for MARGINAL-regime fill-vs-squatter
    contention (designs/011 — the tick-72 honest form made concrete).

    Returns the measured window curve (quoted receipts), the chain
    values (validated at w4: receipt 0.74135, held-out dev 0.0035,
    fresh dev 0.0254), extrapolations beyond the fit grid (labelled),
    tier labels, and the frozen-class quote (a window can tilt a
    marginal vacancy but cannot repair first-come)."""
    out = {}
    for w in windows:
        rec = {"window_mult": w,
               "read_time": f"w x 400 e^Gmc at Gmc 9.5, dG 2"}
        if w in WINDOW_MEASURED:
            m = WINDOW_MEASURED[w]
            rec["measured_share"] = m["d2t"] / float(
                m["d2t"] + m["l2"])
            rec["measured_census"] = f"{m['d2t']}:{m['l2']}"
            rec["measured_source"] = m["source"]
        if w == 1:
            v0 = VH_BASIS["v0"]
            rec["chain_share"] = v0[1] / (v0[1] + v0[2])
            rec["chain_kind"] = ("snapshot init (fit range "
                                 "112:122 = 0.4787)")
        elif w <= 4:
            rec["chain_share"] = _vh_share(w)
            rec["chain_kind"] = ("fit-grid prediction (validated at "
                                 "w4: receipt 0.74135, held-out dev "
                                 "0.0035)")
        else:
            rec["chain_share"] = _vh_share(w)
            rec["chain_kind"] = "EXTRAPOLATED (phase-4 hazards held)"
            rec["hazard95_share"] = _vh_share(
                w, {1: VH_BASIS["haz_d2t"][1],
                    2: VH_BASIS["haz_d2t"][2],
                    3: 3.2763010789370227e-09,
                    4: 3.096599867561759e-09})
            rec["hazard95_source"] = (
                "Poisson-95 upper bounds on the late D2T hazards "
                "(VH1 receipt 3.28e-9 / 3.10e-9) — the extrapolation "
                "bracket, not a second prediction")
        best = rec.get("measured_share", rec["chain_share"])
        rec["tier"] = window_tier(best)
        out[str(w)] = rec
    return {
        "basis": "VH ratchet fit — see VH_BASIS sources (quoted "
                 "receipts, never asserted)",
        "windows": out,
        "frozen_class": FROZEN_QUOTE,
        "homo_stationary": VH_BASIS["homo_pi_receipt"],
        "note": "the read window is the third contention knob: the "
                "fill-vs-squatter split moves 0.503 (w1, contested) "
                "-> 0.737 (w4, tilted) while the FROZEN squatter "
                "class persists (0.826) — a window can tilt a "
                "marginal vacancy but cannot repair first-come",
    }


def check_d4(build, canon=None, *, lock_sites=None, strength=None,
             dg=None):
    """Emit-time off-channel census (d4).  WARNING severity: returns
    the report; never gates emission (designs/004 A3).  ``dg``
    selects the operating point the severity ranking is priced at
    (default DEFAULT_DG = 0.5, the protocol point)."""
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
    mispl = lock_misplacements(build, canon, strength)
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
        "lock_misplacements": mispl,
        "vacancy_contention": vacancy_contention(build, canon, strength),
        "contention_severity": contention_severity(
            build, dg=dg, canon=canon, strength=strength),
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
    for site, mis in sorted(report["lock_misplacements"].items()):
        for tile, ch in sorted(mis.items()):
            lines.append(
                f"  lock misplacement: {tile} at {site} "
                f"(bond {ch['bond']}, faces {ch['faces']}"
                + (", w-read channel — doubles under a "
                   "strength-reinforced lock read" if ch["w_read"]
                   else "")
                + ") — the misplaced-lock class measured dominant "
                  "under s2 (L2@3,3 67, L3@3,2 43, 82 Vp-arm of 500; "
                  "strength2.out K1/K2)")
    for sp, sites in sorted(report.get("vacancy_contention",
                                      {}).items()):
        for site, contenders in sorted(sites.items()):
            knob_sensitive = any(
                c["stable_under"] and (
                    "stack_partner" in c["classes"]
                    or any(cl.endswith("squatter") for cl in c["classes"]))
                for c in contenders.values())
            if not knob_sensitive:
                continue
            parts = []
            for tile, c in sorted(contenders.items()):
                if not c["stable_under"]:
                    continue
                bonds = "/".join(str(c["bond"][k])
                                 for k in sorted(c["bond"]))
                parts.append(f"{tile}({'/'.join(c['classes'])}, "
                             f"b {bonds}, stable "
                             f"{'/'.join(c['stable_under'])})")
            if not parts:
                continue
            lines.append(
                f"  vacancy contention ({sp}-missing) at {site}: "
                + "; ".join(parts)
                + " — price lock-reinforcement knobs against the WHOLE "
                  "set (measured s2 Vp-arm: fill 0.908 -> 0.406, "
                  "first-come among three stable contenders; "
                  "vacancy_bg.out VB1/VB3)")
    sev = report.get("contention_severity")
    if sev:
        lines.append(
            f"  contention severity at dG {sev['dg']} — regime "
            f"{sev['regime']}"
            + (" (interpolated: nearest measured regime)"
               if sev["interpolated"] else "")
            + f", lock-reinforcement knob verdict: "
              f"{sev['knob_verdict']}")
        for sp, sites in sorted(sev["vacancies"].items()):
            for site, s in sorted(sites.items()):
                if s["tier"] in ("low",):
                    continue
                lines.append(
                    f"    {sp}-missing @{site}: tier {s['tier']} — "
                    f"minted {','.join(s['minted']) or '-'} over "
                    f"family-stable {','.join(s['family_stable']) or '-'}; "
                    f"{s['note']}")
    wp = sev.get("window_pricing") if sev else None
    if wp:
        curve = " -> ".join(
            f"w{k} " + format(
                v.get("measured_share", v["chain_share"]), ".3f")
            for k, v in sorted(wp["windows"].items(),
                               key=lambda kv: int(kv[0])))
        lines.append(
            "    window pricing (MARGINAL): fill share " + curve
            + f" (frozen class window-immune "
              f"{wp['frozen_class']['persist']}) — pick the read "
              "window against this curve, not by default")
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
    if scope not in ("row", "class"):
        raise ValueError(
            f"lock_glue_scope must be 'family', 'row' or 'class', "
            f"got {scope!r}")
    if canon is None:
        canon = canonical_assembly(build)
    new = copy.deepcopy(build)
    tiles = new["tiles"]

    def value_family(g):
        return g.endswith(SHARED_VALUE_SUFFIXES)

    def class_extra(g):
        # 'class' (tick 35) extends the row rule to the glue classes
        # row never qualified — the designs/004 boundary (go* spine
        # entries, and*/base/w* relays) — with the strength-2 spine
        # self-relays exempt (designs/002: strength-1 spines attach
        # nothing in row 1 at tau=2).  Value bonds keep EXACTLY the
        # row treatment, so 'class' is row plus the class-glue
        # renames and nothing else.
        return (not value_family(g)) and (not g.startswith("SP"))

    renames = []
    for (x, y) in sorted(canon):
        t = canon[(x, y)]
        east = canon.get((x + 1, y))
        if east is not None:
            g = tiles[t].get("E")
            e_rule = east.startswith("L") and value_family(g)
            c_rule = scope == "class" and class_extra(g)
            if g and g == tiles[east].get("W") and (e_rule or c_rule):
                ng = f"{g}-lk{y}"
                renames += [(t, "E", ng), (east, "W", ng)]
        north = canon.get((x, y + 1))
        if north is not None:
            g = tiles[t].get("N")
            n_rule = value_family(g) or (
                scope == "class" and class_extra(g))
            if g and g == tiles[north].get("S") and n_rule:
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
    class_build = apply_lock_glue_scope(build, "class", canon)
    fam_rep = check_d4(build, canon)
    row_rep = check_d4(row_build, canon)
    class_rep = check_d4(class_build, canon)

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
        "class": class_rep,
        "row_build": row_build,
        "class_build": class_build,
        "repair_bonds": {
            "family": repair_bonds(build), "row": repair_bonds(row_build),
            "class": repair_bonds(class_build)},
    }


# ---------- glue-CLASS boundary (designs/004, tick 35) ------------------


def glue_class(g):
    """Classify a glue name (``-lk{i}`` scope tags stripped): the
    shared value families — the repairability/squattability currency
    (R3b, R4) — vs the structural classes (spine, go* entries,
    and*/base relays, one-off caps/relays) that the row rule never
    qualified: the designs/004 glue-CLASS boundary."""
    import re
    base = re.sub(r"-lk\d+$", "", g)
    if base.endswith(SHARED_VALUE_SUFFIXES):
        return "value"
    if base.startswith("SP"):
        return "spine"
    if base.startswith("go"):
        return "go"
    if base.startswith("and"):
        return "and"
    if base.startswith("base") or base.startswith("vb"):
        return "base"
    if base.startswith("f-"):
        return "fact"
    if base.endswith("-relay"):
        return "relay"
    return "cap"


def glue_class_census(build, canon=None):
    """Enumerate every glue's users (tile faces + seed slots) and
    classify each as ``canonical_pair`` / ``seed_bond`` /
    ``inert_single`` / ``shared``.

    A non-value glue that is canonical_pair-exclusive cannot host
    an off-channel channel: a scope rename touches exactly its two
    canonical faces, and no third use exists to split.  This census
    is the machine check that the glue-CLASS boundary is inert for
    a given inventory — run it on every new build family.  A
    ``shared`` non-value glue is the honest boundary where the
    ``class`` scope starts to bite (tick 35: none exists in
    BUILD1/2/3 — the census receipt pins it)."""
    if canon is None:
        canon = canonical_assembly(build)
    users = {}
    for t, faces in sorted(build["tiles"].items()):
        for face, g in sorted(faces.items()):
            if g:
                users.setdefault(g, []).append(f"{t}.{face}")
    for slot, g in sorted(build["seed"].items()):
        users.setdefault(g, []).append(f"seed{slot[0]}")
    canon_pairs = set()
    for (x, y) in sorted(canon):
        t = canon[(x, y)]
        east = canon.get((x + 1, y))
        if east is not None:
            canon_pairs.add(frozenset((f"{t}.E", f"{east}.W")))
        north = canon.get((x, y + 1))
        if north is not None:
            canon_pairs.add(frozenset((f"{t}.N", f"{north}.S")))
    out = {}
    for g, ulist in sorted(users.items()):
        faces = [u for u in ulist if not u.startswith("seed")]
        seeds = [u for u in ulist if u.startswith("seed")]
        status = "shared"
        if len(ulist) == 1:
            status = "inert_single"
        elif len(faces) == 2 and not seeds and any(
                frozenset(faces) == p for p in canon_pairs):
            status = "canonical_pair"
        elif len(faces) == 1 and len(seeds) == 1:
            status = "seed_bond"
        out[g] = {"class": glue_class(g), "users": sorted(ulist),
                  "status": status}
    return out


def scope_bond_identity(build, scope_a, scope_b, canon=None):
    """Exact matching-predicate comparison of two scoped builds:
    for every opposing tile-face pair in the inventory (plus every
    tile S-face vs seed slot), the bond strength under ``scope_a``
    vs ``scope_b``.

    kTAM/aTAM dynamics depend only on this predicate and the bond
    strengths, so an EMPTY diff proves the two scopes are
    kinetically identical for that inventory — the machine form of
    "the class boundary is inert" (tick 35).  Unlike a sampled
    channel census this enumeration is complete, so no Monte Carlo
    is needed to decide it."""
    if canon is None:
        canon = canonical_assembly(build)
    a = apply_lock_glue_scope(build, scope_a, canon)
    b = apply_lock_glue_scope(build, scope_b, canon)
    diff = {}
    for t1 in sorted(a["tiles"]):
        for f1 in ("N", "S", "E", "W"):
            for t2 in sorted(a["tiles"]):
                if t1 == t2:
                    continue
                f2 = OPPOSITE[f1]
                sa = glue_strength(a["tiles"][t1].get(f1),
                                   a["tiles"][t2].get(f2))
                sb = glue_strength(b["tiles"][t1].get(f1),
                                   b["tiles"][t2].get(f2))
                if sa != sb:
                    diff[f"{t1}.{f1}<->{t2}.{f2}"] = [sa, sb]
    for t in sorted(a["tiles"]):
        for slot, gs in sorted(a["seed"].items()):
            sa = glue_strength(a["tiles"][t].get("S"), gs)
            sb = glue_strength(b["tiles"][t].get("S"),
                               b["seed"].get(slot))
            if sa != sb:
                diff[f"{t}.S<->seed{slot[0]}"] = [sa, sb]
    return diff
