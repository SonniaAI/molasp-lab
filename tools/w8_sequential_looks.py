#!/usr/bin/env python3
"""w8 sequential-look error map — pre-registered BEFORE the datum
(tick 94, 2026-10-09; queued falsifier ed50c7ba...4daa85).

The tick-92 census policy froze a STAGED collection ladder:

  look 1: pooled census (x1, k1=500).  Wilson-95 inside one tick-86
          region -> verdict-ready, STOP (the atlas reads it).
          region-ambiguous -> grow to k_line.
  look 2: pooled census (x1 + xg, k_line).  verdict-ready -> STOP.
          still ambiguous -> ONE final census at k80.
  look 3: pooled census (.. + xg2, k80).  verdict-ready -> STOP.
          still ambiguous -> stage 3 (dispersion receipt, escalate;
          NO verdict -- tick 93's receipt lives there).

Stopping is DATA-DEPENDENT (ambiguity at look i buys look i+1), and
tick 88 priced verdict-flip risk at a SINGLE look only.  This tool
closes that gap before any datum exists: the exact probability that
the staged procedure's FINAL gate verdict is wrong, decomposed by
look, under a grid of truth shares s.

Machine verdict (frozen, receipt-duplicated from the collector and
tick-88's datum_noise on purpose -- the duplication is the
independence):  HELD iff Fraction-exact FLOOR*k <= x <= CEIL*k.
The five-region map and Wilson-95 are imported STRUCTURALLY from the
tick-91 planner (wilson, contained, REGIONS), so this module cannot
drift from the surfaces the collection day will actually run.

Pre-registered model (assumptions, falsifiable at collection):
  A1  arms are iid Bin(k_i, s_true) at a common true share
      (tick-91 assumption 1; per-arm dispersion must receipt clean
      before pooling -- tick 93 -- or the ladder voids to stage 3).
  A2  the ladder grows by the CANONICAL committed prices
      k1=500 -> k_line=1442 (3 pooled arms) -> k80=2895 (6 pooled
      arms), the tick-92 prices for the expected phat neighborhood.
      The realized k_line/k80 are phat-dependent (policy prices them
      per datum); the pinned k_line sensitivity in the tests shows
      the error map is flat under plausible movement.
  A3  "verdict-ready" == the atlas attribution rule: Wilson-95
      entirely inside one tick-86 region (contained(), EPS as
      frozen).  "ambiguous" == not that.  A stage-3 stop publishes
      NO verdict and is scored safe (no error event).
  A4  error event == the procedure stops verdict-ready at some look
      AND the frozen gate verdict on that pooled census is wrong
      against the truth:  false-HELD (s outside [FLOOR, CEIL] but
      gate says HELD) or false-REFUTED (s inside, gate says REFUTED).

Usage: python3 tools/w8_sequential_looks.py [--json out.json]
"""
import argparse
import json
import math
import sys
from functools import lru_cache
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.w8_census_planner import REGIONS, contained, wilson  # noqa: E402
from tools.w8_datum_noise import CEIL, FLOOR  # noqa: E402  (receipt-duplicated constants)

K1 = 500                    # stage 0: the queued first arm's ceiling census
K_LINE = 1442               # tick-92 canonical line census (3 pooled arms)
K80 = 2895                  # tick-92 canonical decisive census (6 pooled arms)
GROW2 = K_LINE - K1         # 942 fresh terminals bought by look 2
GROW3 = K80 - K_LINE        # 1453 fresh terminals bought by look 3

TRUTHS = [                  # region edges, arms and +/-0.01 gate-edge probes
    "0.71415",              # chain-falsified / trend-alive boundary
    "0.76415",              # l2-loglinear-trend arm (tick-86 outlier arm)
    "0.77376",              # 0.01 BELOW the floor (false-HELD side)
    "0.78376",              # gate floor (inclusive edge)
    "0.79376",              # 0.01 inside the floor (false-REFUTED side)
    "0.81415",              # form-ambiguous / hold-only boundary (interior)
    "0.83376",              # primary point (tick-86 hold-last identity)
    "0.87376",              # 0.01 inside the ceiling
    "0.88376",              # gate ceiling (inclusive edge)
    "0.89376",              # 0.01 ABOVE the ceiling (false-HELD side)
]
_F_FLOOR = Fraction(FLOOR).limit_denominator(10 ** 6)   # 0.78376 exact
_F_CEIL = Fraction(CEIL).limit_denominator(10 ** 6)     # 0.88376 exact


