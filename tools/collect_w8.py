#!/usr/bin/env python3
"""Executable pre-registration: w8 hazard-hold collection (tick 80).

Turns the frozen interpretation map of
research-log/2026-10-08-w8-hazardhold.md into code committed BEFORE
the falsifier's data exists.  Given the raw cluster-job stdout
(run.out) of request ed50c7ba…4daa85 (nonce molasp-w8-hazardhold-t77,
harness evidence/2026-10-08-w8-hazardhold/ktam_w8_hazardhold.py):

  1. parse the full stats JSON line and the final VERDICTS line;
  2. INDEPENDENTLY recompute the frozen CAL/W8 gates from the stats
     (the constants below are duplicated from the harness on purpose:
     the collector must not import the instrument under test — the
     duplication IS the independent check);
  3. cross-check the recomputation against the harness's own VERDICTS
     line (any disagreement raises unless --force);
  4. emit a machine-readable receipt: branch, descriptive numbers,
     and the pre-registered follow-up actions.

Every branch's gate arithmetic is pinned by tests/test_collect_w8.py
on synthetic outputs, so collection day is mechanical and the branch
cannot be chosen after seeing the numbers.

Usage:
  python3 tools/collect_w8.py evidence/2026-10-08-w8-hazardhold/run.out \
      [--out evidence/2026-10-08-w8-hazardhold/verdict.json] [--force]
"""
import argparse
import json
import math
import sys

# Frozen pre-registration values (tick 74, verbatim from the harness
# docstring/gates — duplicated deliberately, see module docstring).
CAL_D2T = 367            # CAL mid-window (4x) pair census, EXACT (tick-63/DW9 receipt)
CAL_L2 = 131
PRED_W8 = 0.83376        # designs/011 P3 chain w8 point ("0.834" in the pre-registration)
BAND = 0.05              # |s - pred| <= BAND -> HELD, else REFUTED
MIN_EVENTS = 50          # fresh pair terminals below this -> NO_EVENTS
HAZ95_ARM = 0.81585      # hazard-95 bracket arm (sensitivity arm, not a fit)
DW9_FRESH_W4 = 0.716     # receipts for the descriptive fresh mid-window cross-check
VH_FRESH_W4 = 0.7379032258064516
N_FULL = 500

ACTIONS = {
    "CAL_OK+HELD": [
        "w8 tier stands on a measured receipt: designs/011 P3 point 0.834 is now "
        "cross-seed measured within the pre-registered +/-0.05 band",
        "re-render designs/assets/011-window-curve.svg with the w8 point drawn "
        "CLOSED/measured (tools/window_curve_svg.py)",
        "write the collection note (research-log/2026-10-08-w8-hazardhold.md "
        "addendum) quoting this receipt's numbers verbatim",
        "HELD is the pre-registered genuine milestone: draft + publish the blog "
        "post with every number from this receipt",
    ],
    "CAL_OK+REFUTED": [
        "retract the designs/011 w8 tier entry (pre-registered refutation)",
        "quarantine the extrapolated arm beyond w4 in the figure and designs/011",
        "re-render designs/assets/011-window-curve.svg WITHOUT the beyond-w4 "
        "extrapolation",
        "collection note names the hazard-hold assumption falsified at w8; the "
        "hazard-95 bracket stays what it always was: a sensitivity arm, not a fit",
    ],
    "CAL_FAIL+VOID": [
        "everything VOID: instrument drift vs the tick-63 receipt — diagnose "
        "before ANY science claim",
        "do not touch designs/011 tiers with this output",
        "diff the harness against the f56f393-era instrument and re-submit only "
        "after a named cause",
    ],
    "CAL_OK+NO_EVENTS": [
        "no verdict: fresh pair terminals < 50; tiers unchanged",
        "diagnose / extend sampling per the pre-registration before any claim",
    ],
    "SMOKE_NOT_VERDICTABLE": [
        "smoke output (n != 500) is not verdictable; rerun the full job",
    ],
}


def wilson(k, n, z=1.96):
    """Wilson 95% CI (same formula/rounding as the harness)."""
    if not n:
        return None
    p = k / float(n)
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 5), round(c + h, 5)]


def parse_runout(text):
    """Return (stats, verdicts): the full stats JSON line and the final
    VERDICTS line of the harness stdout, tolerating preamble/junk."""
    stats = None
    verdicts = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("VERDICTS "):
            verdicts = json.loads(s[len("VERDICTS "):])
            continue
        try:
            obj = json.loads(s)
        except ValueError:
            continue
        if isinstance(obj, dict) and "cal_mid_w4" in obj:
            stats = obj
    if stats is None or verdicts is None:
        raise ValueError("run.out missing the stats line or the VERDICTS line")
    return stats, verdicts


