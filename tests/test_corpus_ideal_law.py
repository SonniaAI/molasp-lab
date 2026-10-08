"""Tick-66 pins: the corpus-wide well-founded law (SON-4861).

Live re-derivation for every compiling corpus program with pinned
text (PC1..PC9 via parity.CORPUS; PC10, PC11, PC12-N4, PC12-DOC,
PR13-dead): the BFS presence sets EQUAL the well-founded sets of
the face-table attach grammar (molasp/poset.py), both directions.

Receipt: evidence/2026-10-08-corpus-ideal-law/probe2.out (run at
HEAD 1915589 + this tick's molasp/poset.py; probe.out = v1 receipt
that FALSIFIED the naive DAG-ideal law by measurement — local
or-support is the norm, so the law lives at the well-founded
level where unreachable local options never materialise).

Measured constants pinned below (EMPIRICAL, labeled): the
binomial box law now covers PC12-N4 (70 = C(8,4)), PC12-DOC
(126 = C(9,4)), PR13-dead (210 = C(10,4)) AND PC11's presence
level (126 = C(9,4) — the tick-62 "147" is name-contention above
the poset level: 147 assemblies over 126 presence sets).  Name
contention deltas (assemblies vs presence) pinned per program;
contention is contended-SHARED everywhere, including PC7's
three-way terminal row.  Nothing here is a validated result until
independently reviewed.
"""

import unittest
from math import comb

from molasp.compiler import compile_program
from molasp.parity import CORPUS, producible
from molasp.poset import grammar, presence_sets, well_founded_sets

EXTRAS = {
    "PC10": "p. q :- z. r :- q.",
    "PC11": "p. q. s. q2 :- p. r :- q2, s. r :- q2.",
    "PC12-N4": "p. q. q2 :- p. r :- q2, q.",
    "PC12-DOC": "p. s. q. q2 :- p. r :- q2, q.",
    "PR13-dead": "p. s. q. q2 :- z. r :- q2, q.",
}

PROGRAMS = {k: v[0] for k, v in CORPUS.items()}
PROGRAMS.update(EXTRAS)

# EMPIRICAL (probe2.out, 2026-10-08 tick 66): name-level assemblies
# vs presence-level well-founded sets; equal where no contention.
ASSEMBLIES = {"PC1": 15, "PC2": 45, "PC3": 35, "PC4": 35, "PC5": 70,
              "PC6": 85, "PC7": 100, "PC8": 85, "PC9": 35, "PC10": 70,
              "PC11": 147, "PC12-N4": 70, "PC12-DOC": 126,
              "PR13-dead": 210}
WELL_FOUNDED = {"PC1": 15, "PC2": 35, "PC3": 35, "PC4": 35, "PC5": 70,
                "PC6": 70, "PC7": 70, "PC8": 70, "PC9": 35, "PC10": 70,
                "PC11": 126, "PC12-N4": 70, "PC12-DOC": 126,
                "PR13-dead": 210}

# EMPIRICAL grammar-class histograms (probe2.out): every program
# has or-support sites; "and" is always exactly the S-column rows.
CLASSES = {
    "PC1": {"and": 3, "or-support": 5},
    "PC2": {"and": 3, "contended-shared": 2, "or-support": 7},
    "PC3": {"and": 3, "or-support": 9},
    "PC4": {"and": 3, "or-support": 9},
    "PC5": {"and": 3, "or-support": 13},
    "PC6": {"and": 3, "contended-shared": 2, "or-support": 11},
    "PC7": {"and": 3, "contended-shared": 2, "or-support": 11},
    "PC8": {"and": 3, "contended-shared": 2, "or-support": 11},
    "PC9": {"and": 3, "or-support": 9},
    "PC10": {"and": 3, "or-support": 13},
    "PC11": {"and": 3, "contended-shared": 2, "or-support": 15},
    "PC12-N4": {"and": 3, "or-support": 13},
    "PC12-DOC": {"and": 3, "or-support": 17},
    "PR13-dead": {"and": 3, "or-support": 21},
}


