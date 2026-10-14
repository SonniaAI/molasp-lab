#!/usr/bin/env python3
"""Figures for the w8 domain-of-exactness envelope (tick 132 receipt -> 012,
tick 134 geometric-tail-bound receipt -> 013).

Deterministic, stdlib-only: reads a pinned evidence receipt and emits an SVG.
No RNG, no timestamps, no network: byte-stable for a given receipt, which
tests/test_w8_envelope_figure.py pins.  Regenerating after a NEW receipt
changes the figure and requires a fresh pin by design (measure-then-pin,
not pin-then-forget).

All data-dependent text is derived from the receipt (never layout-hardcoded):
the worst-point annotation x follows the decade of its measured mass, the
"decades below" prose is the floor-decade difference, the direct-path bar
label is the ceil-2-sig-fig domain maximum, and the transition band is drawn
only when the receipt still has complement buckets below its edge decade.

Chart: log-log.  X = decade of true tail mass (0 .. -8); Y = max relative
deviation per decade bucket.  Curves are the COMPLEMENT branches of
binom_cdf / binom_sf_ge; the direct paths (short_side / deep_direct) appear
as the annotated two-method bar, one dashed line at 1e-10.
"""

from __future__ import annotations

import argparse
import json
import math
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
TRANSITION_EDGE_DEC = -5              # guard bound >= 1e-5; true mass below

# Text-width model for the in-repo geometry audit (tick 133, catch 10a):
# monospace glyphs are ~0.6 * font-size wide; boxes that would leave the
# canvas or overlap another label are a layout bug, not a style choice.
CHAR_W = 0.6


def fx(dec: int) -> float:
    return L + (dec - X_MIN_DEC) / (X_MAX_DEC - X_MIN_DEC) * PW


def fy(dev: float) -> float:
    return T + (Y_MAX_EXP - math.log10(dev)) / (Y_MAX_EXP - Y_MIN_EXP) * PH


def fmt(dev: float) -> str:
    return f"{dev:.2e}"


def ceil_2sig(v: float) -> float:
    """Round UP to two significant figures (labels stay conservative)."""
    exp = math.floor(math.log10(v))
    scaled = v / 10.0 ** exp          # in [1, 10)
    return math.ceil(scaled * 10) / 10 * 10.0 ** exp


def bucket_curve(helper: dict, branch: str) -> list[tuple[int, float]]:
    buckets = helper[branch]["decade_buckets"]
    pts = [(int(k), float(v)) for k, v in buckets.items() if float(v) > 0.0]
    return sorted(pts, reverse=True)  # decade 0 first (mass near 1)


def _text_w(font_size: float, s: str) -> float:
    return CHAR_W * font_size * len(s)


