#!/usr/bin/env python3
"""W8 block-position trend/adjacency instrument (tick 112, SON-5142).

Pre-registered in research-log/2026-10-13-w8-blockpos-prereg.md BEFORE any
permutation output was computed. Deterministic exact enumeration over
existing receipts only: no new trajectories, no cluster job, no RNG.

Reads three committed receipts, rebuilds the eight observed 500-seed windows,
runs the frozen guards (expected-table equality, seed-scan set equality, CAL
identity chain, hotrepro cross-sums), then evaluates the two frozen stratified
exact permutation tests (P1 first-vs-rest, S2 position-scored trend) with
Holm-Bonferroni at family alpha 0.05 and emits the frozen branch verdict.

Output: pretty JSON receipt on stdout; final line `VERDICTS {...}`.
Guard failure: diagnostic JSON + exit 3 (no receipt, no verdicts).
"""

import glob
import itertools
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LINE = "evidence/2026-10-09-w8-line/run.out"
BLOCKPROBE = "evidence/2026-10-09-w8-blockprobe/run.out"
HOTREPRO = "evidence/2026-10-13-w8-hotrepro/run.out"
BLOCKPOWER = "evidence/2026-10-13-w8-blockpower/run.out"
# This instrument's OWN receipt quotes every window seed base as
# provenance metadata; the seed-scan guard must skip it or any
# re-run after collection would refuse on its own output.
OWN_RECEIPT = "evidence/2026-10-13-w8-blockpos/run.out"

# Frozen expected table: (block, pos, seed_base, offset, x, n, source, field)
EXPECTED = [
    ("B340", 1, 340261107, 0, 389, 500, LINE, "arm6_terminal_w8"),
    ("B340", 2, 340261607, 0, 372, 500, BLOCKPROBE, "arm6b_terminal_w8"),
    ("B340", 3, 340262107, 0, 347, 500, HOTREPRO, "afresh_subwindows[0]"),
    ("B340", 4, 340262607, 0, 344, 499, HOTREPRO, "afresh_subwindows[1]"),
    ("B350", 1, 350261107, 0, 391, 500, BLOCKPROBE, "arm8_terminal_w8"),
    ("B350", 2, 350261607, 0, 346, 500, HOTREPRO, "bfresh_subwindows[0]"),
    ("B350", 3, 350262107, 0, 368, 500, HOTREPRO, "bfresh_subwindows[1]"),
    ("B360", 1, 360261107, 0, 365, 499, LINE, "arm7_terminal_w8"),
]

# Frozen seed-scan: base -> exact set of evidence/*/run.out files that may
# mention it (sources plus whitelisted non-source mentions, with reasons).
SEED_SCAN = {
    "340261107": {
        "files": {LINE, "evidence/2026-10-13-w8-arm6/run.out", HOTREPRO, BLOCKPOWER},
        "non_source": {
            "evidence/2026-10-13-w8-arm6/run.out": "tick-110 stale-premise deterministic replay, superseded by correction b7623fd; never data",
            HOTREPRO: "burned_context metadata only",
            BLOCKPOWER: "pre-registered blockpower arbitration datum (tick 143, sha e6335756): fresh-offset burn [2000,5560) past every prior burn of the block; no subwindow reuse",
        },
    },
    "340261607": {"files": {BLOCKPROBE}, "non_source": {}},
    "340262107": {"files": {HOTREPRO}, "non_source": {}},
    "340262607": {"files": {HOTREPRO}, "non_source": {}},
    "350261107": {
        "files": {BLOCKPROBE, HOTREPRO, BLOCKPOWER},
        "non_source": {
            HOTREPRO: "burned_context metadata only",
            BLOCKPOWER: "pre-registered blockpower GAP arm (tick 143, sha e6335756): fresh-offset burn [1500,5060) past every prior burn of the block; no subwindow reuse",
        },
    },
    "350261607": {"files": {HOTREPRO}, "non_source": {}},
    "350262107": {"files": {HOTREPRO}, "non_source": {}},
    "360261107": {"files": {LINE}, "non_source": {}},
}

CAL_EXPECTED = {"D2T": 367, "L2": 131, "other": 2}
TEST_BLOCKS = ["B340", "B350"]  # B360 (arm-7) structurally excluded: single window
ALPHA = 0.05
TOL = 1e-12


def load_receipt(path):
    with open(os.path.join(REPO_ROOT, path), "r") as f:
        text = f.read()
    try:
        return json.loads(text), text
    except json.JSONDecodeError:
        pass
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("VERDICTS"):
            continue
        try:
            return json.loads(line), text
        except json.JSONDecodeError:
            continue
    raise ValueError("no JSON object found in %s" % path)


