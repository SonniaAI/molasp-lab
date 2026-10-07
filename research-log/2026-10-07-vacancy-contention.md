# 2026-10-07 — Vacancy contention-set pricing (tick 42, SON-4810)

Question (designs/007 design consequence): can the emit-time census
price a lock-reinforcement knob against the FULL contention set of
an affected vacancy — fill, via-site lock squat, reader stack —
instead of one hazard class at a time?

Method: static deterministic enumeration, no cluster job (tick-37
standing rule).  New layer `molasp.offchannel.vacancy_contention`:
species-death backgrounds (species removed, its canonical sites
empty), contenders admitted on any family face, per-knob own bond,
or an enabling stack; classes fill / via_squatter (w_read) /
lock_squatter / stack_partner (load-bearing pair b_with>=2 >
b_without); `stable_under` per knob from own bond or enabled stack.
`matched_s2` promoted verbatim from the evidence scripts into the
census module.  Gates C1–C5 registered before the census ran.

Result: C1/C2/C3/C5 CONFIRMED; C4 CONFIRMED after a disclosed
registration-defect correction (v1 falsified receipt kept).

- BUILD1 Vp@2,2 family-stable {D2T, L2} (measured 454/36) → s2
  stable {D1T, D2T, DBr, L2, V0p} (measured fill share 454→203,
  0.908→0.406).  The pricing story: reinforcement wins by MINTING
  frozen contenders (first-come), not by beating the fill.
- DBr priced as stack_partner: own family bond 1, enables L3@3,2
  (s2 b_with 2 > b_without 0) — the tick-39 "zero solo bond"
  falsification is now census arithmetic.
- Corpus: minting is constructional — every BUILD1/2/3 vacancy
  grows its stable set under s2; lock/spine vacancies 0 → 3–6.

Honest boundaries: single-species backgrounds only (L3@(2,2), the
54/500 occupant, needs a second event — recorded, not asserted);
bond_fns priced are family and s2 (future knobs plug in the same
way).

Artifacts: evidence/2026-10-07-vacancy-contention/ (census script,
.out, v1 falsified receipt); tests/test_vacancy_contention.py (11
pins incl. cross-receipt consistency with vacancy_bg.out); d4 auto-
attach + warning line; suite 338 OK / 1 skip under the exact CI
command.

Tooling notes: one test-side precision bug caught by the suite
(MEASURED_CONTEXT quotes 0.214, receipt stores 0.214285… — compare
at quote precision, the tick-25 serialized-receipt lesson); one
registration-side threshold bug caught by the census's own first
run and corrected with the receipt kept — both are the
measure-then-claim discipline working, not noise.
