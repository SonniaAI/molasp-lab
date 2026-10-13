#!/usr/bin/env python3
"""W8 position-tagged fresh-window probe (SON-5144, tick 113) — the
tick-112 named successor, pre-registered from the CORRECTED state.

Open dispute: the w8 share census ladder is PAUSED (tick 112) between
the window-noise account (windows iid at a common rate) and position-
along-block structure.  Measured anchors, from committed receipts:

  - tick-112 blockpos, eight observed 500-seed windows: pooled FIRST
    window 780/1000 = 0.780 vs rest 1777/2499 = 0.71108 (delta 0.069);
    S2 raw p = 5/144 = 0.0347, Holm-adj 0.0694 -> NOT detected;
    P1 structurally unpowered (floor 12/144).
  - arm-6 block decline (descriptive, tick-111 subwindows):
    0.778, 0.744, 0.694, 0.689; arm-8 block: 0.782, 0.692, 0.736.
  - six-window heterogeneity study (tick-102/103), blocks
    380261107..480261107 pooled [0,5000) each: shares 0.7289, 0.7417,
    0.7385, 0.7351, 0.7395, 0.7400, Pearson p = 0.735 -> HETEROGENEITY_
    NOT_DETECTED.  Under a strong universal spike (first 500 at 0.78,
    rest at 0.711) a pooled 5000-window would read ~0.717; measured
    0.729-0.742 sits 1.5-2 sigma above that, so a strong UNIVERSAL
    position effect is already disfavored in THOSE blocks.

SEED-SCAN FIRST (durable lesson, tick 110): the tick-112 note named
candidate blocks 380261107/400261107 as unburned — STALE.  Both are
burned [0,5000) by the tick-102 six-window study (their seed0 literals
are in evidence/2026-10-09-w8-window-heterogeneity/run.out).  Full-tree
scan this tick (evidence/ tools/ molasp/ tests/ log/ research-log/
designs/, zero-hit verified): the chosen blocks are virgin.  NOTE the
blockprobe lineage base is 220261107 (not the strength-2 160261107 or
recombination 100261107 bases): this probe uses BASE_SEED + 17/18 *
STRIDE = 560261107 / 580261107.  240/500/520/540 x261107 are also
clean, but 560/580 sit farthest from every burned lineage.  The suite
run.out guards are the enforced backstop.

Instrument: the simulation core imported VERBATIM from
ktam_w8_blockprobe.py (same BUILD1 Vp-missing protocol, same s2
lock-read arithmetic, same run_traj — DW9's function verbatim, no
RNG-order change — same WIN_MULT=8 read window, same CAL identity gate:
mid-window pair census over seeds 260261107+[0,500) must be EXACTLY
D2T 367 : L2 131; this job is the 8th consecutive identity run when it
lands).

  CAL    seeds 260261107 + i, i in [0,500)   (unchanged).
  U1E    seeds 560261107 + 0    + i, i in [0,1000) — virgin block 17,
         EARLY window (500-seed positions 1-2).
  U1L    seeds 560261107 + 9000 + i, i in [0,1000) — same block, LATE
         window (500-seed positions 19-20).
  U2E    seeds 580261107 + 0    + i, i in [0,1000) — virgin block 18,
         EARLY window.
  U2L    seeds 580261107 + 9000 + i, i in [0,1000) — LATE window.

PRIMARY (single gate, one-sided, direction frozen from the anchors):
pooled EARLY (U1E+U2E) vs pooled LATE (U1L+U2L) terminal pair census,
Fisher's exact one-sided p = P(X >= x_early | hypergeometric with both
margins fixed), H1: share(early) > share(late), alpha = 0.05.

Branch map (frozen, exhaustive, mechanical, no default):
  CAL_FAIL                        -> VOID (instrument, not science)
  min(n_early, n_late) < 1600     -> NO_EVENTS
  p <= 0.05                       -> POSITION_DECLINE_DETECTED
  p > 0.05                        -> POSITION_DECLINE_NOT_DETECTED

POSITION_DECLINE_DETECTED: window iid (the window-noise account) is
rejected at this resolution in virgin blocks; future pooling must
stratify by position; ladder redesign required before any growth arm.
POSITION_DECLINE_NOT_DETECTED: window-noise stands unrefuted at this
resolution (not proven); the ladder's iid-pooling premise is
reinforced, with the standing q0 pos-1-weighting caveat (q0=1110/1499
is first-window-weighted; this probe's primary is INTERNAL early-vs-
late, so no q0 dependence).

POWER (planned, normal approximation, stated BEFORE submission,
n=2000 per pooled group, one-sided alpha=0.05, p_bar~0.745):
  delta=0.069 (measured first-vs-rest): power ~ 0.9996
  delta=0.030 (half):                   power ~ 0.70
  MDE at 90% power:                     ~ 0.040
  (SE of the difference at n=2000/group, p_bar=0.745:
  sqrt(2*0.745*0.255/2000) = 0.01378; an earlier draft of this
  note said 0.029 from a single-variance SE — corrected pre-commit.)
Per-block pair (descriptive only, n=1000/group): delta=0.069 ->
power ~ 0.97.  Compare tick-112 P1: this design has NO structural
floor problem (the Fisher support under both-margins-fixed is fine-
grained at these n; the smallest attainable one-sided p is the
all-successes point, << 0.001).

DESCRIPTIVE (no gates ride on these): per-window shares + Wilson 95;
per-block two-sided Fisher; late-vs-late cross-block two-sided Fisher
(block-effect check); per-500-subwindow shares (4 per window —
localization input for any later pre-registration); observed deltas.

Boundaries (frozen): the pre-registered direction is DECLINE
(early > late); a realized INCREASE surfaces in descriptives only and
needs a fresh pre-registration — no post-hoc flip.  EARLY-vs-LATE is a
contrast, not monotonicity; subwindow descriptives carry the shape.
Two virgin blocks do not certify all blocks (six-window context above
already disfavors a strong universal effect); a DETECTION localizes
structure to at least these blocks, a non-detection bounds it.  In
silico kTAM simulation only; no physical-replicate inference, no
chemical-performance claim, no wet-lab execution.

SMOKE=1 runs 8 trajectories per arm and labels output SMOKE_ONLY; it
is never a verdict surface.
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
SEED0_U1 = BASE_SEED + 17 * SEED_STRIDE      # 500261107 — virgin block
SEED0_U2 = BASE_SEED + 18 * SEED_STRIDE      # 520261107 — virgin block
LATE_OFFSET = 9000                           # window [9000,10000)
N_WIN = 8 if os.environ.get("SMOKE") else 1000
N_CAL = 8 if os.environ.get("SMOKE") else 500

ALPHA = 0.05
MIN_EVENTS = 1600                            # pooled pair-n floor


def log_choose(n, k):
    return (math.lgamma(n + 1) - math.lgamma(k + 1)
            - math.lgamma(n - k + 1))


def fisher_one_sided(xe, ne, xl, nl):
    """Exact one-sided Fisher: p = P(X >= xe | margins fixed),
    early-vs-late 2x2 with H1 share(early) > share(late)."""
    tot = ne + nl
    succ = xe + xl
    denom = log_choose(tot, ne)
    hi = min(ne, succ)
    terms = []
    for k in range(xe, hi + 1):
        logp = (log_choose(succ, k) + log_choose(tot - succ, ne - k)
                - denom)
        terms.append(math.exp(logp))
    return math.fsum(terms)


def fisher_two_sided(xe, ne, xl, nl):
    """Exact two-sided Fisher (sum of table probabilities <= observed),
    for descriptive per-block / cross-block contrasts only."""
    tot = ne + nl
    succ = xe + xl
    denom = log_choose(tot, ne)
    lo = max(0, succ - nl)
    hi = min(ne, succ)
    probs = []
    for k in range(lo, hi + 1):
        logp = (log_choose(succ, k) + log_choose(tot - succ, ne - k)
                - denom)
        probs.append((k, math.exp(logp)))
    obs = None
    for k, p in probs:
        if k == xe:
            obs = p
            break
    return math.fsum(p for _, p in probs if p <= obs * (1 + 1e-9))


def branch_map(xe, ne, xl, nl, cal_ok):
    """Frozen branch map. Returns (branch, tests)."""
    if not cal_ok:
        return "VOID", None
    tests = {"p_fisher_one_sided": fisher_one_sided(xe, ne, xl, nl),
             "alpha": ALPHA, "share_early": xe / float(ne) if ne else None,
             "share_late": xl / float(nl) if nl else None}
    if ne < MIN_EVENTS or nl < MIN_EVENTS:
        return "NO_EVENTS", tests
    if tests["p_fisher_one_sided"] <= ALPHA:
        return "POSITION_DECLINE_DETECTED", tests
    return "POSITION_DECLINE_NOT_DETECTED", tests


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

    cal_tr = [run_traj(b1v, matched_s2, canon, SEED0_CAL + i,
                       DG, WIN_MULT) for i in range(N_CAL)]
    arms = {}
    for name, seed0 in (("u1e", SEED0_U1), ("u1l", SEED0_U1 + LATE_OFFSET),
                        ("u2e", SEED0_U2), ("u2l", SEED0_U2 + LATE_OFFSET)):
        arms[name] = [run_traj(b1v, matched_s2, canon, seed0 + i,
                               DG, WIN_MULT) for i in range(N_WIN)]

    cal_mid = census(cal_tr, "mid")
    cal_ok = (N_CAL != 500 or
              (cal_mid["D2T"] == CAL_D2T and cal_mid["L2"] == CAL_L2))

    censuses = {}
    for name, trajs in arms.items():
        c, n = win_census(trajs)
        censuses[name] = (c, n)

    xe = censuses["u1e"][0]["D2T"] + censuses["u2e"][0]["D2T"]
    ne = censuses["u1e"][1] + censuses["u2e"][1]
    xl = censuses["u1l"][0]["D2T"] + censuses["u2l"][0]["D2T"]
    nl = censuses["u1l"][1] + censuses["u2l"][1]

    branch, tests = branch_map(xe, ne, xl, nl, cal_ok)

    def blk(name):
        c, n = censuses[name]
        return {"x": c["D2T"], "pair_n": n,
                "share": c["D2T"] / float(n) if n else None,
                "wilson95": wilson(c["D2T"], n)}

    b1 = censuses["u1e"]; b2 = censuses["u1l"]
    b3 = censuses["u2e"]; b4 = censuses["u2l"]
    out = {
        "label": "SMOKE_ONLY" if os.environ.get("SMOKE") else "W8_POSFRESH",
        "n_cal": N_CAL, "n_win": N_WIN,
        "seed0_cal": SEED0_CAL, "seed0_u1": SEED0_U1, "seed0_u2": SEED0_U2,
        "late_offset": LATE_OFFSET, "dg": DG, "win_mult": WIN_MULT,
        "t_mid_is_w4": True,
        "cal_mid_w4": cal_mid, "cal": "CAL_OK" if cal_ok else "CAL_FAIL",
        "u1e": blk("u1e"), "u1l": blk("u1l"),
        "u2e": blk("u2e"), "u2l": blk("u2l"),
        "pooled_early": {"x": xe, "pair_n": ne},
        "pooled_late": {"x": xl, "pair_n": nl},
        "observed_delta": (xe / float(ne) - xl / float(nl))
        if (ne and nl) else None,
        "descriptive": {
            "fisher_block_u1_two_sided": fisher_two_sided(
                b1[0]["D2T"], b1[1], b2[0]["D2T"], b2[1]),
            "fisher_block_u2_two_sided": fisher_two_sided(
                b3[0]["D2T"], b3[1], b4[0]["D2T"], b4[1]),
            "fisher_late_vs_late_cross_block": fisher_two_sided(
                b2[0]["D2T"], b2[1], b4[0]["D2T"], b4[1]),
            "fisher_early_vs_early_cross_block": fisher_two_sided(
                b1[0]["D2T"], b1[1], b3[0]["D2T"], b3[1]),
            "u1e_subwindows": subwindow_shares(arms["u1e"], SEED0_U1),
            "u1l_subwindows": subwindow_shares(
                arms["u1l"], SEED0_U1 + LATE_OFFSET),
            "u2e_subwindows": subwindow_shares(arms["u2e"], SEED0_U2),
            "u2l_subwindows": subwindow_shares(
                arms["u2l"], SEED0_U2 + LATE_OFFSET),
        },
        "branch": branch, "tests": tests,
    }
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
