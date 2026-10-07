#!/usr/bin/env python3
"""Collection harness for the tick-47 dG-2 window + L3-at-vacancy run
(SON-4821, pre-registration frozen at df958f2).

Reads the raw stdout of ktam_dg2_window_l3.py — the four per-arm JSON
records, the verdicts JSON line, and the final "VERDICTS {...}" line —
independently recomputes the pre-registered verdicts DW8-DW11 / LV1-LV2
from the raw per-arm numbers, refuses to render if the experiment
script's own machine verdicts disagree with the re-computation, and
emits the research-log collection fragment (markdown) carrying every
number it checked.

Instrument code on purpose: the gate thresholds below are duplicated
verbatim from the pre-registration docstring (NOT imported from the
experiment module) so that a transcription or aggregation bug in the
experiment script cannot silently flow through collection.  If the two
ever disagree, this harness fails loudly and the collection commit
does not happen until a human-readable diff explains which side moved.

Usage:
    python3 collect.py run.out            # writes collection.md
    python3 collect.py run.out -          # writes fragment to stdout

Exit codes: 0 ok; 2 verdict mismatch; 3 malformed run output.
"""
import json
import sys

ARMS = ["s2_dg0.5_l3probe", "s2_dg0.5_win4",
        "s2_dg2_win4", "fam_dg2_win4"]

# Pre-registered thresholds, duplicated verbatim from the docstring of
# ktam_dg2_window_l3.py at df958f2 (refs are committed tick-43 receipt
# values, not this run's).
REF_S2_DG2_FILL = 0.464
REF_PROBE_FILL = 0.412
REF_PROBE_L3_CENSUS = 0.100
DW8_CONFIRM, DW8_FALSIFY = 0.10, 0.03
DW9_LO, DW9_HI, DW9_FLO, DW9_FHI, DW9_MIN_EVENTS = 0.40, 0.60, 0.35, 0.65, 50
DW10_FLOOR = 0.70
DW11_CONFIRM, DW11_FALSIFY = 0.80, 0.65
LV1_CENSUS_FLOOR, LV1_EP_CONFIRM, LV1_EP_FALSIFY, LV1_EP_MIN = 0.05, 0.7, 0.5, 10
LV2_CONFIRM, LV2_FALSIFY = 0.05, 0.10


class MalformedRun(ValueError):
    pass


class VerdictMismatch(ValueError):
    pass


def parse_run_out(text):
    """Return (per_arm dict, script verdicts dict) from raw stdout."""
    per, verdicts = {}, None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("VERDICTS "):
            verdicts = json.loads(line[len("VERDICTS "):])
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue          # progress noise / banners
        if isinstance(obj, dict) and "arm" in obj:
            per[obj["arm"]] = obj
        elif isinstance(obj, dict):
            verdicts = obj    # the bare verdicts JSON line
    if set(per) != set(ARMS):
        raise MalformedRun("expected arms %r, got %r"
                           % (sorted(ARMS), sorted(per)))
    if verdicts is None:
        raise MalformedRun("no VERDICTS line found")
    return per, verdicts