def _derive(name):
    build = compile_program(PROGRAMS[name], name=name)
    seen, _terminals = producible(build)
    presence = presence_sets(seen)
    supports, classes, _occ = grammar(build, seen)
    wf = well_founded_sets(supports)
    hist = {c: sum(1 for v in classes.values() if v == c)
            for c in sorted(set(classes.values()))}
    return build, seen, presence, wf, hist


class CorpusWellFoundedLaw(unittest.TestCase):
    """The law: presence sets == well-founded sets, every program."""

    def test_law_holds_for_every_program(self):
        for name in sorted(PROGRAMS):
            with self.subTest(name=name):
                _build, seen, presence, wf, _hist = _derive(name)
                self.assertEqual(len(seen), ASSEMBLIES[name])
                self.assertEqual(presence, wf)
                self.assertEqual(len(wf), WELL_FOUNDED[name])

    def test_grammar_class_histograms(self):
        for name in sorted(PROGRAMS):
            with self.subTest(name=name):
                _b, _s, _p, _w, hist = _derive(name)
                self.assertEqual(hist, CLASSES[name])


class BinomialBoxLaw(unittest.TestCase):
    """Tick-65's box law extends to PR13-dead and to PC11's
    presence level (all EMPIRICAL anchors from probe2.out)."""

    def test_box_counts(self):
        # n=4..6 box ideals, closed form C(n+4,4)
        self.assertEqual(WELL_FOUNDED["PC12-N4"], comb(8, 4))
        self.assertEqual(WELL_FOUNDED["PC12-DOC"], comb(9, 4))
        self.assertEqual(WELL_FOUNDED["PR13-dead"], comb(10, 4))
        self.assertEqual(WELL_FOUNDED["PC11"], comb(9, 4))

    def test_pr13_dead_box_shape(self):
        build, seen, presence, wf, _hist = _derive("PR13-dead")
        self.assertEqual(len(presence), 210)
        # full 4x6 box occupied somewhere; dead tiles BFS-absent
        placed = {n for asm in seen for p, n in asm if p[1] >= 1}
        self.assertEqual(sorted(set(build["tiles"]) - placed),
                         ["AD6r", "UD5q2"])
        full = frozenset((x, y) for y in range(1, 7) for x in range(4))
        self.assertIn(full, wf)


class NameContention(unittest.TestCase):
    """Contention is name-level only: presence-level grammar stays
    well-founded-clean; deltas pinned (EMPIRICAL)."""

    DELTAS = {"PC2": 10, "PC6": 15, "PC7": 30, "PC8": 15, "PC11": 21}

    def test_deltas(self):
        for name, delta in self.DELTAS.items():
            with self.subTest(name=name):
                self.assertEqual(ASSEMBLIES[name] - WELL_FOUNDED[name],
                                 delta)


# Tick-76 correction (SON-4883): the "PR9 hole of one" claimed in
# the tick-66 log, the counting-law blog post and guide 04 never
# existed.  PR9's refusal-registry text (molasp/parity.py @
# 4b71903, removed by the stage-6 landing ff60932 with the diff
# note "PR9-out (compiles now)") is BYTE-IDENTICAL to the PC11
# pin in EXTRAS above: the shape designed as designs/009's
# PC11, refused at tick 48 and registered as PR9, compiling again
# since stage 6, was probed inside the 14/14 law under its
# candidate name.  The corpus-wide presence law covered every
# compiling shape with a known text from the day it was measured.
PR9_REGISTRY_TEXT = "p. q. s. q2 :- p. r :- q2, s. r :- q2."


class PR9HoleOfOneClosed(unittest.TestCase):
    """The hole of one is closed by identity, not by a new probe."""

    def test_pr9_registry_text_is_the_pc11_pin(self):
        self.assertEqual(PROGRAMS["PC11"], PR9_REGISTRY_TEXT)

    def test_pr9_shape_is_inside_the_law(self):
        _b, seen, presence, wf, _hist = _derive("PC11")
        self.assertEqual(presence, wf)
        self.assertEqual(len(seen), ASSEMBLIES["PC11"])


if __name__ == "__main__":
    unittest.main()
