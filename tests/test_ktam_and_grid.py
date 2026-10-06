"""CI invariants for the designs/003 F4 harness (tick 19,
evidence/2026-10-06-and-ktam-grid/).

Pins the pre-registration contract, not the measured curve (the
full 6000-trajectory grid runs on the cluster queue; its run.out is
evidence):
  1. Protocol constants: Gse=9, Gmc grid, n=500/point, seed base —
     the pre-registered grid cannot drift silently.
  2. Structural decode impossibilities (why K4 runs on the loose
     decode): in build3 an L2 lock reads r-t, so a strict "q" decode
     cannot exist; in build1 an L3 lock reads r-t and no false locks
     exist, so strict non-{pqr, partial} cannot exist; build2's
     inventory has no q/r true tiles at all.
  3. Behavioural, fixed-seed small MC at dG=2 (12 traj/build):
     every strict decode is the expected one or "partial", and no
     reassertion-typed pair (strict partial + loose true-model
     subset) is observed — CI-safe: 36 trajectories, ~0.2 s.
"""
import os
import sys
import unittest

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
EV = os.path.join(HERE, "evidence", "2026-10-06-and-ktam-grid")
SIB = os.path.join(HERE, "evidence", "2026-10-06-body-conjunction-builds")
for p in (EV, SIB):
    if p not in sys.path:
        sys.path.insert(0, p)

import ktam_mc_and as K  # noqa: E402


class TestPreRegistration(unittest.TestCase):
    def test_protocol_constants(self):
        self.assertEqual(K.GSE, 9.0)
        self.assertEqual(K.GMC_GRID, (9.5, 11.0, 13.0, 16.0))
        self.assertEqual(K.N_PER_POINT, 500)
        self.assertEqual(K.BASE_SEED, 20261019)
        self.assertEqual(K.T_READ_MULTIPLIER, 400.0)

    def test_expected_decodes(self):
        got = {a.name: a.expected for a in K.SYSTEMS}
        self.assertEqual(got, {
            "P_AND_corrected": "pqr",
            "P_AND_minus_q": "p",
            "W1_dropped_literal_corrected": "qr",
        })

    def test_structural_lock_reads(self):
        # every lock tile's W face is a value glue; a present lock
        # forces its row's decoded value (this is what makes strict
        # wrong decodes structurally absent and pushes the K4
        # reassertion detector onto the loose decode)
        for api in K.SYSTEMS:
            for name, faces in api.build["tiles"].items():
                if name.startswith("L"):
                    self.assertTrue(
                        faces["W"].endswith(("-t", "-f")),
                        "%s.%s W=%r is not a value glue"
                        % (api.name, name, faces["W"]))

    def test_build2_readers_are_p_only(self):
        # build2's inventory carries no true tiles for q or r: the
        # loose decode can only ever read p (slot-A death is
        # structural, not kinetic)
        readers = K.TRUE_READERS["P_AND_minus_q"]
        self.assertEqual(set(readers), {"p"})
        exposed = set()
        for faces in K.BUILDS["build2"]["tiles"].values():
            exposed.update(faces.values())
        self.assertNotIn("q-t", exposed)
        self.assertNotIn("r-t", exposed)
        self.assertNotIn("and1_r", exposed)


class TestSmallMC(unittest.TestCase):
    """12 fixed-seed trajectories per build at dG=2 (CI-safe)."""

    def test_strict_decodes_are_expected_or_partial(self):
        import math
        T = 400.0 * math.exp(11.0)
        for idx, api in enumerate(K.SYSTEMS):
            for i in range(12):
                strict, loose = K.run_assembly(
                    api, 11.0, 9.0, T, 90210 + idx * 1000 + i).split("|")
                self.assertIn(
                    strict, (api.expected, "partial"),
                    "%s traj %d strict=%r loose=%r"
                    % (api.name, i, strict, loose))
                # NOTE: the reassertion GATE (<= 3/500 at dG in
                # {2,4,7}) is a full-grid statistic evaluated on the
                # queue job's run.out; a 12-traj CI sample sees the
                # ordinary partial-growth channel (strict partial +
                # loose subset ~ 2/12 at dG=2) and must not assert on
                # it.


