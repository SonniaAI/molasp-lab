#!/usr/bin/env python3
"""W8 POWERED PAIRED BLOCK-MECHANISM ARBITRATION PROBE (tick 120
pre-registration, SON-5152) — the tick-119 escalation, executed.

Open dispute (receipts, frozen): the tick-101 block probe landed
AMBIG_MIDDLE because its contrast — gap-block control 391/500 = 0.782
vs arm-6-block continuation 372/500 = 0.744, delta 0.038 — sat just
under the design's MDE 0.040 at n = 2000/group.  The tick-119 Branch A
dispersion gate re-read POOLING_CONTESTED at the corrected four arms
(min_exact_p 0.0293258, driver arm-6) and closed both pooled verdict
readings as unclaimable; the frozen escalation path is a POWERED paired
arbitration probe at delta_target = 0.030 with per-group n scaled by
the frozen (0.040/delta)^2 rule: n = 2000 x (0.040/0.030)^2 = 3555.6
-> 3560 seeds/group (2 matched 1780-seed windows per group).

The question this probe arbitrates, stated before any datum:
  account A (window noise): BOTH hot readings — arm-6 389/500 = 0.778
    and gap control 391/500 = 0.782 — were window-level fluctuations;
    fresh continuations of the SAME two blocks do NOT differ
    persistently.  Prediction: |share(GAP) - share(A6)| small;
    one-sided p > 0.05 at this power.
  account B (block mechanism): the mid-stride gap block (base
    350261107) runs elevated RELATIVE to arm-6's block (base
    340261107) as a persistent between-block contrast.  Standing
    direction, measured twice independently: +0.038 (tick 101,
    n=500/group) and +0.0223 (hotrepro continuations 714/1000 vs
    691/999).  Pooled over both: GAP 1105/1500 = 0.73667 vs A6
    1063/1499 = 0.70914, delta +0.02753.  Prediction at power:
    share(GAP) > share(A6) with one-sided p <= 0.05.

Groups (fresh windows, virgin by full-tree range scan this tick):
  GAP   seeds 350261107 + 1500 + i, i in [0,3560) — gap block,
        burned [0,1500) by arm8 [0,500) (tick 101) + B-fresh
        [500,1500) (hotrepro); fresh range [1500,5060).
        Windows: gap_w1 [1500,3280), gap_w2 [3280,5060).
  A6    seeds 340261107 + 2000 + i, i in [0,3560) — arm-6 block,
        burned [0,2000) by arm6 [0,500) (tick 99) + arm6b [500,1000)
        (tick 101) + A-fresh [1000,2000) (hotrepro); fresh range
        [2000,5560).  Windows: a6_w1 [2000,3780), a6_w2 [3780,5560).
  Pairing: window index matched across groups (w1/w2 hold the same
  position within each group's fresh range); the PRIMARY ignores the
  pairing and pools windows within group (Fisher support is fine-
  grained at these n; no structural floor, unlike tick-112 P1).

  CAL   seeds 260261107 + i, i in [0,500) — unchanged identity gate:
        mid-window pair census must be EXACTLY D2T 367 : L2 131
        (10th consecutive identity run when it lands).

PRIMARY (single gate, one-sided, direction frozen from the anchors):
pooled GAP vs pooled A6 terminal pair census, Fisher's exact
one-sided p = P(X >= x_gap | hypergeometric, both margins fixed),
H1: share(GAP) > share(A6), alpha = 0.05.

Branch map (frozen, exhaustive, mechanical, no default):
  CAL_FAIL                     -> VOID (instrument, not science)
  min(n_gap, n_a6) < 3400      -> NO_EVENTS
  p <= 0.05                    -> BLOCK_MECHANISM_SUPPORTED
  p > 0.05                     -> BLOCK_MECHANISM_NOT_DETECTED

BLOCK_MECHANISM_SUPPORTED: a persistent between-block elevation
survives a powered paired test; block-level heterogeneity stands;
pooling across stride/half-stride blocks is structurally unsafe for
census purposes; family estimates go per-block; the ladder's iid-
pooling premise is downgraded (major finding — blog only after
independent review).
BLOCK_MECHANISM_NOT_DETECTED: the twice-observed direction (+0.038,
+0.0223) does not survive a powered test; window-noise stands as the
operating account for BOTH hot readings; tick-101's AMBIG_MIDDLE
resolves to noise-at-power; the pooling premise stands at family
level with the standing q0 pos-1 caveat; the four-arm
POOLING_CONTESTED receipt remains the operative constraint (pooled
line REPORTED-NOT-CLAIMABLE) and the ladder stays PAUSED pending the
next pre-registered step.

POWER (planned, normal approximation, stated BEFORE submission,
one-sided alpha = 0.05, p_bar ~ 0.745, n = 3560/group):
  SE(diff) = sqrt(2 x 0.745 x 0.255 / 3560) = 0.010332
  MDE at 90% power: (1.645 + 1.2816) x 0.010332 = 0.03024 ~ 0.030
  power at delta = 0.030 (design target):  ~ 0.896
  power at delta = 0.038 (tick-101 realized): ~ 0.979
  power at delta = 0.0223 (hotrepro realized): ~ 0.696
Pair-n expectation: terminal 'other' rate <= 0.5% across every
committed w8 window; expected pair-n >= ~3542 of 3560; the 3400 floor
carries ~4.5% headroom.

DESCRIPTIVE (no gates ride on these): per-window shares + Wilson 95;
per-group two-sided exact binomial vs family 1110/1499 (the qF
readings, tick-101 style); within-block cross-window two-sided
Fisher; matched-window deltas (w1, w2); per-500 subwindow shares.

Boundaries (frozen): direction is GAP > A6; a realized REVERSE
difference surfaces in descriptives only and needs a fresh
pre-registration — no post-hoc flip.  Two blocks do not certify the
lattice; a SUPPORT localizes persistent structure to at least this
block pair, a NOT_DETECT bounds it at this power.  In silico kTAM
simulation only; no physical-replicate inference, no
chemical-performance claim, no wet-lab execution.

SMOKE=1 runs 8 trajectories per window (16/group) and labels output
SMOKE_ONLY; it is never a verdict surface.  One clean-extraction
SMOKE run is executed locally before submission (tick-113
precedent); the queued job runs the full windows.
"""

