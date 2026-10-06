"""Exact first-passage CTMC for the v2.1 empty/unfounded channels.

designs/001 (tick 4, 2026-10-06) left a measured anomaly: at dG=2 the
empty channel reads .174 against the single-shot trap formula
1/(1+e^{dG}) ~ .12, hypothesis "site-reopening retries". This file
replaces the hand wave: it enumerates the exact continuous-time Markov
chain over the decision/lock window of the v2.1 construction of record
(tiles_v2.py glue arithmetic, unchanged), and solves for the joint
first-passage distribution of the two decision locks.

Window (context fixed: full seed + S1 at (0,1), both b=2-stable):
  (1,1) D1T/D1F   (2,1) L1   (0,2) S1/S2   (1,2) D2T/D2F   (2,2) L2

Rates exactly as ktam_mc_v2.py (kTAM no-mismatch, k_f = 1/s):
  attach k_f*e^{-Gmc} per (site, tile) with matched strength >= 1;
  detach k_f*e^{-b*Gse}, b = summed matched strength (SP pairs count 2).

A row-i "lock event" is the first instant the decision tile of row i
sits at b >= 2 (D1T/D1F at (1,1); D2T/D2F at (1,2)); the chain is
absorbed when both rows have locked, and the terminal state is
classified with the same decode map as the aTAM claim (a / empty /
ap / p). First-passage probabilities are well defined even though
b=2 states can still detach (rate e^{-2Gse}); the MC grid reads at
T = 400*e^{Gmc}, so passage-at-infinity matches the read whenever
growth completes well inside T (dG <= 4; see log entry for dG=7).

Also reported per dG: expected number of D1F excursions at (1,1)
before row-1 lock (the "retry" count), and attribution variants that
disable one trap channel at a time:
  full            -- the honest chain;
  no-L1-first     -- L1 may not attach at (2,1) while (1,1) is open;
  D1F-W-only      -- additionally, nothing except L1-attach may raise
                     a resident D1F's bond count (kills the S2/D2F
                     chain traps), leaving pure per-excursion races
                     with reopening.

Output: JSON lines, one per dG point, reproducible (no RNG anywhere).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "2026-10-05-c2-ktam"))

from tiles_v2 import TILES, SEED_TILES, matched_strength  # noqa: E402
from atam_check_v2 import decode  # noqa: E402

GSE = 9.0
BASE = dict(SEED_TILES)
BASE[(0, 1)] = "S1"          # spine row 1: b=2 via SP1, treated as settled context
WINDOW = [(1, 1), (2, 1), (0, 2), (1, 2), (2, 2)]
DEC = {(1, 1): ("D1T", "D1F"), (1, 2): ("D2T", "D2F")}


def full_asm(state):
    a = dict(BASE)
    a.update(state)
    return a


def bond_of(asm, site):
    """Summed matched strength of the tile currently at site."""
    return matched_strength(asm, site, asm[site])


def locked_class(state):
    """None while either row is unlocked; else decode-class of the joint lock."""
    asm = full_asm(state)
    for site in DEC:
        t = asm.get(site)
        if t not in DEC[site] or bond_of(asm, site) < 2:
            return None
    a = asm[(1, 1)] == "D1T"
    p = asm[(1, 2)] == "D2T"
    if a and p:
        return "ap"
    if a:
        return "a"
    if p:
        return "p"
    return "empty"


def transitions(state, Gmc, variant):
    """Yield (rate, next_state) under the kTAM event rule."""
    st = dict(state)
    asm = full_asm(st)
    rf = math.exp(-Gmc)
    for site in WINDOW:
        if site in st:
            b = bond_of(asm, site)
            nxt = dict(st)
            del nxt[site]
            yield math.exp(-b * GSE), tuple(sorted(nxt.items()))
            continue
        for tile in TILES:
            b = matched_strength(asm, site, tile)
            if b < 1:
                continue
            if variant == "no-L1-first" and tile == "L1" and site == (2, 1) \
                    and (1, 1) not in st:
                continue
            if variant == "D1F-W-only" and st.get((1, 1)) == "D1F" \
                    and (tile == "S1" or tile == "S2" or
                         (site == (1, 2) and tile in ("D2F", "D2T"))):
                continue
            nxt = dict(state)
            nxt[site] = tile
            yield rf, tuple(sorted(nxt.items()))


def enumerate_states(Gmc, variant):
    start = tuple()
    seen, absorbing = {start}, {}
    frontier = [start]
    edges = {start: list(transitions(start, Gmc, variant))}
    while frontier:
        s = frontier.pop()
        cls = locked_class(dict(s))
        if cls is not None:
            absorbing[s] = cls
            continue
        for rate, nxt in edges[s]:
            if nxt not in seen:
                seen.add(nxt)
                edges[nxt] = list(transitions(nxt, Gmc, variant))
                frontier.append(nxt)
    return sorted(seen), edges, absorbing


def solve(seen, edges, absorbing, reward=None):
    """Absorption probabilities (per class) and optional expected reward.

    Reward: expected count of reward(state, event) accumulations before
    absorption, computed by the standard cumulative-reward linear system.
    """
    idx = {s: i for i, s in enumerate(seen)}
    n = len(seen)
    trans = [s for s in seen if s not in absorbing]
    tidx = {s: i for i, s in enumerate(trans)}
    # P[i] = sum_j w_ij P[j] + b_i ; solve per class by Gaussian elimination.
    def lin_solve(mat, rhs):
        m = [row[:] + [rhs[i]] for i, row in enumerate(mat)]
        ncols = len(trans)
        for col in range(ncols):
            piv = next(r for r in range(col, ncols) if abs(m[r][col]) > 1e-300)
            m[col], m[piv] = m[piv], m[col]
            pv = m[col][col]
            m[col] = [v / pv for v in m[col]]
            for r in range(ncols):
                if r != col and m[r][col] != 0.0:
                    f = m[r][col]
                    m[r] = [a - f * b for a, b in zip(m[r], m[col])]
        return {trans[i]: m[i][-1] for i in range(ncols)}

    mat = [[0.0] * len(trans) for _ in trans]
    base = {c: [0.0] * len(trans) for c in ("a", "empty", "ap", "p")}
    rew = [0.0] * len(trans) if reward is not None else None
    for i, s in enumerate(trans):
        tot = sum(r for r, _ in edges[s])
        mat[i][i] = 1.0
        for rate, nxt in edges[s]:
            w = rate / tot
            if nxt in absorbing:
                base[absorbing[nxt]][i] += w
            else:
                mat[i][tidx[nxt]] -= w
            if reward is not None:
                rew[i] += w * reward(s, nxt)
    out = {c: lin_solve([row[:] for row in mat], base[c]) for c in base}
    exp_reward = lin_solve(mat, rew) if reward is not None else None
    start = seen[0]
    probs = {c: out[c].get(start, 1.0 if absorbing.get(start) == c else 0.0)
             for c in ("a", "empty", "ap", "p")}
    return probs, (exp_reward.get(start, 0.0) if exp_reward else 0.0)


def d1f_excursion_reward(s, nxt):
    """+1 for a D1F arrival at (1,1) from an open site."""
    d = dict(nxt)
    return 1.0 if d.get((1, 1)) == "D1F" and dict(s).get((1, 1)) is None else 0.0


def point(dG, variant="full", reward=None):
    Gmc = GSE + dG
    seen, edges, absorbing = enumerate_states(Gmc, variant)
    probs, exp = solve(seen, edges, absorbing, reward=reward)
    return probs, exp, len(seen), len(absorbing)


def main():
    print(json.dumps({"model": "exact first-passage CTMC, v2.1 window",
                      "Gse": GSE, "context": "seed + S1 settled",
                      "absorption": "joint first lock of rows 1-2 "
                      "(decision tile at b>=2)"}))
    for dG in (0.5, 2.0, 4.0):
        probs, exc, ns, na = point(dG, reward=d1f_excursion_reward)
        t1 = probs["empty"] + probs["p"]      # row-1 first-lock = D1F
        t2 = probs["ap"] + probs["p"]         # row-2 first-lock = D2T
        row = {"dG": dG, "states": ns, "absorbing": na,
               "P": {k: round(v, 4) for k, v in probs.items()},
               "t1_row1_traps_D1F": round(t1, 4),
               "t2_row2_traps_D2T": round(t2, 4),
               "E_d1f_excursions": round(exc, 4),
               "singleshot_formula": round(1.0 / (1.0 + math.exp(dG)), 4),
               "cells": {"empty_pred": round(t1 * (1 - t2), 4),
                         "unfounded_pred": round((1 - t1) * t2 + t1 * t2, 4)}}
        print(json.dumps(row), flush=True)
    print(json.dumps({"attribution_at_dG2": {}}))
    for variant in ("full", "no-L1-first", "D1F-W-only"):
        probs, exc, ns, _ = point(2.0, variant=variant, reward=d1f_excursion_reward)
        t1 = probs["empty"] + probs["p"]
        print(json.dumps({"variant": variant, "t1": round(t1, 4),
                          "E_d1f_excursions": round(exc, 4)}), flush=True)


if __name__ == "__main__":
    main()