def recompute(per):
    """Recompute DW8-DW11 / LV1-LV2 from raw per-arm records using the
    pre-registered thresholds (verbatim mirror of the docstring)."""
    v = {}
    w2 = per["s2_dg2_win4"]
    gain = w2["fill_frac"] - REF_S2_DG2_FILL
    v["DW8"] = ("CONFIRMED" if gain >= DW8_CONFIRM else
                "FALSIFIED" if gain <= DW8_FALSIFY else "INCONCLUSIVE")
    d2t = w2["site_occupants"].get("D2T", 0)
    l2 = w2["site_occupants"].get("L2", 0)
    if d2t + l2 < DW9_MIN_EVENTS:
        v["DW9"] = "NO_EVENTS"
    else:
        share = d2t / float(d2t + l2)
        v["DW9"] = ("CONFIRMED" if DW9_LO <= share <= DW9_HI else
                    "FALSIFIED" if share < DW9_FLO or share > DW9_FHI
                    else "INCONCLUSIVE")
    v["DW10"] = ("CONFIRMED" if per["fam_dg2_win4"]["fill_frac"]
                 >= DW10_FLOOR else "FALSIFIED")
    p = per["s2_dg0.5_win4"]["first_stable_persist"]
    if p is None:
        v["DW11"] = "NO_EVENTS"
    else:
        v["DW11"] = ("CONFIRMED" if p >= DW11_CONFIRM else
                     "FALSIFIED" if p < DW11_FALSIFY else "INCONCLUSIVE")
    probe, win4 = per["s2_dg0.5_l3probe"], per["s2_dg0.5_win4"]
    census_ok = max(probe["l3_terminal_frac"],
                    win4["l3_terminal_frac"]) >= LV1_CENSUS_FLOOR
    ep_n = probe["l3_episode_n"] + win4["l3_episode_n"]
    ep_term = ((probe["l3_episode_terminal_frac"] or 0.0)
               * probe["l3_episode_n"]
               + (win4["l3_episode_terminal_frac"] or 0.0)
               * win4["l3_episode_n"])
    ep_persist = ep_term / float(ep_n) if ep_n >= LV1_EP_MIN else None
    if not census_ok:
        v["LV1"] = "FALSIFIED"
    elif ep_persist is None:
        v["LV1"] = "NO_EVENTS"
    elif ep_persist >= LV1_EP_CONFIRM:
        v["LV1"] = "CONFIRMED"
    elif ep_persist < LV1_EP_FALSIFY:
        v["LV1"] = "FALSIFIED"
    else:
        v["LV1"] = "INCONCLUSIVE"
    diff = abs(win4["l3_terminal_frac"] - probe["l3_terminal_frac"])
    v["LV2"] = ("CONFIRMED" if diff <= LV2_CONFIRM else
                "FALSIFIED" if diff > LV2_FALSIFY else "INCONCLUSIVE")
    return v


def check(per, script_verdicts):
    mine = recompute(per)
    if mine != script_verdicts:
        bad = {k: (script_verdicts.get(k), mine[k])
               for k in mine if script_verdicts.get(k) != mine[k]}
        raise VerdictMismatch("script vs re-computed verdicts differ "
                              "(script, recomputed): %r" % bad)
    return mine


