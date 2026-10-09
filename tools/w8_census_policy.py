#!/usr/bin/env python3
"""w8 collection-day census policy — pre-registered BEFORE the datum (tick 92).

Tick 91 priced, region by region, the pooled census size k at which a
Wilson-95 interval can attribute at all (tools/w8_census_planner.py).
What stayed open is the MECHANICAL collection-day decision: given the
first arm's actual pooled census (x1, k1), what exactly does the loop
queue next, what does it cost in arms/wall, and what is the probability
that the growth census actually attributes.

Pre-registered stage ladder (fixed before any datum exists):
  stage 0: the already-queued first arm (k1 <= 500 fresh-arm terminals).
  stage 1: if the first census's Wilson-95 interval already lies inside a
           single tick-86 s-region -> VERDICT-READY, no growth (the atlas
           still makes the reading; this tool only prices growth).
           Otherwise grow to k_line: the smallest pooled census whose
           >=3-count practical attribution window contains the
           point-estimate line x = round(phat * k), ties away from zero.
  stage 2: only if the grown census is STILL region-ambiguous -> one
           final census at k80: the smallest k whose attribution
           probability under phat is >= 0.80.
  stage 3: ambiguity after stage 2 is EVIDENCE AGAINST the iid pooling
           assumption (tick-91 assumption 1) -> stop growing, receipt
           per-arm dispersion, and escalate with the recommended path
           per the loop-card rule. Never an automatic stage 4.

Point-estimate discipline (assumption, falsifiable at collection): the
ladder is priced under the MLE hypothesis p = phat = x1/k1, NOT a full
posterior integration; attribution probability means
P( Bin(k, phat) lands in the union of the five tick-86 aim windows at k ).
This is a POLICY, not a reader: it never verdicts the science content of
a datum. The frozen collector (tools/collect_w8.py) and the atlas
(tools/w8_decision_atlas.py) remain the only collection-day verdict
surfaces. Constants are imported from the tick-91 planner module and
identity-pinned in tests/test_w8_census_policy.py.
"""

import math
import sys
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.w8_census_planner import (  # noqa: E402
    EPS,
    K_SCAN_MAX,
    MIN_EVENTS,
    REGIONS,
    TERMINALS_PER_ARM,
    WALL_S_PER_ARM,
    Z95,
    aim_window,
    arms_for_k,
    contained,
    serial_wall_hours,
    wilson,
)

P50 = 0.50  # coin-flip attribution threshold (planning floor)
P80 = 0.80  # decisive-census threshold (stage 2)


def round_half_up(v):
    """Ties away from zero on the non-negative domain (tick-91 rounding
    rule; planner uses int(p0*k + 0.5), identical for v >= 0)."""
    return int(math.floor(v + 0.5))


def point_regions(p):
    """Every tick-86 region whose closed/open convention admits the point
    p (mirrors contained()'s EPS semantics exactly). Empty on the edge
    no-man's points (e.g. exactly 0.81415)."""
    out = []
    for region in REGIONS:
        _, _, a, b, lo_side, hi_side = region
        ok = True
        if a is not None:
            ok = (p > a + EPS) if lo_side == "open" else (p >= a - EPS)
        if ok and b is not None:
            ok = (p < b - EPS) if hi_side == "open" else (p <= b + EPS)
        if ok:
            out.append(region)
    return out


def _hi_bounded(x, k, region):
    """contained()'s hi-side pass condition alone (monotone: True for
    small x, False for large x)."""
    _, _, a, b, lo_side, hi_side = region
    if b is None:
        return True
    hi = wilson(x, k)[1]
    if hi_side == "open":
        return hi < b - EPS
    return hi <= b + EPS


def _lo_bounded(x, k, region):
    """contained()'s lo-side pass condition alone (monotone: False for
    small x, True for large x)."""
    _, _, a, b, lo_side, hi_side = region
    if a is None:
        return True
    lo = wilson(x, k)[0]
    if lo_side == "open":
        return lo > a + EPS
    return lo >= a - EPS


