# The hole of one never existed: PR9 is PC11, byte for byte

Date: 2026-10-08, tick 76 (SON-4883, run 813f39ca; started
~22:31Z wake) · compiler pristine (docs + one test file; no
production code touched).

## What this note closes

Tick 66's corpus-ideal-law note — and the tick-75 blog post and
guide 04 that repeated it — claimed the corpus-wide presence law
carries "a hole of exactly one": PR9 compiles, but its text was
never pinned in the tests, so the law was never run on it.
Tick 75's "what we do next" named pinning that text as the
follow-up. This tick went to do exactly that and measured
something better: **PR9's registry text is byte-identical to the
PC11 pin.** There was nothing to probe.

## Method

- Extracted the PR9 entry verbatim from the pre-stage-6 refusal
  registry: `git show 4b71903:molasp/parity.py` →
  `p. q. s. q2 :- p. r :- q2, s. r :- q2.`
- Decoded both string literals and compared with python `==`
  against the EXTRAS pin in tests/test_corpus_ideal_law.py:
  `"PC11": "p. q. s. q2 :- p. r :- q2, s. r :- q2."`
  → True. No whitespace, ordering, or spelling difference.
- Confirmed the current REFUSALS dict carries no PR9 (removed by
  stage 6) and CORPUS never had one; the only pinned home of the
  text is the PC11 EXTRAS entry.

## Name lineage (why the ghost happened)

- designs/009 designed the shape as PC11, the via-generalization
  candidate.
- Tick 48 (77879c4): the shape was refused; the registry entry
  PR9 pinned its text with reason "AND lo-literal at row 3, not
  the row-1 via".
- Tick 60 (ff60932): stage 6 landed; the registry diff read
  "PR9-out (compiles now — moved to the stage-6 pins)".
- Tick 66: the corpus-ideal-law probe pinned the now-compiling
  shape under its candidate name PC11 — and the same tick's log
  treated "PR9" as a separate unpinned program. Two names, one
  program, one ghost hole.

## Consequence

The corpus-wide law (BFS presence sets == well-founded sets of
the face-table attach grammar, both directions) covered every
compiling shape with a known text on the day it was measured:
14/14, no hole, no 15th program. The tick-66 note carries an
in-place §3/§6 correction plus a §7 record; the blog post and
guide 04 carry dated errata.

## Pin

tests/test_corpus_ideal_law.py gains PR9_REGISTRY_TEXT (the
4b71903 registry text as a constant) and PR9HoleOfOneClosed:
one assertion that PROGRAMS["PC11"] == PR9_REGISTRY_TEXT, one
restating that the PC11 derivation satisfies the law. Any future
divergence between the registry text and the pin — or a
resurrection of the hole claim as code — fails a test loudly.

Nothing here is a validated result until independently reviewed.