def render(per, vs):
    """Research-log collection fragment with every decisive number."""
    probe, win4 = per["s2_dg0.5_l3probe"], per["s2_dg0.5_win4"]
    w2, fam = per["s2_dg2_win4"], per["fam_dg2_win4"]
    n = w2["n"]
    d2t = w2["site_occupants"].get("D2T", 0)
    l2 = w2["site_occupants"].get("L2", 0)
    share = d2t / float(d2t + l2) if d2t + l2 else float("nan")
    gain = w2["fill_frac"] - REF_S2_DG2_FILL
    ep_n = probe["l3_episode_n"] + win4["l3_episode_n"]
    ep_term = ((probe["l3_episode_terminal_frac"] or 0.0)
               * probe["l3_episode_n"]
               + (win4["l3_episode_terminal_frac"] or 0.0)
               * win4["l3_episode_n"])
    ep_persist = ep_term / float(ep_n) if ep_n else float("nan")
    l3diff = abs(win4["l3_terminal_frac"] - probe["l3_terminal_frac"])
    lines = [
        "### tick 47 collection — dG-2 window + L3-at-vacancy "
        "(n=%d/arm)" % n,
        "",
        "| arm | fill | D2T:L2 census | first-stable persist | "
        "L3 census | L3 episodes (n, terminal) |",
        "|---|---|---|---|---|---|",
        "| s2_dg0.5_l3probe | %.3f (ref %.3f) | — | %s | %.3f "
        "(ref %.3f) | %d, %s |" % (
            probe["fill_frac"], REF_PROBE_FILL,
            ("%.3f" % probe["first_stable_persist"]
             if probe["first_stable_persist"] is not None else "n/a"),
            probe["l3_terminal_frac"], REF_PROBE_L3_CENSUS,
            probe["l3_episode_n"], probe["l3_episode_terminal_frac"]),
        "| s2_dg0.5_win4 | %.3f | — | %s | %.3f | %d, %s |" % (
            win4["fill_frac"],
            ("%.3f" % win4["first_stable_persist"]
             if win4["first_stable_persist"] is not None else "n/a"),
            win4["l3_terminal_frac"], win4["l3_episode_n"],
            win4["l3_episode_terminal_frac"]),
        "| s2_dg2_win4 | %.3f (ref %.3f, gain %+.3f) | %d : %d "
        "(share %.3f) | %s | %.3f | %d, %s |" % (
            w2["fill_frac"], REF_S2_DG2_FILL, gain, d2t, l2, share,
            ("%.3f" % w2["first_stable_persist"]
             if w2["first_stable_persist"] is not None else "n/a"),
            w2["l3_terminal_frac"], w2["l3_episode_n"],
            w2["l3_episode_terminal_frac"]),
        "| fam_dg2_win4 | %.3f | — | %s | %.3f | %d, %s |" % (
            fam["fill_frac"],
            ("%.3f" % fam["first_stable_persist"]
             if fam["first_stable_persist"] is not None else "n/a"),
            fam["l3_terminal_frac"], fam["l3_episode_n"],
            fam["l3_episode_terminal_frac"]),
        "",
        "Machine verdicts (script == independent re-computation, "
        "this harness):",
        "",
        "| gate | verdict | decisive number |",
        "|---|---|---|",
        "| DW8 dG-2 window gain | %s | fill gain %+.3f "
        "(confirm >= +%.2f, falsify <= +%.2f) |" % (
            vs["DW8"], gain, DW8_CONFIRM, DW8_FALSIFY),
        "| DW9 coin survival | %s | D2T share %.3f over %d events "
        "(confirm [%.2f, %.2f]) |" % (
            vs["DW9"], share, d2t + l2, DW9_LO, DW9_HI),
        "| DW10 family window-neutrality | %s | fam fill %.3f "
        "(floor %.2f) |" % (vs["DW10"], fam["fill_frac"], DW10_FLOOR),
        "| DW11 frozen-regime immunity | %s | persist %s "
        "(confirm >= %.2f, falsify < %.2f) |" % (
            vs["DW11"],
            ("%.3f" % win4["first_stable_persist"]
             if win4["first_stable_persist"] is not None else "n/a"),
            DW11_CONFIRM, DW11_FALSIFY),
        "| LV1 L3 frozen-contender class | %s | pooled episode "
        "persistence %s over %d episodes (census max %.3f) |" % (
            vs["LV1"],
            ("%.3f" % ep_persist if ep_n else "n/a"), ep_n,
            max(probe["l3_terminal_frac"], win4["l3_terminal_frac"])),
        "| LV2 L3 window stability | %s | census diff %.3f "
        "(confirm <= %.2f, falsify > %.2f) |" % (
            vs["LV2"], l3diff, LV2_CONFIRM, LV2_FALSIFY),
        "",
    ]
    return "\n".join(lines)


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 3
    src, dst = argv[1], argv[2]
    with open(src) as fh:
        text = fh.read()
    try:
        per, script_vs = parse_run_out(text)
    except MalformedRun as exc:
        print("MALFORMED run output: %s" % exc, file=sys.stderr)
        return 3
    try:
        vs = check(per, script_vs)
    except VerdictMismatch as exc:
        print("VERDICT MISMATCH — refusing to render: %s" % exc,
              file=sys.stderr)
        return 2
    fragment = render(per, vs)
    if dst == "-":
        print(fragment)
    else:
        with open(dst, "w") as fh:
            fh.write(fragment + "\n")
        print("wrote %s (verdicts: %s)" % (dst, json.dumps(vs,
                                                           sort_keys=True)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
