#!/usr/bin/env python3
"""Exact-Decimal certification of the w8 exactness-envelope maxima.

Tick 132 measured the domain-of-exactness envelope of
tools/w8_exact_bands.binom_cdf / binom_sf_ge against an independent
per-term-lgamma logsumexp oracle and disclosed an honesty limit: the
direct-class maxima (6.4e-11 .. 7.4e-11) "partly reflect the oracle's
own logsumep floor", with the deepest ground truth then being tick
131's isolated Decimal adjudication.  Tick 134 re-measured the
envelope under the geometric tail-ratio bound (transition band
eliminated; receipt evidence/2026-10-14-w8-geometric-tail-bound/
envelope-full.json, sha256 8ed76df3..f844).

This module CLOSES that limit at the extrema: for every branch-class
argmax point recorded in the pinned tick-134 receipt (2 helpers x
{short_side, deep_direct, complement} = 6 points), the true mass is
recomputed by EXACT-INTEGER-factorial Decimal partial sums at prec 80
(the tick-131 method, applied to the envelope's own worst points), and
the module AND the oracle are both scored against that exact truth:

- rel_module  — the module's TRUE deviation (what the envelope claim
  actually claims, oracle noise removed);
- rel_oracle  — the oracle's deviation, i.e. the share of the old
  two-method number that was oracle noise;
- envelope_rel_recomputed — |module - oracle| / oracle recomputed live
  and cross-checked against the receipt's stored max_rel (a drift
  guard: any walk-bit change in either code path flips it).

Method notes (why the truth is exact to ~1e-76 relative):
- Decimal(p) converts the module's ACTUAL float argument to its exact
  binary value, so the truth is the true mass at the p the module,
  oracle and receipt all evaluated — no float-vs-literal gap;
- binomial coefficients are exact integers by O(1) integer recurrence;
- powers are maintained incrementally (one Decimal multiply / divide
  per step, each <= 1 ulp at prec 80), so the per-term relative error
  is <= ~2n ulp_80 <= 1e-76 at n = 4999 — six orders below every
  compared deviation (~1e-9 and up);
- cdf sums j = 0..k and sf_ge sums j = k..n — the DEFINING side in
  every case, never the 1 - x complement, independent of the module's
  branch routing (the recorded class is re-derived live and must match
  the receipt).

Deterministic: stdlib only, no RNG, byte-reproducible.  ZERO kTAM
trajectories, no gate, ladder stays PAUSED.

Usage:
  python3 tools/w8_decimal_certify.py            # prints JSON
  python3 tools/w8_decimal_certify.py --out PATH # writes JSON receipt
"""

from __future__ import annotations

import argparse
import json
from decimal import Decimal, getcontext
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from w8_exact_bands import binom_cdf, binom_sf_ge  # noqa: E402
from w8_exactness_envelope import (  # noqa: E402
    _cdf_oracle,
    _sf_oracle,
    classify_cdf,
    classify_sf,
)

DECIMAL_PREC = 80
SOURCE_RECEIPT = ROOT / "evidence" / "2026-10-14-w8-geometric-tail-bound" \
    / "envelope-full.json"
DIRECT_BAR = 1e-10       # tick 131's two-method bar, now vs exact truth
COMPLEMENT_BAR = 1e-8    # tick 134's complement-safe bar (masses >= 1e-5)


def _decimal_mass(lo: int, hi: int, n: int, p: float) -> Decimal:
    """Exact sum_{j=lo}^{hi} C(n, j) p^j q^(n-j), q = 1 - p, at prec 80.

    Requires 0 <= lo <= hi <= n.  Exact-integer binomials; incremental
    Decimal powers; per-term relative error <= ~2n ulp_80 (~1e-76 at
    n = 4999).  This is ground truth, not a float in disguise: return
    the Decimal itself.
    """
    if not (0 <= lo <= hi <= n):
        raise ValueError(f"need 0 <= lo <= hi <= n, got {lo}, {hi}, {n}")
    getcontext().prec = DECIMAL_PREC
    pd = Decimal(p)                    # exact binary value of the float
    qd = Decimal(1) - pd               # exact at prec 80
    binom = 1
    for j in range(0, lo):             # exact integer C(n, lo)
        binom = binom * (n - j) // (j + 1)
    pw = pd ** lo
    qw = qd ** (n - lo)
    total = Decimal(0)
    for j in range(lo, hi + 1):
        total += Decimal(binom) * pw * qw
        binom = binom * (n - j) // (j + 1)
        pw *= pd
        qw /= qd
    return total


