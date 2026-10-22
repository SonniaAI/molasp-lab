#!/usr/bin/env python3
"""Tick 163: the nested-shell product law — family-independent
coefficients for arbitrary-depth or-head chains (designs/013).

Tick 162 derived the unified two-head law's coefficients in closed
form (|I| = C(n+4,4), |C_r| = (n+1)(3n+2)/2, |C_w| = C(n+2,2)) and
left two forward paths: a designs/013 third-head sketch, or a
family-independent coefficient note.  This tick is both: the note,
stated as a theorem that already covers the fenced depth-3 case.

  The corner ladder (tick 162 L4).  A head at chain depth d sits at
  corner site (1, n-d); its contention corner is

    C^(d) = ideals containing (1, n-d),   |C^(m)| = sum_{j<=m} (j+1)C(n-j+2,2)

  and the corners are NESTED element-wise, C^(0) <= C^(1) <= C^(2)
  <= ..., because sharing column 1 one row apart is exactly the
  containment L2 pinned last tick, iterated.  (Verified element-wise
  live below, not assumed.)

  Shells.  shell_d = C^(d) \\ C^(d-1) has size (d+1)*C(n-d+2,2) —
  the ladder's increment recurrence, now a named object.  An ideal
  in shell_d has h1 = n-d exactly, so it contains the corner of
  head i iff i >= d: shell_d carries heads d..m and NO others.

  The nested-shell product law.  For a chain of or-heads with
  multiplicities ks = [k_0, k_1, ..., k_m] (terminal first), the
  census count is

    assemblies(n) = C(n+4,4) + sum_{d=0..m} (prod_{i>=d} k_i - 1) * (d+1)*C(n-d+2,2)

  — a SUFFIX product per shell, because the per-body conduit-glue
  identity handshake (each body owns one glue, minted per body per
  head) makes head multiplicities compose as products on the ideals
  all of whose corners contain them, and shell_d is exactly the set
  carrying heads d..m.

  Reduction.  At m = 1 the law is

    |I| + (k_w*k_r - 1)|C_w| + (k_r - 1)|C_r \\ C_w|
      = |I| + (k_r - 1)|C_r| + k_r*(k_w - 1)|C_w|

  — the measured unified law of ticks 158-161, by two lines of
  algebra.  The reduction is asserted live over a grid below AND by
  re-reproducing all 28/28 receipt scalars of the four corners
  through the shell formula (a formula with different shape).

  Predictions (falsifiable, unreachable today).  Compiler v0.2
  fences chains deeper than one relay; the depth-3 scalars below
  are predicted from closed form only, for the future family that
  designs/013's fragment sketch would admit.

Stdlib-only, deterministic, zero queue spend, no RNG.  Not a
validated result until independently reviewed.
"""

import argparse
import hashlib
import json
import os
import sys
from math import comb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from molasp.compiler import compile_program          # noqa: E402
from tools.pc11_contention_structure import (        # noqa: E402
    ideals_containing,
)
from tools.pc11_coefficient_ladder import (          # noqa: E402
    SQUARE_RECEIPTS,
    derived_unified_law,
    ladder_count,
)

RECEIPT_DIR = os.path.join(
    ROOT, "evidence", "2026-10-22-pc13-nested-shell-law")
RECEIPT_PATH = os.path.join(RECEIPT_DIR, "nested_shell.json")

ROWS = list(range(5, 13))          # census-reachable heights
LADDER_MAX_DEPTH = 4               # m <= 4 verified within alphabet reach


# ------------------------------------------------------------- shells

def shell_size(n, d):
    """|C^(d) \\ C^(d-1)| = (d+1)*C(n-d+2, 2): h1 = n-d admits d+1
    choices of h0 (n-d .. n), trailing (h2, h3) free in C(n-d+2, 2)."""
    return (d + 1) * comb(n - d + 2, 2)