def _first_true(pred, k, want):
    """Binary search the boundary of a monotone predicate over x in
    [0, k]. want='last' returns the largest x with pred(x) True (assumes
    True-prefix); want='first' returns the smallest x with pred(x) True
    (assumes True-suffix). None when the prefix/suffix is empty."""
    lo, hi = 0, k
    if want == "last":
        if not pred(lo):
            return None
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if pred(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo
    if not pred(hi):
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if pred(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def aim_window_fast(region, k):
    """aim_window() by binary search instead of linear scan (identical
    endpoint semantics; identity-pinned against the planner in tests).
    Returns [xlo, xhi] or None when empty."""
    _, _, a, b, _, _ = region
    xlo = _first_true(lambda x: _lo_bounded(x, k, region), k, "first")
    if xlo is None:
        return None
    xhi = _first_true(lambda x: _hi_bounded(x, k, region), k, "last")
    if xhi is None or xlo > xhi:
        return None
    if not contained(*wilson(xlo, k), region) or not contained(
        *wilson(xhi, k), region
    ):
        # Knife-edge wobble: settle it exactly the planner's way.
        xs = aim_window(region, k)
        if not xs:
            return None
        return [xs[0], xs[-1]]
    return [xlo, xhi]


def _log_pmf(x, k, p):
    if x == 0:
        return k * math.log1p(-p)
    if x == k:
        return k * math.log(p)
    return (
        math.lgamma(k + 1.0)
        - math.lgamma(x + 1.0)
        - math.lgamma(k - x + 1.0)
        + x * math.log(p)
        + (k - x) * math.log1p(-p)
    )


def attribution_probability(k, phat):
    """P( Bin(k, phat) lands in the union of the five aim windows at k ).
    Exact to float: per-window anchor pmf via lgamma, then the standard
    binomial recurrence inside the window."""
    if not 0.0 < phat < 1.0:
        raise ValueError("phat must be strictly inside (0, 1)")
    total = 0.0
    for region in REGIONS:
        win = aim_window_fast(region, k)
        if win is None:
            continue
        logp = _log_pmf(win[0], k, phat)
        acc = math.exp(logp)
        for x in range(win[0] + 1, win[1] + 1):
            logp += math.log((k - x + 1.0) / x) + math.log(phat / (1.0 - phat))
            acc += math.exp(logp)
        total += acc
    return total


def line_scan(phat, k_start, k_cap=K_SCAN_MAX):
    """Smallest k > k_start whose point-estimate line datum
    x = round(phat*k) has a Wilson-95 CI inside a single region
    (theoretical), and the smallest such k where that region's aim
    window is >= 3 wide AND contains the line count (practical)."""
    theo = None
    prac = None
    for k in range(max(k_start + 1, MIN_EVENTS), k_cap + 1):
        x = round_half_up(phat * k)
        lo, hi = wilson(x, k)
        fits = [r for r in REGIONS if contained(lo, hi, r)]
        if not fits:
            continue
        if theo is None:
            theo = {"k": k, "x": x, "region": fits[0], "lo": lo, "hi": hi}
        if prac is None:
            win = aim_window_fast(fits[0], k)
            if win is not None and (win[1] - win[0] + 1) >= 3 and win[0] <= x <= win[1]:
                prac = {"k": k, "x": x, "region": fits[0], "window": (win[0], win[1])}
        if theo is not None and prac is not None:
            break
    return theo, prac


def prob_scan(phat, k_start, k_cap=K_SCAN_MAX, at_k=None):
    """Smallest k > k_start with attribution probability >= P50 and >= P80
    (stage-2 pricing), plus the probability at a specific k (the stage-1
    line census) when given."""
    p50 = None
    p80 = None
    at = None
    for k in range(max(k_start + 1, MIN_EVENTS), k_cap + 1):
        p = attribution_probability(k, phat)
        if at_k is not None and k == at_k:
            at = {"k": k, "p": p}
        if p50 is None and p >= P50:
            p50 = {"k": k, "p": p}
        if p80 is None and p >= P80:
            p80 = {"k": k, "p": p}
            if at is not None or at_k is None or k >= at_k:
                break
    return p50, p80, at


def policy(x1, k1):
    """The mechanical collection-day decision for a first pooled census
    (x1, k1). Light: no probability scan (that lives in
    collection_report). Total over every 0 <= x1 <= k1, k1 >= MIN_EVENTS."""
    if k1 < MIN_EVENTS:
        raise ValueError("k1 below the MIN_EVENTS floor")
    if not 0 <= x1 <= k1:
        raise ValueError("x out of range")
    w1 = wilson(x1, k1)
    fits = [r for r in REGIONS if contained(w1[0], w1[1], r)]
    if fits:
        return {
            "mode": "verdict_ready",
            "x1": x1,
            "k1": k1,
            "w1": w1,
            "regions": [r[0] for r in fits],
            "growth": None,
        }
    phat = x1 / k1
    theo, prac = line_scan(phat, k1)
    if prac is None:
        return {
            "mode": "escalate_dispersion",
            "x1": x1,
            "k1": k1,
            "w1": w1,
            "phat": phat,
            "k_line_theo": theo["k"] if theo else None,
            "growth": None,
            "reason": (
                "no k <= %d puts a practical line window at p=%.5f; "
                "stage-3 rule: stop growing, receipt per-arm dispersion, "
                "escalate with recommended path" % (K_SCAN_MAX, phat)
            ),
        }
    arms_now = arms_for_k(k1)
    arms_line = arms_for_k(prac["k"])
    add = max(arms_line - arms_now, 0)
    return {
        "mode": "grow",
        "x1": x1,
        "k1": k1,
        "w1": w1,
        "phat": phat,
        "k_line_theo": theo["k"] if theo else None,
        "growth": {
            "k_line_prac": prac["k"],
            "line_x_at_k": prac["x"],
            "region": prac["region"][0],
            "window": prac["window"],
            "total_arms": arms_line,
            "additional_arms": add,
            "growth_wall_hours": add * WALL_S_PER_ARM / 3600.0,
            "growth_wall_note": (
                "%d additional arm(s) x %d s, one running job per owner"
                % (add, WALL_S_PER_ARM)
            ),
        },
    }


def collection_report(x1, k1):
    """policy() plus the stage-2 ladder pricing: attribution probability
    at the stage-1 line census, the P50/P80 census sizes, and the
    expected collection days under the MLE hypothesis."""
    d = policy(x1, k1)
    out = StringIO()
    w = out.write
    w("w8 collection-day census policy (pre-registered tick 92, before the datum)\n")
    w("first census: x=%d / k=%d -> Wilson-95 CI [%.5f, %.5f]\n"
      % (x1, k1, d["w1"][0], d["w1"][1]))
    if d["mode"] == "verdict_ready":
        w("  VERDICT-READY: CI inside %s — no growth census (atlas reads it).\n"
          % "/".join(d["regions"]))
        return out.getvalue()
    if d["mode"] == "escalate_dispersion":
        w("  STAGE-3: %s\n" % d["reason"])
        phat = d["phat"]
        edges = sorted(
            {v for _, _, a, b, _, _ in REGIONS for v in (a, b) if v is not None}
        )
        dmin = min(abs(phat - e) for e in edges)
        k_ext = int(math.ceil(Z95 * Z95 * phat * (1.0 - phat) / (dmin * dmin)))
        w("  outside-cap extrapolation (normal approx, planning-grade only): "
          "k ~ %d to shrink the halfwidth to the nearest-edge distance "
          "%.5f\n" % (k_ext, dmin))
        w("  recommended path on escalation: size the census from k_ext or "
          "accept the\n  region-ambiguous prose; both need a founder-visible "
          "receipt, never a silent retry.\n")
        return out.getvalue()
    g = d["growth"]
    w("  region-ambiguous (crosses an edge) -> stage-1 growth policy:\n")
    w("    line k=%d (theoretical opening k=%s), x_line=%d, region %s\n"
      % (g["k_line_prac"], d["k_line_theo"], g["line_x_at_k"], g["region"]))
    w("    practical window at line k: [%d, %d]\n" % g["window"])
    w("    cost: %s; pooled census %d arms total\n"
      % (g["growth_wall_note"], g["total_arms"]))
    phat = d["phat"]
    p50, p80, at = prob_scan(phat, k1, at_k=g["k_line_prac"])
    if at is not None:
        w("  attribution probability AT the line census: %.3f "
          "(expected collection days under p=%.5f: %.1f)\n"
          % (at["p"], phat, 1.0 / at["p"] if at["p"] > 0 else float("inf")))
    if p50 is not None:
        w("  P>=%.2f at k=%d (%d arm(s), wall %.2f h)\n"
          % (P50, p50["k"], arms_for_k(p50["k"]), serial_wall_hours(p50["k"])))
    if p80 is not None:
        w("  P>=%.2f (stage-2 decisive census) at k=%d (%d arm(s), wall %.2f h)\n"
          % (P80, p80["k"], arms_for_k(p80["k"]), serial_wall_hours(p80["k"])))
    w("  stage ladder: line census -> if still ambiguous, ONE census at the "
      "P>=%.2f k;\n" % P80)
    w("  ambiguity after that = evidence against iid pooling: stop, receipt "
      "per-arm\n  dispersion, escalate with recommended path (never stage 4).\n")
    w("  binding constraint on every arm count: queue admission capacity.\n")
    return out.getvalue()


def main(argv):
    if len(argv) != 3:
        sys.stdout.write("usage: w8_census_policy.py X1 K1\n")
        return 2
    sys.stdout.write(collection_report(int(argv[1]), int(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
