"""kTAM history-aware mechanism study: the surviving stable b=2
recombination channel (tick 33, SON-4778).

Tick 31 falsified the row-scope elimination reading: under row
scope the read-block survives at 0.144 (Vp@(3,2) 72/500 via b=1
transients) and STABLE (b>=2) D2T repair of the Vp vacancy
survives at 0.162 over all terminals (family: 0.908).  The n=8
tick-30 smoke showed one mechanism — a D2T+Vp MUTUAL PAIR
(D2T's relay bond + an E-face pair with a Vp lock-squat)
reconstituting b=2 from two b=1 channels — but the tick-31 grid
had NO history, so the mechanism of the surviving channel is
open: cooperative recombination (a partner tile supplies the
second bond) vs solo holds (an intrinsic bond the static census
missed), and if cooperative, whether the partner is an
off-channel squatter (the smoke's mechanism transposed) or a
canonical neighbour bonded on a normally-unused face.

Instrument: the tick-23/24 protocol of record (Gse=9, Gmc=9.5,
T_read = 400*e^Gmc, no-mismatch kTAM, per-run RNG, deterministic
seeds).  Fresh seed base 100261107, stride 2e7 — disjoint from
the v2 grid block (20261107 + sys*1e7), vp-residual (40261107),
and row-scope (80261107) blocks.  Systems: BUILD1 x
{family,row} x {plain, Vp-missing}.  4 x 1000 = 4,000
trajectories at dG 0.5 only, with per-trajectory history: first
passages (D2T@(2,2); any non-L2 at (3,2); Vp@(3,2)), the
stabilization time t_stab (first moment D2T@(2,2) reaches
matched b >= 2) with its partner snapshot, cumulative stable
dwell, and read-time per-partner bond decomposition (partner
contribution = matched b minus b recomputed with that partner
removed).

Pre-registered BEFORE this MC runs (falsifiers in brackets).
"Stable hold" = D2T@(2,2) present at read with matched b >= 2.
"Load-bearing partner" = a co-resident neighbour whose removal
drops D2T@(2,2) below b=2.  "Non-canonical partner" = partner
tile != CANON[partner site] (off-channel squatter); a canonical
occupant bonded on a face the canonical assembly does not use
is "canonical-new-face".

H1 (row Vp-missing, cooperative): among read-time stable holds,
load-bearing-partner fraction (any partner) >= 0.8
    [<= 0.5 falsified: the row stable channel is solo/intrinsic,
    i.e. the static census under-counted row-live repair bonds;
    0.5-0.8 inconclusive].
H1b (family contrast): among family_Vp read-time stable holds,
load-bearing NON-canonical partner fraction <= 0.3
    [>= 0.6 falsified: family's stable repair is also squatter-
    mediated, so the recombination mechanism is not what row
    scope created; 0.3-0.6 inconclusive].
H1c (row, squatter mechanism): among row_Vp read-time stable
holds, load-bearing NON-canonical partner fraction >= 0.5
    [< 0.3 falsified: the row partner is a canonical-new-face
    relay, not the smoke's squatter mechanism; 0.3-0.5
    inconclusive — still cooperative, different partner].
H2 (nucleation order, row_Vp): among read-time stable holds
whose load-bearing non-canonical partner sits at (3,2), the
partner's first passage at (3,2) precedes D2T's first passage
at (2,2) in >= 0.5 of cases
    [<= 0.25 falsified: D2T seeds and the squatter completes;
    either order is recombination — the gate fixes the dominant
    direction for the write-up].
H3 (row build1, read-block pair): among read-time blocked
terminals, the fraction holding the mutual pair Vp@(3,2) AND
D2T@(2,2) with the pair link load-bearing (removing D2T@(2,2)
drops Vp@(3,2) to matched b = 0) is >= 0.7
    [<= 0.4 falsified: the row read-block is solo squatters,
    not the tick-32 mutual-pair class; 0.4-0.7 inconclusive].
H4 (calibration): row_build1 blocked frac within 0.05 of 0.144
AND row_Vp stable fill over all terminals within 0.05 of 0.162
AND family_build1 blocked frac within 0.05 of 0.27
    [any >= 0.10 off: protocol drift — stop interpreting].
    Secondary (reported, 0.10 tolerance): family_Vp stable fill
    vs 0.908.

Verdicts are machine-computed in the job's final line.
"""
import json
import math
import os
import random
import sys
from collections import Counter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SIB_AND = os.path.join(os.path.dirname(HERE),
                       "2026-10-06-body-conjunction-builds")
