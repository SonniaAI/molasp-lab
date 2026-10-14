#!/usr/bin/env python3
"""Domain-of-exactness envelope for the w8 exact-band tail helpers.

Ticks 129-131 pinned the deep-tail behaviour of
tools/w8_exact_bands.binom_cdf / binom_sf_ge at isolated byte-pinned
points.  This sweep turns those isolated pins into a MEASURED ENVELOPE
over the advertised domain: a stratified (n, p, k) grid, module output
vs the independent per-term-lgamma logsumexp oracle (the established
two-method bar; no shared code with the module under test), max
relative deviation recorded PER BRANCH CLASS:

- short_side  — the helper's short side is summed directly
                (k+1 <= n-k for cdf; n-k+1 <= k for sf_ge);
- deep_direct — tick 131's guard fires: tail mass provably below
                _DEEP_TAIL_DIRECT_SWITCH = 1e-5, so the 1-x complement
                is routed to the direct short-side walk;
- complement  — the 1 - x branch (mid-tail).  Since tick 134's
                geometric tail-ratio bound on the deep-tail guard,
                the guard fires within a few percent of the true
                mass, so NO measured grid point with true mass
                < 1e-5 takes this branch: the tick-132/133
                transition band (worst 1.69e-4 at mass 1.03e-8,
                cdf(2484, 2500, 0.999) — now deep_direct at 2.1e-13)
                is eliminated; the class is bucketed by decade of
                true mass and its deepest bucket is -5.

Deterministic: no RNG, stdlib only.  Two grids:
  full  — n in {100, 500, 1000, 2500, 4999}, p in
          {0.05, 0.246696, 0.25, 0.5, 0.753304, 0.95, 0.999}
  quick — n in {100, 1000}, p in {0.25, 0.753304}  (suite-speed subset)

Comparison floor ORACLE_FLOOR = 1e-290: below it the walk's documented
subnormal-seed behaviour (returns 0.0 below ~1e-304 true mass at
n ~ 5000) makes relative comparison meaningless — such points are
counted as below_floor, never compared.  A module 0.0 while the oracle
sits ABOVE the floor is a hard failure (exit 2).

Usage:
  python3 tools/w8_exactness_envelope.py --grid full   # prints JSON
  python3 tools/w8_exactness_envelope.py --grid quick
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from w8_exact_bands import (  # noqa: E402
    _deep_lower_direct,
    _deep_upper_direct,
    binom_cdf,
    binom_sf_ge,
)

ORACLE_FLOOR = 1e-290
CLASS_BAR = 1e-10          # two-method bar for non-transition classes
TRANSITION_TOP = 1e-4      # complement masses below this: transition band

FULL_NS = (100, 500, 1000, 2500, 4999)
FULL_PS = (0.05, 0.246696, 0.25, 0.5, 0.753304, 0.95, 0.999)
QUICK_NS = (100, 1000)
QUICK_PS = (0.25, 0.753304)
SIGMAS = (0.0, 2.0, 5.0, 9.0)


# --- independent oracle: per-term lgamma + logsumexp (fsum) ---------------

def _log_pmf(j: int, n: int, p: float) -> float:
    return (math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1)
            + j * math.log(p) + (n - j) * math.log1p(-p))


def _cdf_oracle(k: int, n: int, p: float) -> float:
    logs = [_log_pmf(j, n, p) for j in range(k + 1)]
    m = max(logs)
    return math.exp(m + math.log(math.fsum(math.exp(x - m) for x in logs)))


def _sf_oracle(k: int, n: int, p: float) -> float:
    logs = [_log_pmf(j, n, p) for j in range(k, n + 1)]
    m = max(logs)
    return math.exp(m + math.log(math.fsum(math.exp(x - m) for x in logs)))


# --- grid ------------------------------------------------------------------

def k_grid(n: int, p: float) -> list[int]:
    """Endpoints, mode, and +-2/5/9 sigma points (clipped, deduped)."""
    sigma = math.sqrt(n * p * (1.0 - p))
    mode = int((n + 1) * p)
    pts = {0, n, mode}
    for s in SIGMAS:
        for sign in (-1, 1):
            k = int(round(mode + sign * s * sigma))
            if 0 <= k <= n:
                pts.add(k)
    return sorted(pts)


def classify_cdf(k: int, n: int, p: float) -> str:
    if k + 1 <= n - k:
        return "short_side"
    if _deep_lower_direct(k, n, p):
        return "deep_direct"
    return "complement"


def classify_sf(k: int, n: int, p: float) -> str:
    if n - k + 1 <= k:
        return "short_side"
    if _deep_upper_direct(k, n, p):
        return "deep_direct"
    return "complement"


def sweep(ns, ps) -> dict:
    """Run the envelope; returns the receipt dict (or raises on a hard
    module failure — a 0.0 against an above-floor oracle mass)."""
    per_helper = {
        "binom_cdf": {
            "short_side": _ClassAcc("short_side"),
            "complement": _ClassAcc("complement"),
            "deep_direct": _ClassAcc("deep_direct"),
        },
        "binom_sf_ge": {
            "short_side": _ClassAcc("short_side"),
            "complement": _ClassAcc("complement"),
            "deep_direct": _ClassAcc("deep_direct"),
        },
    }
    below_floor = 0
    compared = 0
    for n in ns:
        for p in ps:
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
                    per_helper[helper][classify(k, n, p)].add(rel, k, n, p,
                                                              truth)
    out = {
        "points_compared": compared,
        "points_below_floor": below_floor,
        "oracle_floor": ORACLE_FLOOR,
        "per_helper": {
            h: {c: acc.result() for c, acc in classes.items()}
            for h, classes in per_helper.items()
        },
    }
    return out


class _ClassAcc:
    """Max relative deviation for one branch class, plus per-decade
    buckets for the complement transition band."""

    def __init__(self, name: str):
        self.name = name
        self.max_rel = 0.0
        self.argmax = None          # (k, n, p)
        self.mass_at_argmax = None
        self.buckets = {}           # decade exponent -> max rel

    def add(self, rel: float, k: int, n: int, p: float, truth: float):
        if rel > self.max_rel:
            self.max_rel = rel
            self.argmax = [k, n, p]
            self.mass_at_argmax = truth
        decade = math.floor(math.log10(truth)) if truth > 0 else -999
        if decade not in self.buckets or rel > self.buckets[decade]:
            self.buckets[decade] = rel

    def result(self) -> dict:
        return {
            "max_rel": self.max_rel,
            "argmax_k_n_p": self.argmax,
            "mass_at_argmax": self.mass_at_argmax,
            "decade_buckets": {str(d): self.buckets[d]
                               for d in sorted(self.buckets)},
        }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--grid", choices=("full", "quick"), default="quick")
    args = ap.parse_args()
    ns, ps = (FULL_NS, FULL_PS) if args.grid == "full" else (QUICK_NS,
                                                             QUICK_PS)
    receipt = sweep(ns, ps)
    receipt["grid"] = args.grid
    receipt["grid_ns"] = list(ns)
    receipt["grid_ps"] = list(ps)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
