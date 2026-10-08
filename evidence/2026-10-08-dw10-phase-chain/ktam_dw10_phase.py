#!/usr/bin/env python3
"""DW10 time-inhomogeneous chain falsifier (tick 69, SON-4869) —
executes the falsifier candidate named by tick 68's collection note
(research-log/2026-10-08-dw9-compounding-chain.md S5/post-hoc):

  "Next falsifier candidate: time-inhomogeneous chain per window
   phase, to be pre-registered before running."

Hypothesis under test (H_TI): the SITE occupancy chain is
time-inhomogeneous across the read window — effective rates drift by
window phase — and that drift accounts for the residual by which the
homogeneous stationary pi_pair (0.697-0.712, DW9 post-hoc) undershoots
the measured terminal shares (held-out 0.737, fresh 0.716).

Protocol of record is VERBATIM DW9 (ktam_dw9_compound.py), which is
VERBATIM tick 47/63: BUILD1 Vp-missing, Gmc=9.5, gse=Gmc-dG=7.5,
s2 lock-read arithmetic (matched_s2 doubling), canonical map from
the FULL build, stability checked on every event, read window
4x400*e^Gmc at dG=2.  run_traj below is DW9's function unchanged —
same seeds, same RNG stream, so the 1000 trajectories reproduce the
DW9 logs exactly; CAL proves instrument identity.  All new science
is in the analysis, not the simulation.

Phase split: quartiles of t_read.  phi in {1,2,3,4}, boundary
t_read*phi/4.  Per-phase chain: attach counts, detach counts and
occupancy time attributed by event/split time; a spell crossing a
phase boundary splits its time between phases.

PRE-REGISTERED gates (frozen before submission; machine verdicts on
the final VERDICTS line):
  CAL instrument identity: pooled terminal census over i in [0,500)
      must be EXACTLY D2T 367 : L2 131 (DW9 receipt).  [any mismatch
      -> CAL_FAIL and every TI verdict VOID]
  TI1 rate-drift detection: fit per-phase stationary shares
      pi_pair^phi on the fit range [0,250).  Spread = max-min over
      the four phases.  CONFIRMED if spread >= 0.03 (drift large
      enough to explain the ~0.03 residual);  FALSIFIED if spread
      < 0.015;  middle INCONCLUSIVE.  [any phase with < 20 attach
      or detach counts for D2T or L2 -> NO_FIT]
  TI2 late-phase governance: fit the late-half chain (phases 3+4
      pooled) on [0,250), predict the held-out [250,500) terminal
      share from its stationary pi_pair^late.  CONFIRMED if
      |pi_pair^late - share| <= 0.05 (CC1's band, for
      comparability);  FALSIFIED if > 0.05.  [fit counts < 20 per
      species NO_FIT; held-out pair terminals < 50 NO_EVENTS]
  TI3 snapshot-share trend: over orig [0,500), pair occupancy share
      at snapshot times t_read/4 and 3*t_read/4.  CONFIRMED if
      |share(3/4) - share(1/4)| >= 0.03 (the occupancy share still
      moves across the window);  FALSIFIED if < 0.015;  middle
      INCONCLUSIVE.

Interpretation map (recorded in the note, NOT in the machine):
  TI1 CONFIRMED + TI2 CONFIRMED -> phase drift governs the terminal
      census; time-inhomogeneity accounts for the DW9 residual.
  TI1 FALSIFIED + TI3 CONFIRMED -> homogeneous rates, moving
      occupancy share: initialization/slow-mixing account.
  TI1 FALSIFIED + TI3 FALSIFIED + TI2 CONFIRMED -> homogeneous
      stationary chain already governs; DW9's failure was entirely
      the frozen-survivor mixture component.
  TI1 FALSIFIED + TI2 FALSIFIED -> neither phase drift nor the
      homogeneous stationary share predicts the terminal census;
      mechanism search reopens (next candidate: terminal-vs-
      occupancy conditioning, since 'terminal' is any tile present
      at t_read while pi weights occupancy time).

Descriptive (labelled, no gates): per-phase per-roll pair odds,
per-phase dwell ratio, homogeneous full-window and fit-range
pi_pair (reproduces DW9's 0.697-0.712), |dev_late| vs |dev_homo|
on the held-out range, snapshot shares at all four quartile times.

SMOKE=1 runs n=8 per range (instrument check only; CAL skipped —
gates stay verbatim per the tick-43 lesson).
"""
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SIB_AND = os.path.join(os.path.dirname(HERE),
                       "2026-10-06-body-conjunction-builds")