SIB_DEATH = os.path.join(os.path.dirname(HERE),
                         "2026-10-06-structural-death")
SIB_REPAIR = os.path.join(os.path.dirname(HERE),
                          "2026-10-07-repair-mechanism")
for p in (HERE, REPO, SIB_AND, SIB_DEATH, SIB_REPAIR):
    if p not in sys.path:
        sys.path.insert(0, p)

import trap_census  # noqa: E402
from tiles_and import BUILD1  # noqa: E402
from tiles_death import build_missing_species  # noqa: E402
from atam_check_and import matched_strength  # noqa: E402
from molasp.offchannel import apply_lock_glue_scope  # noqa: E402

GSE = 9.0
GMC = 9.5
BASE_SEED = 100261107
SEED_STRIDE = 20000000
N_PER_ARM = 1000
T_READ_MULTIPLIER = 400.0
CANON = dict(trap_census.CANON)
LOCK_SITES = ((3, 1), (3, 2), (3, 3))
SITES = sorted(CANON)
SITE_SET = set(SITES)
DIRS = {"E": (1, 0), "N": (0, 1), "S": (0, -1), "W": (-1, 0)}
VAC = (2, 2)          # Vp canonical site (the substitution vacancy)
LOCK32 = (3, 2)       # the lock Vp squats / east of the vacancy
READERS = {"p": ("D1T", (1, 1)), "q": ("D2T", (1, 2)),
           "r": ("DBr", (2, 3))}
REFS = {"row_build1_blocked": 0.144, "row_Vp_stable_fill": 0.162,
        "family_build1_blocked": 0.27, "family_Vp_stable_fill": 0.908}


class ArmAPI(object):
    def __init__(self, build, scope):
        self.build = build
        self.scope = scope
        name = build["name"]
        self.removed = (name.rsplit("_missing_", 1)[-1]
                        if "_missing_" in name else None)

    def tiles(self):
        return self.build["tiles"]

    def seed(self):
        return {(x, 0): "seed" + str(x) for x in range(4)}

    def sites(self):
        return SITES

    def matched(self, assembly, site, tile):
        return matched_strength(self.build, assembly, site, tile)

    def neighbour(self, assembly, site):
        return any((site[0] + dx, site[1] + dy) in assembly
                   for dx, dy in DIRS.values())

    def decode(self, assembly):
        # scope-aware (as tick 31): under row scope lock W glues
        # read "{atom}-t-lk{y}" — still the atom's TRUE family.
        b = self.build
        spined = all(assembly.get((0, r)) == "S%d" % r for r in (1, 2, 3))
        locks = [assembly.get((3, r)) for r in (1, 2, 3)]
        locked = all(l is not None and str(l).startswith("L")
                     for l in locks)
        if not spined or not locked:
            return "partial"
        true_atoms = []
        for y, atom in b["rows"].items():
            lock = assembly[(3, y)]
            if b["tiles"][lock]["W"].startswith(atom + "-t"):
                true_atoms.append(atom)
        return "".join(true_atoms) if true_atoms else "empty"

    def decode_loose(self, assembly):
        bits = "".join(atom for atom, (tile, site) in
                       sorted(READERS.items())
                       if assembly.get(site) == tile)
        return bits if bits else "empty"


def build_systems():
    systems = []
    for scope in ("family", "row"):
        base = apply_lock_glue_scope(BUILD1, scope)
        systems.append(ArmAPI(base, scope))
        systems.append(ArmAPI(build_missing_species(base, "Vp"), scope))
    return systems


SYSTEMS = build_systems()


