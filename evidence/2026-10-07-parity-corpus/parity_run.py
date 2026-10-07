"""Parity-corpus run harness (tick 46).

Runs molasp/parity.py's corpus report and prints the per-program
verdicts plus a JSON block.  The saved output of this script IS the
receipt (run.out); tests/test_parity_corpus.py pins against it and
independently recomputes the three smallest BFS arms.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", ".."))

from molasp.parity import CORPUS, REFUSALS, corpus_report  # noqa: E402


def main():
    t0 = time.perf_counter()
    rep = corpus_report()
    wall = time.perf_counter() - t0
    print("OR-AND parity corpus — compiler v0.1 (tick 46)")
    print("programs: %d compiling + %d refusals | total wall %.2fs"
          % (len(rep["corpus"]), len(rep["refusals"]), wall))
    for r in rep["corpus"]:
        print("  %s ok=%-5s n=%d tiles=%2d asm=%3d term=%d decode=%s "
              "locks=%s dead=%s absent=%s bfs=%.2fs"
              % (r["name"], r["ok"], r["n_rows"], r["tiles"],
                 r["assemblies"], r["terminals"],
                 "+".join(r["terminal_decodes"][0])[:20]
                 if r["terminal_decodes"] else "?",
                 r["full_locks"], ",".join(r["dead_variant_glues"]) or "-",
                 all(r["dead_glues_absent"].values()), r["seconds_bfs"]))
        print("      axis: %s" % CORPUS[r["name"]][2])
    for r in rep["refusals"]:
        print("  %s ok=%-5s %s: %s" % (r["name"], r["ok"], r["raised"],
                                       r["message"]))
        print("      axis: %s" % REFUSALS[r["name"]][4])
    print("ALL_OK", rep["all_ok"])
    print("--- json ---")
    print(json.dumps(rep, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
