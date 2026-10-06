# 2026-10-06 — Value-agnostic locking: the cage attempt (tick 11)

**Question.** Catalogue entry (b) of designs/001 claims that where
value-agnostic locks are unavoidable, requiring two independent bonds
gives error ~e^{−2·dG}. Ticks 4–10 never built that variant: v2.1 is
the one-coincidence blind lock, v3 is the fully typed one. This tick
attempts the realization.

**Construction (maximally-blind cage).** Take v3's geometry and strip
every value-independent support bond, keeping all lock glues blind:
L1.W=r1 bonds D1T.E and D1F.E alike; L2.W=r2 bonds D2F.E and D2T.E
alike; L1.S=cap1 and D2F.S=cap3 bond nothing (seed bond and row
coupling removed). Every closure in the cage now rides on sub-tau
residents: D2F(b=1)∧L1(b=1) overlap, then L2 arrives at b=2 and makes
the cage τ-stable.

**Measured (aTAM, exhaustive, `run.out`).** The concession is total.
τ=2 BFS from the seed reaches exactly ONE terminal, {seed, S1, S2,
D1T}, decode `partial`: the CORRECT terminal {a} is unreachable,
because the remaining closures are mutually dependent b=1 transients.
D1F/D2T attach 0 times. Contrast v3 (10 producible, 1 terminal {a},
wrong tiles 0/10) — the blind cage loses aTAM-producible growth
outright; correct growth survives only kinetically.

**Lemma.** A lock whose glues are value-blind bonds the wrong value
with the same strength as the correct one, so its bond count cannot
depend on the value. Either it keeps some value-independent support
bond — then some wrong-value closure is a single coincidence
(~e^{−dG}; v2.1 measured 355/2000, channels .058/.174) — or every
support bond is stripped and correct growth itself goes cooperative.

**Ratio arithmetic (prediction).** Correct completion ~e^{−2·dG}
(D2F∧L1 overlap + L2 arrival over D1T's τ-residency); wrong completion
~e^{−3·dG} (adds D1F's b=1 window). Wrong/correct ~e^{−dG} — the SAME
error/throughput ratio as v2.1. Value-agnostic locking preserves the
ratio; value-typing (v3) is the move that shifts it. This is the
kinetic mirror of the foundedness argument: geometry moves error
ratios, kinetics cannot.

**Catalogue correction.** Entry (b) amended in designs/001: e^{−2·dG}
is a rate statement paid equally by correct growth, not a free
suppression. Falsifier (queued MC): wrong completions at or above
e^{−2·dG} with correct completion within e^{−dG} of v3's rate refutes
the lemma.

**Status.** Design + structural result; unreviewed notebook promotion
per lab convention. No C-claim advanced; C2 unchanged. CI pins
blindness symmetry, stripped bonds, and the single-partial-terminal
concession (`tests/test_tiles_v3p.py`).