def partner_bonds(api, assembly, site, tile):
    """Per-partner bond contributions for tile at site: matched b
    minus b recomputed with each co-resident neighbour removed."""
    b0 = api.matched(assembly, site, tile)
    out = {}
    for dname, (dx, dy) in DIRS.items():
        nb = (site[0] + dx, site[1] + dy)
        if nb in assembly and nb in SITE_SET:
            occ = assembly[nb]
            reduced = {k: v for k, v in assembly.items() if k != nb}
            b1 = api.matched(reduced, site, tile)
            if b0 - b1 > 0:
                out["%s@%d,%d:%s" % (dname, nb[0], nb[1], occ)] = {
                    "bond": b0 - b1,
                    "load_bearing": (b0 - (b0 - b1)) < 2,
                    "canonical": occ == CANON.get(nb),
                }
    return b0, out


def run_assembly_history(api, Gmc, Gse, T_read, seed):
    """Protocol of record + history.  Returns a dict with the
    read-time assembly plus first passages, t_stab with partner
    snapshot, and cumulative stable dwell for D2T@(2,2)."""
    rng = random.Random(seed)
    rf = math.exp(-Gmc)
    tiles = api.tiles()
    assembly = api.seed()
    sites = api.sites()
    t = 0.0
    t_first_d2t22 = None
    t_first_noncanon32 = None
    t_first_vp32 = None
    t_stab = None
    stab_partners = None
    stable_dwell = 0.0
    stable_open = None
    while True:
        events = []
        for site in sites:
            if site in assembly:
                b = api.matched(assembly, site, assembly[site])
                events.append((math.exp(-b * Gse), "detach", site))
            elif api.neighbour(assembly, site):
                for tile in tiles:
                    if api.matched(assembly, site, tile) >= 1:
                        events.append((rf, "attach", (site, tile)))
        total = sum(r for r, _, _ in events)
        if total <= 0 or t > T_read:
            break
        t += rng.expovariate(total)
        if t > T_read:
            break
        r = rng.random() * total
        acc = 0.0
        for rate, kind, arg in events:
            acc += rate
            if acc >= r:
                if kind == "attach":
                    assembly[arg[0]] = arg[1]
                    if arg[0] == VAC and arg[1] == "D2T" and \
                            t_first_d2t22 is None:
                        t_first_d2t22 = t
                    if arg[0] == LOCK32 and arg[1] != CANON[LOCK32]:
                        if t_first_noncanon32 is None:
                            t_first_noncanon32 = t
                        if arg[1] == "Vp" and t_first_vp32 is None:
                            t_first_vp32 = t
                else:
                    del assembly[arg]
                break
        # stability bookkeeping for D2T@(2,2)
        if assembly.get(VAC) == "D2T":
            b = api.matched(assembly, VAC, "D2T")
            if b >= 2:
                if t_stab is None:
                    t_stab = t
                    _, stab_partners = partner_bonds(api, assembly,
                                                     VAC, "D2T")
                if stable_open is None:
                    stable_open = t
            elif stable_open is not None:
                stable_dwell += t - stable_open
                stable_open = None
        elif stable_open is not None:
            stable_dwell += t - stable_open
            stable_open = None
    now = t if t < T_read else T_read
    if stable_open is not None:
        stable_dwell += now - stable_open
    return {
        "assembly": assembly,
        "t_first_d2t22": t_first_d2t22,
        "t_first_noncanon32": t_first_noncanon32,
        "t_first_vp32": t_first_vp32,
        "t_stab": t_stab,
        "stab_partners": stab_partners,
        "stable_dwell": stable_dwell,
        "T_read": T_read,
    }


def read_lock_squats(assembly):
    blocked = False
    ctr = Counter()
    for site in LOCK_SITES:
        occ = assembly.get(site)
        if occ is not None and occ != CANON[site]:
            blocked = True
            ctr["%d,%d:%s" % (site[0], site[1], occ)] += 1
    return blocked, ctr


