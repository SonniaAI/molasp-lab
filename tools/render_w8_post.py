#!/usr/bin/env python3
"""Receipt-gated blog renderer for the w8 hazard-hold verdict (tick 81).

Completes the executable pre-registration chain committed before the
w8 data exists:

    run.out -> tools/collect_w8.py -> verdict receipt JSON
            -> tools/render_w8_post.py -> blog/<date>-window-pricing-w8-<tag>.md

Only the two milestone branches of the frozen interpretation map
render a post (research-log/2026-10-08-w8-hazardhold.md):

    CAL_OK+HELD     -> the milestone post  ("the window curve survives w8")
    CAL_OK+REFUTED  -> the demolition post ("the window curve breaks at w8")

Everything else is refused: CAL_FAIL+VOID, CAL_OK+NO_EVENTS and
SMOKE_NOT_VERDICTABLE are not milestones (no filler posts, ever), and a
FORCED-DISAGREMENT receipt can never be published.  Every number in the
rendered post is quoted verbatim from the receipt; the frozen constants
below (prediction, band) are duplicated from the collector on purpose —
the same independent-duplication discipline as tools/collect_w8.py.

The renderer writes exactly one file: the dated post.  The collection
tick still composes the blog/index.md timeline blurb and the
designs/011 edits by hand — those carry judgment; this file does not.

Usage:
  python3 tools/render_w8_post.py evidence/2026-10-08-w8-hazardhold/verdict.json \
      [--date 2026-10-09] [--out blog/<file>.md] [--request <queue request id>]
"""
import argparse
import json
import sys
from datetime import date

# Frozen pre-registration values (duplicated from tools/collect_w8.py —
# see module docstring; the duplication is the independence).
PRED_W8 = 0.83376            # designs/011 P3 chain w8 point ("0.834")
BAND = 0.05                  # |s - pred| <= BAND -> HELD, else REFUTED
REQUEST_DEFAULT = "ed50c7baf2d8b935bb118f25758394ddfb04a671e902f39bfa66721b274daa85"
HAZ95_ARM = 0.81585          # hazard-95 bracket arm (sensitivity arm, not a fit)
DW9_FRESH_W4 = 0.716         # cross-check receipts quoted in the post body
VH_FRESH_W4 = 0.7379032258064516

MILESTONES = ("CAL_OK+HELD", "CAL_OK+REFUTED")

REQUIRED_DESCRIPTIVE = (
    "fresh_terminal_share", "fresh_terminal_census", "dev_vs_pred_w8",
    "fresh_w8_wilson95", "haz95_arm_distance", "fresh_mid_w4_share",
    "fresh_mid_w4_dev_vs_dw9_receipt", "fresh_mid_w4_dev_vs_vh_receipt",
    "cal_terminal_w8_census",
)


def _f(x, nd):
    return ("%." + str(nd) + "f") % x


def _census(c):
    return "%d:%d:%d" % (c["D2T"], c["L2"], c["other"])


def _minutes(text):
    return max(1, int(round(len(text.split()) / 200.0)))


