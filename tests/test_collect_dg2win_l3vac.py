"""Pins for the tick-47 collection harness
(evidence/2026-10-07-dg2-window-l3vac/collect.py).

The fixture numbers below are SYNTHETIC — they exist to pin the
harness's parsing, independent gate re-computation, mismatch refusal,
and rendering.  They are not measurements and pin no science.  The
real run's numbers land in the collection commit only after the
harness agrees with the experiment script's own machine verdicts.

Threshold sources: pre-registration docstring frozen at df958f2
(DW8-DW11, LV1-LV2; refs 0.464 s2 dG-2 fill / 0.412 probe fill /
0.100 probe L3 census).
"""
import importlib.util
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE), "evidence",
                  "2026-10-07-dg2-window-l3vac", "collect.py")

spec = importlib.util.spec_from_file_location("collect_dg2win_l3vac", EV)
collect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect)


def arm(name, **over):
    rec = {"arm": name, "dg": 0.5, "win_mult": 4.0, "n": 500,
           "fill_frac": 0.40, "frozen_nonfill_frac": 0.1,
           "churn_per_read": 0.001, "churn_total_mean": 3.0,
           "first_stable_persist": 0.72, "persist_n": 480,
           "site_dwell_frac": 0.5, "site_occupants": {},
           "mean_canonical_partial": 0.5, "first_stable_persist_by_name": {},
           "l3_terminal_frac": 0.0, "l3_episode_n": 40,
           "l3_episode_terminal_frac": 0.75}
    rec.update(over)
    return rec


def fixture_per():
    """Synthetic four-arm output: DW8/DW10/DW11/LV1/LV2 CONFIRMED,
    DW9 INCONCLUSIVE (share 124/200 = 0.62, inside the upper dead
    band (0.60, 0.65))."""
    return {
        "s2_dg0.5_l3probe": arm(
            "s2_dg0.5_l3probe", dg=0.5, win_mult=1.0, fill_frac=0.418,
            first_stable_persist=0.72, l3_terminal_frac=0.098,
            l3_episode_n=45, l3_episode_terminal_frac=0.80),
        "s2_dg0.5_win4": arm(
            "s2_dg0.5_win4", dg=0.5, win_mult=4.0, fill_frac=0.402,
            first_stable_persist=0.87, l3_terminal_frac=0.102,
            l3_episode_n=41, l3_episode_terminal_frac=0.78),
        "s2_dg2_win4": arm(
            "s2_dg2_win4", dg=2.0, win_mult=4.0, fill_frac=0.576,
            first_stable_persist=0.55,
            site_occupants={"D2T": 124, "L2": 76, "L3": 6},
            l3_terminal_frac=0.012, l3_episode_n=6,
            l3_episode_terminal_frac=0.5),
        "fam_dg2_win4": arm(
            "fam_dg2_win4", dg=2.0, win_mult=4.0, fill_frac=0.912,
            first_stable_persist=0.93, l3_terminal_frac=0.0,
            l3_episode_n=0, l3_episode_terminal_frac=None),
    }


FIXTURE_VERDICTS = {"DW8": "CONFIRMED", "DW9": "INCONCLUSIVE",
                    "DW10": "CONFIRMED", "DW11": "CONFIRMED",
                    "LV1": "CONFIRMED", "LV2": "CONFIRMED"}


def fixture_stdout():
    lines = ["[noise] arm sweep starting"]
    for name in collect.ARMS:
        lines.append(collect.json.dumps(fixture_per()[name]))
    lines.append(collect.json.dumps(FIXTURE_VERDICTS))
    lines.append("VERDICTS " + collect.json.dumps(FIXTURE_VERDICTS,
                                                  sort_keys=True))
    return "\n".join(lines) + "\n"


class TestParse(unittest.TestCase):
    def test_parse_extracts_arms_and_verdicts(self):
        per, vs = collect.parse_run_out(fixture_stdout())
        self.assertEqual(sorted(per), sorted(collect.ARMS))
        self.assertEqual(vs, FIXTURE_VERDICTS)

    def test_parse_rejects_missing_arm(self):
        text = fixture_stdout().replace(
            collect.json.dumps(fixture_per()["fam_dg2_win4"]), "")
        with self.assertRaises(collect.MalformedRun):
            collect.parse_run_out(text)

    def test_parse_rejects_missing_verdicts(self):
        text = "\n".join(
            l for l in fixture_stdout().splitlines()
            if not l.startswith("{\"DW8\"") and not l.startswith("VERDICTS"))
        with self.assertRaises(collect.MalformedRun):
            collect.parse_run_out(text)