SIB_DEATH = os.path.join(os.path.dirname(HERE),
                         "2026-10-06-structural-death")
for p in (HERE, REPO, SIB_AND, SIB_DEATH):
    if p not in sys.path:
        sys.path.insert(0, p)

from tiles_and import BUILD1                          # noqa: E402
from tiles_death import build_missing_species         # noqa: E402
from molasp.offchannel import (canonical_assembly,    # noqa: E402
                               matched_strength)

GMC = 9.5
BASE_SEED = 220261107
SEED_STRIDE = 20000000
ARM_IDX = 2                    # tick-63 s2_dg2_win4 (DW9 layout)
SEED0 = BASE_SEED + ARM_IDX * SEED_STRIDE
N_PER_RANGE = 8 if os.environ.get("SMOKE") else 500
DG = 2.0
WIN_MULT = 4.0
SITE = (2, 2)                  # the Vp vacancy: fill/substitution site
FACE_DIR = {"E": (1, 0), "N": (0, 1), "S": (0, -1), "W": (-1, 0)}
CAL_D2T = 367
CAL_L2 = 131
N_PHASES = 4
DRIFT_BAND = 0.03
DRIFT_FLOOR = 0.015
BAND = 0.05
MIN_EVENTS = 50
MIN_FIT = 20


def matched_s2(build, asm, site, tile_name):
    """Family matched strength with the lock-read bond doubled
    (verbatim tick-38/41/43/DW9 arithmetic)."""
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


def run_traj(build, matched, canon, seed, dg, win_mult):
    """One trajectory, protocol of record — VERBATIM DW9 run_traj
    (hence verbatim tick-47/63) with DW9's passive SITE occupancy
    log.  RNG stream unchanged from DW9."""
    rng = random.Random(seed)
    rf = math.exp(-GMC)
    gse = GMC - dg
    t_read = win_mult * 400.0 * math.exp(GMC)
    assembly = dict((s, "seed") for s in build["seed"])
    sites = sorted(canon)
    t = 0.0
    churn = 0
    first_stable = None
    persists = None
    prev = assembly.get(SITE)
    log = []
    dwell_open = None
    dwell = 0.0
    l3_episode = False
    while True:
        events = []
        for site in sites:
            if site in assembly:
                b = matched(build, assembly, site, assembly[site])
                events.append((math.exp(-b * gse), "detach", site))
            elif any((site[0] + dx, site[1] + dy) in assembly
                     for dx, dy in FACE_DIR.values()):
                for tile in build["tiles"]:
                    if matched(build, assembly, site, tile) >= 1:
                        events.append((rf, "attach", (site, tile)))
        total = sum(r for r, _, _ in events)
        if total <= 0 or t > t_read:
            break
        t_next = t + rng.expovariate(total)
        if t_next > t_read:
            if dwell_open is not None:
                dwell += t_read - dwell_open
                dwell_open = None
            t = t_read
            break
        t = t_next
        r = rng.random() * total
        acc = 0.0
        for rate, kind, arg in events:
            acc += rate
            if acc >= r:
                if kind == "attach":
                    assembly[arg[0]] = arg[1]
                else:
                    del assembly[arg]
                break
        occ = assembly.get(SITE)
        if occ != prev:
            churn += 1
            log.append((t, prev, occ))
            prev = occ
        if occ is not None and first_stable is None and matched(
                build, assembly, SITE, occ) >= 2:
            first_stable = occ
        if first_stable is not None and persists is None:
            if occ is None or occ != first_stable:
                persists = False
        if occ is not None and dwell_open is None:
            dwell_open = t
        elif occ is None and dwell_open is not None:
            dwell += t - dwell_open
            dwell_open = None
        if (not l3_episode and occ == "L3" and matched(
                build, assembly, SITE, "L3") >= 2):
            l3_episode = True
    if dwell_open is not None:
        dwell += t_read - dwell_open
    if persists is None and first_stable is not None:
        persists = True
    l3_terminal = False
    toc = assembly.get(SITE)
    if toc == "L3" and matched(build, assembly, SITE, "L3") >= 2:
        l3_terminal = True
    return {"terminal": toc, "churn": churn,
            "first_stable": first_stable, "persists": persists,
            "dwell": dwell, "t_read": t_read, "log": log,
            "l3_episode": l3_episode, "l3_terminal": l3_terminal}