def decimal_cdf(k: int, n: int, p: float) -> Decimal:
    """Exact P(X <= k) on the defining side (sum j = 0..k)."""
    if k < 0:
        return Decimal(0)
    if k >= n:
        return Decimal(1)
    return _decimal_mass(0, k, n, p)


def decimal_sf_ge(k: int, n: int, p: float) -> Decimal:
    """Exact P(X >= k) on the defining side (sum j = k..n)."""
    if k <= 0:
        return Decimal(1)
    if k > n:
        return Decimal(0)
    return _decimal_mass(k, n, n, p)


def _rel_vs_truth(value: float, truth: Decimal) -> float:
    getcontext().prec = DECIMAL_PREC
    return float(abs(Decimal(value) - truth) / truth)


def certify_point(helper: str, k: int, n: int, p: float,
                  cls: str) -> dict:
    """Certify one (helper, point, class) against exact Decimal truth.

    The branch class is re-derived LIVE from the current module guards
    and must match the class the envelope receipt recorded — if a
    future guard change re-routes the point, this raises.
    """
    if helper == "binom_cdf":
        module = binom_cdf(k, n, p)
        oracle = _cdf_oracle(k, n, p)
        live_cls = classify_cdf(k, n, p)
        truth = decimal_cdf(k, n, p)
    elif helper == "binom_sf_ge":
        module = binom_sf_ge(k, n, p)
        oracle = _sf_oracle(k, n, p)
        live_cls = classify_sf(k, n, p)
        truth = decimal_sf_ge(k, n, p)
    else:
        raise ValueError(f"unknown helper {helper!r}")
    if live_cls != cls:
        raise AssertionError(
            f"{helper}({k}, {n}, {p}) now classifies {live_cls!r}, "
            f"receipt recorded {cls!r} — guard drift")
    rel_module = _rel_vs_truth(module, truth)
    rel_oracle = _rel_vs_truth(oracle, truth)
    envelope_rel = abs(module - oracle) / oracle
    bar = DIRECT_BAR if cls != "complement" else COMPLEMENT_BAR
    return {
        "helper": helper,
        "cls": cls,
        "k": k, "n": n, "p": p,
        "module": module,
        "oracle": oracle,
        "truth": str(truth),
        "rel_module_vs_exact": rel_module,
        "rel_oracle_vs_exact": rel_oracle,
        "envelope_rel_recomputed": envelope_rel,
        "bar": bar,
        "module_bar_held": rel_module <= bar,
    }


def certify_receipt(path: Path = SOURCE_RECEIPT) -> dict:
    """Certify every branch-class argmax recorded in the pinned
    envelope receipt.  Pure function of that receipt."""
    receipt = json.loads(Path(path).read_text())
    points = []
    for helper in sorted(receipt["per_helper"]):
        for cls in sorted(receipt["per_helper"][helper]):
            k, n, p = receipt["per_helper"][helper][cls]["argmax_k_n_p"]
            row = certify_point(helper, k, n, p, cls)
            row["envelope_max_rel_recorded"] = receipt["per_helper"][
                helper][cls]["max_rel"]
            points.append(row)
    direct = [r for r in points if r["cls"] != "complement"]
    complement = [r for r in points if r["cls"] == "complement"]
    return {
        "source_receipt": str(Path(path).resolve()
                              .relative_to(ROOT)),
        "decimal_prec": DECIMAL_PREC,
        "points": points,
        "direct_bar": DIRECT_BAR,
        "complement_bar": COMPLEMENT_BAR,
        "all_direct_module_holds_bar":
            all(r["module_bar_held"] for r in direct),
        "all_complement_module_holds_bar":
            all(r["module_bar_held"] for r in complement),
        "max_rel_module_vs_exact_overall":
            max(r["rel_module_vs_exact"] for r in points),
        "max_rel_oracle_vs_exact_overall":
            max(r["rel_oracle_vs_exact"] for r in points),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=None,
                    help="also write the JSON receipt to this path")
    args = ap.parse_args()
    cert = certify_receipt()
    text = json.dumps(cert, indent=2, sort_keys=True)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