def recompute(stats):
    """Independent gate recomputation from the stats line only."""
    n = stats.get("n_per_range")
    if n != N_FULL:
        return {"branch": "SMOKE_NOT_VERDICTABLE",
                "CAL": None, "W8": None, "dev": None, "pairs": None}
    cal_mid = stats["cal_mid_w4"]
    cal = ("CAL_OK" if (cal_mid["D2T"] == CAL_D2T and cal_mid["L2"] == CAL_L2)
           else "CAL_FAIL")
    fr = stats["fresh_terminal_w8"]
    pairs = fr["D2T"] + fr["L2"]
    if cal != "CAL_OK":
        w8, dev = "VOID", None          # CAL failure voids everything
    elif pairs < MIN_EVENTS:
        w8, dev = "NO_EVENTS", None
    else:
        share = fr["D2T"] / float(pairs)
        dev = abs(share - PRED_W8)
        w8 = "HELD" if dev <= BAND else "REFUTED"
    return {"branch": cal + "+" + w8, "CAL": cal, "W8": w8,
            "dev": dev, "pairs": pairs}


def collect(text, force=False):
    """Full collection receipt for one run.out (raises on cross-check
    disagreement unless force=True)."""
    stats, harness_vs = parse_runout(text)
    rec = recompute(stats)
    receipt = {
        "branch": rec["branch"],
        "n_per_range": stats.get("n_per_range"),
        "harness_verdicts": harness_vs,
        "recomputed_verdicts": {"CAL": rec["CAL"], "W8": rec["W8"]},
    }
    if rec["branch"] == "SMOKE_NOT_VERDICTABLE":
        receipt["cross_check"] = "skipped (smoke)"
        receipt["actions"] = ACTIONS[rec["branch"]]
        return receipt

    mine = {"CAL": rec["CAL"], "W8": rec["W8"]}
    if harness_vs != mine:
        if not force:
            raise ValueError(
                "cross-check failed: harness VERDICTS %r vs recomputed %r "
                "(use --force only with a written justification)" % (harness_vs, mine))
        receipt["cross_check"] = "FORCED-DISAGREEMENT"
    else:
        receipt["cross_check"] = "ok"

    fr = stats["fresh_terminal_w8"]
    pairs = fr["D2T"] + fr["L2"]
    share = fr["D2T"] / float(pairs) if pairs else None
    fm = stats["fresh_mid_w4"]
    fm_share = fm.get("share")
    if share is not None and fr.get("share") is not None:
        if abs(share - fr["share"]) > 1e-9:
            raise ValueError("fresh terminal share disagrees with stats line")
    if rec["dev"] is not None and stats.get("dev_fresh_w8") is not None:
        if abs(rec["dev"] - stats["dev_fresh_w8"]) > 1e-9:
            raise ValueError("dev_fresh_w8 disagrees with recomputation")
    receipt["descriptive"] = {
        "fresh_terminal_share": share,
        "fresh_terminal_census": {"D2T": fr["D2T"], "L2": fr["L2"],
                                  "other": fr.get("other")},
        "dev_vs_pred_w8": rec["dev"],
        "fresh_w8_wilson95": wilson(fr["D2T"], pairs),
        "haz95_arm_distance": abs(share - HAZ95_ARM) if share is not None else None,
        "fresh_mid_w4_share": fm_share,
        "fresh_mid_w4_dev_vs_dw9_receipt":
            abs(fm_share - DW9_FRESH_W4) if fm_share is not None else None,
        "fresh_mid_w4_dev_vs_vh_receipt":
            abs(fm_share - VH_FRESH_W4) if fm_share is not None else None,
        "cal_terminal_w8_census": stats["cal_terminal_w8"],
    }
    receipt["actions"] = ACTIONS[rec["branch"]]
    return receipt


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("runout", help="path to the raw cluster job stdout (run.out)")
    ap.add_argument("--out", help="optional path for the verdict receipt JSON")
    ap.add_argument("--force", action="store_true",
                    help="record a cross-check disagreement instead of raising")
    args = ap.parse_args(argv)
    with open(args.runout) as fh:
        text = fh.read()
    try:
        receipt = collect(text, force=args.force)
    except ValueError as exc:
        print("COLLECTION REFUSED: %s" % exc, file=sys.stderr)
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(receipt, fh, indent=2, sort_keys=True)
            fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
