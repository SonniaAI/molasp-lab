#!/usr/bin/env python3
"""DW9 compounding-chain falsifier (tick 68, SON-4867) — executes the
falsifier pre-registered in research-log/2026-10-08-dw9-window-tilt.md
S5, frozen before submission:

  "trajectory-level re-roll chain extraction at dG 2 — per-roll
   attach probabilities and per-incumbent persistence, fit on half
   the seeds — then predict the window-arm share analytically from
   the chain's stationary distribution on the held-out seeds. A
   prediction outside +/-0.05 of 0.737 refutes the compounding-chain
   account."

Protocol of record is VERBATIM tick 47/63 (ktam_dg2_window_l3.py):
BUILD1 Vp-missing, Gmc=9.5, gse=Gmc-dG=7.5, s2 lock-read arithmetic
(matched_s2 doubling), canonical map from the FULL build, stability
checked on every event, read window 4x400*e^Gmc at dG=2.  run_traj
below is that script's function with PASSIVE event logging added at
the existing churn hook — no RNG-order change, so the original 500
seeds reproduce the tick-63 trajectories exactly.

Seed layout: seed0 = 220261107 + 2*2e7 = 260261107 (tick-63 arm
index 2, s2_dg2_win4).  i in [0,500) = the exact tick-63 seeds
(fit half [0,250), held-out half [250,500)); i in [500,1000) are
fresh, never-run seeds inside the same reserved stride block.

Chain model (fit on event logs, species-aggregated at SITE):
  states {empty, D2T, L2, other}; empty->s at rate lambda*p_s,
  s->empty at rate d_s.  Stationary pi_s/pi_E = p_s/d_s, so
  pi_pair = x_D2T/(x_D2T+x_L2) with x_s = p_s/d_s (lambda cancels).
Freeze-mixture prediction (the S5 mechanism account: frozen
survivors + compounded re-rollers):
  P_mix = f*fs_pair + (1-f)*pi_pair
  f = first-stable persistence fraction on the fit range;
  fs_pair = D2T share among first-stable occupants in the pair.

PRE-REGISTERED gates (falsifiers in brackets; fixed before
submission; machine verdicts on the final VERDICTS line):
  CAL instrument identity: pooled terminal census over i in [0,500)
      must be EXACTLY D2T 367 : L2 131 (tick-63 receipt).  [any
      mismatch -> CAL_FAIL and every CC verdict VOID: the
      instrument is not the tick-63 instrument]
  CC1 registered falsifier: fit chain on seeds [0,250), predict
      held-out share on seeds [250,500).  CONFIRMED if
      |P_mix - share| <= 0.05  [> 0.05 FALSIFIED: the
      compounding-chain account does not explain the tilt;
      pair terminals < 50 NO_EVENTS; fit counts < 20 NO_FIT]
  CC2 out-of-sample generalization: refit on all 500 original
      seeds, predict the fresh-seed share [500,1000).  Same bands
      as CC1.
  CC3 fresh-seed replication of the DW9 number: |share_fresh -
      0.737| <= 0.05 CONFIRMED  [> 0.10 FALSIFIED: 0.737 is not a
      stable regime number; middle INCONCLUSIVE]

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
ARM_IDX = 2                    # tick-63 s2_dg2_win4
SEED0 = BASE_SEED + ARM_IDX * SEED_STRIDE
N_PER_RANGE = 8 if os.environ.get("SMOKE") else 500
DG = 2.0
WIN_MULT = 4.0
SITE = (2, 2)                  # the Vp vacancy: fill/substitution site
FACE_DIR = {"E": (1, 0), "N": (0, 1), "S": (0, -1), "W": (-1, 0)}
CAL_D2T = 367
CAL_L2 = 131
BAND = 0.05
FAR = 0.10
MIN_EVENTS = 50
MIN_FIT = 20


def matched_s2(build, asm, site, tile_name):
    """Family matched strength with the lock-read bond doubled
    (verbatim tick-38/41/43 arithmetic)."""
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
    """One trajectory, protocol of record — VERBATIM tick-47/63
    run_traj with one addition: `log` records every SITE occupancy
    change (t, from, to) at the existing churn hook.  Passive only;
    the RNG stream is unchanged."""
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


def chain_fit(trajs):
    """Aggregate CTMC rate fit over trajectory records (species-
    aggregated at SITE).  Returns fitted parameters + both
    predictions, or {'ok': False, 'reason': ...}."""
    att = Counter()
    det = Counter()
    occ_t = defaultdict(float)
    persist_n = 0
    persist_hit = 0
    fs_d2t = 0
    fs_pair = 0
    for tr in trajs:
        state = None
        open_s = None
        open_t = 0.0
        for (t, frm, to) in tr["log"]:
            if frm != state:
                return {"ok": False,
                        "reason": "log_inconsistent"}
            if state is None and to is not None:
                att[str(to)] += 1
                open_s = str(to)
                open_t = t
            elif state is not None and to is None:
                det[state] += 1
                occ_t[state] += t - open_t
                open_s = None
            elif state is None and to is None:
                return {"ok": False, "reason": "log_null_change"}
            else:
                return {"ok": False, "reason": "log_direct_swap"}
            state = to
        if state is not None:
            occ_t[str(state)] += tr["t_read"] - open_t
        if tr["first_stable"] is not None and tr["persists"] is not None:
            persist_n += 1
            if tr["persists"]:
                persist_hit += 1
            if tr["first_stable"] in ("D2T", "L2"):
                fs_pair += 1
                if tr["first_stable"] == "D2T":
                    fs_d2t += 1
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
    f = persist_hit / float(persist_n) if persist_n else None
    fs_share = fs_d2t / float(fs_pair) if fs_pair else None
    p_mix = (f * fs_share + (1.0 - f) * pi_pair
             if f is not None and fs_share is not None else None)
    return {"ok": True, "p": p, "d": d, "pi_pair": pi_pair,
            "f": f, "fs_pair_share": fs_share, "p_mix": p_mix,
            "att": dict(att), "det": dict(det),
            "mean_spell_D2T": occ_t["D2T"] / det["D2T"],
            "mean_spell_L2": occ_t["L2"] / det["L2"],
            "rolls_per_traj": total_att / float(len(trajs)),
            "per_roll_pair_odds": att["D2T"] / float(att["D2T"] +
                                                    att["L2"])}


def terminal_share(trajs):
    d2t = sum(1 for tr in trajs if tr["terminal"] == "D2T")
    l2 = sum(1 for tr in trajs if tr["terminal"] == "L2")
    other = len(trajs) - d2t - l2
    share = d2t / float(d2t + l2) if d2t + l2 else None
    return {"D2T": d2t, "L2": l2, "other": other, "share": share}


def predict_verdict(fit, sharerec):
    """One prediction-vs-measurement gate (CC1/CC2 shape)."""
    if not fit["ok"]:
        return "NO_FIT", fit.get("reason")
    if sharerec["D2T"] + sharerec["L2"] < MIN_EVENTS:
        return "NO_EVENTS", None
    dev = abs(fit["p_mix"] - sharerec["share"])
    return ("CONFIRMED" if dev <= BAND else "FALSIFIED"), round(dev, 4)


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
    fit_a = chain_fit(orig[:half])
    fit_b = chain_fit(orig)
    sh_held = terminal_share(orig[half:])
    sh_fresh = terminal_share(fresh)
    sh_orig = terminal_share(orig)
    cal = ("CAL_OK" if (N_PER_RANGE != 500 or
                        (sh_orig["D2T"] == CAL_D2T and
                         sh_orig["L2"] == CAL_L2)) else "CAL_FAIL")
    cc1, dev1 = predict_verdict(fit_a, sh_held)
    cc2, dev2 = predict_verdict(fit_b, sh_fresh)
    if cal != "CAL_OK":
        cc1 = cc2 = "VOID"
    if sh_fresh["D2T"] + sh_fresh["L2"] < MIN_EVENTS:
        cc3 = "NO_EVENTS"
    else:
        delta = abs(sh_fresh["share"] - 0.737)
        cc3 = ("CONFIRMED" if delta <= BAND else
               "FALSIFIED" if delta > FAR else "INCONCLUSIVE")
    out = {
        "n_per_range": N_PER_RANGE, "seed0": SEED0,
        "dg": DG, "win_mult": WIN_MULT,
        "orig_terminal": sh_orig, "heldout_terminal": sh_held,
        "fresh_terminal": sh_fresh,
        "fit_half": {k: v for k, v in fit_a.items()},
        "fit_all": {k: v for k, v in fit_b.items()},
        "deviations": {"CC1": dev1, "CC2": dev2},
    }
    print(json.dumps(out))
    vs = {"CAL": cal, "CC1": cc1, "CC2": cc2, "CC3": cc3}
    print(json.dumps(vs))
    print("VERDICTS " + json.dumps(vs, sort_keys=True))


if __name__ == "__main__":
    main()