def _log_binom_table(k, p):
    """log pmf table for Bin(k, p), index 0..k (log-space, stable)."""
    if p <= 0.0:
        t = [float("-inf")] * (k + 1)
        t[0] = 0.0
        return t
    if p >= 1.0:
        t = [float("-inf")] * (k + 1)
        t[k] = 0.0
        return t
    logs = [0.0] + [math.log(i) for i in range(1, k + 1)]
    # binomial coefficient via log recurrence (stable, exact in log space)
    lc = []
    logc = 0.0
    for i in range(k + 1):
        if i > 0:
            logc += logs[k - i + 1] - logs[i]
        lc.append(logc)
    lp = math.log(p)
    lq = math.log1p(-p)
    return [lc[i] + i * lp + (k - i) * lq for i in range(k + 1)]


def _exp(logv):
    return 0.0 if logv == float("-inf") else math.exp(logv)


def _gate_held_x(k):
    """Fraction-exact HELD indicator per pooled count x at census k
    (x/k inside [FLOOR, CEIL], edges inclusive -- the collector's
    decimal-string gate, receipt-duplicated)."""
    lo = math.ceil(_F_FLOOR * k)      # smallest x with x/k >= FLOOR
    hi = math.floor(_F_CEIL * k)      # largest x with x/k <= CEIL
    return [lo <= x <= hi for x in range(k + 1)], lo, hi


def _attr_ok_x(k):
    """Atlas attribution indicator per x at census k: Wilson-95
    entirely inside ONE tick-86 region (frozen contained/EPS)."""
    out = []
    for x in range(k + 1):
        lo, hi = wilson(x, k)
        out.append(any(contained(lo, hi, r) for r in REGIONS))
    return out


@lru_cache(maxsize=None)
def sequential_map(s, k1=K1, k_line=K_LINE, k80=K80):
    """Exact staged-procedure distribution under truth share s.

    Returns per-look stop probabilities, the stage-3 probability,
    and the false-HELD / false-REFUTED error mass with its
    decomposition by look (A1-A4 as pre-registered above).
    """
    sf = float(s)  # pmf arithmetic in float; gate truth stays Fraction-exact
    s_inside = _F_FLOOR <= Fraction(s).limit_denominator(10 ** 8) <= _F_CEIL

    p1 = _log_binom_table(k1, sf)
    held1, _, _ = _gate_held_x(k1)
    attr1 = _attr_ok_x(k1)

    stop1 = e1_wrong = e1_held = e1_refu = 0.0
    amb1 = []          # look-1 counts whose Wilson-95 stays region-ambiguous
    for x1 in range(k1 + 1):
        w = _exp(p1[x1])
        if w == 0.0:
            continue
        if attr1[x1]:
            stop1 += w
            wrong = held1[x1] != s_inside
            if wrong:
                e1_wrong += w
                if held1[x1]:
                    e1_held += w
                else:
                    e1_refu += w
        else:
            amb1.append((x1, w))

    # look 2: pooled (x1 + xg, k_line), only counts ambiguous at look 1
    k2 = k_line
    p2 = _log_binom_table(k2 - k1, sf)
    held2, _, _ = _gate_held_x(k2)
    attr2 = _attr_ok_x(k2)
    stop2 = e2_wrong = e2_held = e2_refu = 0.0
    u_mass = {}        # pooled u -> P(ambiguous at look 2, reached)
    for x1, w1 in amb1:
        for xg in range(k2 - k1 + 1):
            w = w1 * _exp(p2[xg])
            if w == 0.0:
                continue
            u = x1 + xg
            if attr2[u]:
                stop2 += w
                wrong = held2[u] != s_inside
                if wrong:
                    e2_wrong += w
                    if held2[u]:
                        e2_held += w
                    else:
                        e2_refu += w
            else:
                u_mass[u] = u_mass.get(u, 0.0) + w
    amb2 = sorted(u_mass)

    # look 3: pooled (u + xg2, k80), only u still ambiguous
    k3 = k80
    p3 = _log_binom_table(k3 - k2, sf)
    held3, _, _ = _gate_held_x(k3)
    attr3 = _attr_ok_x(k3)
    stop3 = e3_wrong = e3_held = e3_refu = 0.0
    for u in amb2:
        wu = u_mass[u]
        for xg2 in range(k3 - k2 + 1):
            w = wu * _exp(p3[xg2])
            if w == 0.0:
                continue
            if attr3[u + xg2]:
                stop3 += w
                wrong = held3[u + xg2] != s_inside
                if wrong:
                    e3_wrong += w
                    if held3[u + xg2]:
                        e3_held += w
                    else:
                        e3_refu += w
    stage3 = 1.0 - (stop1 + stop2 + stop3)

    return {
        "truth": s,
        "truth_inside_band": s_inside,
        "stop1": stop1,
        "stop2": stop2,
        "stop3": stop3,
        "stage3_no_verdict": stage3,
        "false_held": e1_held + e2_held + e3_held,
        "false_refuted": e1_refu + e2_refu + e3_refu,
        "error_total": e1_wrong + e2_wrong + e3_wrong,
        "by_look": {
            "1": {"stop": stop1, "error": e1_wrong},
            "2": {"stop": stop2, "error": e2_wrong},
            "3": {"stop": stop3, "error": e3_wrong},
        },
    }