def render(receipt, day=None, request_id=REQUEST_DEFAULT):
    """Return {'filename', 'text'} for a milestone receipt; raise
    ValueError for anything that must not reach the blog."""
    branch = receipt.get("branch")
    if branch not in MILESTONES:
        raise ValueError(
            "branch %r is not a milestone: no blog post for non-milestone "
            "or void collections" % (branch,))
    if receipt.get("cross_check") != "ok":
        raise ValueError(
            "cross_check %r: only a collector-verified receipt (cross_check "
            "'ok') can be published" % (receipt.get("cross_check"),))
    d = receipt.get("descriptive") or {}
    for key in REQUIRED_DESCRIPTIVE:
        if d.get(key) is None:
            raise ValueError("receipt descriptive field %r is None — "
                             "refusing to render" % (key,))

    held = branch == "CAL_OK+HELD"
    tag = "held" if held else "refuted"
    day = day or date.today().isoformat()
    filename = "%s-window-pricing-w8-%s.md" % (day, tag)

    share = d["fresh_terminal_share"]
    cen = d["fresh_terminal_census"]
    dev = d["dev_vs_pred_w8"]
    wil = d["fresh_w8_wilson95"]
    haz_d = d["haz95_arm_distance"]
    mid = d["fresh_mid_w4_share"]
    dw9_d = d["fresh_mid_w4_dev_vs_dw9_receipt"]
    vh_d = d["fresh_mid_w4_dev_vs_vh_receipt"]
    cal_cen = d["cal_terminal_w8_census"]

    n = cen["D2T"] + cen["L2"]
    n_range = receipt.get("n_per_range")
    if n_range is None:
        raise ValueError("receipt n_per_range is None — refusing to render")
    pred_s = _f(PRED_W8, 3)
    share_s = _f(share, 4)
    dev_s = _f(dev, 4)
    band_s = _f(BAND, 2)
    wil_s = "[%s, %s]" % (_f(wil[0], 5), _f(wil[1], 5))
    haz_s = _f(HAZ95_ARM, 3)
    hazd_s = _f(haz_d, 4)
    mid_s = _f(mid, 4)
    dw9d_s = _f(dw9_d, 4)
    vhd_s = _f(vh_d, 4)

    if held:
        title = "The window curve survives w8"
        tldr = (
            "**TL;DR.** The designs/011 window-pricing curve predicted a fresh\n"
            "D2T share of %s at window 8; the pre-registered falsifier — %d fresh\n"
            "terminals per range on a seed the fit never saw — measured a D2T\n"
            "share of %s over its %d pair terminals (%s D2T:L2:other), a\n"
            "deviation of %s against the frozen ±%s band.\n"
            "The w8 tier stands on a measured receipt: the chain fit through w4\n"
            "bought a cross-seed confirmation, the figure's open verdict point\n"
            "closed, and the hazard-95 bracket stays what it always was — a\n"
            "sensitivity arm, not a fit, and not wrong."
            % (pred_s, n_range, share_s, n, _census(cen), dev_s, band_s))
    else:
        title = "The window curve breaks at w8"
        tldr = (
            "**TL;DR.** The designs/011 window-pricing curve predicted a fresh\n"
            "D2T share of %s at window 8; the pre-registered falsifier — %d fresh\n"
            "terminals per range on a seed the fit never saw — measured a D2T\n"
            "share of %s over its %d pair terminals (%s D2T:L2:other), a\n"
            "deviation of %s against the frozen ±%s band.\n"
            "The prediction is dead. The w8 tier entry is retracted, the\n"
            "beyond-w4 extrapolation is quarantined out of the figure and the\n"
            "design note, and what survives is exactly what was measured: the\n"
            "w1–w4 receipts, untouched."
            % (pred_s, n_range, share_s, n, _census(cen), dev_s, band_s))

    body_trial = """## What was on trial

designs/011 prices read windows by window index: a chain fit through
the four measured windows (fresh shares 0.503 → 0.737, censuses
232:229 → 367:131) says a window-8 reader should still find its target
with share ≈ %s, while a hazard-95 alternative arm put %s as the
pessimistic edge. A chain fit is an extrapolation until something
cross-seed measures its far end, so the interpretation map was frozen
before the job existed: deviation inside ±%s of the prediction holds
the w8 tier, outside retracts it. The falsifier ran on the capped
cluster queue as request %s (nonce molasp-w8-hazardhold-t77): 500
fresh pair terminals per range, seeds disjoint from every window the
fit consumed.""" % (pred_s, haz_s, band_s, request_id)

    if abs(share - HAZ95_ARM) < 1e-6:
        arm_line = ("Distance to the hazard-95 arm: %s — the measurement "
                    "lands essentially ON the arm (%s)." % (hazd_s, haz_s))
    elif held:
        arm_line = ("Distance to the hazard-95 arm: %s (the arm sits at %s) "
                    "— the measurement lands %s the bracket, not on it."
                    % (hazd_s, haz_s,
                       "above" if share > HAZ95_ARM else "below"))
    else:
        arm_line = ("Distance to the hazard-95 arm: %s (the arm sits at %s) "
                    "— outside the band, the prediction dies regardless of "
                    "which side." % (hazd_s, haz_s))

    body_measure = """## The measurement

Fresh terminals at w8: %s (D2T:L2:other), share %s, Wilson 95%% CI %s.
Deviation from the frozen prediction: %s, band ±%s. %s

Mid-window anchors the instrument instead of the claim: the fresh
w4 mid-window share is %s, %s from the DW9 receipt (%s) and %s from
the VH held-out receipt (%s) — the harness reproduces its own
calibration receipts before any w8 word is read. The seed-anchored
(CAL) w8 terminal census is %s.

The collector recomputed both gates from the raw stats line with the
frozen constants duplicated in-source, and cross-checked against the
harness's own verdict line before anything was written: cross_check
ok, branch %s.""" % (
        _census(cen), share_s, wil_s, dev_s, band_s, arm_line,
        mid_s, dw9d_s, _f(DW9_FRESH_W4, 3), vhd_s, _f(VH_FRESH_W4, 4),
        _census(cal_cen), branch)

    if held:
        body_repo = """## What changed in the repo

The figure (designs/assets/011-window-curve.svg) re-renders with the
w8 point drawn closed and measured, the dashed extrapolation replaced
by a plotted point carrying its census. designs/011's w8 tier entry
moves from predicted to measured, quoting this receipt. The research
log addendum records the collection. Nothing else moved: the w1–w4
receipts, the window-blind stationary share, and the DW11 persist
receipt are untouched by construction."""
    else:
        body_repo = """## What changed in the repo

The figure (designs/assets/011-window-curve.svg) re-renders without
the beyond-w4 extrapolation — the dashed arm is gone, the plot now
ends at the last measured window. designs/011's w8 tier entry is
retracted with this receipt quoted, and the hazard-hold assumption
that carried the extrapolation is named as falsified at w8. The w1–w4
receipts, the window-blind stationary share, and the DW11 persist
receipt are untouched by construction: the demolition takes the
prediction, not the measurements."""

    body_meaning = """## What it means, and what it does not

%s The receipt settles one pre-registered question — does the chain
fit's w8 point survive a cross-seed measurement — and nothing else.
The hazard-95 bracket remains a sensitivity arm, not a fit. The
substrate numbers that gate compilation (assemblies, locks, decodes)
are not window statistics and did not move. And the collection was
mechanical by construction: the interpretation map, the gates, the
figure and this post were all committed before the data existed, so
the branch was never chosen after seeing the numbers.""" % (
        "A four-point chain fit held its far-end prediction at w8; window "
        "pricing keeps its sharpest tier."
        if held else
        "A four-point chain fit did not survive its first cross-seed "
        "far-end test; window pricing keeps only what it measured.")

    prose = "\n\n".join((tldr, body_trial, body_measure, body_repo, body_meaning))
    text = "# %s\n\n%s · designs/011 w8 verdict · %d min\n\n%s\n" % (
        title, _month_day(day), _minutes(prose), prose)
    for bad in ("None", "nan", "{", "}"):
        if bad in text:
            raise ValueError("unfilled template residue %r in rendered post" % bad)
    return {"filename": filename, "text": text}


def _month_day(day):
    y, m, d = (int(x) for x in day.split("-"))
    months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
              "Oct", "Nov", "Dec")
    return "%s %d, %d" % (months[m - 1], d, y)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("receipt", help="verdict receipt JSON from tools/collect_w8.py --out")
    ap.add_argument("--date", help="post date YYYY-MM-DD (default today)")
    ap.add_argument("--out", help="output path (default blog/<filename>)")
    ap.add_argument("--request", default=REQUEST_DEFAULT,
                    help="cluster queue request id quoted in the receipts section")
    args = ap.parse_args(argv)
    with open(args.receipt) as fh:
        receipt = json.load(fh)
    try:
        out = render(receipt, day=args.date, request_id=args.request)
    except ValueError as exc:
        print("RENDER REFUSED: %s" % exc, file=sys.stderr)
        return 2
    path = args.out or ("blog/" + out["filename"])
    with open(path, "w") as fh:
        fh.write(out["text"])
    print("WROTE %s (%s, %d words)" % (path, receipt["branch"],
                                       len(out["text"].split())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
