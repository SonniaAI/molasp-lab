#!/usr/bin/env python3
"""One-command collection-day application of the w8 verdict receipt (tick 82).

Closes the last mechanical seam of the executable pre-registration: on
collection day the whole chain is

  job_queue result -> run.out -> tools/collect_w8.py --out verdict.json
                    -> THIS -> figure + blog post + collection note.

Dispatch follows the receipt's own pre-registered action list:

  CAL_OK+HELD     figure re-rendered with the w8 point drawn CLOSED/measured
                  (+ Wilson 95 bar, every number from the receipt); milestone
                  blog post rendered; collection-note addendum appended to
                  research-log/2026-10-08-w8-hazardhold.md.
  CAL_OK+REFUTED  figure re-rendered WITHOUT the beyond-w4 extrapolation
                  (pre-registered quarantine); demolition blog post rendered;
                  addendum appended.
  anything else   REFUSED (exit 2) with the receipt's action list printed:
                  VOID / NO_EVENTS / SMOKE / FORCED-DISAGREEMENT need
                  diagnosis, never auto-writing.

The addendum and the blog quote every number from the receipt — same
discipline as tools/render_w8_post.py: no number from memory.  The one
remaining hand step, on purpose: the designs/011 prose edit that the
receipt's action list spells out.

Usage:
  python3 tools/apply_w8_receipt.py evidence/2026-10-08-w8-hazardhold/verdict.json \
      [--repo-root PATH] [--date YYYY-MM-DD] [--request QUEUE_REQUEST_ID]
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

NOTE_REL = Path("research-log/2026-10-08-w8-hazardhold.md")
FIGURE_REL = Path("designs/assets/011-window-curve.svg")
BLOG_DIR = Path("blog")
MILESTONES = ("CAL_OK+HELD", "CAL_OK+REFUTED")
REQUEST_DEFAULT = "ed50c7baf2d8b935bb118f25758394ddfb04a671e902f39bfa66721b274daa85"


def _f5(x):
    return "n/a" if x is None else "%.5f" % x


def _cen(c):
    if not c:
        return "n/a"
    return "D2T %s / L2 %s / other %s" % (
        c.get("D2T", "?"), c.get("L2", "?"), c.get("other", "?"))


def figure_nums(receipt):
    """The held-mode w8 drawing numbers, read only from the receipt."""
    d = receipt["descriptive"]
    cen = d["fresh_terminal_census"]
    return {"share": d["fresh_terminal_share"],
            "census": "%d:%d" % (cen["D2T"], cen["L2"]),
            "wilson95": d["fresh_w8_wilson95"],
            "dev": d["dev_vs_pred_w8"]}


def addendum(receipt, date, request_id, blog_filename, mode):
    branch = receipt["branch"]
    d = receipt["descriptive"]
    w95 = d.get("fresh_w8_wilson95") or [None, None]
    lines = []
    a = lines.append
    a("")
    a("## Collection (%s, SON-4885) — %s" % (date, branch))
    a("")
    a("Request `%s` (nonce molasp-w8-hazardhold-t77); receipt cross_check %s."
      % (request_id, receipt.get("cross_check")))
    a("Applied mechanically by `tools/apply_w8_receipt.py`; every number below")
    a("is quoted from the receipt, none from memory.")
    a("")
    a("- fresh pair terminals w8: %s (n_per_range %s)"
      % (_cen(d["fresh_terminal_census"]), receipt.get("n_per_range")))
    a("- fresh_terminal_share %s vs chain w8 point 0.83376 -> dev %s "
      "(pre-registered band +/-0.05)"
      % (_f5(d["fresh_terminal_share"]), _f5(d["dev_vs_pred_w8"])))
    a("- Wilson 95 [%s, %s]; hazard-95 arm distance %s"
      % (_f5(w95[0]), _f5(w95[1]), _f5(d.get("haz95_arm_distance"))))
    a("- fresh_mid_w4 share %s (DW9 receipt dev %s; VH receipt dev %s)"
      % (_f5(d.get("fresh_mid_w4_share")),
         _f5(d.get("fresh_mid_w4_dev_vs_dw9_receipt")),
         _f5(d.get("fresh_mid_w4_dev_vs_vh_receipt"))))
    a("- cal_terminal_w8 census %s" % _cen(d.get("cal_terminal_w8_census")))
    a("")
    if branch == "CAL_OK+HELD":
        a("The w8 tier of designs/011 stands on a measured receipt: the chain")
        a("point 0.834 is confirmed within the pre-registered +/-0.05 band")
        a("(dev %s). The hazard-95 bracket remains what it always was — a"
          % _f5(d["dev_vs_pred_w8"]))
        a("sensitivity arm, not a fit.")
    else:
        a("The hazard-hold assumption is falsified at w8: fresh_terminal_share")
        a("%s lies outside the pre-registered +/-0.05 band around 0.83376."
          % _f5(d["fresh_terminal_share"]))
        a("The beyond-w4 extrapolation is quarantined in figure and designs/011;")
        a("the hazard-95 bracket stays a sensitivity arm, not a fit.")
    a("")
    a("Applied by this run: figure `%s` re-rendered (%s); blog post" % (FIGURE_REL, mode))
    a("`%s/%s` rendered. Remaining hand step per the receipt's" % (BLOG_DIR, blog_filename))
    a("action list: the designs/011 prose edit.")
    return "\n".join(lines) + "\n"


def apply(receipt, repo_root, date=None, request_id=None):
    """Apply one verdict receipt. Returns the written-paths record.

    Raises ValueError (refusing to write anything) for non-milestone
    branches and FORCED-DISAGREEMENT receipts.
    """
    from tools.render_w8_post import render as render_post
    from tools.window_curve_svg import render as render_svg

    branch = receipt.get("branch")
    if branch not in MILESTONES:
        raise ValueError(
            "refusing branch %r; pre-registered actions:\n%s"
            % (branch, "\n".join("- " + x for x in receipt.get("actions", []))))
    if receipt.get("cross_check") != "ok":
        raise ValueError(
            "refusing receipt with cross_check=%r — a forced receipt can "
            "never autowrite" % receipt.get("cross_check"))
    date = date or datetime.date.today().isoformat()
    request_id = request_id or REQUEST_DEFAULT
    mode = "held" if branch == "CAL_OK+HELD" else "refuted"
    nums = figure_nums(receipt) if mode == "held" else None

    root = Path(repo_root)
    fig = root / FIGURE_REL
    fig.parent.mkdir(parents=True, exist_ok=True)
    fig.write_text(render_svg(w8_mode=mode, w8=nums), encoding="utf-8")

    post = render_post(receipt, day=date, request_id=request_id)
    blog = root / BLOG_DIR / post["filename"]
    blog.parent.mkdir(parents=True, exist_ok=True)
    blog.write_text(post["text"], encoding="utf-8")

    note = root / NOTE_REL
    marker = "## Collection (%s, SON-4885) — %s" % (date, branch)
    existing = note.read_text(encoding="utf-8") if note.exists() else ""
    appended = False
    if marker not in existing:
        with open(note, "a", encoding="utf-8") as fh:
            fh.write(addendum(receipt, date, request_id, post["filename"], mode))
        appended = True
    return {"branch": branch, "mode": mode, "figure": str(fig),
            "blog": str(blog), "note": str(note),
            "note_appended": appended}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("receipt", help="verdict receipt JSON from tools/collect_w8.py --out")
    ap.add_argument("--repo-root", default=str(REPO),
                    help="repo root the figure/blog/note are written under")
    ap.add_argument("--date", help="collection date YYYY-MM-DD (default today)")
    ap.add_argument("--request", default=REQUEST_DEFAULT,
                    help="queue request id quoted in the note")
    args = ap.parse_args(argv)
    with open(args.receipt) as fh:
        receipt = json.load(fh)
    try:
        out = apply(receipt, args.repo_root, date=args.date, request_id=args.request)
    except ValueError as exc:
        print("APPLICATION REFUSED: %s" % exc, file=sys.stderr)
        return 2
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