from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PREVIOUS = os.path.join(REPO, "evidence", "2026-10-09-w8-blockprobe")
TILES_AND_DIR = os.path.join(REPO, "evidence", "2026-10-06-body-conjunction-builds")
TILES_DEATH_DIR = os.path.join(REPO, "evidence", "2026-10-06-structural-death")
for path in (REPO, PREVIOUS, TILES_AND_DIR, TILES_DEATH_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from ktam_w8_blockprobe import (  # noqa: E402
    BASE_SEED,
    BUILD1,
    CAL_D2T,
    CAL_L2,
    DG,
    SEED0_CAL,
    SEED_STRIDE,
    WIN_MULT,
    build_missing_species,
    canonical_assembly,
    census,
    matched_s2,
    run_traj,
    wilson,
)

# ---- frozen probe constants (identity-pinned in tests) ----
A6_BLOCK = BASE_SEED + 6 * SEED_STRIDE            # 340261107
GAP_BLOCK = BASE_SEED + (13 * SEED_STRIDE) // 2   # 350261107 (6.5 strides)
A6_OFFSET = 2000                                  # burned [0,2000)
GAP_OFFSET = 1500                                 # burned [0,1500)
SEED0_A6 = A6_BLOCK + A6_OFFSET                   # 340263107
SEED0_GAP = GAP_BLOCK + GAP_OFFSET                # 350262607
N_WIN = 8 if os.environ.get("SMOKE") else 1780    # per window
N_GROUP = 2 * N_WIN                               # 3560 seeds/group

ALPHA = 0.05
MIN_EVENTS = 3400                                 # per pooled group

# fixed references from committed receipts (never re-derived here)
FAMILY = {"x": 1110, "k": 1499}                   # arms 3+5+7 full-n
ARM6 = {"x": 389, "k": 500}                       # tick-99
ARM6B = {"x": 372, "k": 500}                      # tick-101
ARM8 = {"x": 391, "k": 500}                       # tick-101
AFRESH = {"x": 691, "k": 999}                     # hotrepro
BFRESH = {"x": 714, "k": 1000}                    # hotrepro


def log_choose(n, k):
    return (math.lgamma(n + 1) - math.lgamma(k + 1)
            - math.lgamma(n - k + 1))


def fisher_one_sided(xg, ng, xa, na):
    """Exact one-sided Fisher: p = P(X >= x_gap | margins fixed),
    GAP-vs-A6 2x2 with H1 share(GAP) > share(A6)."""
    tot = ng + na
    succ = xg + xa
    denom = log_choose(tot, ng)
    hi = min(ng, succ)
    terms = []
    for k in range(xg, hi + 1):
        logp = (log_choose(succ, k) + log_choose(tot - succ, ng - k)
                - denom)
        terms.append(math.exp(logp))
    return math.fsum(terms)


def fisher_two_sided(xg, ng, xa, na):
    """Exact two-sided Fisher (sum of table probabilities <= observed),
    descriptive cross-window contrasts only."""
    tot = ng + na
    succ = xg + xa
    denom = log_choose(tot, ng)
    lo = max(0, succ - na)
    hi = min(ng, succ)
    probs = []
    for k in range(lo, hi + 1):
        logp = (log_choose(succ, k) + log_choose(tot - succ, ng - k)
                - denom)
        probs.append((k, math.exp(logp)))
    obs = None
    for k, p in probs:
        if k == xg:
            obs = p
            break
    return math.fsum(p for _, p in probs if p <= obs * (1 + 1e-9))


def binom_two_sided(n, p0, x):
    """Exact two-sided binomial vs a fixed reference share (the qF
    family-consistency readings, tick-101 style)."""
    logp_obs = (log_choose(n, x)
                + x * math.log(p0) + (n - x) * math.log1p(-p0))
    tot = 0.0
    for k in range(n + 1):
        logp = (log_choose(n, k)
                + k * math.log(p0) + (n - k) * math.log1p(-p0))
        if logp <= logp_obs + 1e-9:
            tot += math.exp(logp)
    return min(1.0, tot)


def branch_map(xg, ng, xa, na, cal_ok):
    """Frozen branch map. Returns (branch, tests)."""
    if not cal_ok:
        return "VOID", None
    tests = {"p_fisher_one_sided": fisher_one_sided(xg, ng, xa, na),
             "alpha": ALPHA,
             "share_gap": xg / float(ng) if ng else None,
             "share_a6": xa / float(na) if na else None}
    if ng < MIN_EVENTS or na < MIN_EVENTS:
        return "NO_EVENTS", tests
    if tests["p_fisher_one_sided"] <= ALPHA:
        return "BLOCK_MECHANISM_SUPPORTED", tests
    return "BLOCK_MECHANISM_NOT_DETECTED", tests


def subwindow_shares(trajs, seed0, sub=500):
    out = []
    for start in range(0, len(trajs), sub):
        chunk = trajs[start:start + sub]
        c = census(chunk, "terminal")
        n = c["D2T"] + c["L2"]
        out.append({"seed0": seed0 + start, "n": len(chunk),
                    "x": c["D2T"], "pair_n": n,
                    "share": (c["D2T"] / n) if n else None})
    return out


def win_census(trajs):
    c = census(trajs, "terminal")
    return c, c["D2T"] + c["L2"]


def main():
    b1v = build_missing_species(BUILD1, "Vp")
    canon = canonical_assembly(BUILD1)

    n_cal = 8 if os.environ.get("SMOKE") else 500
    cal_tr = [run_traj(b1v, matched_s2, canon, SEED0_CAL + i,
                       DG, WIN_MULT) for i in range(n_cal)]
    arms = {}
    for name, seed0 in (("gap_w1", SEED0_GAP),
                        ("gap_w2", SEED0_GAP + N_WIN),
                        ("a6_w1", SEED0_A6),
                        ("a6_w2", SEED0_A6 + N_WIN)):
        arms[name] = [run_traj(b1v, matched_s2, canon, seed0 + i,
                               DG, WIN_MULT) for i in range(N_WIN)]

    cal_mid = census(cal_tr, "mid")
    cal_ok = (n_cal != 500 or
              (cal_mid["D2T"] == CAL_D2T and cal_mid["L2"] == CAL_L2))

    censuses = {}
    for name, trajs in arms.items():
        censuses[name] = win_census(trajs)

    xg = censuses["gap_w1"][0]["D2T"] + censuses["gap_w2"][0]["D2T"]
    ng = censuses["gap_w1"][1] + censuses["gap_w2"][1]
    xa = censuses["a6_w1"][0]["D2T"] + censuses["a6_w2"][0]["D2T"]
    na = censuses["a6_w1"][1] + censuses["a6_w2"][1]

    branch, tests = branch_map(xg, ng, xa, na, cal_ok)

    def blk(name):
        c, n = censuses[name]
        return {"x": c["D2T"], "pair_n": n,
                "share": c["D2T"] / float(n) if n else None,
                "wilson95": wilson(c["D2T"], n)}

    g1 = censuses["gap_w1"]; g2 = censuses["gap_w2"]
    a1 = censuses["a6_w1"]; a2 = censuses["a6_w2"]
    fam_p = FAMILY["x"] / float(FAMILY["k"])
    out = {
        "label": "SMOKE_ONLY" if os.environ.get("SMOKE") else "W8_BLOCKPOWER",
        "n_cal": n_cal, "n_win": N_WIN, "n_group": N_GROUP,
        "seed0_cal": SEED0_CAL, "seed0_gap": SEED0_GAP,
        "seed0_a6": SEED0_A6, "a6_block": A6_BLOCK, "gap_block": GAP_BLOCK,
        "a6_offset": A6_OFFSET, "gap_offset": GAP_OFFSET,
        "dg": DG, "win_mult": WIN_MULT, "t_mid_is_w4": True,
        "cal_mid_w4": cal_mid, "cal": "CAL_OK" if cal_ok else "CAL_FAIL",
        "gap_w1": blk("gap_w1"), "gap_w2": blk("gap_w2"),
        "a6_w1": blk("a6_w1"), "a6_w2": blk("a6_w2"),
        "pooled_gap": {"x": xg, "pair_n": ng},
        "pooled_a6": {"x": xa, "pair_n": na},
        "observed_delta": (xg / float(ng) - xa / float(na))
        if (ng and na) else None,
        "references": {"arm6": ARM6, "arm6b": ARM6B, "arm8": ARM8,
                       "afresh_340": AFRESH, "bfresh_350": BFRESH,
                       "family": FAMILY},
        "descriptive": {
            "qF_gap_vs_family": binom_two_sided(ng, fam_p, xg),
            "qF_a6_vs_family": binom_two_sided(na, fam_p, xa),
            "fisher_gap_w1_w2": fisher_two_sided(
                g1[0]["D2T"], g1[1], g2[0]["D2T"], g2[1]),
            "fisher_a6_w1_w2": fisher_two_sided(
                a1[0]["D2T"], a1[1], a2[0]["D2T"], a2[1]),
            "matched_w1_delta": (
                g1[0]["D2T"] / g1[1] - a1[0]["D2T"] / a1[1])
            if g1[1] and a1[1] else None,
            "matched_w2_delta": (
                g2[0]["D2T"] / g2[1] - a2[0]["D2T"] / a2[1])
            if g2[1] and a2[1] else None,
            "gap_subwindows": subwindow_shares(arms["gap_w1"], SEED0_GAP)
            + subwindow_shares(arms["gap_w2"], SEED0_GAP + N_WIN),
            "a6_subwindows": subwindow_shares(arms["a6_w1"], SEED0_A6)
            + subwindow_shares(arms["a6_w2"], SEED0_A6 + N_WIN),
        },
        "branch": branch, "tests": tests,
    }
    print(json.dumps(out, indent=1, sort_keys=True))
    verdict = {"CAL": out["cal"], "PROBE": branch}
    print(json.dumps(verdict))
    print("VERDICTS", json.dumps(verdict))


if __name__ == "__main__":
    main()