class TestRecompute(unittest.TestCase):
    def test_fixture_verdicts(self):
        self.assertEqual(collect.recompute(fixture_per()),
                         FIXTURE_VERDICTS)

    def _gate(self, gate, **arm_over):
        per = fixture_per()
        if arm_over:
            target = arm_over.pop("_arm", "s2_dg2_win4")
            per[target] = arm(target, **arm_over)
        return collect.recompute(per)[gate]

    def test_dw8_gain_bands(self):
        self.assertEqual(self._gate("DW8", fill_frac=0.6),
                         "CONFIRMED")          # gain +0.136
        self.assertEqual(self._gate("DW8", fill_frac=0.5),
                         "INCONCLUSIVE")       # gain +0.036
        self.assertEqual(self._gate("DW8", fill_frac=0.4),
                         "FALSIFIED")          # gain -0.064

    def test_dw9_event_floor_and_share_bands(self):
        self.assertEqual(
            self._gate("DW9", site_occupants={"D2T": 24, "L2": 25}),
            "NO_EVENTS")                      # 49 < 50
        self.assertEqual(
            self._gate("DW9", site_occupants={"D2T": 30, "L2": 20}),
            "CONFIRMED")                      # share 0.60 boundary-in
        self.assertEqual(
            self._gate("DW9", site_occupants={"D2T": 17, "L2": 33}),
            "FALSIFIED")                      # share 0.34 < 0.35
        self.assertEqual(
            self._gate("DW9", site_occupants={"D2T": 35, "L2": 15}),
            "FALSIFIED")                      # share 0.70 > 0.65

    def test_dw10_floor_is_inclusive(self):
        self.assertEqual(
            self._gate("DW10", _arm="fam_dg2_win4", fill_frac=0.70),
            "CONFIRMED")
        self.assertEqual(
            self._gate("DW10", _arm="fam_dg2_win4", fill_frac=0.69),
            "FALSIFIED")

    def test_dw11_persist_bands_and_no_events(self):
        per = fixture_per()
        per["s2_dg0.5_win4"]["first_stable_persist"] = 0.80
        self.assertEqual(collect.recompute(per)["DW11"], "CONFIRMED")
        per["s2_dg0.5_win4"]["first_stable_persist"] = 0.65
        self.assertEqual(collect.recompute(per)["DW11"], "INCONCLUSIVE")
        per["s2_dg0.5_win4"]["first_stable_persist"] = None
        self.assertEqual(collect.recompute(per)["DW11"], "NO_EVENTS")

    def test_lv1_census_falsified_and_episode_floor(self):
        per = fixture_per()
        per["s2_dg0.5_l3probe"]["l3_terminal_frac"] = 0.04
        per["s2_dg0.5_win4"]["l3_terminal_frac"] = 0.04
        self.assertEqual(collect.recompute(per)["LV1"], "FALSIFIED")
        per = fixture_per()
        per["s2_dg0.5_l3probe"]["l3_episode_n"] = 4
        per["s2_dg0.5_win4"]["l3_episode_n"] = 5   # pooled 9 < 10
        self.assertEqual(collect.recompute(per)["LV1"], "NO_EVENTS")
        per = fixture_per()                        # pooled persist 0.40
        per["s2_dg0.5_l3probe"]["l3_episode_terminal_frac"] = 0.40
        per["s2_dg0.5_win4"]["l3_episode_terminal_frac"] = 0.40
        self.assertEqual(collect.recompute(per)["LV1"], "FALSIFIED")

    def test_lv2_diff_bands(self):
        per = fixture_per()
        per["s2_dg0.5_l3probe"]["l3_terminal_frac"] = 0.14
        per["s2_dg0.5_win4"]["l3_terminal_frac"] = 0.10
        self.assertEqual(collect.recompute(per)["LV2"], "CONFIRMED")
        per["s2_dg0.5_l3probe"]["l3_terminal_frac"] = 0.15
        per["s2_dg0.5_win4"]["l3_terminal_frac"] = 0.08   # diff 0.07
        self.assertEqual(collect.recompute(per)["LV2"], "INCONCLUSIVE")
        per["s2_dg0.5_l3probe"]["l3_terminal_frac"] = 0.20
        per["s2_dg0.5_win4"]["l3_terminal_frac"] = 0.05   # diff 0.15
        self.assertEqual(collect.recompute(per)["LV2"], "FALSIFIED")


class TestCheckAndRender(unittest.TestCase):
    def test_check_passes_on_agreement(self):
        per = fixture_per()
        self.assertEqual(collect.check(per, dict(FIXTURE_VERDICTS)),
                         FIXTURE_VERDICTS)

    def test_check_refuses_on_mismatch(self):
        per = fixture_per()
        bad = dict(FIXTURE_VERDICTS, DW8="FALSIFIED")
        with self.assertRaises(collect.VerdictMismatch):
            collect.check(per, bad)

    def test_render_carries_decisive_numbers(self):
        frag = collect.render(fixture_per(), FIXTURE_VERDICTS)
        for needle in ("0.576", "0.912", "0.87", "124 : 76",
                       "DW8", "DW9", "DW10", "DW11", "LV1", "LV2",
                       "CONFIRMED", "INCONCLUSIVE"):
            self.assertIn(needle, frag)


class TestFileModeDefaultDestination(unittest.TestCase):
    """Tick-64 regression: the documented two-argument file mode
    (`collect.py run.out`) used to fall into the usage branch and
    return 3 — the code documented as 'malformed run output' — so
    file-mode exits were untrustworthy after tick 63's collection
    (dash mode was the working path).  The fix defaults the
    destination to collection.md and gives usage errors their own
    exit code so a usage mistake can never masquerade as a malformed
    run again."""

    def test_two_arg_file_mode_writes_collection_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "run.out")
            with open(src, "w") as fh:
                fh.write(fixture_stdout())
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                rc = collect.main(["collect.py", src])
                self.assertEqual(rc, 0)
                out = os.path.join(tmp, "collection.md")
                self.assertTrue(os.path.exists(out))
                with open(out) as fh:
                    self.assertIn("tick 47 collection", fh.read())
            finally:
                os.chdir(cwd)

    def test_three_arg_file_mode_still_writes_named_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "run.out")
            dst = os.path.join(tmp, "frag.md")
            with open(src, "w") as fh:
                fh.write(fixture_stdout())
            self.assertEqual(
                collect.main(["collect.py", src, dst]), 0)
            self.assertTrue(os.path.exists(dst))

    def test_usage_error_is_distinct_from_malformed(self):
        self.assertEqual(collect.main(["collect.py"]), 64)
        self.assertEqual(
            collect.main(["collect.py", "a", "b", "c"]), 64)


if __name__ == "__main__":
    unittest.main()
