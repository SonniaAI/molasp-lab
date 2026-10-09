#!/usr/bin/env python3
"""w8 decision atlas — the joint collection-day reading surface
(tick 89, 2026-10-09; queued falsifier ed50c7ba...4daa85).

The frozen W8 gate is NOT touched: HELD iff |s_w8 - 0.83376| <= 0.05
stays the machine verdict on the point estimate, exactly as
pre-registered in evidence/2026-10-08-w8-hazardhold/ and implemented
independently in tools/collect_w8.py.  What this tool adds is the ONE
COMMAND that, on collection day, turns the datum (fresh-arm pair
census x of k) into the full pre-registered reading by composing the
three uncertainty axes that ticks 86-88 committed BEFORE the datum:

  axis 1 (tick 86, tools/w8_sensitivity.py):  extrapolation-FORM —
    the five-region reading map (which hazard arms a datum leaves
    alive), with region bounds receipt-quoted below;
  axis 2 (tick 87, tools/w8_param_sensitivity.py): FIT parameters —
    the w1-census Wilson bracket induces w8 width 0.02481 (entirely
    inside HELD: initial conditions can neither create nor rescue a
    verdict) and no odds probe at +/-0.04 reaches refutation, so a
    REFUTED-low datum indicts the late-L2 leak rate (form or fit),
    never initial conditions or odds;
  axis 3 (tick 88, tools/w8_datum_noise.py): DATUM census noise —
    the Wilson-95 the datum carries, the attribution overlay
    (indictment prose allowed only if the Wilson-95 lies entirely
    inside the attributed region), and the k=500 quiet core.

Discipline: the VERDICT comparison is Fraction-exact on the decimal
edge strings (tick-88 guard); the overlay is prose discipline and
compares 5-dp-rounded Wilson endpoints.  All quoted constants are
duplicated from committed receipts on purpose (the reading surface
must not import the instrument under test); tests pin every
duplicated constant back to the tick-86/88 modules.

Usage:
  python3 tools/w8_decision_atlas.py X K [--json out.json]
      X = fresh-arm strict pair terminals, K = fresh-arm census.
"""
import argparse
import json
import math
import os
import sys
from fractions import Fraction

# --- receipt-quoted constants (duplicated; pinned by tests) --------
PRIMARY = 0.83376          # designs/011 P3 / instrument centre (receipt)
BAND = 0.05                # frozen instrument band (receipt)
MIN_EVENTS = 50            # protocol floor (collect_w8.py receipt)
FLOOR_S, CEIL_S = "0.78376", "0.88376"     # gate edges, exact strings
FLOOR, CEIL = float(FLOOR_S), float(CEIL_S)
TREND_LO_S, TREND_HI_S = "0.71415", "0.81415"   # tick-86 region bounds
TREND_LO, TREND_HI = float(TREND_LO_S), float(TREND_HI_S)
QUIET_CORE_K500 = [0.81743, 0.85263]       # tick-88 receipt (k=500)
W1_CENSUS_W8_WIDTH = 0.02481               # tick-87 receipt
Z = 1.96                   # same z as the tick-87/88 Wilson formula


def wilson95(k, n, z=Z):
    """Wilson score interval — the tick-87/88 formula, verbatim."""
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1.0 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


# --- the five tick-86 regions (receipt-quoted reading map) ---------
REGIONS = [
    {"id": 1, "s": "[0.78376, 0.81415]", "verdict": "HELD",
     "name": "form-ambiguous",
     "arms": "A and C alive (B nested): the datum cannot separate "
             "hold-last from the log-linear trend; chain intact"},
    {"id": 2, "s": "(0.81415, 0.88376]", "verdict": "HELD",
     "name": "hold-only",
     "arms": "A only: hold-last confirmed over the trend"},
    {"id": 3, "s": "[0.71415, 0.78376)", "verdict": "REFUTED",
     "name": "trend-alive",
     "arms": "C not A: falsified content is the hazard-HOLD choice, "
             "not the chain account; frozen refutation actions still "
             "apply"},
    {"id": 4, "s": "< 0.71415", "verdict": "REFUTED",
     "name": "chain-falsified",
     "arms": "none: the flux/chain account itself is falsified beyond "
             "w4 (D predicts a FALL below w4's 0.74135)"},
    {"id": 5, "s": "> 0.88376", "verdict": "REFUTED (high)",
     "name": "unmodeled-acceleration",
     "arms": "none: no hazard form predicts above the band; only the "
             "stationary ceiling (0.97865) lies above"},
]

