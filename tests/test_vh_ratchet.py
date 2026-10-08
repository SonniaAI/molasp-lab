"""Receipt pins for the VH vanishing-hazard ratchet collection
(tick 70, SON-4871; evidence/2026-10-08-vh-ratchet/run.out) and a
CI-time validation of the pure-python matrix exponential.

Receipt: request e6c0c16d18f7b5f907befff192e3d075bb4e6c96e804248928669e15840f6394,
HX-QUEUE-EXIT:0. Verdicts CAL_OK / VH1 CONFIRMED / VH2 CONFIRMED /
VH3 CONFIRMED. Machine verdicts stand as printed; these pins fail
loudly if the receipt changes or a refactor breaks the ratchet
arithmetic the receipt records.
"""
import json
import math
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RECEIPT = os.path.join(
    REPO, "evidence", "2026-10-08-vh-ratchet", "run.out")
EV = os.path.join(REPO, "evidence", "2026-10-08-vh-ratchet")

sys_path_patched = False
try:
    import sys
    if EV not in sys.path:
        sys.path.insert(0, EV)
        sys_path_patched = True
    import ktam_vh_ratchet as vh
finally:
    if sys_path_patched:
        try:
            import sys
            sys.path.remove(EV)
        except ValueError:
            pass


def _load():
    """Parse the receipt envelope: the JSON lines, with the
    VERDICTS prefix stripped (tick-34 lesson: write/parse order)."""
    data = None
    verdicts = None
    with open(RECEIPT) as f:
        for line in f:
            line = line.strip()
            if line.startswith("VERDICTS "):
                verdicts = json.loads(line[len("VERDICTS "):])
            elif line.startswith('{"CAL"'):
                verdicts = verdicts or json.loads(line)
            elif line.startswith('{"n_per_range"'):
                data = json.loads(line)
    assert data is not None and verdicts is not None
    return data, verdicts


class TestVHRatchetReceipt(unittest.TestCase):
    """Pins against the committed collection receipt."""

    @classmethod
    def setUpClass(cls):
        cls.data, cls.verdicts = _load()

    def test_cal_census_exact(self):
        """CAL identity: orig [0,500) census EXACTLY 367:131:2."""
        t = self.data["orig_terminal"]
        self.assertEqual((t["D2T"], t["L2"], t["other"]), (367, 131, 2))

    def test_verdicts_all_confirmed(self):
        self.assertEqual(
            self.verdicts,
            {"CAL": "CAL_OK", "VH1": "CONFIRMED",
             "VH2": "CONFIRMED", "VH3": "CONFIRMED"})

    def test_vh1_ratchet_inequality_holds(self):
        """The pinned gate arithmetic: d^1 >= d^2 and
        max(d^3, d^4) <= 0.10 * d^1, from the receipt's hazards."""
        h = self.data["hazards_D2T"]
        d1, d2 = float(h["1"]), float(h["2"])
        late = max(float(h["3"]), float(h["4"]))
        self.assertGreaterEqual(d1, d2)
        self.assertLessEqual(late, 0.10 * d1)
        # the collapse is not marginal: ~76x by phase 2
        self.assertGreater(d1 / d2, 50.0)

    def test_vh2_prediction_in_band(self):
        self.assertLessEqual(self.data["deviations"]["VH2"], 0.05)
        self.assertAlmostEqual(
            self.data["share_pred"], 0.7414, places=3)

    def test_vh3_fresh_in_band(self):
        self.assertLessEqual(self.data["deviations"]["VH3"], 0.05)

    def test_homo_pi_reproduces_dw9(self):
        """DW9 fit_half pi_pair reproduced bit-exact (quote
        precision per the tick-42 rule)."""
        self.assertAlmostEqual(
            self.data["homo_pi_pair_fitrange"], 0.7123954, places=6)

    def test_snapshots_reproduce_dw10(self):
        """DW10's 0.503/0.646/0.704 snapshot sweep reproduced."""
        sn = self.data["snapshots"]
        self.assertAlmostEqual(sn["0.25"]["share"], 0.503, places=2)
        self.assertAlmostEqual(sn["0.5"]["share"], 0.646, places=2)
        self.assertAlmostEqual(sn["0.75"]["share"], 0.704, places=2)

    def test_terminal_vector_is_a_distribution(self):
        vf = self.data["vf"]
        self.assertAlmostEqual(sum(vf), 1.0, places=6)
        self.assertTrue(all(x >= 0 for x in vf))
        # site essentially never empty at read time
        self.assertLess(vf[0], 0.001)

    def test_ratchet_is_d2t_specific(self):
        """L2 keeps detaching: no comparable collapse (the
        descriptive asymmetry that makes it a ratchet)."""
        hl = self.data["hazards_L2"]
        self.assertGreater(float(hl["4"]), 0.0)
        self.assertLess(float(hl["4"]), float(hl["1"]))


class TestVHExpm(unittest.TestCase):
    """The pure-python expm stays validated in CI (2-state closed
    form, absorbing column) — the same battery run pre-registration."""

    def test_two_state_closed_form(self):
        for (a, b, dt) in [(0.3, 0.7, 2.0),
                           (1e-7, 2.4e-7, 2.14e7),
                           (1e-2, 3e-3, 5.0)]:
            Q = [[-a, a], [b, -b]]
            E = vh.expm(Q, dt)
            want = (b + a * math.exp(-(a + b) * dt)) / (a + b)
            self.assertAlmostEqual(
                E[0][0], want, delta=1e-9 * max(1.0, abs(want)))
            self.assertAlmostEqual(E[0][0] + E[0][1], 1.0, places=10)

    def test_absorbing_state_stays_absorbed(self):
        lam = 6.6e-7
        p = {"D2T": 0.26, "L2": 0.24, "O": 0.5}
        Q = vh.build_Q(lam, p, 0.0, 1.37e-7, 1.0e-2)
        E = vh.expm(Q, 5.35e6)
        self.assertLess(E[1][0], 1e-15)

    def test_series_sums_to_one(self):
        """Regression for the registration-day bug: the uniformi-
        zation series must not double the identity component."""
        Q = [[-0.3, 0.3], [0.7, -0.7]]
        E = vh.expm(Q, 2.0)
        for i in range(2):
            self.assertAlmostEqual(sum(E[i]), 1.0, places=10)


if __name__ == "__main__":
    unittest.main()
