#!/usr/bin/env python3
"""Deterministic SVG of the designs/011 window-indexed pricing curve.

Every number is read from ``molasp.offchannel.marginal_window_pricing()``
(committed receipts only — the tick-37 static rule).  No plotting
dependencies; identical curve inputs give byte-identical SVG.  The w8
point is drawn as VERDICT PENDING until the pre-registered falsifier's
receipt is imported (see research-log/2026-10-08-w8-hazardhold.md).

Usage: python3 tools/window_curve_svg.py [out.svg] [--w8-mode pending|held|refuted]
       python3 tools/window_curve_svg.py --receipt verdict.json [out.svg]
Default output: designs/assets/011-window-curve.svg (repo-relative).
--w8-mode pending (default) keeps the open VERDICT-PENDING point, byte-identical
to the tick-79 render; held draws the measured w8 point closed with its Wilson
95 bar (numbers from --receipt / apply_w8_receipt.py); refuted omits the
beyond-w4 extrapolation entirely (pre-registered quarantine).
"""

from pathlib import Path
import sys

W, H = 880, 560
ML, MR, MT, MB = 70, 216, 46, 64
PW, PH = W - ML - MR, H - MT - MB
XMIN, XMAX = 0.5, 8.6
YMIN, YMAX = 0.40, 0.90
XW = [1, 2, 3, 4, 8]  # window indices with rows in the curve


def _x(w):
    return ML + (w - XMIN) / (XMAX - XMIN) * PW


def _y(s):
    return MT + (YMAX - s) / (YMAX - YMIN) * PH


def _esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# label, lo, hi, fill  (share bands; labels kept clear of the w8 stack)
TIER_BANDS = [
    ("contested  < 0.55", YMIN, 0.55, "#fdecea"),
    ("ratchet-tilting  0.55-0.75", 0.55, 0.75, "#fff6e5"),
    ("ratchet-tilted  >= 0.75", 0.75, YMAX, "#e9f7ee"),
]
TIER_LABEL_Y = {"contested  < 0.55": _y(0.462),
                "ratchet-tilting  0.55-0.75": _y(0.645),
                "ratchet-tilted  >= 0.75": _y(0.873)}


