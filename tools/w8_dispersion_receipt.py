#!/usr/bin/env python3
"""w8 stage-3 per-arm dispersion receipt — pre-registered BEFORE the datum (tick 93).

The tick-92 census policy (tools/w8_census_policy.py) fixed the
collection-day growth ladder mechanically: stage 1 verdict-ready or grow
to k_line, stage 2 one final P>=0.80 census, and stage 3 — ambiguity
after stage 2 is EVIDENCE AGAINST the tick-91 iid pooling assumption ->
stop growing, receipt per-arm dispersion, escalate WITH a recommended
path, never an automatic stage 4. Stage 3 named that receipt but nothing
produced it. This tool is the receipt generator, written before any
pooled datum exists.

What it does: given per-arm census counts (x_i, k_i) — one arm = one
queued 500-terminal census run — it prints a dispersion receipt:
per-arm p_hat_i, the pooled p_hat, a leave-one-out pooled p_hat_(-i)
per arm, and a two-sided EXACT binomial p-value per arm
(point-probability method, log-space) testing that arm against the pool
of the OTHER arms only. Leaving the tested arm out is deliberate:
testing an arm against a pool that contains it would shrink its own
surprise.

Pre-registered mechanical rule (fixed now, before the datum):
  POOLING_CONTESTED  iff min_i p_i < alpha        (default alpha 0.05)
  POOLING_SUPPORTED  otherwise
The receipt reports min_exact_p either way. No chi-square statistic:
the ladder pools 2-6 arms, so an asymptotic dispersion statistic would
be decoration; the exact per-arm tests carry the whole rule.

Authority: NONE over the science. This tool adjudicates only the
pooling assumption behind the ladder arithmetic (tick-91 assumption 1);
the frozen collector (tools/collect_w8.py) and the atlas
(tools/w8_decision_atlas.py) remain the only collection-day verdict
surfaces. A CONTESTED receipt voids the arm math and triggers the
stage-3 escalation path — it never HELDs/REFUTEs the substrate.

Caveats, pre-registered: arms are few, the per-arm tests are not
independent (they share one pool), and no multiplicity correction is
applied — alpha is a planning convention in the tick-92 spirit (the
0.50/0.80 thresholds were fixed before the datum; 0.05 is fixed here
before any dispersion exists).
"""

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

DEFAULT_ALPHA = 0.05
_EPS = 1e-9


def logpmf(k: int, p: float, x: int) -> float:
    """log P(X = x) for X ~ Bin(k, p), log-space via lgamma."""
    if x < 0 or x > k:
        return -math.inf
    return (
        math.lgamma(k + 1)
        - math.lgamma(x + 1)
        - math.lgamma(k - x + 1)
        + x * math.log(p)
        + (k - x) * math.log1p(-p)
    )


def exact_two_sided_p(k: int, p: float, x_obs: int) -> float:
    """Two-sided exact binomial p-value, point-probability method:
    P(pmf(X) <= pmf(x_obs)), computed in log-space."""
    if not (0.0 < p < 1.0):
        return 1.0
    lp_obs = logpmf(k, p, x_obs)
    if lp_obs == -math.inf:
        return 1.0
    total = 0.0
    for x in range(k + 1):
        lp = logpmf(k, p, x)
        if lp <= lp_obs + _EPS:
            total += math.exp(lp - lp_obs)
    return min(1.0, total * math.exp(lp_obs))


def parse_arm(token: str):
    """Parse 'x:k' -> (x, k); refuse anything malformed."""
    parts = token.split(":")
    if len(parts) != 2:
        raise ValueError(f"arm must be x:k, got {token!r}")
    x_s, k_s = parts
    try:
        x, k = int(x_s), int(k_s)
    except ValueError:
        raise ValueError(f"arm counts must be integers, got {token!r}")
    if k <= 0:
        raise ValueError(f"arm size must be positive, got {token!r}")
    if x < 0 or x > k:
        raise ValueError(f"arm count out of range [0,k], got {token!r}")
    return x, k


def receipt(arms, alpha: float) -> dict:
    """Build the dispersion receipt for [(x_i, k_i), ...] (>=2 arms)."""
    if len(arms) < 2:
        raise ValueError("dispersion is undefined for fewer than 2 arms")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must lie in (0,1)")
    sum_x = sum(x for x, _ in arms)
    sum_k = sum(k for _, k in arms)
    pooled = sum_x / sum_k
    rows = []
    for i, (x, k) in enumerate(arms):
        loo_x = sum_x - x
        loo_k = sum_k - k
        loo_p = loo_x / loo_k if loo_k > 0 else float("nan")
        p_i = exact_two_sided_p(k, loo_p, x)
        rows.append(
            {
                "arm": i,
                "x": x,
                "k": k,
                "phat": x / k,
                "loo_pooled_phat": loo_p,
                "exact_two_sided_p": p_i,
            }
        )
    min_p = min(r["exact_two_sided_p"] for r in rows)
    verdict = "POOLING_CONTESTED" if min_p < alpha else "POOLING_SUPPORTED"
    return {
        "arms": len(arms),
        "pooled_phat": pooled,
        "alpha": alpha,
        "rows": rows,
        "min_exact_p": min_p,
        "verdict": verdict,
    }


def render(rep: dict) -> str:
    lines = [
        "w8 stage-3 dispersion receipt (pre-registered tick 93, before the datum)",
        f"arms: {rep['arms']}  pooled_phat: {rep['pooled_phat']:.6f}  alpha: {rep['alpha']}",
        "",
        "arm       x     k    p_hat   loo_pooled   exact_p(two-sided)",
    ]
    for r in rep["rows"]:
        lines.append(
            f"{r['arm']:>3}  {r['x']:>5} {r['k']:>5}  {r['phat']:.6f}  "
            f"{r['loo_pooled_phat']:.6f}   {r['exact_two_sided_p']:.6e}"
        )
    lines += [
        "",
        f"min_exact_p: {rep['min_exact_p']:.6e}",
        f"verdict: {rep['verdict']}",
        "authority: pooling assumption only — never a HELD/REFUTED reader",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("arms", nargs="+", help="per-arm census counts as x:k, e.g. 417:500")
    ap.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    args = ap.parse_args(argv)
    try:
        arms = [parse_arm(t) for t in args.arms]
        rep = receipt(arms, args.alpha)
    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(render(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
