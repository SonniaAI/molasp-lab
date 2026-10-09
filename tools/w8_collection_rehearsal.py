#!/usr/bin/env python3
"""Collection-day REHEARSAL for the w8 chain (tick 90, 2026-10-09).

Every piece of the five-step collection chain is committed and pinned
piecewise (tick 80 collector gates, tick 84 import glue, ticks 86-89
the three uncertainty axes and the decision atlas), but nothing drives
the chain END TO END through the real command lines.  This tool does
exactly that, on clearly-labeled SYNTHETIC data, before the datum
exists:

  step 1  build a synthetic protocol-2 result blob for the REAL
          request id (frame format pinned from the queue client
          source by tick 84);
  step 2  python3 tools/import_queue_result.py <blob>
              --request <RID> --evidence-root <root>/<scenario>
  step 3  python3 tools/collect_w8.py <root>/<scenario>/run.out
              --out <root>/<scenario>/verdict.json
  step 4  python3 tools/w8_decision_atlas.py <x> <k>
              --json <root>/<scenario>/atlas.json
  step 5  write <root>/rehearsal_receipt.json; PASS/FAIL per step.

The steps run the REAL CLIs as subprocesses (exactly the collection-day
command lines), not imported functions — so argument surfaces, exit
codes and file plumbing are what gets proven.

Discipline:
- ZERO interpretive authority added: the synthetic stdout is stamped
  with a REHEARSAL-SYNTHETIC preamble line, every artifact lives under
  the rehearsal root, and the receipt records "synthetic": true.  The
  frozen gates stay in tools/collect_w8.py, untouched.
- The rehearsal root must not resolve inside the repo's evidence/
  tree — the guard refuses first, so synthetic data can never be
  mistaken for the real datum by path.
- Refusal spot-checks ride along at CLI level: wrong request id,
  empty stdout section, census below the MIN_EVENTS floor.

Usage:
  python3 tools/w8_collection_rehearsal.py [--root DIR] [--keep]
Default root: a fresh tempdir (kept only with --keep or on failure).
"""
import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REQUEST_ID = ("ed50c7baf2d8b935bb118f25758394ddfb04a671e902f39bfa6"
              "721b274daa85")
PRED_W8 = 0.83376          # collect_w8.py receipt constant (duplicated)
Z = 1.96                   # same z as the tick-87/88 Wilson formula


class RehearsalRefused(Exception):
    """Raised when the rehearsal cannot run safely."""


def _wilson95(k, n, z=Z):
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1.0 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def _census(d2t, l2, n=500):
    return {"D2T": d2t, "L2": l2, "other": n - d2t - l2,
            "share": d2t / float(d2t + l2) if d2t + l2 else None}


def synthetic_runout(fr_term, w8_label):
    """Harness stdout shape (as pinned by tests/test_collect_w8.py),
    stamped with a REHEARSAL-SYNTHETIC preamble line."""
    dev = abs(fr_term[0] / float(sum(fr_term)) - PRED_W8)
    stats = {
        "n_per_range": 500, "seed0_cal": 260261107,
        "seed0_fresh": 280261107, "dg": 2, "win_mult": 8,
        "t_mid_is_w4": True,
        "cal_mid_w4": _census(367, 131),          # CAL_OK census
        "cal_terminal_w8": _census(419, 73),
        "fresh_mid_w4": _census(368, 132),
        "fresh_terminal_w8": _census(*fr_term),
        "pred_w8": PRED_W8, "haz95_arm": 0.81585,
        "dev_fresh_w8": dev,
        "fresh_w8_wilson95": _wilson95(fr_term[0], sum(fr_term)),
        "fresh_mid_w4_dev_vs_dw9_receipt": abs(368 / 500.0 - 0.716),
        "receipts": {"dw9_fresh_w4": 0.716,
                     "vh_heldout_w4": 0.7379032258064516},
    }
    verdict = {"CAL": "CAL_OK", "W8": w8_label}
    lines = ["REHEARSAL-SYNTHETIC — not the datum (tick 90 drill)",
             "[cluster preamble] node spark-4a06", ""]
    lines.append(json.dumps(stats))
    lines.append(json.dumps(verdict))
    lines.append("VERDICTS " + json.dumps(verdict, sort_keys=True))
    return "\n".join(lines) + "\n"


def synth_blob(stdout_text, request_id=REQUEST_ID, stderr_text="",
               exit_status=0):
    """Protocol-2 frame exactly as tick 84 pinned it from the queue
    client source: each section is file content + ONE `echo` newline
    (a blank line).  Built by explicit concatenation — a join-based
    draft added one newline too many per section and the rehearsal's
    own byte-exactness check caught it pre-landing (disclosed in the
    tick-90 log)."""
    parts = [
        "HX-OUT-BEGIN:%s\n" % request_id,
        "HX-FILE:status\n%d\n\n" % exit_status,
        "HX-FILE:stderr\n%s\n" % stderr_text,
        "HX-FILE:stdout\n%s\n" % stdout_text,
        "HX-QUEUE-EXIT:%d\n" % exit_status,
        "HX-OUT-END:%s\n" % request_id,
    ]
    return "".join(parts)


def ensure_safe_root(root):
    """The rehearsal root must never be inside the evidence tree."""
    root = Path(root).resolve()
    evidence = (REPO / "evidence").resolve()
    if root == evidence or evidence in root.parents:
        raise RehearsalRefused(
            "rehearsal root %s is inside the evidence tree %s — "
            "synthetic data must never land there" % (root, evidence))
    return root


def _cli(args):
    return subprocess.run([sys.executable] + [str(a) for a in args],
                          cwd=str(REPO), capture_output=True,
                          text=True)