@lru_cache(maxsize=None)
def single_look_error(s, k=K1):
    """Tick-88 single-look baseline: gate error at ONE k=500 census,
    no stopping rule (for the optional-stopping inflation ratio)."""
    s_inside = _F_FLOOR <= Fraction(s).limit_denominator(10 ** 8) <= _F_CEIL
    p = _log_binom_table(k, float(s))
    held, _, _ = _gate_held_x(k)
    fh = fr = 0.0
    for x in range(k + 1):
        w = _exp(p[x])
        if w == 0.0:
            continue
        if held[x] and not s_inside:
            fh += w
        if (not held[x]) and s_inside:
            fr += w
    return fh, fr


def build_report():
    rows = []
    for s in TRUTHS:
        m = sequential_map(s)
        fh1, fr1 = single_look_error(s, K1)
        err1 = fh1 + fr1
        m["single_look_error_k500"] = err1
        m["inflation_ratio"] = (m["error_total"] / err1) if err1 > 0 else None
        rows.append(m)
    return {
        "ladder": {"k1": K1, "k_line": K_LINE, "k80": K80},
        "truths": rows,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", metavar="OUT", default=None)
    args = ap.parse_args(argv)
    rep = build_report()
    hdr = ("truth", "insid", "stop1", "stop2", "stop3", "stage3",
           "falseHELD", "falseREFU", "err_seq", "err_1look", "infl")
    print("%-8s %-5s %-7s %-7s %-7s %-7s %-9s %-9s %-8s %-8s %-6s" % hdr)
    for m in rep["truths"]:
        infl = "-" if m["inflation_ratio"] is None else "%.3f" % m["inflation_ratio"]
        print("%-8s %-5s %-7.4f %-7.4f %-7.4f %-7.4f %-9.3e %-9.3e %-8.3e %-8.3e %-6s" % (
            m["truth"], "Y" if m["truth_inside_band"] else "N",
            m["stop1"], m["stop2"], m["stop3"], m["stage3_no_verdict"],
            m["false_held"], m["false_refuted"], m["error_total"],
            m["single_look_error_k500"], infl))
    if args.json:
        Path(args.json).write_text(json.dumps(rep, indent=1) + "\n")
        print("json -> %s" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