def phase_of(t, t_read):
    """1-based phase index in [1, N_PHASES]."""
    p = int(min(N_PHASES - 1, (t / t_read) * N_PHASES)) + 1
    return max(1, p)


def phase_chain_fit(trajs, phase_lo=None, phase_hi=None):
    """Aggregate CTMC rate fit over a phase window (inclusive bounds,
    None = open).  Spells crossing a phase boundary split their
    occupancy time; attach/detach events attribute by event time.
    Returns fitted pi_pair etc., or {'ok': False, 'reason': ...}."""
    t_read = trajs[0]["t_read"]
    in_win = lambda p: ((phase_lo is None or p >= phase_lo) and
                        (phase_hi is None or p <= phase_hi))
    att = Counter()
    det = Counter()
    occ_t = defaultdict(float)
    for tr in trajs:
        state = None
        open_s = None
        open_t = 0.0
        for (t, frm, to) in tr["log"]:
            if frm != state:
                return {"ok": False, "reason": "log_inconsistent"}
            # attribute the closing spell fragment to phases
            if state is not None:
                seg_lo = open_t
                for (tt, _f, _o) in [(t, None, None)]:
                    seg_hi = tt
                p_a = phase_of(seg_lo, t_read)
                p_b = phase_of(seg_hi, t_read)
                for p in range(p_a, p_b + 1):
                    if not in_win(p):
                        continue
                    b_lo = max(seg_lo, t_read * (p - 1) / N_PHASES)
                    b_hi = min(seg_hi, t_read * p / N_PHASES)
                    if b_hi > b_lo:
                        occ_t[state] += b_hi - b_lo
            if state is None and to is not None:
                if in_win(phase_of(t, t_read)):
                    att[str(to)] += 1
                open_s = str(to)
                open_t = t
            elif state is not None and to is None:
                if in_win(phase_of(t, t_read)):
                    det[state] += 1
                open_s = None
            elif state is None and to is None:
                return {"ok": False, "reason": "log_null_change"}
            else:
                return {"ok": False, "reason": "log_direct_swap"}
            state = to
        if state is not None:
            p_a = phase_of(open_t, t_read)
            for p in range(p_a, N_PHASES + 1):
                if not in_win(p):
                    continue
                b_lo = max(open_t, t_read * (p - 1) / N_PHASES)
                b_hi = min(t_read, t_read * p / N_PHASES)
                if b_hi > b_lo:
                    occ_t[str(state)] += b_hi - b_lo
    total_att = sum(att.values())
    if total_att == 0:
        return {"ok": False, "reason": "no_attach_events"}
    if min(att["D2T"], att["L2"], det["D2T"], det["L2"]) < MIN_FIT:
        return {"ok": False, "reason": "fit_counts_below_min",
                "att_D2T": att["D2T"], "att_L2": att["L2"],
                "det_D2T": det["D2T"], "det_L2": det["L2"]}
    if occ_t["D2T"] <= 0 or occ_t["L2"] <= 0:
        return {"ok": False, "reason": "zero_occupancy"}
    p = {"D2T": att["D2T"] / total_att, "L2": att["L2"] / total_att,
         "other": (total_att - att["D2T"] - att["L2"]) / total_att}
    d = {"D2T": det["D2T"] / occ_t["D2T"],
         "L2": det["L2"] / occ_t["L2"]}
    x = {"D2T": p["D2T"] / d["D2T"], "L2": p["L2"] / d["L2"]}
    pi_pair = x["D2T"] / (x["D2T"] + x["L2"])
    return {"ok": True, "p": p, "d": d, "pi_pair": pi_pair,
            "att": dict(att), "det": dict(det),
            "mean_spell_D2T": occ_t["D2T"] / det["D2T"],
            "mean_spell_L2": occ_t["L2"] / det["L2"],
            "per_roll_pair_odds":
                att["D2T"] / float(att["D2T"] + att["L2"])}


def state_at(tr, t_star):
    """SITE occupancy at time t_star from the passive log
    (None before the first event)."""
    state = None
    for (t, _frm, to) in tr["log"]:
        if t <= t_star:
            state = to
        else:
            break
    return state


def snapshot_pair_share(trajs, frac):
    t_star = trajs[0]["t_read"] * frac
    d2t = sum(1 for tr in trajs if state_at(tr, t_star) == "D2T")
    l2 = sum(1 for tr in trajs if state_at(tr, t_star) == "L2")
    share = d2t / float(d2t + l2) if d2t + l2 else None
    return {"frac": frac, "D2T": d2t, "L2": l2, "share": share}