def arm_chunk(args):
    sys_idx, seed0, n = args
    api = SYSTEMS[sys_idx]
    T_read = T_READ_MULTIPLIER * math.exp(GMC)
    outs = []
    for i in range(n):
        h = run_assembly_history(api, GMC, GSE, T_read, seed0 + i)
        asm = h["assembly"]
        strict = api.decode(asm)
        blocked, squats = read_lock_squats(asm)
        occ22 = asm.get(VAC)
        stable = occ22 == "D2T" and api.matched(asm, VAC, "D2T") >= 2
        b22, partners = (partner_bonds(api, asm, VAC, "D2T")
                         if occ22 == "D2T" else (None, None))
        # H3 pair link: Vp@(3,2) with D2T@(2,2) load-bearing for Vp
        pair_link = False
        if asm.get(LOCK32) == "Vp" and occ22 == "D2T":
            bvp = api.matched(asm, LOCK32, "Vp")
            reduced = {k: v for k, v in asm.items() if k != VAC}
            pair_link = bvp >= 1 and api.matched(
                reduced, LOCK32, "Vp") == 0
        outs.append({
            "strict": strict, "loose": api.decode_loose(asm),
            "blocked": blocked, "squats": dict(squats),
            "occ22": occ22, "stable": stable, "b22": b22,
            "partners": partners, "pair_link": pair_link,
            "t_first_d2t22": h["t_first_d2t22"],
            "t_first_noncanon32": h["t_first_noncanon32"],
            "t_first_vp32": h["t_first_vp32"],
            "t_stab": h["t_stab"],
            "stab_partners": h["stab_partners"],
            "stable_dwell": h["stable_dwell"],
        })
    return sys_idx, outs


def stable_cohort(outs):
    """Aggregate the read-time stable-hold cohort of one arm."""
    sel = [o for o in outs if o["stable"]]
    n_sel = len(sel)
    if not n_sel:
        return {"n": 0}
    lb_any = 0
    lb_noncanon = 0
    lb_canon_newface = 0
    partner_ctr = Counter()
    lb32_noncanon = 0
    order_partner_first = 0
    order_d2t_first = 0
    order_undef = 0
    t_stabs = []
    dwells = []
    b22_ctr = Counter()
    all_partner_ctr = Counter()
    b_ge3 = 0
    for o in sel:
        t_stabs.append(o["t_stab"])
        dwells.append(o["stable_dwell"])
        b22_ctr[o["b22"]] += 1
        if (o["b22"] or 0) >= 3:
            b_ge3 += 1
        ps = o["partners"] or {}
        for k, p in ps.items():
            all_partner_ctr["%s:%d" % (k, p["bond"])] += 1
        ps = o["partners"] or {}
        any_lb = any(p["load_bearing"] for p in ps.values())
        noncanon_lb = any(p["load_bearing"] and not p["canonical"]
                          for p in ps.values())
        canon_lb = any(p["load_bearing"] and p["canonical"]
                       for p in ps.values())
        if any_lb:
            lb_any += 1
        if noncanon_lb:
            lb_noncanon += 1
        if canon_lb and not noncanon_lb:
            lb_canon_newface += 1
        for k, p in ps.items():
            if p["load_bearing"]:
                partner_ctr[k] += 1
        o32 = [p for k, p in ps.items()
               if "@3,2:" in k and p["load_bearing"] and
               not p["canonical"]]
        if o32:
            lb32_noncanon += 1
            tp = o["t_first_noncanon32"]
            td = o["t_first_d2t22"]
            if tp is not None and td is not None:
                if tp < td:
                    order_partner_first += 1
                else:
                    order_d2t_first += 1
            else:
                order_undef += 1
    nn = float(n_sel)
    # Reporting added after the n=8 smoke (gates unchanged): the
    # smoke produced a stable hold with NO load-bearing partner
    # (redundant b>=3 bonds), which is uninterpretable without
    # the full partner table and b histogram.
    return {
        "n": n_sel,
        "b22_hist": dict(sorted(b22_ctr.items())),
        "b_ge3_frac": round(b_ge3 / nn, 4),
        "all_partners": dict(sorted(all_partner_ctr.items())),
        "lb_any_frac": round(lb_any / nn, 4),
        "lb_noncanon_frac": round(lb_noncanon / nn, 4),
        "lb_canon_newface_only_frac": round(lb_canon_newface / nn, 4),
        "lb32_noncanon_n": lb32_noncanon,
        "order_partner_first": order_partner_first,
        "order_d2t_first": order_d2t_first,
        "order_undef": order_undef,
        "load_bearing_partners": dict(sorted(partner_ctr.items())),
        "mean_t_stab": (round(sum(t_stabs) / nn, 1) if t_stabs else
                        None),
        "mean_stable_dwell": (round(sum(dwells) / nn, 1)
                              if dwells else None),
    }


