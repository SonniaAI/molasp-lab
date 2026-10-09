#!/usr/bin/env python3
"""w8 follow-up census planner — pre-registered BEFORE the datum (tick 91).

Tick 88/89 established that the queued k<=500 fresh-arm census can barely
attribute anything: the tick-86 s-regions are mostly narrower than the
Wilson-95 interval at k=500 (atlas verdict: region-ambiguous is the
EXPECTED collection-day attribution prose). This tool prices, region by
region, the pooled census size k at which attribution becomes possible at
all, and converts k into cluster arms and serial wall hours so the
follow-up decision is mechanical on collection day.

Receipt-duplicated constants — this file deliberately imports nothing from
the instrument, from tools/collect_w8.py, or from the tick-86/88/89
modules:
  - region bounds: tick-86 five-region map
    (research-log/2026-10-09-w8-extrapolation-sensitivity.md)
  - MIN_EVENTS = 50, <= 500 fresh-arm terminals per arm: tick-80/88 receipts
  - wall 2400 s per arm, one running job per owner: cluster queue contract
  - primary expectation p0 = 0.83376 (hold-last identity, tick-86 receipt)

No interpretive authority: this planner never verdicts a datum. The frozen
collector (tools/collect_w8.py) and the atlas (tools/w8_decision_atlas.py)
remain the only collection-day readers. Pooling assumption is stated in the
output: arms are iid replicates of the same protocol, so terminal counts
pool additively; per-arm dispersion must be receipted before pooling.
"""

import math
import sys
from io import StringIO

Z95 = 1.959963984540054
MIN_EVENTS = 50
TERMINALS_PER_ARM = 500
WALL_S_PER_ARM = 2400
K_SCAN_MAX = 6000
P0 = 0.83376  # hold-last identity arm (tick-86 receipt; 417/500 at k=500)

# (name, gloss, lo, hi, lo_side, hi_side); None = unbounded on that side.
# Sides are the tick-86 conventions: R1 [0.78376,0.81415),
# R2 (0.81415,0.88376], R3 [0.71415,0.78376), R4 <0.71415, R5 >0.88376.
REGIONS = [
    ("R1", "HELD/form-ambiguous",     0.78376, 0.81415, "closed", "open"),
    ("R2", "HELD/hold-only",          0.81415, 0.88376, "open",   "closed"),
    ("R3", "REFUTED-but-trend-alive", 0.71415, 0.78376, "closed", "open"),
    ("R4", "chain-falsified",         None,    0.71415, "unbounded", "open"),
    ("R5", "unmodeled-acceleration",  0.88376, None,    "open",   "unbounded"),
]

# Any Wilson halfwidth at k >= 50 is < 0.139, so a scan window of +/-0.15
# around the finite region bound(s) provably covers every x whose CI could
# be contained in the region.
WINDOW_MARGIN = 0.15
EPS = 1e-9


def wilson(x, k):
    """Wilson score interval at 95% (z pinned above). Returns (lo, hi)."""
    if k <= 0:
        raise ValueError("k must be positive")
    if not 0 <= x <= k:
        raise ValueError("x out of range")
    p = x / k
    z2 = Z95 * Z95
    denom = 1.0 + z2 / k
    center = (p + z2 / (2.0 * k)) / denom
    rad = Z95 * math.sqrt(p * (1.0 - p) / k + z2 / (4.0 * k * k)) / denom
    return center - rad, center + rad


def contained(lo, hi, region):
    _, _, a, b, lo_side, hi_side = region
    if a is not None:
        if lo_side == "closed":
            if lo < a - EPS:
                return False
        else:
            if lo <= a + EPS:
                return False
    if b is not None:
        if hi_side == "closed":
            if hi > b + EPS:
                return False
        else:
            if hi >= b - EPS:
                return False
    return True


def _x_window(region, k):
    _, _, a, b, _, _ = region
    lo_ref = 0.0 if a is None else a
    hi_ref = 1.0 if b is None else b
    start = max(0, math.floor(k * (lo_ref - WINDOW_MARGIN)))
    stop = min(k, math.ceil(k * (hi_ref + WINDOW_MARGIN)))
    return range(start, stop + 1)


def aim_window(region, k):
    """All census counts x whose Wilson-95 CI lies entirely in the region."""
    return [x for x in _x_window(region, k) if contained(*wilson(x, k), region)]


def side_margin(lo, hi, region):
    """Min distance from the CI to the region's finite edges (0 if crossing)."""
    _, _, a, b, lo_side, hi_side = region
    margins = []
    if a is not None:
        margins.append(lo - a if lo_side == "closed" else lo - a)
    if b is not None:
        margins.append(b - hi if hi_side == "closed" else b - hi)
    return min(margins)


