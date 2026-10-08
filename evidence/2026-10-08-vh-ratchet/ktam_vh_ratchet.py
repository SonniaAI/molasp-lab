#!/usr/bin/env python3
"""VH vanishing-hazard ratchet falsifier (tick 70, SON-4871) —
executes the falsifier named by DW10's collection note
(research-log/2026-10-08-dw10-phase-chain.md section 6), verbatim
scope:

  "Named next falsifier (pre-register before running): VH1
   vanishing-hazard ratchet — fit per-phase D2T detach hazard
   (CONFIRM if monotone to ~0 by phases 3-4), forward-integrate
   the fitted non-homogeneous chain from the 1/4-window snapshot
   state to t_read, predict the held-out terminal share within
   +/-0.05. Holds -> the DW9 tilt is fully accounted and
   designs/007 window pricing gets its measured basis;
   non-monotone hazard -> reopen at the hazard shape."

Hypothesis under test (H_VH): the SITE occupancy chain's D2T detach
hazard COLLAPSES across the read window (ratchet: once D2T sits
late, the assembly context holds it), while attach odds stay
homogeneous (DW10's closest branch); forward-integrating the
fitted non-homogeneous chain from the 1/4-window snapshot then
predicts the terminal pair share.

Protocol of record is VERBATIM DW9/DW10 (ktam_dw10_phase.py ==
ktam_dw9_compound.py == tick-47/63): BUILD1 Vp-missing, Gmc=9.5,
gse=7.5, matched_s2 lock-read doubling, canonical map from the
FULL build, read window 4x400*e^Gmc at dG=2, seeds SEED0+i
(i in [0,1000)). run_traj below is DW10's function UNCHANGED —
same RNG stream, so the 1000 trajectories reproduce the DW9/DW10
logs exactly; CAL proves identity. All new science is in the
analysis, not the simulation.

Model spec (frozen):
  states {E, D2T, L2, O}; quartile phases phi=1..4 of t_read.
  Attach: E -> s at rate lambda*p_s; p_s = pooled attach odds on
  the fit range [0,250) (DW10 branch: homogeneous odds); lambda =
  total attach events / total empty time on the fit range.
  Hazards: s -> E at d_s^phi, fitted per phase for D2T and L2 on
  the fit range (spell time split at phase boundaries, DW10
  attribution); O hazard pooled over the whole window (fast
  b=1 churn; labelled modelling choice, not a claim).
  Initial state: empirical SITE occupancy distribution at
  t = t_read/4 over the fit range (state_at).
  Integration: v(t_read) = v(t_read/4) * exp(Q^2*D) * exp(Q^3*D) *
  exp(Q^4*D), D = t_read/4; exp via scaling-and-squaring +
  uniformization (pure python, no scipy); share_pred =
  v[D2T]/(v[D2T]+v[L2]).

PRE-REGISTERED gates (frozen before submission; machine verdicts
on the final VERDICTS line):
  CAL instrument identity: pooled terminal census over i in [0,500)
      must be EXACTLY D2T 367 : L2 131 (DW9/DW10 receipt).  [any
      mismatch -> CAL_FAIL and every VH verdict VOID]
  VH1 hazard-ratchet shape (fit range): per-phase D2T hazards
      d^phi = det_D2T^phi / occ_D2T^phi.  CONFIRMED iff
      d^1 >= d^2  AND  max(d^3, d^4) <= 0.10 * d^1
      (the named 'monotone to ~0 by phases 3-4', in noise-robust
      form: the 0->1-count wiggle between late phases cannot flip
      it; late-phase point hazards sit orders below 10% of d^1).
      [det_D2T^1 < 20 or occ_D2T^phi <= 0 for any phi -> NO_FIT]
  VH2 forward-integrated prediction: |share_pred - share on
      held-out [250,500)| <= 0.05 CONFIRMED  [> 0.05 FALSIFIED:
      the ratchet-integrated chain does not predict the terminal
      census; held-out pair terminals < 50 NO_EVENTS]
  VH3 out-of-sample fresh: same prediction vs the fresh
      [500,1000) share.  Same bands as VH2.

Descriptive (labelled, no gates): per-phase L2 hazards; per-phase
attach counts/odds; Poisson 95% upper bounds (3/occ) for zero-
count late D2T hazards; snapshot pair shares at 1/4, 1/2, 3/4 on
orig [0,500) (must reproduce DW10's 0.503/0.646/0.704);
homogeneous fit-range pi_pair (must reproduce DW9's 0.7124);
|dev_pred| vs |dev_homo| on held-out and fresh.

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
ARM_IDX = 2                    # tick-63 s2_dg2_win4 (DW9/DW10 layout)
SEED0 = BASE_SEED + ARM_IDX * SEED_STRIDE
N_PER_RANGE = 8 if os.environ.get("SMOKE") else 500
DG = 2.0
WIN_MULT = 4.0
SITE = (2, 2)                  # the Vp vacancy: fill/substitution site
FACE_DIR = {"E": (1, 0), "N": (0, 1), "S": (0, -1), "W": (-1, 0)}
CAL_D2T = 367
CAL_L2 = 131
N_PHASES = 4
BAND = 0.05
MIN_EVENTS = 50
MIN_DET_EARLY = 20
LATE_FRAC = 0.10


def matched_s2(build, asm, site, tile_name):
    """Family matched strength with the lock-read bond doubled
    (verbatim tick-38/41/43/DW9/DW10 arithmetic)."""
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
    """One trajectory, protocol of record — VERBATIM DW10/DW9
    run_traj with the passive SITE occupancy log.  RNG stream
    unchanged."""
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


def phase_counts(trajs, phase_lo=None, phase_hi=None):
    """att/det counts and occupancy/empty time attributed to a
    phase window (inclusive bounds, None = open).  Spell-splitting
    as DW10's phase_chain_fit: a spell crossing a phase boundary
    splits its time between phases; events attribute by event
    time.  Returns None on log inconsistency (protocol guard)."""
    t_read = trajs[0]["t_read"]
    in_win = lambda p: ((phase_lo is None or p >= phase_lo) and
                        (phase_hi is None or p <= phase_hi))
    att = Counter()
    det = Counter()
    occ_t = defaultdict(float)
    empty_t = 0.0
    for tr in trajs:
        state = None
        open_t = 0.0
        for (t, frm, to) in tr["log"]:
            if frm != state:
                return None
            lo = open_t
            hi = t
            p_a = phase_of(lo, t_read)
            p_b = phase_of(hi, t_read)
            for p in range(p_a, p_b + 1):
                if not in_win(p):
                    continue
                b_lo = max(lo, t_read * (p - 1) / N_PHASES)
                b_hi = min(hi, t_read * p / N_PHASES)
                if b_hi > b_lo:
                    if state is not None:
                        occ_t[state] += b_hi - b_lo
                    else:
                        empty_t += b_hi - b_lo
            ph = phase_of(t, t_read)
            if in_win(ph):
                if state is None and to is not None:
                    att[str(to)] += 1
                elif state is not None and to is None:
                    det[state] += 1
            state = to
            open_t = t
        lo = open_t
        p_a = phase_of(lo, t_read)
        for p in range(p_a, N_PHASES + 1):
            if not in_win(p):
                continue
            b_lo = max(lo, t_read * (p - 1) / N_PHASES)
            b_hi = min(t_read, t_read * p / N_PHASES)
            if b_hi > b_lo:
                if state is not None:
                    occ_t[str(state)] += b_hi - b_lo
                else:
                    empty_t += b_hi - b_lo
    return {"att": dict(att), "det": dict(det),
            "occ_t": dict(occ_t), "empty_t": empty_t}


def state_at(tr, t_star):
    """SITE occupancy at time t_star from the passive log
    (None before the first event).  Verbatim DW10."""
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


def mat_mul(A, B):
    n = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(n))
             for j in range(n)] for i in range(n)]


def expm(Q, dt):
    """Matrix exponential via scaling-and-squaring + uniformization
    (pure python).  Robust to stiff Q (huge O-churn hazard)."""
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
    E = [[0.0] * n for _ in range(n)]   # zero: the k=0 term of the
    # series supplies e^{-mu h} * I itself — starting from I would
    # double the identity component (caught by the expm validation).
    term = math.exp(-mu * h)
    Pv = [[(1.0 if i == j else 0.0) for j in range(n)]
          for i in range(n)]          # P^k, starts at P^0 = I
    for k in range(0, 200):
        # add term * P^k
        for i in range(n):
            for j in range(n):
                E[i][j] += term * Pv[i][j]
        if term < 1e-20 and k > mu * h + 20:
            break
        term = term * (mu * h) / (k + 1)
        Pv = mat_mul(Pv, P)
    for _ in range(m):
        E = mat_mul(E, E)
    for i in range(n):
        s = sum(E[i])
        assert abs(s - 1.0) < 1e-6, "expm row sum %.12f" % s
    return E


STATES = ("E", "D2T", "L2", "O")


def build_Q(lam, p, d_d2t, d_l2, d_o):
    Q = [[0.0] * 4 for _ in range(4)]
    Q[0] = [-lam, lam * p["D2T"], lam * p["L2"], lam * p["O"]]
    Q[1] = [d_d2t, -d_d2t, 0.0, 0.0]
    Q[2] = [d_l2, 0.0, -d_l2, 0.0]
    Q[3] = [d_o, 0.0, 0.0, -d_o]
    return Q


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
    t_read = trajs[0]["t_read"]

    # CAL — instrument identity (DW9/DW10 receipt)
    sh_orig = terminal_share(orig)
    cal = ("CAL_OK" if (N_PER_RANGE != 500 or
                        (sh_orig["D2T"] == CAL_D2T and
                         sh_orig["L2"] == CAL_L2)) else "CAL_FAIL")

    # ---- per-phase counts on the fit range ----
    pc = {p: phase_counts(fit_range, p, p) for p in range(1, 5)}
    if any(c is None for c in pc.values()):
        print(json.dumps({"error": "log_inconsistent"}))
        print("VERDICTS " + json.dumps(
            {"CAL": "CAL_FAIL", "VH1": "VOID", "VH2": "VOID",
             "VH3": "VOID"}, sort_keys=True))
        return
    whole = phase_counts(fit_range)

    # ---- VH1: per-phase D2T hazards, ratchet shape ----
    occ_d2t = {p: pc[p]["occ_t"].get("D2T", 0.0) for p in range(1, 5)}
    det_d2t = {p: pc[p]["det"].get("D2T", 0) for p in range(1, 5)}
    d_d2t = {p: (det_d2t[p] / occ_d2t[p] if occ_d2t[p] > 0 else None)
             for p in range(1, 5)}
    if det_d2t[1] < MIN_DET_EARLY or any(v <= 0 for v in occ_d2t.values()):
        vh1 = "NO_FIT"
    else:
        vh1 = ("CONFIRMED" if (d_d2t[1] >= d_d2t[2] and
                               max(d_d2t[3], d_d2t[4]) <=
                               LATE_FRAC * d_d2t[1]) else "FALSIFIED")
    # Poisson 95% upper bounds for late phases (3 events / exposure)
    ub = {p: (3.0 / occ_d2t[p] if occ_d2t[p] > 0 else None)
          for p in (3, 4)}

    # ---- fitted model parameters (fit range) ----
    att_all = Counter(whole["att"])
    total_att = sum(att_all.values())
    p = {"D2T": att_all["D2T"] / total_att,
         "L2": att_all["L2"] / total_att,
         "O": (total_att - att_all["D2T"] - att_all["L2"]) / total_att}
    lam = total_att / whole["empty_t"] if whole["empty_t"] > 0 else None
    occ_l2 = {p: pc[p]["occ_t"].get("L2", 0.0) for p in range(1, 5)}
    det_l2 = {p: pc[p]["det"].get("L2", 0) for p in range(1, 5)}
    d_l2 = {p: (det_l2[p] / occ_l2[p] if occ_l2[p] > 0 else None)
            for p in range(1, 5)}
    occ_o = sum(v for k, v in whole["occ_t"].items()
                if k not in ("D2T", "L2"))
    det_o = sum(v for k, v in whole["det"].items()
                if k not in ("D2T", "L2"))
    d_o = det_o / occ_o if occ_o > 0 else None
    # homogeneous pi_pair reproduction (DW9 0.7124)
    d_h_d2t = whole["det"].get("D2T", 0) / whole["occ_t"]["D2T"]
    d_h_l2 = whole["det"].get("L2", 0) / whole["occ_t"]["L2"]
    x2 = p["D2T"] / d_h_d2t
    xl = p["L2"] / d_h_l2
    homo_pi = x2 / (x2 + xl)

    # ---- forward integration from the 1/4-window snapshot ----
    snap0 = {"E": 0, "D2T": 0, "L2": 0, "O": 0}
    t_star = t_read / 4.0
    for tr in fit_range:
        s = state_at(tr, t_star)
        snap0["E" if s is None else
               ("O" if s not in ("D2T", "L2") else s)] += 1
    n0 = sum(snap0.values())
    v0 = [snap0[k] / float(n0) for k in STATES]
    share_pred = None
    vf = None
    ok_fit = lam is not None and d_o is not None and \
        all(d_d2t[p] is not None for p in range(2, 5)) and \
        all(d_l2[p] is not None for p in range(2, 5))
    if ok_fit:
        v = v0[:]
        for phi in range(2, 5):
            Q = build_Q(lam, p, d_d2t[phi], d_l2[phi], d_o)
            E = expm(Q, t_read / 4.0)
            v = [sum(v[i] * E[i][j] for i in range(4))
                 for j in range(4)]
        vf = v
        share_pred = v[1] / (v[1] + v[2]) if (v[1] + v[2]) > 0 else None

    # ---- VH2 / VH3 ----
    sh_held = terminal_share(held)
    sh_fresh = terminal_share(fresh)
    if not ok_fit or share_pred is None:
        vh2 = vh3 = "NO_FIT"
        dev2 = dev3 = None
    else:
        if sh_held["D2T"] + sh_held["L2"] < MIN_EVENTS:
            vh2 = "NO_EVENTS"
            dev2 = None
        else:
            dev2 = abs(share_pred - sh_held["share"])
            vh2 = "CONFIRMED" if dev2 <= BAND else "FALSIFIED"
        if sh_fresh["D2T"] + sh_fresh["L2"] < MIN_EVENTS:
            vh3 = "NO_EVENTS"
            dev3 = None
        else:
            dev3 = abs(share_pred - sh_fresh["share"])
            vh3 = "CONFIRMED" if dev3 <= BAND else "FALSIFIED"
    if cal != "CAL_OK":
        vh1 = vh2 = vh3 = "VOID"

    snaps = {str(f): snapshot_pair_share(orig, f)
             for f in (0.25, 0.5, 0.75)}
    out = {
        "n_per_range": N_PER_RANGE, "seed0": SEED0,
        "dg": DG, "win_mult": WIN_MULT, "n_phases": N_PHASES,
        "orig_terminal": sh_orig, "heldout_terminal": sh_held,
        "fresh_terminal": sh_fresh,
        "phase_counts": {str(p): {"att": pc[p]["att"],
                                  "det": pc[p]["det"],
                                  "occ_D2T": pc[p]["occ_t"].get("D2T", 0.0),
                                  "occ_L2": pc[p]["occ_t"].get("L2", 0.0)}
                         for p in range(1, 5)},
        "hazards_D2T": {str(p): d_d2t[p] for p in range(1, 5)},
        "hazards_L2": {str(p): d_l2[p] for p in range(1, 5)},
        "hazard_upper95_D2T_late": {str(p): ub[p] for p in (3, 4)},
        "pooled_p": p, "lambda": lam, "d_O": d_o,
        "homo_pi_pair_fitrange": homo_pi,
        "snapshot_init": snap0, "v0": v0, "vf": vf,
        "share_pred": share_pred,
        "deviations": {"VH2": dev2, "VH3": dev3},
        "dev_homo_heldout": (abs(homo_pi - sh_held["share"])
                             if sh_held["share"] is not None else None),
        "snapshots": snaps,
    }
    print(json.dumps(out))
    vs = {"CAL": cal, "VH1": vh1, "VH2": vh2, "VH3": vh3}
    print(json.dumps(vs))
    print("VERDICTS " + json.dumps(vs, sort_keys=True))


if __name__ == "__main__":
    main()
