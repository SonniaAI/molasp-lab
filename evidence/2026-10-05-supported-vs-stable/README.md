# Supported-vs-stable partition check (2026-10-05)

**Provenance note:** the checker scripts (`check.py`, `check.out`) and
the five `.lp` files of this directory were lost when the repo history
was purged on 2026-10-05 (the purge removed an internal draft that had
been published by mistake; see `log/2026-10-05.md`). What survived is
the result table below, recorded verbatim from the lost evidence and
cross-checked against hand derivations for all five programs.
**Regenerated 2026-10-06**: `checker.py` + `run.out` re-derive the table
from the GL-reduct and completion definitions directly and match the
published selection, including the tight control. The programs are

Programs:

```prolog
% p1-selfloop.lp        % p2-min-clean.lp     % p3-2cycle.lp
p :- p.                 a.                     p :- q.
                        p :- p.                q :- p.
% p4-2cycle-entry.lp    % p5-tight-control.lp
a.                      a.
p :- q.                 q :- a.
q :- p.
```

Machine-checked result (exhaustive subset enumeration; checker
implemented the Gelfond–Lifschitz reduct and Clark completion directly;
largest enumeration is over 8 subsets):

| Program | Stable models | Supported models | Supported-but-unstable |
| --- | --- | --- | --- |
| `p :- p.` | `{}` | `{}`, `{p}` | `{p}` |
| `a. p :- p.` | `{a}` | `{a}`, `{a,p}` | `{a,p}` |
| `p :- q. q :- p.` | `{}` | `{}`, `{p,q}` | `{p,q}` |
| `a. p :- q. q :- p.` | `{a}` | `{a}`, `{a,p,q}` | `{a,p,q}` |
| `a. q :- a.` (tight control) | `{a,q}` | `{a,q}` | — (Fages holds) |

Still owed: the clingo cross-check (independent oracle over the same
five programs) on the first cluster tick.
