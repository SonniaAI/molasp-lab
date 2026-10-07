"""Pin the kTAM species-death grid receipt (tick 23, SON-4775).

The grid ran on the capped cluster queue (job hxq-20828594,
paperclip-test image, node spark-4a06, exit 0; queue receipt beside
the data). This test pins the numbers the narrative cites so the
receipt cannot silently drift from the claims.

Raw receipt: evidence/2026-10-06-species-death-survey/ktam_grid.out
Pre-registration: ktam_mc_survey.py header (committed before the run).

History note (QA re-review of 424d4dc, 2026-10-06): this file first
landed with module-level test functions and no unittest.TestCase, so
`python3 -m unittest discover` collected 0 of them — the pins were
dead code while CI stayed green. They now live in a TestCase class;
tests/test_collection_guard.py keeps that defect class from recurring.
"""
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "evidence",
                   "2026-10-06-species-death-survey", "ktam_grid.out")

BUILD1 = "P_AND_corrected"
TICK19_BUILD1 = {0.5: 0.540, 2.0: 0.790, 4.0: 0.984, 7.0: 0.870}

# strict "pqr" counts / 500, keyed by removed species (None = build1)
PINNED_PQR = {
    None: {0.5: 270, 2.0: 397, 4.0: 493, 7.0: 437},
    "D1T": {0.5: 292, 2.0: 411, 4.0: 483, 7.0: 9},
    "D2T": {0.5: 272, 2.0: 374, 4.0: 488, 7.0: 2},
    "V0p": {0.5: 337, 2.0: 386, 4.0: 466, 7.0: 0},
    "Vp": {0.5: 412, 2.0: 464, 4.0: 324, 7.0: 0},
    "DAr": {0.5: 238, 2.0: 330, 4.0: 350, 7.0: 2},
    "DBr": {0.5: 121, 2.0: 58, 4.0: 10, 7.0: 0},
    "L3": {0.5: 18, 2.0: 5, 4.0: 0, 7.0: 0},
    "L1": {0.5: 0, 2.0: 0, 4.0: 0, 7.0: 0},
    "L2": {0.5: 0, 2.0: 0, 4.0: 0, 7.0: 0},
    "S1": {0.5: 0, 2.0: 0, 4.0: 0, 7.0: 0},
    "S2": {0.5: 0, 2.0: 0, 4.0: 0, 7.0: 0},
    "S3": {0.5: 0, 2.0: 0, 4.0: 0, 7.0: 0},
}

EXPECTED_P3_VIOLATIONS = [["D1T", 0.5], ["D1T", 2.0], ["D1T", 4.0],
                          ["D2T", 0.5], ["D2T", 2.0], ["D2T", 4.0],
                          ["V0p", 0.5], ["V0p", 2.0], ["V0p", 4.0],
                          ["Vp", 0.5], ["Vp", 2.0], ["Vp", 4.0]]


def load():
    with open(OUT) as f:
        lines = [l for l in f.read().splitlines() if l.strip()]
    header = json.loads(lines[0])
    rows, totals, verdicts = {}, {}, None
    for l in lines[1:]:
        d = json.loads(l)
        if "verdicts" in d:
            verdicts = d["verdicts"]
        elif "pqr_ci95_upper" in d:
            totals[d["system"]] = d
        else:
            rows.setdefault(d["system"], {})[d["dGmc"]] = d
    return header, rows, totals, verdicts


def sysname(suffix):
    return BUILD1 if suffix is None else BUILD1 + "_missing_" + suffix


class TestKtamSurveyReceipt(unittest.TestCase):
    def test_header_protocol_of_record(self):
        header, rows, totals, _ = load()
        assert header["Gse"] == 9.0
        assert header["T_read_rule"] == "400*exp(Gmc)"
        assert header["n_per_point"] == 500
        assert header["seed_base"] == 20261031
        assert len(header["systems"]) == 13          # build1 + 12 removals
        assert len(rows) == 13 and len(totals) == 13
        for name, points in rows.items():            # 4 points each
            assert sorted(points) == [0.5, 2.0, 4.0, 7.0], name

    def test_s4_calibration_within_2x_and_near_exact(self):
        _, rows, _, _ = load()
        for dG, ref in TICK19_BUILD1.items():
            f = rows[BUILD1][dG]["pqr_frac"]
            assert 0.5 <= f / ref <= 2.0, (dG, f)
        # protocol of record reproduces tick-19 almost exactly
        assert abs(rows[BUILD1][0.5]["pqr_frac"] - 0.540) < 0.01
        assert abs(rows[BUILD1][2.0]["pqr_frac"] - 0.794) < 0.01
        assert abs(rows[BUILD1][4.0]["pqr_frac"] - 0.986) < 0.005
        assert abs(rows[BUILD1][7.0]["pqr_frac"] - 0.874) < 0.01

    def test_pinned_strict_pqr_counts(self):
        _, rows, _, _ = load()
        for suffix, points in PINNED_PQR.items():
            for dG, n in points.items():
                got = rows[sysname(suffix)][dG]["pqr"]
                assert got == n, (suffix, dG, got, n)

    def test_verdicts_against_pre_registration(self):
        _, _, _, v = load()
        assert v["P2_violations"] == [["L3", 0.5], ["L3", 2.0]]
        assert sorted(map(tuple, v["P3_violations"])) == \
            sorted(map(tuple, EXPECTED_P3_VIOLATIONS))
        assert v["P4_violations"] == []
        assert v["S4_min_ratio"] == 1.0

    def test_p1_refuted_half_dbr_never_repairs(self):
        # DAr repairs (ratio >= 0.5 somewhere at dG <= 4) but DBr does not
        _, rows, _, _ = load()
        dar = rows[sysname("DAr")]
        dbr = rows[sysname("DBr")]
        assert max(dar[d]["ratio"] for d in (0.5, 2.0, 4.0)) >= 0.5
        for dG in (0.5, 2.0, 4.0, 7.0):
            r = dbr[dG]["ratio"]
            assert r is not None and r < 0.5, (dG, r)

    def test_dg7_starvation_reads_the_atam_terminal(self):
        # P4 positive form: at dG 7 the loose readout is the residual model
        _, rows, _, _ = load()
        loose = rows[sysname("DBr")][7.0]["decode_loose"]
        assert loose.get("pq", 0) >= 499            # drop_r_rule stable model
        # L3-missing: readers still compute r (DBr needs no lock tile) while
        # the strict lock decode is dead — pinned as measured
        loose3 = rows[sysname("L3")][7.0]["decode_loose"]
        assert loose3.get("pq", 0) == 77 and loose3.get("pqr", 0) == 423

    def test_queue_receipt_matches_job_record(self):
        import hashlib
        ev = os.path.dirname(OUT)
        with open(os.path.join(ev, "ktam_grid_queue_receipt.json")) as f:
            r = json.load(f)
        assert r["job"] == "hxq-20828594fc9d3d0e"
        assert r["state"] == "complete" and r["exit_code"] == 0
        assert r["image_verified"] is True
        assert r["collection_errors"] == []
        assert r["image_alias"] == "paperclip-test"
        assert r["node"] == "spark-4a06"
        assert r["job_completion"] == "2026-10-06T23:26:39Z"


if __name__ == "__main__":
    unittest.main()
