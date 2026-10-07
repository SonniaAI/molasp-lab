"""Static off-channel attachment census — repair-mechanism study
(tick 24, SON-4778).

Tick 23's survey left two mechanism questions open: (i) why do V0p
and Vp removals EXCEED build1 parity at dG 0.5 (1.25x / 1.53x), and
(ii) the L3-only falsifier channel (18/500 strict "pqr" with the
lock species absent). This file is the structural half: for build1
and each single-species-removal system, enumerate every
(site, tile) pair that bonds with b >= 1 against the CANONICAL
build1 assembly background (the removed species' own site held
vacant), excluding the canonical occupant. These are the
misincorporation channels the no-mismatch kTAM actually exposes at
rate k_f*e^-Gmc each.

Two censuses:
  * off_channel: single-site perturbation of the canonical
    background (the "who can squat where" table).
  * lock_deep_probe: for each lock site (3,y), also allow the WEST
    neighbour site to be re-occupied by any tile that bonds there
    (b >= 1) before testing lock-site channels — a bounded two-site
    search that catches channels needing one background
    substitution (the hand-derived Vp@(2,3) -> L2@(3,3) misread
    candidate for the L3-missing 18/500).

Machine-checked facts this census pins (tests/test_repair_mechanism.py):
  - build1: Vp squats at (2,1),(1,2),(3,2),(2,3); V0p at (3,1);
    D2T/DBr/L2 at (2,2); DBr at (1,2); L1 at (2,1).
  - D1T, DAr, L3, S1, S2, S3 have ZERO off-channel sites — their
    glues are unique to their own sites.
  - Spine sites (0,1..3) admit no squatter in any system.
  - L3-missing lock_deep_probe at (3,3): L2 bonds iff the west
    neighbour exposes a q-t value glue (Vp@(2,3)).

This is a measurement (exhaustive glue arithmetic), not a
prediction; the trajectory-level predictions it motivates are
pre-registered in ktam_mc_trap.py BEFORE that MC runs.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIB_AND = os.path.join(os.path.dirname(HERE),
                       "2026-10-06-body-conjunction-builds")
SIB_DEATH = os.path.join(os.path.dirname(HERE),
                         "2026-10-06-structural-death")
for p in (HERE, SIB_AND, SIB_DEATH):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_and import BUILD1  # noqa: E402
from tiles_death import build_missing_species  # noqa: E402
from atam_check_and import matched_strength  # noqa: E402

CANON = {
    (0, 1): "S1", (1, 1): "D1T", (2, 1): "V0p", (3, 1): "L1",
    (0, 2): "S2", (1, 2): "D2T", (2, 2): "Vp", (3, 2): "L2",
    (0, 3): "S3", (1, 3): "DAr", (2, 3): "DBr", (3, 3): "L3",
}
CANON_RSITE = {t: s for s, t in CANON.items()}
SITES_ORDER = sorted(CANON)
LOCKS = ((3, 1), (3, 2), (3, 3))
REMOVALS = ("Vp", "V0p", "D1T", "D2T", "DAr", "DBr", "L3")


def skey(site):
    return "%d,%d" % site


def background(build):
    """Canonical build1 assembly minus this system's vacancy."""
    bg = dict(CANON)
    name = build["name"]
    if "_missing_" in name:
        sp = name.rsplit("_missing_", 1)[-1]
        bg = {s: t for s, t in bg.items() if t != sp}
    return bg


def off_channel(build):
    bg = background(build)
    table = {}
    for site in SITES_ORDER:
        squatters = {}
        for tile in sorted(build["tiles"]):
            if tile == CANON[site]:
                continue
            b = matched_strength(build, bg, site, tile)
            if b >= 1:
                squatters[tile] = b
        if squatters:
            table[skey(site)] = squatters
    return table


def lock_deep_probe(build):
    """Channels at each lock site allowing one west-neighbour
    substitution in the background. Returns, per lock site, the map
    {west_substitute: {lock_tile: bond}} for bonds >= 1 that are NOT
    the canonical lock tile (or any channel when the canonical lock
    tile is absent from this system)."""
    bg0 = background(build)
    out = {}
    for lock in LOCKS:
        west = (lock[0] - 1, lock[1])
        west_canon = CANON[west]
        found = {}
        # west neighbour candidates: canonical occupant (if present
        # in this system) plus any tile bonding >= 1 at west in bg0
        west_options = []
        if west_canon in build["tiles"]:
            west_options.append(west_canon)
        for tile in sorted(build["tiles"]):
            if tile == west_canon:
                continue
            if matched_strength(build, bg0, west, tile) >= 1:
                west_options.append(tile)
        for wtile in west_options:
            bg = dict(bg0)
            bg[west] = wtile
            channels = {}
            for tile in sorted(build["tiles"]):
                if tile == CANON[lock]:
                    continue
                b = matched_strength(build, bg, lock, tile)
                if b >= 1:
                    channels[tile] = b
            if channels:
                found[wtile] = channels
        if found:
            out[skey(lock)] = found
    return out


def compute():
    systems = [("build1", BUILD1)]
    for sp in REMOVALS:
        systems.append((sp, build_missing_species(BUILD1, sp)))
    rows = {}
    for sp, build in systems:
        oc = off_channel(build)
        rows[sp] = {
            "off_channel": oc,
            "off_channel_sites_per_species": {
                tile: sorted(s for s, sq in oc.items() if tile in sq)
                for tile in sorted(build["tiles"])
                if any(tile in sq for sq in oc.values())
            },
            "lock_deep_probe": lock_deep_probe(build),
        }
    return {"canonical": {skey(s): t for s, t in CANON.items()},
            "systems": rows}


def main():
    report = compute()
    out = os.path.join(HERE, "trap_census.out")
    with open(out, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    print(json.dumps(report, indent=1, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
