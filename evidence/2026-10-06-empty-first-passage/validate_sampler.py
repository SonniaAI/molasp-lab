"""Independent Gillespie sampler of the same window CTMC.

Cross-checks the linear solver: passage-class frequencies from direct
simulation of the enumerated chain must agree with solve()'s numbers
within binomial noise. Not part of CI (stochastic); evidence only.
"""
import math
import random
import sys

import ctmc_first_passage as C

N = 4000
SEED = 20261007


def sample(dG, seed):
    Gmc = C.GSE + dG
    rng = random.Random(seed)
    counts = {"a": 0, "empty": 0, "ap": 0, "p": 0}
    exc = 0
    for _ in range(N):
        s = tuple()
        while True:
            cls = C.locked_class(dict(s))
            if cls is not None:
                counts[cls] += 1
                break
            ev = list(C.transitions(s, Gmc, "full"))
            tot = sum(r for r, _ in ev)
            t = rng.expovariate(tot)
            r = rng.random() * tot
            acc = 0.0
            for rate, nxt in ev:
                acc += rate
                if acc >= r:
                    if dict(nxt).get((1, 1)) == "D1F" and dict(s).get((1, 1)) is None:
                        exc += 1
                    s = nxt
                    break
    return counts, exc / N


for dG in (0.5, 2.0, 4.0):
    counts, exc = sample(dG, SEED + int(dG * 10))
    n = sum(counts.values())
    probs, exc_exact, ns, _ = C.point(dG, reward=C.d1f_excursion_reward)
    print({"dG": dG, "n": n,
           "sample": {k: round(v / n, 4) for k, v in counts.items()},
           "exact": {k: round(v, 4) for k, v in probs.items()},
           "E_excursions_sample": round(exc, 3),
           "E_excursions_exact": round(exc_exact, 3)})
