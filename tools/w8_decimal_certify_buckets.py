#!/usr/bin/env python3
"""Exact-Decimal certification of the complement decade-bucket maxima.

Tick 136 closed the envelope's honesty limit AT THE EXTREMA: the six
branch-class argmax points of the pinned tick-134 receipt
(evidence/2026-10-14-w8-geometric-tail-bound/envelope-full.json,
sha256 8ed76df3..f844) were re-scored against exact-integer-factorial
Decimal ground truth (tools/w8_decimal_certify.py, receipt
evidence/2026-10-14-w8-decimal-certify/certify.json).  Its honesty box
disclosed the remaining limit: "certifies the six argmax extrema (the
class-maxima claim), not all 537 grid points".

This module closes the next ring inward for the COMPLEMENT classes --
the branch that actually carries the 1e-8 bar and the figure-013
curves: every per-decade bucket maximum recorded in the receipt
(binom_cdf complement: decades 0,-1..-5, six buckets; binom_sf_ge
complement: decades 0,-1,-2,-5, four buckets) is re-located on the
identical deterministic sweep grid and certified against the same
exact Decimal ground truth.  After this, every point the figure-013
complement curves plot (each bucket's worst measured deviation) is
exact-certified, not just the two global extrema.

Method (identical to tick 136, reused from w8_decimal_certify):
- Decimal(p) converts the module's ACTUAL float argument exactly;
- exact-integer binomial coefficients, incremental powers, prec 80,
  defining-side sums only (cdf j=0..k, sf_ge j=k..n), per-term
  relative error <= ~2n ulp_80 (~1e-76 at n = 4999);
- certify_point re-derives the branch class LIVE and refuses on
  guard drift.

Determinism guards (all must hold, else the run REFUSES):
- re-sweeping the pinned grid with the sweep's own comparison rule
  reproduces every stored decade_buckets value EXACTLY (float ==),
- the re-derived complement class argmax equals the receipt's
  argmax_k_n_p and max_rel EXACTLY,
- points_compared == 537 and points_below_floor == 37 as stored.

Bucket argmax points are not stored in the envelope receipt, so this
tool re-locates them by replaying tools/w8_exactness_envelope.sweep's
iteration (same ns/ps tuples, same k_grid, same rel rule, same
first-strictly-greater tie behaviour).  The chosen point per bucket is
deterministic for a given code state; the value-equality guard proves
the located point carries exactly the receipt's recorded maximum.

Deterministic: stdlib only, no RNG, byte-reproducible.  ZERO kTAM
trajectories, no gate, ladder stays PAUSED.

Usage:
  python3 tools/w8_decimal_certify_buckets.py
  python3 tools/w8_decimal_certify_buckets.py --out PATH
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from w8_exact_bands import binom_cdf, binom_sf_ge  # noqa: E402
from w8_exactness_envelope import (  # noqa: E402
    FULL_NS,
    FULL_PS,
    ORACLE_FLOOR,
    _cdf_oracle,
    _sf_oracle,
    classify_cdf,
    classify_sf,
    k_grid,
)
from w8_decimal_certify import (  # noqa: E402
    COMPLEMENT_BAR,
    DECIMAL_PREC,
    SOURCE_RECEIPT,
    certify_point,
)


def locate_complement_buckets(receipt: dict) -> tuple[dict, dict]:
    """Replay the pinned sweep and return (bucket_points, sweep_facts).

    bucket_points maps (helper, decade) -> (k, n, p) for the
    COMPLEMENT class only, first-strictly-greater tie behaviour, and
    sweep_facts carries the replay's compared/below-floor counts and
    per-helper complement argmax (for the determinism guards).
    """
    buckets: dict[tuple[str, int], list[float]] = {}
    points: dict[tuple[str, int], list[int | float]] = {}
    compared = 0
    below_floor = 0
    comp_max: dict[str, tuple[float, list]] = {}
    for n in FULL_NS:
        for p in FULL_PS:
            for k in k_grid(n, p):
                for helper, module_fn, oracle_fn, classify in (
                    ("binom_cdf", binom_cdf, _cdf_oracle, classify_cdf),
                    ("binom_sf_ge", binom_sf_ge, _sf_oracle, classify_sf),
                ):
                    if helper == "binom_cdf" and (k < 0 or k > n):
                        continue
                    truth = oracle_fn(k, n, p)
                    if truth < ORACLE_FLOOR:
                        below_floor += 1
                        continue
                    got = module_fn(k, n, p)
                    if got == 0.0:
                        raise SystemExit(
                            f"HARD FAILURE: {helper}(k={k}, n={n}, p={p})"
                            f" returned 0.0 against oracle mass {truth!r}")
                    rel = abs(got - truth) / truth
                    compared += 1
                    if classify(k, n, p) != "complement":
                        continue
                    if helper not in comp_max or rel > comp_max[helper][0]:
                        comp_max[helper] = (rel, [k, n, p])
                    decade = math.floor(math.log10(truth)) if truth > 0 \
                        else -999
                    key = (helper, decade)
                    if key not in buckets or rel > buckets[key]:
                        buckets[key] = rel
                        points[key] = [k, n, p]
    facts = {
        "points_compared": compared,
        "points_below_floor": below_floor,
        "complement_argmax": {
            h: {"max_rel": m[0], "argmax_k_n_p": m[1]}
            for h, m in comp_max.items()
        },
    }
    return points, facts


def certify_buckets(path: Path = SOURCE_RECEIPT) -> dict:
    """Locate and exact-certify every complement bucket maximum of the
    pinned envelope receipt.  Pure function of that receipt + code."""
    receipt = json.loads(Path(path).read_text())
    points, facts = locate_complement_buckets(receipt)

    # --- determinism guards: refuse before certifying on any drift ---
    if facts["points_compared"] != receipt["points_compared"]:
        raise AssertionError(
            f"replay compared {facts['points_compared']} points, receipt "
            f"stored {receipt['points_compared']}")
    if facts["points_below_floor"] != receipt["points_below_floor"]:
        raise AssertionError(
            f"replay below-floor {facts['points_below_floor']}, receipt "
            f"stored {receipt['points_below_floor']}")
    rows = []
    for helper in sorted(receipt["per_helper"]):
        stored = receipt["per_helper"][helper]["complement"]
        replay_arg = facts["complement_argmax"][helper]
        if replay_arg["argmax_k_n_p"] != stored["argmax_k_n_p"]:
            raise AssertionError(
                f"{helper} complement argmax drifted: replay "
                f"{replay_arg['argmax_k_n_p']} vs stored "
                f"{stored['argmax_k_n_p']}")
        if replay_arg["max_rel"] != stored["max_rel"]:
            raise AssertionError(
                f"{helper} complement max_rel drifted: replay "
                f"{replay_arg['max_rel']!r} vs stored "
                f"{stored['max_rel']!r}")
        for decade_str, stored_rel in sorted(
                stored["decade_buckets"].items(),
                key=lambda kv: -int(kv[0])):
            decade = int(decade_str)
            key = (helper, decade)
            if key not in points:
                raise AssertionError(
                    f"{helper} complement bucket {decade} missing from "
                    "replay")
            replay_rel = None
            # recover the replay rel for the located point
            k, n, p = points[key]
            row = certify_point(helper, k, n, p, "complement")
            row["decade"] = decade
            row["bucket_rel_recorded"] = stored_rel
            if row["envelope_rel_recomputed"] != stored_rel:
                raise AssertionError(
                    f"{helper} bucket {decade}: located point rel "
                    f"{row['envelope_rel_recomputed']!r} != stored bucket "
                    f"max {stored_rel!r}")
            rows.append(row)

    return {
        "source_receipt": str(Path(path).resolve().relative_to(ROOT)),
        "decimal_prec": DECIMAL_PREC,
        "complement_bar": COMPLEMENT_BAR,
        "buckets_certified": len(rows),
        "points": rows,
        "all_complement_module_holds_bar":
            all(r["module_bar_held"] for r in rows),
        "max_rel_module_vs_exact_overall":
            max(r["rel_module_vs_exact"] for r in rows),
        "max_rel_oracle_vs_exact_overall":
            max(r["rel_oracle_vs_exact"] for r in rows),
        "replay_points_compared": facts["points_compared"],
        "replay_points_below_floor": facts["points_below_floor"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=None,
                    help="also write the JSON receipt to this path")
    args = ap.parse_args()
    cert = certify_buckets()
    text = json.dumps(cert, indent=2, sort_keys=True)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