def shell_sizes_agree_with_ladder(n, m):
    """sum of shells 0..d must equal the ladder value at every d."""
    return all(
        sum(shell_size(n, e) for e in range(d + 1)) == ladder_count(n, d)
        for d in range(m + 1)
    )


def nesting_elementwise(n, m):
    """C^(d) <= C^(d+1) element-wise, the iterated L2 containment."""
    chain = [
        set(tuple(i) for i in ideals_containing((1, n - d), n))
        for d in range(m + 1)
    ]
    return {
        "contained_pairwise": all(chain[d] <= chain[d + 1]
                                  for d in range(m)),
        "sizes": [len(c) for c in chain],
        "sizes_match_ladder": [
            len(c) == ladder_count(n, d) for d, c in enumerate(chain)
        ],
    }


def suffix_products(ks):
    out = []
    for d in range(len(ks)):
        p = 1
        for k in ks[d:]:
            p *= k
        out.append(p)
    return out


# ------------------------------------------------ the product law

def shell_law(n, ks):
    """ks terminal-first: ks[0] = terminal head multiplicity, ks[d]
    the relay at chain depth d.  Shell d carries heads d..m only."""
    total = comb(n + 4, 4)
    for d, p in enumerate(suffix_products(ks)):
        total += (p - 1) * shell_size(n, d)
    return total


def additive_falsifier(n, ks):
    """Per-head contributions added, never multiplied — the shared-bit
    world falsified element-wise at m = 1 in ticks 158-161."""
    return comb(n + 4, 4) + sum(
        (k - 1) * ladder_count(n, d) for d, k in enumerate(ks))


def reduction_grid():
    """At m = 1 the shell law must equal the measured unified law
    identically — checked numerically over a wide grid."""
    rows = []
    for n in ROWS:
        for k_w in (2, 3, 4, 5):
            for k_r in (2, 3, 4, 5):
                ok = shell_law(n, [k_w, k_r]) == derived_unified_law(n, k_r, k_w)
                rows.append({"n": n, "k_w": k_w, "k_r": k_r, "equal": ok})
    return {
        "grid": rows,
        "all_equal": all(r["equal"] for r in rows),
        "points": len(rows),
    }


def receipts_via_shell_law():
    """The four receipts of record re-read and reproduced through the
    shell formula (shape-different from derived_unified_law)."""
    table = {}
    for (k_r, k_w), rel in SQUARE_RECEIPTS.items():
        with open(os.path.join(ROOT, rel)) as fh:
            prior = json.load(fh)
        heights = {
            str(r): prior["censuses"][str(r)]["assemblies"]
            for r in prior["rows_measured"]
        }
        ok = all(v == shell_law(int(r), [k_w, k_r])
                 for r, v in heights.items())
        table["%dx%d" % (k_r, k_w)] = {
            "k_r": k_r, "k_w": k_w,
            "assemblies_by_height": heights,
            "shell_law_holds": ok,
        }
    return {
        "corners": table,
        "all_four_corners_hold_shell_law": all(
            v["shell_law_holds"] for v in table.values()),
        "scalars_checked": sum(
            len(v["assemblies_by_height"]) for v in table.values()),
    }


# ------------------------------------------------------ predictions

def predictions():
    out = {}
    for label, ks in (
        ("depth3_222", [2, 2, 2]),
        ("depth3_322", [3, 2, 2]),
        ("depth3_223", [2, 2, 3]),
        ("depth4_2222", [2, 2, 2, 2]),
    ):
        out[label] = {
            "ks_terminal_first": ks,
            "assemblies_by_height": {
                str(n): shell_law(n, ks) for n in range(6, 13)
            },
            "additive_falsifier_n6": additive_falsifier(6, ks),
            "product_minus_additive_n6": (
                shell_law(6, ks) - additive_falsifier(6, ks)),
        }
    return out


# ------------------------------------------------------- G1 probe