# (name, fresh_terminal census, expected W8 label, atlas x/k source,
#  expected atlas verdict, expected region name)
SCENARIOS = [
    ("held", (384, 77), "HELD", "HELD", "hold-only"),
    ("refuted", (300, 200), "REFUTED", "REFUTED", "chain-falsified"),
    ("no_events", (30, 10), "NO_EVENTS", "NO_EVENTS", None),
]


def rehearse(root):
    """Run the full chain on all scenarios; return the receipt dict.

    Raises AssertionError on any step mismatch, RehearsalRefused on an
    unsafe root.  Refusal spot-checks are recorded, not raised.
    """
    root = ensure_safe_root(root)
    root.mkdir(parents=True, exist_ok=True)
    receipt = {"schema": 1, "tool": "w8_collection_rehearsal",
               "synthetic": True, "request_id": REQUEST_ID,
               "scenarios": [], "refusals": {},
               "interpretation": "none — the frozen gates live in "
                                 "tools/collect_w8.py; this drill "
                                 "proves plumbing only"}
    for name, fr_term, w8, atlas_v, region_name in SCENARIOS:
        scen_root = root / name
        blob_path = root / ("%s.blob" % name)
        stdout_text = synthetic_runout(fr_term, w8)
        blob_path.write_text(synth_blob(stdout_text))

        proc = _cli(["tools/import_queue_result.py", blob_path,
                     "--request", REQUEST_ID,
                     "--evidence-root", scen_root])
        assert proc.returncode == 0, "import failed (%s): %s" % (
            name, proc.stderr.strip()[-400:])
        run_out = (scen_root / "run.out").read_text()
        assert run_out == stdout_text, \
            "run.out not byte-exact for %s" % name
        assert run_out.startswith("REHEARSAL-SYNTHETIC"), \
            "synthetic stamp lost for %s" % name
        manifest = json.loads(
            (scen_root / "run.out.import.json").read_text())
        assert manifest["interpretation"].startswith("none")

        proc = _cli(["tools/collect_w8.py", scen_root / "run.out",
                     "--out", scen_root / "verdict.json"])
        assert proc.returncode == 0, "collect failed (%s): %s" % (
            name, proc.stderr.strip()[-400:])
        verdict = json.loads((scen_root / "verdict.json").read_text())
        assert verdict["cross_check"] == "ok", name
        assert verdict["branch"] == "CAL_OK+%s" % w8, \
            (name, verdict["branch"])

        x, k = fr_term[0], sum(fr_term)
        proc = _cli(["tools/w8_decision_atlas.py", x, k,
                     "--json", scen_root / "atlas.json"])
        assert proc.returncode == 0, "atlas failed (%s): %s" % (
            name, proc.stderr.strip()[-400:])
        atlas = json.loads((scen_root / "atlas.json").read_text())
        assert atlas["verdict"] == atlas_v, (name, atlas["verdict"])
        if region_name is not None:
            assert atlas["region"]["name"] == region_name, (
                name, atlas["region"]["name"])
        receipt["scenarios"].append(
            {"scenario": name, "datum": [x, k],
             "collector_branch": verdict["branch"],
             "atlas_verdict": atlas["verdict"],
             "atlas_region": region_name,
             "steps": "import+collect+atlas all exit 0"})

    bad_rid = "0" * 64
    blob_path = root / "wrong-request.blob"
    blob_path.write_text(synth_blob(synthetic_runout((384, 77), "HELD"),
                                    request_id=bad_rid))
    proc = _cli(["tools/import_queue_result.py", blob_path,
                 "--request", REQUEST_ID,
                 "--evidence-root", root / "wrong-request"])
    receipt["refusals"]["wrong_request_id"] = {
        "exit": proc.returncode,
        "refused": proc.returncode != 0
                   and "HX-OUT-BEGIN" in proc.stderr}

    blob_path = root / "empty-stdout.blob"
    frame = synth_blob("", )  # empty stdout section
    # rebuild explicitly (empty string section already exact)
    blob_path.write_text(frame)
    proc = _cli(["tools/import_queue_result.py", blob_path,
                 "--request", REQUEST_ID,
                 "--evidence-root", root / "empty-stdout"])
    receipt["refusals"]["empty_stdout"] = {
        "exit": proc.returncode,
        "refused": proc.returncode != 0
                   and "stdout section is empty" in proc.stderr}

    assert all(r["refused"] for r in receipt["refusals"].values()), \
        "a refusal spot-check did not refuse: %r" % receipt["refusals"]
    (root / "rehearsal_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", help="rehearsal root (default: tempdir)")
    ap.add_argument("--keep", action="store_true",
                    help="keep the default tempdir root")
    args = ap.parse_args(argv)
    tmp = None
    if args.root:
        root = Path(args.root)
    else:
        tmp = tempfile.mkdtemp(prefix="w8-rehearsal-")
        root = Path(tmp)
    try:
        receipt = rehearse(root)
    except Exception:
        if tmp and not args.keep:
            print("rehearsal FAILED; artifacts kept at %s" % tmp)
        raise
    for scen in receipt["scenarios"]:
        print("PASS %-10s datum %s -> %s / atlas %s (%s)" % (
            scen["scenario"], scen["datum"], scen["collector_branch"],
            scen["atlas_verdict"], scen["atlas_region"]))
    for name, r in receipt["refusals"].items():
        print("PASS refusal %-16s exit=%d (refused=%s)" % (
            name, r["exit"], r["refused"]))
    print("rehearsal receipt: %s" % (root / "rehearsal_receipt.json"))
    if tmp and not args.keep:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
        print("(tempdir root removed; rerun with --keep to inspect)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
