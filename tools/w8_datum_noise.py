#!/usr/bin/env python3
"""Pre-registered DATUM-SIDE census-noise map for w8 collection day
(tick 88, 2026-10-09; queued falsifier ed50c7ba...4daa85).

The frozen W8 gate is NOT touched: HELD iff |s_w8 - 0.83376| <= 0.05
stays the machine verdict on the point estimate, exactly as
pre-registered in evidence/2026-10-08-w8-hazardhold/.  What this tool
prices, BEFORE the datum exists, is the sampling noise the datum
itself will carry: the fresh arm's terminal pair census is a binomial
draw at k <= 500 trajectories, so the measured share's Wilson-95
width is comparable to the instrument band's own halfwidth.  Ticks
86-87 priced prediction-side uncertainty (form axis, fit axis); this
is the third axis: census noise in the datum.

Three pre-registered quantities (pure arithmetic on committed
receipts; deterministic; no datum input):
  1. Wilson-95 widths on the datum share at census
     k in {50, 100, 200, 300, 400, 500} at region-relevant shares.
     (50 = the protocol's MIN_EVENTS floor.)
  2. Exact one-sided binomial verdict-flip risks at the two gate
     edges (floor 0.78376, ceiling 0.88376): for a true share at
     edge +/- d, d in {0.005, 0.01, 0.02, 0.03}, the probability the
     POINT estimate lands on the wrong side of the gate edge.
  3. Region resolvability for the tick-86 five-region reading map:
     which attribution boundaries a Wilson-95 at census k can and
     cannot separate, and the minimum census that would.

Pre-registered reading overlay (prose discipline, NOT a gate):
  collection-day attribution prose may name a form/fit indictment
  only if the datum's Wilson-95 interval lies entirely inside the
  attributed tick-86 region; otherwise the prose must say
  "region-ambiguous at census k".  The verdict itself never moves.

Region bounds (committed receipts, tick-86 note lines 63-64):
  primary band [0.78376, 0.88376]; trend band [0.71415, 0.81415];
  overlap (form-ambiguous) [0.78376, 0.81415].

Usage: python3 tools/w8_datum_noise.py [--json out.json]
"""
import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

PRIMARY = 0.83376          # designs/011 P3 chain w8 point (receipt)
BAND = 0.05                # frozen instrument band (quoted)
FLOOR = 0.78376            # PRIMARY - BAND (gate edge, low)
CEIL = 0.88376             # PRIMARY + BAND (gate edge, high)
TREND_LO = 0.71415         # l2-trend arm 0.76415 - BAND
TREND_HI = 0.81415         # l2-trend arm 0.76415 + BAND
CENSUSES = [50, 100, 200, 300, 400, 500]   # 50 = MIN_EVENTS floor
DELTAS = [0.005, 0.01, 0.02, 0.03]
Z = 1.96                   # same z as the tick-87 Wilson bracket


def _wilson95(k, n, z=Z):
    """Wilson score interval for k successes in n trials — the
    tick-87 formula, reused verbatim for comparability."""
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1.0 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def _max_x_below(k, edge_str):
    """Largest integer x with x/k < edge.  Fraction-exact on the
    decimal edge string, so float rounding can never move a gate
    comparison."""
    t = Fraction(edge_str) * k
    return math.ceil(t) - 1


def _p_le(k, p, m):
    """P(X <= m) for X ~ Bin(k, p): exact tail sum in log space."""
    if m < 0:
        return 0.0
    if m >= k:
        return 1.0
    if not (0.0 < p < 1.0):
        raise ValueError("binomial p must be in (0,1)")
    lg = math.lgamma
    lp = math.log(p)
    lq = math.log1p(-p)
    total = 0.0
    for x in range(0, m + 1):
        total += math.exp(lg(k + 1) - lg(x + 1) - lg(k - x + 1)
                          + x * lp + (k - x) * lq)
    return min(1.0, total)


def _flip_risks(k, edge_str, edge, side):
    """Verdict-flip probabilities at one gate edge, both directions,
    over the delta grid.  side='lo' (floor: REFUTED below the edge)
    or 'hi' (ceiling: REFUTED above the edge).  false_verdict =
    point estimate crosses the edge although the true share is on
    the other side."""
    m = _max_x_below(k, edge_str)     # x <= m  <=>  share < edge
    out = {"edge": edge, "side": side, "x_threshold": m}
    for d in DELTAS:
        if side == "lo":
            inside, outside = edge + d, edge - d
            false_refuted = _p_le(k, inside, m)
            false_held = 1.0 - _p_le(k, outside, m)
        else:
            inside, outside = edge - d, edge + d
            false_refuted = 1.0 - _p_le(k, inside, m)
            false_held = _p_le(k, outside, m)
        out["false_refuted_%+.3f" % d] = false_refuted
        out["false_held_%+.3f" % d] = false_held
    return out


def _quiet_edge(k, edge_str, edge, side, tol=0.025):
    """Bisection: distance delta from the gate edge (on the HELD
    side) at which the wrong-verdict risk falls to <= tol (default
    2.5%, one-sided 95).  side 'lo'/'hi' selects which HELD-side of
    the edge (floor: inside is above; ceiling: inside is below)."""
    def risk(delta):
        p = edge + delta if side == "lo" else edge - delta
        m = _max_x_below(k, edge_str)
        if side == "lo":
            return _p_le(k, p, m)          # P(false REFUTED-low)
        return 1.0 - _p_le(k, p, m)        # P(false REFUTED-high)

    lo_d, hi_d = 0.0, BAND
    if risk(hi_d) > tol:
        return None                        # quiet core empty at k
    for _ in range(60):
        mid = (lo_d + hi_d) / 2.0
        if risk(mid) > tol:
            lo_d = mid
        else:
            hi_d = mid
    return round(hi_d, 5)


