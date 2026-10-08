# 2026-10-08 — n≥6 build survey: the closure scales to n=9 (tick 64)

Card: SON-4856 (hourly loop, tick 64). Receipt verbatim:
`evidence/2026-10-08-n6-build-survey/probe.out` (probe at HEAD
7714eac, records JSON-lines, timings included). Probe docstring
carried the pre-registered predictions before anything ran;
committed together with this record in the same tick.

## 1. Question

Tick 62 (designs/010 §10.4) removed the SP-table cap and measured
full locks at n=5 — "first n=5 build with full locks, no second
hidden cap" — but that claim was measured at n=5 only. Does it
survive n=6..9?

## 2. Family

PC12-DOC extended with decorative facts between s and q (each adds
one row, nothing reads them; the AND-over-derived geometry keeps
q2 at i-1 / q at i-2, and the unit via read of p grows with n):

| n | program | via distance (p→q2) |
|---|---|---|
| 5 | `p. s. q. q2 :- p. r :- q2, q.` | 3 |
| 6 | `p. s. t. q. q2 :- p. r :- q2, q.` | 4 |
| 7 | `p. s. t. u. q. q2 :- p. r :- q2, q.` | 5 |
| 8 | `p. s. t. u. v. q. q2 :- p. r :- q2, q.` | 6 |
| 9 | `p. s. t. u. v. w. q. q2 :- p. r :- q2, q.` | 7 |

## 3. Predictions (pre-registered, frozen in probe docstring)

P1 rows == n, tiles == 4n · P2 assemblies strictly monotone ·
P3 terminals == 1 · P4 full_locks TRUE (class closure leaves no
table edge) · P5 decode == full least model · P6 no refusal as the
via distance grows (a loud refusal would be a finding: an
ordering-based second cap; do not widen the compiler to avoid it).
Falsifier: any n≥6 with full_locks FALSE, a prefix decode, or an
assembly count equal to the n−1 build's.

## 4. Measured (all six predictions hold; falsifier not fired)

| n | rows | tiles | assemblies | terminals | full locks | decode | s |
|---|---|---|---|---|---|---|---|
| 5 | 5 | 20 | 126 | 1 | TRUE | full model | 0.040 |
| 6 | 6 | 24 | 210 | 1 | TRUE | full model | 0.069 |
| 7 | 7 | 28 | 330 | 1 | TRUE | full model | 0.114 |
| 8 | 8 | 32 | 495 | 1 | TRUE | full model | 0.179 |
| 9 | 9 | 36 | 715 | 1 | TRUE | full model | 0.271 |

The n=5 row re-measured (5, 20, 126, 1) — the tick-62 anchor
reproduced before any new row was trusted (probe self-calibration).

**Empirical closed form (observation, not a theorem):** assemblies
= C(n+4, 4) exactly at every measured point — n=4: 70 = C(8,4)
(ticks 55/62), n=5: 126, n=6: 210, n=7: 330, n=8: 495, n=9: 715.
Six-for-six fit. Growth is quartic (~n⁴/24), polynomial, not
exponential — the decorative-fact family is cheap to enumerate
(0.27 s at n=9, pure Python). Under the pre-closure SP-table cap
the count was stuck at 70 for every n≥5 (the tick-62
"census-generality" divergence class); post-closure the family
tracks the binomial without a kink.

## 5. Consequences

- The tick-62 "no second hidden cap" claim now has measured support
  through n=9 (decorative-fact family, one geometry; still not a
  theorem — designs/010 §10.7 records the widened scope).
- The C(n+4,4) fit is a falsifiable target: prove it from the BFS
  enumerator's structure (why 4-combinations of n+4?) or find the
  n where it breaks. Open, next-tick candidate.
- Offchannel kinetic receipt beyond row 4 (post-closure) and the
  related-work sweep remain the standing backlog.

## 6. Pins

`tests/test_n6_build_survey.py`: shapes/locks/decode at n=5..9
(measured, subTest per n) + the binomial identity as arithmetic on
measured values (labeled EMPIRICAL in the docstring; a future build
change that breaks the fit fails loudly).

Nothing here is a validated result until independently reviewed.