def census_pair_count(block):
    # Receipt convention (verified on all three sources): share = D2T/(D2T+L2);
    # "other" is a non-pair terminal class excluded from the pair denominator
    # (arm-7: 365+134=499 pairs, other=1; cal: 367+131=498, other=2).
    return int(block["D2T"]) + int(block["L2"])


def build_windows(line_d, probe_d, hot_d):
    rows = []
    for blk, pos, base, off, x, n, src, field in EXPECTED:
        if field.startswith("afresh") or field.startswith("bfresh"):
            key = "afresh_subwindows" if field.startswith("afresh") else "bfresh_subwindows"
            idx = int(field[-2])
            sw = hot_d[key][idx]
            got_x, got_n, got_base = sw["x"], sw["pair_n"], sw["seed0"]
        else:
            blk_d = line_d if src == LINE else probe_d
            got_x = blk_d[field]["D2T"]
            got_n = census_pair_count(blk_d[field])
            got_base = None if src == LINE else None
            if src == LINE:
                key = {"arm6_terminal_w8": "seed0_arm6", "arm7_terminal_w8": "seed0_arm7"}[field]
                got_base = line_d[key]
            else:
                key = {"arm6b_terminal_w8": "seed0_arm6b", "arm8_terminal_w8": "seed0_arm8"}[field]
                got_base = probe_d[key]
        rows.append(
            {
                "block": blk,
                "pos": pos,
                "seed_base": base,
                "offset": off,
                "x": got_x,
                "n": got_n,
                "source": src,
                "field": field,
                "ok": got_x == x and got_n == n and got_base == base,
            }
        )
    return rows


def seed_scan():
    detail, ok = {}, True
    for base, spec in SEED_SCAN.items():
        hits = set()
        for f in glob.glob(os.path.join(REPO_ROOT, "evidence/*/run.out")):
            rel = os.path.relpath(f, REPO_ROOT)
            if rel == OWN_RECEIPT:
                continue
            with open(f, "r", errors="replace") as fh:
                if base in fh.read():
                    hits.add(rel)
        want = set(spec["files"])
        detail[base] = {"expected": sorted(want), "found": sorted(hits), "ok": hits == want}
        ok = ok and hits == want
    return detail, ok


def guards(line_d, probe_d, hot_d, rows):
    g = {}
    g["expected_table"] = all(r["ok"] for r in rows)
    detail, ok = seed_scan()
    g["seed_scan"] = {"detail": detail, "ok": ok}
    cal = {
        "line": line_d.get("cal_mid_w4"),
        "blockprobe": probe_d.get("cal_mid_w4"),
        "hotrepro": hot_d.get("cal_mid_w4"),
    }
    # Count-field comparison: the receipt blocks also carry a "share" key,
    # so full-dict equality would fail on the extra field.
    cal_ok = all(
        v is not None
        and {k: v.get(k) for k in ("D2T", "L2", "other")} == CAL_EXPECTED
        for v in cal.values()
    )
    g["cal_identity"] = {"values": cal, "ok": cal_ok}
    g["hotrepro_cross_sums"] = {
        "afresh": hot_d["afresh_subwindows"][0]["x"] + hot_d["afresh_subwindows"][1]["x"]
        == hot_d["afresh_terminal_w8"]["D2T"] == 691,
        "bfresh": hot_d["bfresh_subwindows"][0]["x"] + hot_d["bfresh_subwindows"][1]["x"]
        == hot_d["bfresh_terminal_w8"]["D2T"] == 714,
    }
    g["ok"] = (
        g["expected_table"]
        and ok
        and g["cal_identity"]["ok"]
        and all(g["hotrepro_cross_sums"].values())
    )
    return g


def T_stat(order):
    """order: {block: [(x, n) in position order]} -> first-vs-rest pooled share diff."""
    fx = sum(order[b][0][0] for b in TEST_BLOCKS)
    fn = sum(order[b][0][1] for b in TEST_BLOCKS)
    rx = sum(x for b in TEST_BLOCKS for x, _ in order[b][1:])
    rn = sum(n for b in TEST_BLOCKS for _, n in order[b][1:])
    return fx / fn - rx / rn


def C_stat(order):
    """order: {block: [(x, n) in position order]} -> sum pos*(x/n)."""
    total = 0.0
    for b in TEST_BLOCKS:
        for i, (x, n) in enumerate(order[b], start=1):
            total += i * (x / n)
    return total


def permute(order):
    perms = []
    keys = [order[b] for b in TEST_BLOCKS]
    for p1 in itertools.permutations(keys[0]):
        for p2 in itertools.permutations(keys[1]):
            perms.append({TEST_BLOCKS[0]: list(p1), TEST_BLOCKS[1]: list(p2)})
    return perms