def render(curve=None, w8_mode="pending", w8=None):
    from molasp.offchannel import marginal_window_pricing
    c = curve or marginal_window_pricing()
    wins = c["windows"]
    if w8_mode not in ("pending", "held", "refuted"):
        raise ValueError("w8_mode must be pending|held|refuted")
    if w8_mode == "held" and not w8:
        raise ValueError("held mode needs the receipt numbers (share/census/wilson95/dev)")
    out = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
      f'font-family="ui-monospace, Menlo, Consolas, monospace">')
    a(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    a(f'<text x="{ML}" y="26" font-size="14" font-weight="600" fill="#111">'
      f'Window-indexed marginal pricing — fill share vs read window '
      f'(BUILD1 Vp-missing, s2, dG 2)</text>')

    # tier bands (share semantics: value < band edge)
    for label, lo, hi, fill in TIER_BANDS:
        y1, y2 = _y(hi), _y(lo)
        a(f'<rect x="{ML}" y="{y1:.2f}" width="{PW}" height="{y2 - y1:.2f}" fill="{fill}"/>')
    for label, _, _, _ in TIER_BANDS:
        a(f'<text x="{ML + PW - 140:.2f}" y="{TIER_LABEL_Y[label]:.2f}" font-size="11" '
          f'fill="#8a8a8a" text-anchor="end">{_esc(label)}</text>')

    # axes
    a(f'<rect x="{ML}" y="{MT}" width="{PW}" height="{PH}" fill="none" stroke="#444"/>')
    v = YMIN
    while v <= YMAX + 1e-9:
        a(f'<line x1="{ML - 5}" y1="{_y(v):.2f}" x2="{ML}" y2="{_y(v):.2f}" stroke="#444"/>')
        a(f'<text x="{ML - 8}" y="{_y(v) + 4:.2f}" font-size="11" text-anchor="end" '
          f'fill="#111">{v:.2f}</text>')
        v += 0.05
    for w in XW:
        a(f'<line x1="{_x(w):.2f}" y1="{MT + PH}" x2="{_x(w):.2f}" y2="{MT + PH + 5}" stroke="#444"/>')
        a(f'<text x="{_x(w):.2f}" y="{MT + PH + 20}" font-size="12" text-anchor="middle" '
          f'fill="#111">w{w}</text>')
    a(f'<text x="{ML + PW / 2:.2f}" y="{MT + PH + 40}" font-size="12" text-anchor="middle" '
      f'fill="#111">read window index w (window = w x 400 e^Gmc, Gmc 9.5)</text>')

    # reference lines: window-blind stationary + DW11 frozen persist
    homo = c["homo_stationary"]
    a(f'<line x1="{ML}" y1="{_y(homo):.2f}" x2="{ML + PW}" y2="{_y(homo):.2f}" '
      f'stroke="#8a8a8a" stroke-width="1.5" stroke-dasharray="4 4"/>')
    a(f'<text x="{ML + 120}" y="{_y(homo) + 16:.2f}" font-size="11" fill="#666">'
      f'window-blind stationary {homo:.4f}</text>')
    frozen = c["frozen_class"]["persist"]
    a(f'<line x1="{ML}" y1="{_y(frozen):.2f}" x2="{ML + PW}" y2="{_y(frozen):.2f}" '
      f'stroke="#333" stroke-width="1.5" stroke-dasharray="2 4"/>')
    a(f'<text x="{ML + 120}" y="{_y(frozen) - 6:.2f}" font-size="11" fill="#333">'
      f'frozen class persist {frozen:.3f} (DW11, window-immune)</text>')

    # chain: solid through w4 (fit-grid), dashed w4->w8 (extrapolated;
    # the extrapolated arm is quarantined out on a refuted receipt)
    fit_pts = " ".join(f"{_x(w):.2f},{_y(wins[str(w)]['chain_share']):.2f}" for w in (1, 2, 3, 4))
    w8row = wins["8"]
    a(f'<polyline class="chain-fit" points="{fit_pts}" fill="none" '
      f'stroke="#1f6feb" stroke-width="2"/>')
    if w8_mode != "refuted":
        a(f'<line class="chain-extrap" x1="{_x(4):.2f}" y1="{_y(wins["4"]["chain_share"]):.2f}" '
          f'x2="{_x(8):.2f}" y2="{_y(w8row["chain_share"]):.2f}" stroke="#1f6feb" stroke-width="2" '
          f'stroke-dasharray="7 5"/>')

    # measured points w1-w4 with census + share labels
    for w in (1, 2, 3, 4):
        row = wins[str(w)]
        x, y = _x(w), _y(row["measured_share"])
        a(f'<circle class="measured" cx="{x:.2f}" cy="{y:.2f}" r="5" fill="#111"/>')
        a(f'<text x="{x:.2f}" y="{y - 12:.2f}" font-size="11" text-anchor="middle" '
          f'fill="#111">{_esc(row["measured_census"])}</text>')
        a(f'<text x="{x:.2f}" y="{y + 18:.2f}" font-size="10" text-anchor="middle" '
          f'fill="#777">{row["measured_share"]:.4f}</text>')

    # w8: hazard-95 bracket + (pending|measured|quarantined) + right-margin stack
    hx, c8, h95 = _x(8), w8row["chain_share"], w8row["hazard95_share"]
    lx = hx + 14
    if w8_mode == "refuted":
        a(f'<text class="w8-quarantined" x="{lx:.2f}" y="{_y(c8):.2f}" font-size="11" '
          f'font-weight="600" fill="#b35900">'
          f'beyond-w4 extrapolation QUARANTINED — w8 refuted (receipt)</text>')
    else:
        a(f'<line class="hazard95" x1="{hx:.2f}" y1="{_y(h95):.2f}" x2="{hx:.2f}" '
          f'y2="{_y(c8):.2f}" stroke="#b35900" stroke-width="1.5"/>')
        for yy in (_y(h95), _y(c8)):
            a(f'<line class="hazard95" x1="{hx - 5:.2f}" y1="{yy:.2f}" x2="{hx + 5:.2f}" '
              f'y2="{yy:.2f}" stroke="#b35900" stroke-width="1.5"/>')
        if w8_mode == "pending":
            a(f'<circle class="w8-pending" cx="{hx:.2f}" cy="{_y(c8):.2f}" r="6" fill="none" '
              f'stroke="#b35900" stroke-width="2.5"/>')
        a(f'<text x="{lx:.2f}" y="{_y(c8) - 8:.2f}" font-size="11" fill="#b35900">'
          f'chain {c8:.4f} (extrapolated)</text>')
        a(f'<text x="{lx:.2f}" y="{_y(h95) + 16:.2f}" font-size="11" fill="#b35900">'
          f'hazard-95 bracket {h95:.4f}</text>')
        if w8_mode == "pending":
            a(f'<text x="{lx:.2f}" y="{_y(h95) + 32:.2f}" font-size="11" font-weight="600" '
              f'fill="#b35900">VERDICT PENDING — falsifier queued</text>')
    if w8_mode == "held":
        lo, hi = w8["wilson95"]
        ylo, yhi = _y(hi), _y(lo)   # share axis grows upward
        a(f'<line class="w8-wilson95" x1="{hx:.2f}" y1="{ylo:.2f}" x2="{hx:.2f}" '
          f'y2="{yhi:.2f}" stroke="#111" stroke-width="1.5"/>')
        for yy in (ylo, yhi):
            a(f'<line class="w8-wilson95" x1="{hx - 5:.2f}" y1="{yy:.2f}" x2="{hx + 5:.2f}" '
              f'y2="{yy:.2f}" stroke="#111" stroke-width="1.5"/>')
        ym = _y(w8["share"])
        a(f'<circle class="w8-measured" cx="{hx:.2f}" cy="{ym:.2f}" r="5" fill="#111"/>')
        a(f'<text x="{hx:.2f}" y="{ym - 12:.2f}" font-size="11" text-anchor="middle" '
          f'fill="#111">{_esc(w8["census"])}</text>')
        a(f'<text x="{hx:.2f}" y="{ym + 18:.2f}" font-size="10" text-anchor="middle" '
          f'fill="#777">{w8["share"]:.4f}</text>')
        a(f'<text x="{lx:.2f}" y="{_y(h95) + 48:.2f}" font-size="11" font-weight="600" '
          f'fill="#111">w8 MEASURED — HELD (|d| {w8["dev"]:.4f} &lt;= 0.05)</text>')

    # legend + caption
    legend = '● measured (census)   ─ chain fit   – – chain extrapolated   ▮ hazard-95 bracket'
    if w8_mode == "held":
        legend += '   │ w8 Wilson 95'
    elif w8_mode == "refuted":
        legend = '● measured (census)   ─ chain fit (through w4)'
    a(f'<text x="{ML + 10}" y="{MT + PH - 12}" font-size="11" fill="#555">'
      f'{_esc(legend)}</text>')
    if w8_mode == "pending":
        caption = ('Deterministic render from committed receipts (tools/window_curve_svg.py, '
                   'tick-37 rule). w8 extrapolated with hazard-95 bracket; verdict pending '
                   'queue job ed50c7ba…4daa85.')
    elif w8_mode == "held":
        caption = ('Deterministic render from committed receipts (tools/window_curve_svg.py, '
                   'tick-37 rule). w8 MEASURED (closed point, Wilson 95 bar) from the receipt '
                   'of queue job ed50c7ba…4daa85; dashed chain w8 remains the prediction.')
    else:
        caption = ('Deterministic render from committed receipts (tools/window_curve_svg.py, '
                   'tick-37 rule). Beyond-w4 extrapolation quarantined per the pre-registered '
                   'refutation (receipt of queue job ed50c7ba…4daa85); w1–w4 measured '
                   'receipts unchanged.')
    a(f'<text x="{ML}" y="{H - 8}" font-size="10" fill="#888">{_esc(caption)}</text>')
    a('</svg>')
    return "\n".join(out) + "\n"


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out", nargs="?", help="output path (default designs/assets/011-window-curve.svg)")
    ap.add_argument("--w8-mode", choices=("pending", "held", "refuted"), default="pending")
    ap.add_argument("--receipt", help="verdict.json from tools/collect_w8.py; derives the mode")
    args = ap.parse_args(argv)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    nums = None
    if args.receipt:
        import json
        with open(args.receipt) as fh:
            r = json.load(fh)
        branch = r.get("branch")
        if branch == "CAL_OK+HELD":
            args.w8_mode = "held"
            d = r["descriptive"]
            cen = d["fresh_terminal_census"]
            nums = {"share": d["fresh_terminal_share"],
                    "census": "%d:%d" % (cen["D2T"], cen["L2"]),
                    "wilson95": d["fresh_w8_wilson95"],
                    "dev": d["dev_vs_pred_w8"]}
        elif branch == "CAL_OK+REFUTED":
            args.w8_mode = "refuted"
        else:
            print("figure refuses branch %r (no verdict to draw)" % branch, file=sys.stderr)
            return 2
    out = Path(args.out) if args.out else (
        Path(__file__).resolve().parents[1] / "designs" / "assets" / "011-window-curve.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(w8_mode=args.w8_mode, w8=nums), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(["window_curve_svg"]))