def _scan_region(region):
    """Single pass over k: theoretical opening (any count in the region's
    aim window) and practical opening (>= 3 contiguous achievable counts).
    A width-1 window means the census must land on one exact count to
    attribute — true but useless for planning; both numbers are reported."""
    theo = None
    prac = None
    for k in range(MIN_EVENTS, K_SCAN_MAX + 1):
        xs = aim_window(region, k)
        if not xs:
            continue
        if theo is None:
            lo, hi = wilson(xs[0], k)
            theo = {
                "k": k,
                "window": (xs[0], xs[-1]),
                "margin": side_margin(lo, hi, region),
            }
        if prac is None and (xs[-1] - xs[0] + 1) >= 3:
            prac = {"k": k, "window": (xs[0], xs[-1])}
        if theo is not None and prac is not None:
            break
    return theo, prac


def first_open(region):
    """Smallest k in [MIN_EVENTS, K_SCAN_MAX] with a non-empty aim window."""
    return _scan_region(region)[0]


def practical_open(region):
    """Smallest k whose aim window holds >= 3 contiguous counts."""
    return _scan_region(region)[1]


def arms_for_k(k):
    return -(-k // TERMINALS_PER_ARM)


def serial_wall_hours(k):
    return arms_for_k(k) * WALL_S_PER_ARM / 3600.0


def grown_primary_attribution():
    """First k where the primary-expectation datum (round(p0*k) / k) has its
    Wilson-95 CI entirely inside R2 — the 'if truth is the hold-last
    identity, how many arms until the datum separates hold-only from
    form-ambiguous' line. Pre-registered expectation, not a promise: the
    observed pooled share will not equal round(p0*k) exactly."""
    r2 = REGIONS[1]
    for k in range(MIN_EVENTS, K_SCAN_MAX + 1):
        x = int(P0 * k + 0.5)
        lo, hi = wilson(x, k)
        if contained(lo, hi, r2):
            return {"k": k, "x": x, "lo": lo, "hi": hi}
    return None


def build_report():
    out = StringIO()
    w = out.write
    w("w8 follow-up census planner (pre-registered tick 91, before the datum)\n")
    w("attribution = Wilson-95 CI of the pooled fresh-arm terminal census\n")
    w("entirely inside a tick-86 s-region; arms at <=%d terminals/arm;\n"
      % TERMINALS_PER_ARM)
    w("serial wall = arms x %d s (one running job per owner).\n" % WALL_S_PER_ARM)
    w("pooling assumption: arms are iid protocol replicates; receipt per-arm\n")
    w("dispersion before pooling. No verdict authority (frozen gates unread).\n")
    w("\n")
    for region in REGIONS:
        name, gloss = region[0], region[1]
        w("%s %s\n" % (name, gloss))
        win500 = aim_window(region, 500)
        w("  k=500 aim window: %s\n"
          % ("empty" if not win500 else "[%d, %d]" % (win500[0], win500[-1])))
        op, prac = _scan_region(region)
        if op is None:
            w("  no k <= %d admits attribution\n" % K_SCAN_MAX)
        else:
            w("  attribution opens at k=%d (window [%d, %d], min edge margin %.5f)\n"
              % (op["k"], op["window"][0], op["window"][1], op["margin"]))
            if prac is None:
                w("  no k <= %d gives a >=3-count attribution window\n" % K_SCAN_MAX)
            else:
                w("  practical (>=3-count window) opens at k=%d (window [%d, %d])\n"
                  % (prac["k"], prac["window"][0], prac["window"][1]))
                w("  cost if needed: %d arm(s), serial wall %.2f h\n"
                  % (arms_for_k(prac["k"]), serial_wall_hours(prac["k"])))
        w("\n")
    g = grown_primary_attribution()
    w("grown primary (truth = hold-last identity p0=%.5f):\n" % P0)
    if g is None:
        w("  no k <= %d attributes the primary expectation\n" % K_SCAN_MAX)
    else:
        w("  first k=%d (x=%d) attributes: CI [%.5f, %.5f] inside R2\n"
          % (g["k"], g["x"], g["lo"], g["hi"]))
        w("  cost: %d arm(s), serial wall %.2f h\n"
          % (arms_for_k(g["k"]), serial_wall_hours(g["k"])))
    lo500, hi500 = wilson(417, 500)
    w("  k=500 primary datum 417/500 CI [%.5f, %.5f] crosses the R1/R2 edge\n"
      % (lo500, hi500))
    w("  0.81415: region-ambiguous (atlas-expected collection-day reading)\n")
    w("\n")
    w("binding constraint on every arm count above: queue admission capacity\n")
    w("(ci admission floor on spark-4a06; escalation SON-4895, PE lane).\n")
    return out.getvalue()


def main():
    sys.stdout.write(build_report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