def render(evidence: dict, evidence_name: str) -> str:
    cdf = evidence["per_helper"]["binom_cdf"]
    sf = evidence["per_helper"]["binom_sf_ge"]
    cdf_pts = bucket_curve(cdf, "complement")
    sf_pts = bucket_curve(sf, "complement")
    worst = cdf["complement"]
    w_k, w_n, w_p = worst["argmax_k_n_p"]
    w_mass = worst["mass_at_argmax"]
    w_dev = worst["max_rel"]
    w_dec = math.floor(math.log10(w_mass))       # annotation x follows the data
    n_cmp = evidence["points_compared"]
    n_below = evidence["points_below_floor"]
    oracle_floor = evidence["oracle_floor"]
    direct_max = max(
        h[b]["max_rel"] for h in (cdf, sf) for b in ("short_side", "deep_direct")
    )
    direct_lab = f"{ceil_2sig(direct_max):.1e}"
    has_band = any(d < TRANSITION_EDGE_DEC for d, _ in cdf_pts + sf_pts)
    decades_below = math.floor(math.log10(CONSUMER_FLOOR)) - w_dec

    s: list[str] = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">')
    a(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    a(f'<text x="{L}" y="24" font-size="14" font-weight="600" fill="{INK}">'
      'Domain-of-exactness envelope — w8 tail helpers (complement branches)</text>')
    a(f'<text x="{L}" y="42" font-size="11" fill="{MUTED}">'
      f'max relative deviation vs decade of true tail mass · {n_cmp} compared · '
      f'{n_below} below the {oracle_floor:.0e} oracle floor (counted, not compared)</text>')
    a(f'<text x="{L}" y="56" font-size="11" fill="{MUTED}">'
      f'stratified grid n {min(evidence["grid_ns"])}..{max(evidence["grid_ns"])}, '
      f'{len(evidence["grid_ps"])} rates · evidence {evidence_name}</text>')

    # Transition band (mass < 1e-5 where the monotone guard bound stays >= 1e-5),
    # drawn ONLY while the receipt still measures buckets below its edge; the
    # geometric tail-ratio bound (tick 134) eliminated them domain-wide.
    if has_band:
        band_x = fx(TRANSITION_EDGE_DEC) + (fx(TRANSITION_EDGE_DEC) - fx(TRANSITION_EDGE_DEC - 1)) / 2
        a(f'<rect x="{band_x:.2f}" y="{T}" width="{L + PW - band_x:.2f}" height="{PH}" fill="{BAND}" stroke="none"/>')
        a(f'<text x="{L + PW}" y="{T + 16}" font-size="11" fill="{MUTED}" text-anchor="end">'
          'transition band: guard bound ≥ 1e-5, true mass below — disclosed, monotone price</text>')
    else:
        a(f'<text x="{L + PW}" y="{T + 16}" font-size="11" fill="{MUTED}" text-anchor="end">'
          'transition band eliminated (geometric tail-ratio bound): no bucket below decade −5</text>')

    # Y grid + ticks (every other decade keeps it calm).
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
    a(f'<text x="{L + 8}" y="{y_bar + 16:.2f}" font-size="11" fill="{INK}">two-method bar 1e-10 (direct paths ≤ {direct_lab} domain-wide)</text>')

    # Curves; end labels staggered so the two helpers never collide in the gutter.
    gutter_labels: list[tuple[float, float, str]] = []   # (baseline_y, x0, text)
    for pts, color, name, dy in ((cdf_pts, CDF_COLOR, "binom_cdf complement", -14),
                                 (sf_pts, SF_COLOR, "binom_sf_ge complement", 4)):
        path = " ".join(f"{'M' if i == 0 else 'L'}{fx(d):.2f},{fy(v):.2f}" for i, (d, v) in enumerate(pts))
        a(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="1.8"/>')
        for d, v in pts:
            a(f'<circle cx="{fx(d):.2f}" cy="{fy(v):.2f}" r="3" fill="{color}"/>')
        last_d, last_v = pts[-1]
        a(f'<text x="{L + PW + 6}" y="{fy(last_v) + dy:.2f}" font-size="11" fill="{color}">{name}</text>')
        gutter_labels.append((fy(last_v) + dy, L + PW + 6, name))

    # Worst-point annotation, above the point (empty region: curves sit lower there).
    # If the receipt's worst point sits low-right (near the gutter labels), lift
    # the pair by one line so the prose cannot collide with a curve label.
    wx, wy = fx(w_dec), fy(w_dev)
    t1 = f'worst {fmt(w_dev)} @ cdf({w_k},{w_n},{w_p}), mass {w_mass:.2e}'
    t2 = f'≈{decades_below} decades below the shallowest consumer comparison'
    lift = 0.0
    for gy, gx, gtxt in gutter_labels:
        if abs((wy - 20) - gy) < 12 and wx + 66 + _text_w(11, t2) > gx:
            lift = 14.0
    a(f'<line x1="{wx:.2f}" y1="{wy - 8:.2f}" x2="{wx + 62:.2f}" y2="{wy - 34 - lift:.2f}" stroke="{CDF_COLOR}" stroke-width="1"/>')
    a(f'<text x="{wx + 66:.2f}" y="{wy - 34 - lift:.2f}" font-size="11" fill="{CDF_COLOR}">{t1}</text>')
    a(f'<text x="{wx + 66:.2f}" y="{wy - 20 - lift:.2f}" font-size="11" fill="{MUTED}">{t2}</text>')

    # Frame + y-axis title.
    a(f'<rect x="{L}" y="{T}" width="{PW}" height="{PH}" fill="none" stroke="{AXIS}"/>')
    a(f'<text x="20" y="{T + PH / 2:.1f}" font-size="11" fill="{MUTED}" text-anchor="middle" '
      f'transform="rotate(-90 20 {T + PH / 2:.1f})">max relative deviation (log10)</text>')
    a('</svg>\n')
    return "\n".join(s)


def audit_text_bounds(svg: str) -> list[str]:
    """Geometry audit (tick 133 catch 10a): every <text> box must sit inside
    the canvas and must not overlap another text box.  Returns violations."""
    import re

    boxes: list[tuple[float, float, float, float, str]] = []
    for m in re.finditer(r'<text ([^>]*)>([^<]*)</text>', svg):
        attrs, txt = m.group(1), m.group(2)
        if "transform" in attrs:
            continue
        def attr(name: str) -> float:
            mm = re.search(rf'{name}="(-?[\d.]+)"', attrs)
            return float(mm.group(1)) if mm else 0.0
        x, y, fs = attr("x"), attr("y"), attr("font-size") or 11.0
        w = _text_w(fs, txt)
        anchor = re.search(r'text-anchor="(\w+)"', attrs)
        if anchor and anchor.group(1) == "end":
            x0 = x - w
        elif anchor and anchor.group(1) == "middle":
            x0 = x - w / 2
        else:
            x0 = x
        boxes.append((x0, y - fs, x0 + w, y + 2, txt))
    bad: list[str] = []
    for x0, y0, x1, y1, txt in boxes:
        if x0 < -0.5 or x1 > W + 0.5 or y0 < 0 or y1 > H:
            bad.append(f"out of canvas: {txt!r} box=({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})")
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            ax0, ay0, ax1, ay1, at = boxes[i]
            bx0, by0, bx1, by1, bt = boxes[j]
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                bad.append(f"overlap: {at!r} vs {bt!r}")
    return bad


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--name", type=str, default=None,
                    help="receipt label for the subtitle (default: evidence dir name)")
    args = ap.parse_args()
    evidence = json.loads(args.evidence.read_text())
    name = args.name if args.name is not None else args.evidence.parent.name
    svg = render(evidence, name)
    args.out.write_text(svg)
    violations = audit_text_bounds(svg)
    for v in violations:
        print(f"AUDIT-FAIL {v}")
    if not violations:
        print("audit: all text boxes in-canvas, no overlaps")
    print(f"wrote {args.out} ({len(svg)} bytes) from {args.evidence}")


if __name__ == "__main__":
    main()