FIT_AXIS = {
    "held": "fit axis (tick 87): initial-condition uncertainty cannot "
            "create or rescue a verdict — the w1 census Wilson-95 "
            "(232:229, n=461) induces w8 width %.5f, entirely inside "
            "HELD; no odds probe at +/-0.04 reaches refutation "
            "(min 0.81664 > floor)." % W1_CENSUS_W8_WIDTH,
    "refuted_low": "fit axis (tick 87): a REFUTED-low datum indicts "
                   "the late-L2 leak rate (form or fit: haz_l2[4] "
                   "x0.5-x2 spans 0.12956 and crosses the floor "
                   "between x0.5 and x0.75) — never initial conditions "
                   "(induced width %.5f, inside HELD) and never odds."
                   % W1_CENSUS_W8_WIDTH,
    "refuted_high": "fit axis (tick 87): no fit axis predicts above "
                    "the band; only the stationary ceiling 0.97865 "
                    "lies above — unmodeled acceleration; the fit-axis "
                    "framing does not apply.",
}


def region_of(share):
    """Tick-86 region containing share (Fraction-exact bounds)."""
    s = Fraction("%0.9f" % share) if isinstance(share, float) \
        else Fraction(share)
    if Fraction(FLOOR_S) <= s <= Fraction(TREND_HI_S):
        return REGIONS[0]
    if Fraction(TREND_HI_S) < s <= Fraction(CEIL_S):
        return REGIONS[1]
    if Fraction(TREND_LO_S) <= s < Fraction(FLOOR_S):
        return REGIONS[2]
    if s < Fraction(TREND_LO_S):
        return REGIONS[3]
    return REGIONS[4]


def region_bounds_exact(region_id):
    """(lo, hi, lo_inclusive, hi_inclusive) as exact Fractions."""
    if region_id == 1:
        return Fraction(FLOOR_S), Fraction(TREND_HI_S), True, True
    if region_id == 2:
        return Fraction(TREND_HI_S), Fraction(CEIL_S), False, True
    if region_id == 3:
        return Fraction(TREND_LO_S), Fraction(FLOOR_S), True, False
    if region_id == 4:
        return None, Fraction(TREND_LO_S), None, False
    return Fraction(CEIL_S), None, True, None


def attribution_allowed(x, k, region):
    """Tick-88 overlay: Wilson-95 (5-dp rounded) entirely inside the
    attributed region.  Open-ended regions use the quoted anchors as
    practical bounds (chain-falsified: [0, 0.71415); unmodeled-
    acceleration: (0.88376, 1]) — prose discipline, not a gate."""
    lo, hi = wilson95(x, k)
    lo, hi = round(lo, 5), round(hi, 5)
    blo, bhi, loi, hii = region_bounds_exact(region["id"])
    blo = 0.0 if blo is None else float(blo)
    bhi = 1.0 if bhi is None else float(bhi)
    ok_lo = lo >= blo if loi is not False else lo > blo
    ok_hi = hi <= bhi if hii is not False else hi < bhi
    return ok_lo and ok_hi, [lo, hi], [blo, bhi]


def attribution_windows(k):
    """Pre-registered at census k: the x-ranges whose datum MAY claim
    each region's attribution under the overlay rule (pure grid
    arithmetic over the census, no datum needed)."""
    out = {}
    for reg in REGIONS[:3]:          # the three closed regions only
        xs = [x for x in range(k + 1)
              if attribution_allowed(x, k, reg)[0]]
        out["region%d_%s" % (reg["id"], reg["name"])] = (
            [min(xs), max(xs)] if xs else [])
    return out