class TestMeasuredGrid(unittest.TestCase):
    """Pins the F4 measured curve (tick 19 cluster job 10c9aa52…,
    evidence/2026-10-06-and-ktam-grid/run.out — deterministic seeds,
    BASE_SEED 20261019, n=500/point).

    Pins the three standing claims, not the failed thresholds:
      1. consistent-wrong rate: build3/build1 expected_frac ratio
         >= 0.95 at every point;
      2. slot-A death is kinetically free: build2/build1 ratio
         >= 0.95 at every point;
      3. convergence to the tick-15 anchored curve from dG=4 up
         (all builds >= 0.95x tick-15 CORRECT at dG in {4, 7}).
    Also pins the K2/K3 threshold failures AS MEASURED (fractions
    below 0.9 at dG <= 2) so any drift in a re-run is visible.
    """

    MEASURED = {
        ("P_AND_corrected", 0.5): 0.540,
        ("P_AND_corrected", 2.0): 0.790,
        ("P_AND_corrected", 4.0): 0.984,
        ("P_AND_corrected", 7.0): 0.870,
        ("P_AND_minus_q", 0.5): 0.524,
        ("P_AND_minus_q", 2.0): 0.748,
        ("P_AND_minus_q", 4.0): 0.972,
        ("P_AND_minus_q", 7.0): 0.854,
        ("W1_dropped_literal_corrected", 0.5): 0.560,
        ("W1_dropped_literal_corrected", 2.0): 0.810,
        ("W1_dropped_literal_corrected", 4.0): 0.976,
        ("W1_dropped_literal_corrected", 7.0): 0.844,
    }

    @classmethod
    def setUpClass(cls):
        import json
        cls.rows = {}
        with open(os.path.join(EV, "run.out")) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                if "decode" in d:
                    cls.rows[(d["system"], d["dGmc"])] = d

    def test_runout_matches_pinned_table(self):
        for key, frac in self.MEASURED.items():
            self.assertIn(key, self.rows, "missing point %r" % (key,))
            self.assertAlmostEqual(self.rows[key]["expected_frac"], frac,
                                   places=3, msg=str(key))

    def test_consistent_wrong_rate(self):
        for dG in (0.5, 2.0, 4.0, 7.0):
            b1 = self.MEASURED[("P_AND_corrected", dG)]
            b3 = self.MEASURED[("W1_dropped_literal_corrected", dG)]
            self.assertGreaterEqual(
                b3 / b1, 0.95,
                "wrong compile no longer tracks correct at dG=%s" % dG)

    def test_slot_a_death_is_free(self):
        for dG in (0.5, 2.0, 4.0, 7.0):
            b1 = self.MEASURED[("P_AND_corrected", dG)]
            b2 = self.MEASURED[("P_AND_minus_q", dG)]
            self.assertGreaterEqual(
                b2 / b1, 0.95,
                "false rows cost kinetics at dG=%s" % dG)

    def test_convergence_to_tick15_from_dG4(self):
        tick15 = {4.0: 0.990, 7.0: 0.866}
        for dG, ref in tick15.items():
            for name in ("P_AND_corrected", "P_AND_minus_q",
                         "W1_dropped_literal_corrected"):
                self.assertGreaterEqual(
                    self.MEASURED[(name, dG)] / ref, 0.95,
                    "%s fell off the tick-15 curve at dG=%s" % (name, dG))

    def test_failed_thresholds_pinned_as_measured(self):
        # K2/K3 as pre-registered (>= 0.9 at dG <= 4) failed at
        # dG <= 2 — pinned so a drifted re-run is investigated, not
        # silently absorbed
        for name in ("W1_dropped_literal_corrected", "P_AND_minus_q"):
            self.assertLess(self.MEASURED[(name, 0.5)], 0.9)
            self.assertLess(self.MEASURED[(name, 2.0)], 0.9)


if __name__ == "__main__":
    unittest.main()