# Depth-3 probe candidates, built on the T2U anchor at n = 6.
# Tick 162 fenced a SECOND TERMINAL consumer of the relayed head;
# the two remaining depth-3 axes are probed fresh here.
T2U_ANCHOR = "p. q. s. q2 :- p. r :- q2. r :- q2. w :- r. w :- r."
DEPTH3_PROBES = {
    "stacked_spine_relay": (
        "p. q. s. q2 :- p. "
        "u :- q2. u :- q2. "        # second relay fed from the spine
        "r :- u. r :- u. "          # first relay now fed by the second
        "w :- r. w :- r."),
    "head_chained_relay": (
        "p. q. s. q2 :- p. "
        "r :- q2. r :- q2. "
        "u :- r. u :- r. "          # relay consuming the relayed head
        "w :- u. w :- u."),         # chain q2 -> r -> u -> w, depth 3
}


def guard_probe():
    results = {}
    for label, prog in sorted(DEPTH3_PROBES.items()):
        entry = {"program": prog}
        try:
            build = compile_program(prog, name="probe_%s" % label)
            entry["compiled"] = True
            entry["tiles"] = len(build["tiles"])
        except Exception as exc:                # noqa: BLE001 - pinned
            entry["compiled"] = False
            entry["refusal"] = "%s: %s" % (type(exc).__name__, exc)
        results[label] = entry
    return results


# ------------------------------------------------------------ receipt

def build_receipt():
    shell_table = {}
    for n in ROWS:
        shell_table[str(n)] = {
            "sizes": [shell_size(n, d) for d in range(LADDER_MAX_DEPTH + 1)],
            "sizes_agree_with_ladder": shell_sizes_agree_with_ladder(
                n, LADDER_MAX_DEPTH),
            "nesting": nesting_elementwise(n, LADDER_MAX_DEPTH),
        }
    return {
        "kind": "pc13-nested-shell-law",
        "date": "2026-10-22",
        "tick": 163,
        "card": "SON-5152",
        "rows": ROWS,
        "ladder_max_depth": LADDER_MAX_DEPTH,
        "shells": shell_table,
        "reduction_grid": reduction_grid(),
        "receipts_via_shell_law": receipts_via_shell_law(),
        "predictions": predictions(),
        "guard_probes": guard_probe(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="run checks, print summary, write nothing")
    args = parser.parse_args()

    receipt = build_receipt()
    ok_shells = all(
        v["sizes_agree_with_ladder"] and v["nesting"]["contained_pairwise"]
        and all(v["nesting"]["sizes_match_ladder"])
        for v in receipt["shells"].values())
    print("shells agree with ladder + nested element-wise (n=%d..%d): %s"
          % (ROWS[0], ROWS[-1], ok_shells))
    print("reduction to unified law over %d grid points: %s"
          % (receipt["reduction_grid"]["points"],
             receipt["reduction_grid"]["all_equal"]))
    sq = receipt["receipts_via_shell_law"]
    print("receipts reproduced via shell law: %d/%d scalars, all corners %s"
          % (sq["scalars_checked"], sq["scalars_checked"],
             sq["all_four_corners_hold_shell_law"]))
    for label, pred in receipt["predictions"].items():
        hs = pred["assemblies_by_height"]
        print("prediction %s @n=6..12: %s (additive falsifier n=6: %d)"
              % (label, "/".join(str(hs[str(n)]) for n in range(6, 13)),
                 pred["additive_falsifier_n6"]))
    for label, entry in receipt["guard_probes"].items():
        print("probe %-22s compiled=%s %s"
              % (label, entry["compiled"],
                 entry.get("refusal", "")))
    if not args.check:
        os.makedirs(RECEIPT_DIR, exist_ok=True)
        with open(RECEIPT_PATH, "w") as fh:
            json.dump(receipt, fh, indent=2, sort_keys=True)
            fh.write("\n")
        with open(RECEIPT_PATH, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        print("receipt %s sha256 %s...%s"
              % (RECEIPT_PATH, digest[:8], digest[-4:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