def reading(x, k):
    """The full collection-day reading for datum x of k."""
    if not (isinstance(x, int) and isinstance(k, int)):
        raise TypeError("x and k must be integers")
    if k < 0 or x < 0 or x > k:
        raise ValueError("need 0 <= x <= k")
    if k < MIN_EVENTS:
        return {
            "datum": [x, k], "verdict": "NO_EVENTS",
            "refusal": "census k=%d is below the protocol MIN_EVENTS "
                       "floor (%d) — no reading is emitted, exactly as "
                       "the frozen gate refuses" % (k, MIN_EVENTS),
        }
    s_exact = Fraction(x, k)
    held = Fraction(FLOOR_S) <= s_exact <= Fraction(CEIL_S)
    verdict = "HELD" if held else "REFUTED"
    side = None if held else ("low" if s_exact < Fraction(FLOOR_S)
                              else "high")
    share = x / k
    reg = region_of(s_exact)
    ok, w95, bounds = attribution_allowed(x, k, reg)
    quiet = None
    if k == 500:
        quiet = (QUIET_CORE_K500[0] <= share <= QUIET_CORE_K500[1])
    fit_key = ("held" if held else
               ("refuted_low" if side == "low" else "refuted_high"))
    return {
        "datum": [x, k], "share": round(share, 5),
        "verdict": verdict, "side": side,
        "verdict_rule": "Fraction-exact: HELD iff %s <= %d/%d <= %s"
                        % (FLOOR_S, x, k, CEIL_S),
        "region": {"id": reg["id"], "s": reg["s"],
                   "verdict": reg["verdict"], "name": reg["name"],
                   "arms_alive": reg["arms"]},
        "datum_wilson95_k%d" % k: w95,
        "attribution": {
            "allowed": ok,
            "rule": "indictment prose allowed only if the datum "
                    "Wilson-95 lies entirely inside the attributed "
                    "region (tick 88 overlay)",
            "region_bounds_quoted": bounds,
            "else": "region-ambiguous at census k=%d" % k,
        },
        "quiet_core_k500": (quiet if k == 500 else None),
        "quiet_core_note": ("wrong-verdict risk <= 2.5%% (tick 88 "
                            "receipt) — applies at k=500 only"
                            if k == 500 else
                            "quiet core pinned at k=500 only (tick 88 "
                            "receipt); not quoted at other censuses"),
        "fit_axis": FIT_AXIS[fit_key],
        "gate_untouched": "frozen point gate 0.83376 +/- 0.05 "
                          "(collect_w8.py remains the collector)",
    }


def _prose(r):
    if r.get("verdict") == "NO_EVENTS":
        return ["NO_EVENTS — " + r["refusal"]]
    lines = [
        "datum x=%d of k=%d  ->  share %.5f" % tuple(r["datum"] +
                                                     [r["share"]]),
        "VERDICT  %s%s  (%s)" % (
            r["verdict"], " (" + r["side"] + ")" if r["side"] else "",
            r["verdict_rule"]),
        "REGION %d %s  %s  — %s" % (r["region"]["id"],
                                    r["region"]["name"],
                                    r["region"]["s"],
                                    r["region"]["arms_alive"]),
        "DATUM Wilson-95  %s" % r["datum_wilson95_k%d" % r["datum"][1]],
        "ATTRIBUTION  %s" % ("ALLOWED" if r["attribution"]["allowed"]
                             else r["attribution"]["else"]),
        "QUIET CORE  %s" % r["quiet_core_k500"],
        r["fit_axis"],
        r["gate_untouched"],
    ]
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("x", type=int, help="fresh-arm pair terminals")
    ap.add_argument("k", type=int, help="fresh-arm census")
    ap.add_argument("--json", metavar="OUT", help="also write JSON")
    args = ap.parse_args()
    r = reading(args.x, args.k)
    for line in _prose(r):
        print(line)
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(r, fh, indent=1, sort_keys=True)
        print("wrote %s" % os.path.abspath(args.json))


if __name__ == "__main__":
    sys.exit(main())