def terminal_share(trajs):
    d2t = sum(1 for tr in trajs if tr["terminal"] == "D2T")
    l2 = sum(1 for tr in trajs if tr["terminal"] == "L2")
    other = len(trajs) - d2t - l2
    share = d2t / float(d2t + l2) if d2t + l2 else None
    return {"D2T": d2t, "L2": l2, "other": other, "share": share}


def main():
    b1v = build_missing_species(BUILD1, "Vp")
    canon = canonical_assembly(BUILD1)
    trajs = []
    for i in range(2 * N_PER_RANGE):
        trajs.append(run_traj(b1v, matched_s2, canon,
                              SEED0 + i, DG, WIN_MULT))
    orig = trajs[:N_PER_RANGE]
    fresh = trajs[N_PER_RANGE:]
    half = N_PER_RANGE // 2
    fit_range = orig[:half]
    held = orig[half:]

    # CAL — instrument identity (DW9 receipt)
    sh_orig = terminal_share(orig)
    cal = ("CAL_OK" if (N_PER_RANGE != 500 or
                        (sh_orig["D2T"] == CAL_D2T and
                         sh_orig["L2"] == CAL_L2)) else "CAL_FAIL")

    # TI1 — per-phase drift on the fit range
    phase_fits = {}
    ti1_fit_ok = True
    for phi in range(1, N_PHASES + 1):
        f = phase_chain_fit(fit_range, phase_lo=phi, phase_hi=phi)
        phase_fits[phi] = f
        if not f.get("ok"):
            ti1_fit_ok = False
    if not ti1_fit_ok:
        ti1 = "NO_FIT"
        spread = None
    else:
        pis = [phase_fits[p]["pi_pair"] for p in phase_fits]
        spread = max(pis) - min(pis)
        ti1 = ("CONFIRMED" if spread >= DRIFT_BAND else
               "FALSIFIED" if spread < DRIFT_FLOOR else "INCONCLUSIVE")

    # TI2 — late-half chain predicts held-out terminal share
    sh_held = terminal_share(held)
    late = phase_chain_fit(fit_range, phase_lo=3, phase_hi=4)
    homo = phase_chain_fit(fit_range)  # all phases (homogeneous)
    if not late.get("ok"):
        ti2 = "NO_FIT"
        dev_late = None
    elif sh_held["D2T"] + sh_held["L2"] < MIN_EVENTS:
        ti2 = "NO_EVENTS"
        dev_late = None
    else:
        dev_late = abs(late["pi_pair"] - sh_held["share"])
        ti2 = "CONFIRMED" if dev_late <= BAND else "FALSIFIED"
    dev_homo = (abs(homo["pi_pair"] - sh_held["share"])
                if homo.get("ok") and sh_held["share"] is not None
                else None)

    # TI3 — snapshot-share trend across the window (orig range)
    snaps = {frac: snapshot_pair_share(orig, frac)
             for frac in (0.25, 0.5, 0.75)}
    s14, s34 = snaps[0.25], snaps[0.75]
    if s14["share"] is None or s34["share"] is None:
        ti3 = "NO_EVENTS"
        snap_delta = None
    else:
        snap_delta = abs(s34["share"] - s14["share"])
        ti3 = ("CONFIRMED" if snap_delta >= DRIFT_BAND else
               "FALSIFIED" if snap_delta < DRIFT_FLOOR
               else "INCONCLUSIVE")

    if cal != "CAL_OK":
        ti1 = ti2 = ti3 = "VOID"

    out = {
        "n_per_range": N_PER_RANGE, "seed0": SEED0,
        "dg": DG, "win_mult": WIN_MULT, "n_phases": N_PHASES,
        "orig_terminal": sh_orig, "heldout_terminal": sh_held,
        "phase_fits": {str(p): phase_fits[p] for p in phase_fits},
        "ti1_spread": spread,
        "late_pi_pair": late.get("pi_pair"),
        "homo_pi_pair": homo.get("pi_pair"),
        "dev_late": dev_late, "dev_homo": dev_homo,
        "snapshots": {str(k): v for k, v in snaps.items()},
        "snapshot_delta_14_34": snap_delta,
        "fresh_terminal": terminal_share(fresh),
    }
    print(json.dumps(out))
    vs = {"CAL": cal, "TI1": ti1, "TI2": ti2, "TI3": ti3}
    print(json.dumps(vs))
    print("VERDICTS " + json.dumps(vs, sort_keys=True))


if __name__ == "__main__":
    main()
