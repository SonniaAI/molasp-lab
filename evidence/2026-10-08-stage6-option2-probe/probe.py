#!/usr/bin/env python3
"""Stage-6 Option II probe-first baseline (designs/009 §9.5 landing order, step 1).

Regenerates every pinned receipt generator on the PRISTINE tree
(ec49a73, compiler untouched) and byte-compares against the committed
receipts.  For receipts that embed wall-clock timings, additionally
compares a timing-normalized copy (timing fields masked) to separate
content drift from machine noise.  Freezes the manifest as the pre-edit
reference for the implementation tick.  Reports, never gates (d4).
"""
import hashlib
import json
import os
import re
import subprocess
import sys

REPO = "/home/node/.openclaw/workspaces/research-strategy-executive/molasp-lab"
OUT = os.path.join(REPO, "evidence/2026-10-08-stage6-option2-probe")
TMP = "/tmp/son4850-58232cc7"

GENERATORS = [
    ("evidence/2026-10-07-lock-misplacement-census", "lock_misplacement_census.py", "lock_misplacement_census.out"),
    ("evidence/2026-10-07-census-generality", "census_generality.py", "census_generality.out"),
    ("evidence/2026-10-07-parity-corpus", "parity_run.py", "run.out"),
]

# wall-clock noise: header "total wall 0.03s" and JSON "seconds_*": 0.001
TIMING_PATTERNS = [
    (re.compile(rb"total wall [0-9.]+s"), b"total wall <T>s"),
    (re.compile(rb'"seconds_[a-z]+": [0-9.]+'), b'"seconds_*": <T>'),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize(data):
    for pat, repl in TIMING_PATTERNS:
        data = pat.sub(repl, data)
    return data


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    results = []
    all_raw_ok = True
    all_norm_ok = True
    for d, script, outname in GENERATORS:
        committed = os.path.join(REPO, d, outname)
        regen = os.path.join(TMP, outname)
        with open(regen, "wb") as f:
            proc = subprocess.run([sys.executable, script], cwd=os.path.join(REPO, d),
                                  stdout=f, stderr=subprocess.PIPE)
        identical = norm_identical = False
        csha = rsha = None
        diff_lines = []
        if proc.returncode == 0 and os.path.exists(committed):
            cdata = open(committed, "rb").read()
            rdata = open(regen, "rb").read()
            csha, rsha = sha256(committed), sha256(regen)
            identical = cdata == rdata
            norm_identical = normalize(cdata) == normalize(rdata)
            if not identical:
                cl, rl = cdata.splitlines(), rdata.splitlines()
                for k in range(max(len(cl), len(rl))):
                    a = cl[k] if k < len(cl) else b"<EOF>"
                    b = rl[k] if k < len(rl) else b"<EOF>"
                    if a != b:
                        diff_lines.append({"line": k + 1, "committed": a.decode(errors="replace")[:120],
                                           "regenerated": b.decode(errors="replace")[:120]})
        all_raw_ok = all_raw_ok and identical
        all_norm_ok = all_norm_ok and norm_identical
        results.append({
            "generator": d + "/" + script,
            "committed_receipt": d + "/" + outname,
            "committed_sha256": csha,
            "regenerated_sha256": rsha,
            "byte_identical": identical,
            "timing_normalized_identical": norm_identical,
            "regen_exit": proc.returncode,
            "raw_diff_lines": diff_lines if not identical else [],
        })
    manifest = {
        "probe": "stage6-option2-preedit-baseline",
        "tree_head": head,
        "compiler": "pristine (no gate edits this tick; designs/009 §9.5 step 1)",
        "all_byte_identical": all_raw_ok,
        "all_timing_normalized_identical": all_norm_ok,
        "receipts": results,
    }
    with open(os.path.join(OUT, "probe_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    print(json.dumps({"all_byte_identical": all_raw_ok,
                      "all_timing_normalized_identical": all_norm_ok,
                      "raw_diffs": {r["generator"]: r["raw_diff_lines"] for r in results if r["raw_diff_lines"]}}, indent=2))


if __name__ == "__main__":
    main()