def wilson(x, n, z=1.959963984540054):
    if n == 0:
        return [0.0, 0.0]
    p = x / n
    d = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round((centre - half) / d, 5), round((centre + half) / d, 5)]


def main():
    line_d, _ = load_receipt(LINE)
    probe_d, _ = load_receipt(BLOCKPROBE)
    hot_d, _ = load_receipt(HOTREPRO)
    rows = build_windows(line_d, probe_d, hot_d)
    g = guards(line_d, probe_d, hot_d, rows)
    if not g["ok"]:
        print(json.dumps({"label": "W8_BLOCKPOS", "status": "REFUSED", "guards": g}, indent=2))
        print('VERDICTS {"status": "REFUSED"}')
        return 3

    test_rows = [r for r in rows if r["block"] in TEST_BLOCKS]
    excl_rows = [r for r in rows if r["block"] not in TEST_BLOCKS]
    observed = {b: [[r["x"], r["n"]] for r in sorted(
        [q for q in test_rows if q["block"] == b], key=lambda q: q["pos"])] for b in TEST_BLOCKS}

    t_obs = T_stat(observed)
    c_obs = C_stat(observed)
    perms = permute(observed)
    m = len(perms)
    p1 = sum(1 for o in perms if T_stat(o) >= t_obs - TOL) / m
    p2 = sum(1 for o in perms if C_stat(o) <= c_obs + TOL) / m
    floor = 1.0 / m

    raw = {"P1": p1, "S2": p2}
    order = sorted(raw.items(), key=lambda kv: kv[1])
    adj, reject = {}, {}
    for i, (name, p) in enumerate(order):
        adj[name] = min(1.0, (len(raw) - i) * p)
        reject[name] = adj[name] < ALPHA

    if reject["P1"] and reject["S2"]:
        branch = "POSITION_STRUCTURE_BOTH"
    elif reject["P1"]:
        branch = "FIRST_WINDOW_ELEVATION"
    elif reject["S2"]:
        branch = "POSITION_TREND"
    else:
        branch = "POSITION_STRUCTURE_NOT_DETECTED"

    fx = sum(observed[b][0][0] for b in TEST_BLOCKS)
    fn = sum(observed[b][0][1] for b in TEST_BLOCKS)
    rx = sum(x for b in TEST_BLOCKS for x, _ in observed[b][1:])
    rn = sum(n for b in TEST_BLOCKS for _, n in observed[b][1:])

    out = {
        "label": "W8_BLOCKPOS",
        "status": "OK",
        "windows": rows,
        "excluded_windows": [
            {**{k: v for k, v in r.items() if k != "ok"},
             "reason": "single-window block: no within-block position contrast"}
            for r in excl_rows
        ],
        "guards": g,
        "observed": {
            "pooled_first": {"x": fx, "n": fn, "share": fx / fn, "wilson95": wilson(fx, fn)},
            "pooled_rest": {"x": rx, "n": rn, "share": rx / rn, "wilson95": wilson(rx, rn)},
            "T_obs": t_obs,
            "C_obs": c_obs,
            "block_totals": {
                b: {
                    "x": sum(x for x, _ in observed[b]),
                    "n": sum(n for _, n in observed[b]),
                }
                for b in TEST_BLOCKS
            },
        },
        "tests": {
            "P1": {"stat": t_obs, "p": p1, "perm_count": m, "floor": floor,
                   "alternative": "first > rest", "holm_adj": adj["P1"], "reject": reject["P1"]},
            "S2": {"stat": c_obs, "p": p2, "perm_count": m, "floor": floor,
                   "alternative": "share declines with position (C small)", "holm_adj": adj["S2"], "reject": reject["S2"]},
            "alpha_family": ALPHA,
            "multiplicity": "Holm-Bonferroni over {P1, S2}",
        },
        "branch": branch,
        "interpretation_limits": [
            "directions chosen after seeing these same windows: p quantifies extremity under within-block exchangeability, not independent confirmation",
            "enumeration floor p = 1/%d" % m,
            "arm-7 excluded structurally (single-window block); reported as context only",
            "~500-seed window resolution; sub-window structure undetected by construction",
            "in-silico kTAM simulation only; no physical-replicate claim",
        ],
    }
    print(json.dumps(out, indent=2))
    print('VERDICTS {"P1": "%s", "S2": "%s", "BRANCH": "%s"}' % (
        "REJECT" if reject["P1"] else "NOT_DETECTED",
        "REJECT" if reject["S2"] else "NOT_DETECTED",
        branch,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
