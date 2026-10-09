#!/usr/bin/env python3
"""w8 collection-day LADDER rehearsal — pre-registered BEFORE the datum (tick 95).

Tick 90 rehearsed the five-step RESULT chain (import_queue_result ->
collect_w8 -> apply_w8_receipt -> atlas) on synthetic frames. The growth
tools built AFTER that rehearsal (tick 91 planner, tick 92 census policy,
tick 93 dispersion receipt, tick 94 sequential-look error map) have never
been drilled as a decision chain. This tool closes that gap: it drives the
REAL tools/w8_census_policy.py policy()/collection_report() on synthetic
first-arm censuses (x1, k1=500) at pre-named truths, and checks the
mechanical stage naming against expectations committed in the tick-91/92/94
receipts BEFORE this rehearsal ran.

Pre-named truths and their committed expectation sources:
  primary         0.83376  hold-last identity (_vh_share(8), tick 86);
                           tick-92 receipt: 417/500 -> grow, k_line 1442,
                           3 pooled arms, 1.33 h wall, P(attr) 0.507.
  floor_edge      0.78376  tick-86 region boundary; tick-94 verdict
                           scarcity at gate edges -> stage-3 path.
  ceiling_edge    0.88376  tick-86 region boundary; same as floor_edge.
  trend           0.76415  l2-loglinear-trend arm (tick 86), inside the
                           REFUTED-but-trend-alive region; tick-88: R3
                           attribution-empty at k<=500 -> must grow.
  chain_falsified 0.65     below 0.71415; tick-91: destructive verdicts
                           already attributable at the 50-event floor ->
                           verdict-ready, no growth.
  unmodeled       0.95     above 0.88376; tick-91: attributable -> no
                           growth.
  edge_pointing   407/500  tick-92 receipt: stage-3 directly, outside-cap
                           extrapolation k_ext ~ 25.8M.

Rehearsal finding recorded at first run (pre-registered expectations held;
one NUMBER is new knowledge): the trend arm's mechanical ladder answer is
k_line=1634 (4 arms, +3, 2.00 h), NOT the tick-91 planner's R3 regional
minimum k=653 — the planner prices per-region minima, the policy scans
for the first k whose >=3-count practical window contains the point-
estimate line x=round(phat*k); they agree at the primary and differ at
the trend arm. Documented, not "fixed": two different pre-registered
questions, both receipts stand.

Authority: planning/policy arithmetic only. This tool NEVER verdicts a
real datum and never imports the frozen collector (tools/collect_w8.py)
or the atlas; collection-day verdict surfaces remain exactly those two.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.w8_census_policy import (  # noqa: E402
    MIN_EVENTS,
    collection_report,
    policy,
)

MIN_EVENTS_FLOOR = MIN_EVENTS  # re-export for the pins

K1 = 500  # the already-queued first arm's pooled census size (fresh-arm terminals)

TRUTHS = [
    ("primary", 417),
    ("floor_edge", 392),
    ("ceiling_edge", 442),
    ("trend", 382),
    ("chain_falsified", 325),
    ("unmodeled", 475),
    ("edge_pointing", 407),
]

EXPECT_MODE = {
    "primary": "grow",
    "floor_edge": "escalate_dispersion",
    "ceiling_edge": "escalate_dispersion",
    "trend": "grow",
    "chain_falsified": "verdict_ready",
    "unmodeled": "verdict_ready",
    "edge_pointing": "escalate_dispersion",
}

# Tick-92 committed receipt identities at the primary (drift guard for the
# whole ladder against its own landed record).
RECEIPT_PRIMARY = {"k_line_prac": 1442, "total_arms": 3,
                   "additional_arms": 2, "growth_wall_hours": 1.33}


def rehearse():
    """One policy() decision per pre-named truth. Deterministic."""
    rows = []
    for name, x1 in TRUTHS:
        d = policy(x1, K1)
        g = d.get("growth")
        rows.append({
            "truth": name,
            "x1": x1,
            "k1": K1,
            "mode": d["mode"],
            "regions": d.get("regions"),
            "w1": d["w1"],
            "k_line": g["k_line_prac"] if g else None,
            "region": g["region"] if g else None,
            "total_arms": g["total_arms"] if g else None,
            "additional_arms": g["additional_arms"] if g else None,
            "wall_hours": g["growth_wall_hours"] if g else None,
            "receipt": d,
        })
    return rows


def check(rows):
    """Mode expectations (committed before this rehearsal ran) + the
    tick-92 receipt identities at the primary. Returns failure strings."""
    fails = []
    for row in rows:
        want = EXPECT_MODE[row["truth"]]
        if row["mode"] != want:
            fails.append("%s: mode %s != committed expectation %s"
                         % (row["truth"], row["mode"], want))
        if row["mode"] == "verdict_ready" and row["receipt"].get("growth") is not None:
            fails.append("%s: verdict_ready must carry growth=None" % row["truth"])
    prim = [r for r in rows if r["truth"] == "primary"][0]["receipt"]["growth"]
    for key, want in RECEIPT_PRIMARY.items():
        got = prim[key]
        if isinstance(want, float):
            ok = abs(got - want) < 5e-3
        else:
            ok = got == want
        if not ok:
            fails.append("primary receipt %s: %r != tick-92 %r" % (key, got, want))
    return fails


def render(rows):
    out = []
    out.append("w8 LADDER rehearsal (tick 95, before the datum) — drives the real")
    out.append("tools/w8_census_policy.py policy(); k1=%d fresh-arm terminals." % K1)
    out.append("")
    out.append("truth            x1   mode                 k_line arms +add wall_h  Wilson-95")
    for r in rows:
        out.append(
            "%-15s %4d  %-19s %6s %4s %4s %5s  [%.5f,%.5f]"
            % (r["truth"], r["x1"], r["mode"],
               r["k_line"] if r["k_line"] else "-",
               r["total_arms"] if r["total_arms"] else "-",
               r["additional_arms"] if r["additional_arms"] else "-",
               ("%.2f" % r["wall_hours"]) if r["wall_hours"] else "-",
               r["w1"][0], r["w1"][1]))
    out.append("")
    out.append("Collection-day reading, pre-registered: destructive verdicts")
    out.append("(chain_falsified R4, unmodeled R5) attribute at the first arm;")
    out.append("the primary and the trend arm GROW on the mechanical ladder;")
    out.append("edge-pointing and near-edge truths hit stage-3 DIRECTLY")
    out.append("(dispersion receipt + escalation with recommended path,")
    out.append("never stage 4). Verdict authority stays with collect_w8 +")
    out.append("w8_decision_atlas; this rehearsal has none.")
    return "\n".join(out)


def main(argv):
    rows = rehearse()
    sys.stdout.write(render(rows) + "\n")
    fails = check(rows)
    if fails:
        sys.stdout.write("REHEARSAL FAILURES (%d):\n" % len(fails))
        for f in fails:
            sys.stdout.write("  - %s\n" % f)
        return 1
    sys.stdout.write("REHEARSAL OK: %d/%d truths match committed expectations; "
                     "tick-92 receipt identities reproduced.\n" % (len(rows), len(rows)))
    if "--reports" in argv:
        for name, x1 in TRUTHS:
            sys.stdout.write("\n===== %s x=%d k=%d =====\n" % (name, x1, K1))
            sys.stdout.write(collection_report(x1, K1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