def _resolvability(k):
    """Which tick-86 attribution boundaries a Wilson-95 at census k
    separates.  A boundary is datable only if a datum share AT the
    boundary still yields an interval the attribution rule can act
    on; the operational minimum is that the census interval is
    narrower than the narrower adjacent region."""
    regions = {
        "form_ambiguous": (FLOOR, TREND_HI),        # width 0.03039
        "held_hold_only": (TREND_HI, CEIL),         # width 0.06961
        "refuted_trend_alive": (TREND_LO, FLOOR),   # width 0.06961
    }
    bounds = sorted({FLOOR, TREND_HI, CEIL, TREND_LO})
    out = {}
    for b in bounds:
        # Wilson width near share b at census k (evaluate at the
        # boundary share itself; width varies weakly with p here)
        kk = max(1, int(round(b * k)))
        lo, hi = _wilson95(kk, k)
        width = hi - lo
        out["boundary_%.5f" % b] = {
            "wilson95_width_at_k": round(width, 5),
        }
    for name, (rlo, rhi) in regions.items():
        w = rhi - rlo
        kk = max(1, int(round(0.5 * (rlo + rhi) * k)))
        lo, hi = _wilson95(kk, k)
        width = hi - lo
        # minimum census for a datum CI to fit inside this region:
        # Wilson full width ~ 2*z*sqrt(p(1-p)/k) (plus the small
        # correction); solve directly for k.
        p = 0.5 * (rlo + rhi)
        k_min = (2.0 * Z * math.sqrt(p * (1.0 - p)) / w) ** 2
        out["region_" + name] = {
            "width": round(w, 5),
            "wilson95_width_at_k": round(width, 5),
            "resolvable_at_k": bool(width < w),
            "k_needed_point_estimate": int(math.ceil(k_min)),
        }
    return out


def compute():
    """The full pre-registered map.  Deterministic; no datum input."""
    wilson = {}
    for k in CENSUSES:
        for share in (0.71415, 0.76415, 0.78376, 0.81415, 0.83376,
                      0.88376):
            kk = max(1, int(round(share * k)))
            lo, hi = _wilson95(kk, k)
            wilson["k%d_s%.5f" % (k, share)] = [
                round(lo, 5), round(hi, 5), round(hi - lo, 5)]

    flips = {
        "floor": [_flip_risks(k, "0.78376", FLOOR, "lo")
                  for k in CENSUSES],
        "ceiling": [_flip_risks(k, "0.88376", CEIL, "hi")
                    for k in CENSUSES],
    }
    quiet = {
        "floor": {k: _quiet_edge(k, "0.78376", FLOOR, "lo")
                  for k in CENSUSES},
        "ceiling": {k: _quiet_edge(k, "0.88376", CEIL, "hi")
                    for k in CENSUSES},
    }
    resolve = {k: _resolvability(k) for k in CENSUSES}

    # Headline quiet core at the protocol census (k=500): the HELD
    # interior where a wrong verdict stays under 2.5% probability.
    qf = quiet["floor"][500]
    qc = quiet["ceiling"][500]
    quiet_core = None
    if qf is not None and qc is not None:
        quiet_core = [round(FLOOR + qf, 5), round(CEIL - qc, 5)]

    return {
        "primary": PRIMARY, "band": BAND,
        "floor": FLOOR, "ceiling": CEIL,
        "censuses": CENSUSES, "deltas": DELTAS, "z": Z,
        "wilson95": wilson,
        "verdict_flip_risks": flips,
        "quiet_core_k500": quiet_core,
        "resolvability": resolve,
        "reading_overlay": (
            "VERDICT: frozen point gate, untouched. Attribution prose "
            "may name a form/fit indictment only if the datum's "
            "Wilson-95 lies entirely inside the attributed tick-86 "
            "region; otherwise: region-ambiguous at census k."),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out")
    args = ap.parse_args()
    result = compute()
    txt = json.dumps(result, indent=1, sort_keys=True)
    if args.out:
        Path(args.out).write_text(txt + "\n")
        print("wrote %s" % args.out)
    else:
        print(txt)
    # Human headline (stdout always)
    qc = result["quiet_core_k500"]
    w = result["wilson95"]["k500_s0.83376"]
    print("\nHEADLINES (k=500, the protocol census):")
    print("  datum Wilson-95 at share 0.83376: [%.5f, %.5f] width %.5f"
          % (w[0], w[1], w[2]))
    print("  vs frozen band halfwidth 0.05 -> census spans %.0f%% of it"
          % (100.0 * w[2] / BAND))
    if qc:
        print("  quiet core (wrong-verdict risk <= 2.5%%): "
              "[%.5f, %.5f]" % (qc[0], qc[1]))
    r1 = result["resolvability"][500]["region_form_ambiguous"]
    print("  form-ambiguous region width %.5f vs CI width %.5f -> "
          "resolvable at k=500: %s (needs k >= %d)"
          % (r1["width"], r1["wilson95_width_at_k"],
             r1["resolvable_at_k"], r1["k_needed_point_estimate"]))


if __name__ == "__main__":
    main()
