#!/usr/bin/env python3
"""Figure for the tick-132 domain-of-exactness envelope (w8 tail helpers).

Deterministic, stdlib-only: reads the pinned evidence receipt
(evidence/2026-10-14-w8-exactness-envelope/envelope-full.json) and emits
designs/assets/012-exactness-envelope.svg.  No RNG, no timestamps, no
network: byte-stable for a given receipt, which tests/test_w8_envelope_figure.py
pins.  Regenerating after a NEW receipt changes the figure and requires a
fresh pin by design (measure-then-pin, not pin-then-forget).

Chart: log-log.  X = decade of true tail mass (0 .. -8); Y = max relative
deviation per decade bucket.  Curves are the COMPLEMENT branches of
binom_cdf / binom_sf_ge (the transition-band story); the direct paths
(short_side / deep_direct) hold <= 7.4e-11 domain-wide and appear as the
annotated two-method bar, one dashed line at 1e-10.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_EVIDENCE = REPO / "evidence/2026-10-14-w8-exactness-envelope/envelope-full.json"
DEFAULT_OUT = REPO / "designs/assets/012-exactness-envelope.svg"

# House style (matches designs/assets/011-window-curve.svg).
FONT = "ui-monospace, Menlo, Consolas, monospace"
INK = "#111"
MUTED = "#8a8a8a"
AXIS = "#444"
GRID = "#e8e8e8"
BAND = "#fff6e5"          # transition band (amber, disclosed price)
BAND_EDGE = "#e8d5a8"
CDF_COLOR = "#1f5fa8"
SF_COLOR = "#2c7a4b"
REF = "#666"

# Layout (viewBox 960x560).
W, H = 960, 560
L, R, T, B = 96, 250, 76, 74
PW, PH = W - L - R, H - T - B

# Plot-domain constants.
X_MIN_DEC, X_MAX_DEC = -8, 0          # decades of true tail mass
Y_MIN_EXP, Y_MAX_EXP = -13, -1        # log10 of relative deviation (floor line fits)
CONSUMER_FLOOR = 8.3e-3               # shallowest frozen consumer comparison
TWO_METHOD_BAR = 1e-10
DIRECT_MAX = 7.4e-11                  # max(short_side, deep_direct) domain-wide
TRANSITION_EDGE_DEC = -5              # guard bound >= 1e-5; true mass below


def fx(dec: int) -> float:
    return L + (dec - X_MIN_DEC) / (X_MAX_DEC - X_MIN_DEC) * PW


def fy(dev: float) -> float:
    import math
    return T + (Y_MAX_EXP - math.log10(dev)) / (Y_MAX_EXP - Y_MIN_EXP) * PH


def fmt(dev: float) -> str:
    return f"{dev:.2e}"


def bucket_curve(helper: dict, branch: str) -> list[tuple[int, float]]:
    buckets = helper[branch]["decade_buckets"]
    pts = [(int(k), float(v)) for k, v in buckets.items() if float(v) > 0.0]
    return sorted(pts, reverse=True)  # decade 0 first (mass near 1)


def render(evidence: dict) -> str:
    cdf = evidence["per_helper"]["binom_cdf"]
    sf = evidence["per_helper"]["binom_sf_ge"]
    cdf_pts = bucket_curve(cdf, "complement")
    sf_pts = bucket_curve(sf, "complement")
    worst = cdf["complement"]
    w_k, w_n, w_p = worst["argmax_k_n_p"]
    w_mass = worst["mass_at_argmax"]
    w_dev = worst["max_rel"]
    n_cmp = evidence["points_compared"]
    n_below = evidence["points_below_floor"]

    s: list[str] = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">')
    a(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    a(f'<text x="{L}" y="24" font-size="14" font-weight="600" fill="{INK}">'
      'Domain-of-exactness envelope — w8 tail helpers (complement branches)</text>')
    a(f'<text x="{L}" y="42" font-size="11" fill="{MUTED}">'
      f'max relative deviation vs decade of true tail mass · {n_cmp} compared · '
      f'{n_below} below the 1e-290 oracle floor (counted, not compared)</text>')
    a(f'<text x="{L}" y="56" font-size="11" fill="{MUTED}">'
      'stratified grid n 100..4999, 7 rates · evidence 2026-10-14-w8-exactness-envelope</text>')

    # Transition band (mass < 1e-5 where the monotone guard bound stays >= 1e-5).
    band_x = fx(TRANSITION_EDGE_DEC) + (fx(TRANSITION_EDGE_DEC) - fx(TRANSITION_EDGE_DEC - 1)) / 2
    a(f'<rect x="{band_x:.2f}" y="{T}" width="{L + PW - band_x:.2f}" height="{PH}" fill="{BAND}" stroke="none"/>')
    a(f'<text x="{L + PW}" y="{T + 16}" font-size="11" fill="{MUTED}" text-anchor="end">'
      'transition band: guard bound ≥ 1e-5, true mass below — disclosed, monotone price</text>')

    # Y grid + ticks (every other decade keeps it calm).
    import math
    for e in range(Y_MIN_EXP, Y_MAX_EXP + 1):
        y = fy(10.0 ** e)
        a(f'<line x1="{L}" y1="{y:.2f}" x2="{L + PW}" y2="{y:.2f}" stroke="{GRID}" stroke-width="1"/>')
        if e % 2 == 0:
            a(f'<text x="{L - 8}" y="{y + 4:.2f}" font-size="11" text-anchor="end" fill="{INK}">1e{e}</text>')

    # X ticks.
    for d in range(X_MIN_DEC, X_MAX_DEC + 1):
        x = fx(d)
        a(f'<line x1="{x:.2f}" y1="{T + PH}" x2="{x:.2f}" y2="{T + PH + 5}" stroke="{AXIS}"/>')
        a(f'<text x="{x:.2f}" y="{T + PH + 20}" font-size="11" text-anchor="middle" fill="{INK}">{d}</text>')
    a(f'<text x="{L + PW / 2:.1f}" y="{T + PH + 42}" font-size="11" text-anchor="middle" fill="{MUTED}">'
      'decade of true tail mass (log10) — measured buckets only</text>')

    # Reference lines: consumer floor (top, label in right gutter on two lines),
    # two-method bar (bottom, label inside the empty lower-left of the plot).
    y_floor = fy(CONSUMER_FLOOR)
    a(f'<line x1="{L}" y1="{y_floor:.2f}" x2="{L + PW}" y2="{y_floor:.2f}" stroke="{REF}" stroke-dasharray="2,4"/>')
    a(f'<text x="{L + PW + 6}" y="{y_floor:.2f}" font-size="11" fill="{REF}">shallowest frozen</text>')
    a(f'<text x="{L + PW + 6}" y="{y_floor + 14:.2f}" font-size="11" fill="{REF}">consumer comparison 8.3e-3</text>')
    y_bar = fy(TWO_METHOD_BAR)
    a(f'<line x1="{L}" y1="{y_bar:.2f}" x2="{L + PW}" y2="{y_bar:.2f}" stroke="{AXIS}" stroke-dasharray="6,4"/>')
    a(f'<text x="{L + 8}" y="{y_bar + 16:.2f}" font-size="11" fill="{INK}">two-method bar 1e-10 (direct paths ≤ 7.4e-11 domain-wide)</text>')

    # Curves; end labels staggered so the two helpers never collide in the gutter.
    for pts, color, name, dy in ((cdf_pts, CDF_COLOR, "binom_cdf complement", -14),
                                 (sf_pts, SF_COLOR, "binom_sf_ge complement", 4)):
        path = " ".join(f"{'M' if i == 0 else 'L'}{fx(d):.2f},{fy(v):.2f}" for i, (d, v) in enumerate(pts))
        a(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.8"/>')
        for d, v in pts:
            a(f'<circle cx="{fx(d):.2f}" cy="{fy(v):.2f}" r="3" fill="{color}"/>')
        last_d, last_v = pts[-1]
        a(f'<text x="{L + PW + 6}" y="{fy(last_v) + dy:.2f}" font-size="11" fill="{color}">{name}</text>')

    # Worst-point annotation, above the point (empty region: curves sit lower there).
    wx, wy = fx(-8), fy(w_dev)
    a(f'<line x1="{wx:.2f}" y1="{wy - 8:.2f}" x2="{wx + 62:.2f}" y2="{wy - 34:.2f}" stroke="{CDF_COLOR}" stroke-width="1"/>')
    a(f'<text x="{wx + 66:.2f}" y="{wy - 34:.2f}" font-size="11" fill="{CDF_COLOR}">'
      f'worst {fmt(w_dev)} @ cdf({w_k},{w_n},{w_p}), mass {w_mass:.2e}</text>')
    a(f'<text x="{wx + 66:.2f}" y="{wy - 20:.2f}" font-size="11" fill="{MUTED}">≈5 decades below the shallowest consumer comparison</text>')

    # Frame + y-axis title.
    a(f'<rect x="{L}" y="{T}" width="{PW}" height="{PH}" fill="none" stroke="{AXIS}"/>')
    a(f'<text x="20" y="{T + PH / 2:.1f}" font-size="11" fill="{MUTED}" text-anchor="middle" '
      f'transform="rotate(-90 20 {T + PH / 2:.1f})">max relative deviation (log10)</text>')
    a('</svg>\n')
    return "\n".join(s)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    evidence = json.loads(args.evidence.read_text())
    svg = render(evidence)
    args.out.write_text(svg)
    print(f"wrote {args.out} ({len(svg)} bytes) from {args.evidence}")


if __name__ == "__main__":
    main()