def main():
    smoke = len(sys.argv) > 1 and sys.argv[1] == "SMOKE"
    n = 8 if smoke else N_PER_ARM
    jobs = [(i, BASE_SEED + i * SEED_STRIDE, n)
            for i in range(len(SYSTEMS))]
    print(json.dumps({
        "Gse": GSE, "Gmc": GMC, "dGmc": round(GMC - GSE, 1),
        "T_read_rule": "400*exp(Gmc)", "n_per_arm": n,
        "seed_base": BASE_SEED, "seed_stride": SEED_STRIDE,
        "model": ("kTAM v3 no-mismatch + history (first passages, "
                  "t_stab + partner snapshot, stable dwell, "
                  "per-partner bond decomposition by neighbour "
                  "removal); systems = BUILD1 x {family,row} x "
                  "{plain, Vp-missing} at dG 0.5 only"),
        "predictions": [
            "H1 row_Vp stable holds load-bearing-partner (any) "
            "frac >= 0.8 [<= 0.5 falsified]",
            "H1b family_Vp stable holds load-bearing NON-canonical "
            "partner frac <= 0.3 [>= 0.6 falsified]",
            "H1c row_Vp stable holds load-bearing NON-canonical "
            "partner frac >= 0.5 [< 0.3 falsified]",
            "H2 row_Vp squatter-pair holds: partner-first passage "
            "at (3,2) before D2T@(2,2) in >= 0.5 [<= 0.25 "
            "falsified]",
            "H3 row_build1 blocked terminals holding the "
            "load-bearing Vp@(3,2)+D2T@(2,2) mutual pair >= 0.7 "
            "[<= 0.4 falsified]",
            "H4 row_build1 blocked within 0.05 of 0.144 AND row_Vp "
            "stable fill within 0.05 of 0.162 AND family_build1 "
            "blocked within 0.05 of 0.27 [any >= 0.10 off: "
            "protocol drift]"],
        "references": REFS,
    }), flush=True)
    with Pool(min(8, os.cpu_count() or 1)) as pool:
        results = pool.map(arm_chunk, jobs)
    rows = {}
    for sys_idx, outs in results:
        api = SYSTEMS[sys_idx]
        key = api.scope + "_" + (api.removed or "build1")
        nn = len(outs)
        strict = Counter(o["strict"] for o in outs)
        blocked = sum(1 for o in outs if o["blocked"])
        squat_ctr = Counter()
        occ22_ctr = Counter()
        stable_n = 0
        mutual_pairs = 0
        ever_d2t22 = 0
        ever_noncanon32 = 0
        ever_vp32 = 0
        vp32_read = 0
        for o in outs:
            squat_ctr.update(o["squats"])
            occ22_ctr[o["occ22"] or "None"] += 1
            if o["stable"]:
                stable_n += 1
            if o["pair_link"]:
                mutual_pairs += 1
            if o["t_first_d2t22"] is not None:
                ever_d2t22 += 1
            if o["t_first_noncanon32"] is not None:
                ever_noncanon32 += 1
            if o["t_first_vp32"] is not None:
                ever_vp32 += 1
        asm_vp32 = sum(1 for o in outs
                       if o["squats"].get("3,2:Vp"))
        row = {
            "system": api.build["name"], "key": key, "n": nn,
            "decode": dict(sorted(strict.items())),
            "pqr": strict.get("pqr", 0),
            "pqr_frac": round(strict.get("pqr", 0) / float(nn), 4),
            "blocked_frac": round(blocked / float(nn), 4),
            "lock_squats": dict(sorted(squat_ctr.items())),
            "occ22_read": dict(sorted(occ22_ctr.items())),
            "d2t22_stable_fill_all": round(stable_n / float(nn), 4),
            "mutual_pair_link_n": mutual_pairs,
            "mutual_pair_link_frac": round(mutual_pairs /
                                           float(nn), 4),
            "ever_d2t22_frac": round(ever_d2t22 / float(nn), 4),
            "ever_noncanon32_frac": round(ever_noncanon32 /
                                          float(nn), 4),
            "ever_vp32_frac": (round(ever_vp32 / float(nn), 4)
                               if ever_vp32 or "build1" in key
                               else None),
            "vp32_read_frac": (round(asm_vp32 / float(nn), 4)
                               if "build1" in key else None),
            "stable_cohort": stable_cohort(outs),
        }
        rows[key] = row
        print(json.dumps(row), flush=True)

    # ---- machine verdicts against the pre-registration -----------
    verdicts = {}
    sc = rows["row_Vp"]["stable_cohort"]
    if sc["n"]:
        verdicts["H1"] = {
            "n_stable": sc["n"], "lb_any_frac": sc["lb_any_frac"],
            "call": ("confirmed" if sc["lb_any_frac"] >= 0.8 else
                     "falsified" if sc["lb_any_frac"] <= 0.5 else
                     "inconclusive"),
        }
        verdicts["H1c"] = {
            "n_stable": sc["n"],
            "lb_noncanon_frac": sc["lb_noncanon_frac"],
            "call": ("confirmed" if sc["lb_noncanon_frac"] >= 0.5
                     else "falsified" if sc["lb_noncanon_frac"] < 0.3
                     else "inconclusive"),
        }
        ordn = (sc["order_partner_first"] + sc["order_d2t_first"] +
                sc["order_undef"])
        if ordn:
            pf = sc["order_partner_first"] / float(ordn)
            verdicts["H2"] = {
                "n_pair": sc["lb32_noncanon_n"],
                "partner_first_frac": round(pf, 4),
                "call": ("confirmed" if pf >= 0.5 else
                         "falsified" if pf <= 0.25 else
                         "inconclusive"),
            }
        else:
            verdicts["H2"] = {"n_pair": 0, "call": "no_events"}
    else:
        verdicts["H1"] = {"n_stable": 0, "call": "no_events"}
        verdicts["H1c"] = {"n_stable": 0, "call": "no_events"}
        verdicts["H2"] = {"n_pair": 0, "call": "no_events"}
    fc = rows["family_Vp"]["stable_cohort"]
    if fc["n"]:
        verdicts["H1b"] = {
            "n_stable": fc["n"],
            "lb_noncanon_frac": fc["lb_noncanon_frac"],
            "call": ("confirmed" if fc["lb_noncanon_frac"] <= 0.3
                     else "falsified" if fc["lb_noncanon_frac"] >= 0.6
                     else "inconclusive"),
        }
    else:
        verdicts["H1b"] = {"n_stable": 0, "call": "no_events"}
    rb_blocked = rows["row_build1"]["blocked_frac"]
    mp = rows["row_build1"]["mutual_pair_link_n"]
    if rb_blocked > 0:
        mpf = round(mp / float(rows["row_build1"]["n"]) / rb_blocked, 4)
        verdicts["H3"] = {
            "blocked_frac": rb_blocked,
            "mutual_pair_frac_of_blocked": mpf,
            "call": ("confirmed" if mpf >= 0.7 else
                     "falsified" if mpf <= 0.4 else "inconclusive"),
        }
    else:
        verdicts["H3"] = {"blocked_frac": 0.0, "call": "no_events"}
    devs = {
        "row_build1_blocked": round(
            abs(rb_blocked - REFS["row_build1_blocked"]), 4),
        "row_Vp_stable_fill": round(
            abs(rows["row_Vp"]["d2t22_stable_fill_all"] -
                REFS["row_Vp_stable_fill"]), 4),
        "family_build1_blocked": round(
            abs(rows["family_build1"]["blocked_frac"] -
                REFS["family_build1_blocked"]), 4),
    }
    verdicts["H4"] = {
        "deviations": devs,
        "family_Vp_stable_fill_dev": round(
            abs(rows["family_Vp"]["d2t22_stable_fill_all"] -
                REFS["family_Vp_stable_fill"]), 4),
        "call": ("calibrated" if max(devs.values()) < 0.05 else
                 "protocol_drift" if max(devs.values()) >= 0.10 else
                 "inconclusive"),
    }
    print("VERDICTS " + json.dumps(verdicts), flush=True)


if __name__ == "__main__":
    main()
