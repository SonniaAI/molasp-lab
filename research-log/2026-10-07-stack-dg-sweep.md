# 2026-10-07 — Stack-channel dG sweep (tick 34): redundancy starves

**Question (pre-registered at 7000301 before the job):** the
recombination study (same day) showed both row-scope survivors are
redundant cooperative stacks — the read-block rides the vertical
`Vp@(3,2)+DBr@(3,3)` lock stack (141/141) and the repair rides a
2-of-3 relay fan `N→DAr + S→V0p + W→S2` (153/155 at b=3, lb_any
0.0129). Redundancy is why the single-bond knob failed at dG 0.5.
Does 2-of-3 redundancy starve with dG the way the solo family
channel did (R4: 0.314 → 0.118 → 0.000)?

**Protocol:** BUILD1 row scope, {plain, Vp-missing} × dG
{0.5, 2.0, 4.0} (Gse = 9.5 − dG), n=500/arm, T_read = 400·exp(Gmc),
seed base 120261107 stride 2e7 (disjoint from all prior blocks).
Job hxq-1751ba31889ec345 (paperclip-test, 1 core / 1 GiB / 3600 s),
exit 0, ~70 s on spark-4a06, image-verified; archive blob
1193bab663cca643cfc31b9c5b980b213f5409ae68e6ba63ef9818e46bf2541e =
sha256 of the tarball built from committed HEAD 7000301
(pre-registration precedes the job). Receipt:
`stack_dg.out` + `queue-receipt.json`.

## Verdicts (machine, in the receipt's final line)

- **S1 CONFIRMED — the vertical stack starves.** Row read-block
  0.14 → 0.006 → 0.000, monotone; and at every dG with events the
  blocked cohort IS the vertical stack (co-occurrence 1.0 at both
  dG 0.5 and 2.0). Redundancy does not survive thermodynamics: the
  stack closes by dG 4 exactly like the solo family squatter did.
- **S2 CONFIRMED — the relay repair starves.** Stable D2T fill
  0.128 → 0.04 → 0.000, monotone.
- **S3 CONFIRMED — the redundant fan is the last channel
  standing.** Among surviving stable holds, b≥3 fraction 0.9844
  (dG 0.5) and 0.9 (dG 2.0); mean relay contacts ≈ 3 throughout;
  lb_any stays ≤ 0.1. When the repair channel exists at all, it is
  the redundant stack.
- **S4 CALIBRATED.** dG 0.5 deviations 0.001 (blocked, ref 0.141)
  and 0.027 (fill, ref 0.155) vs recombination.out — no protocol
  drift across studies.

## Reading

- At dG 0.5 redundancy defeated the knob (single-bond
  qualification killed every bond it aimed at; both channels
  re-routed at reduced amplitude). With dG the same channels die
  like everything else: cooperative stacks pay their extra bonds in
  concentration, and by dG 4 nothing is left. **Redundancy is why
  the knob failed; dG is why redundancy loses.**
- Practically: the read window story is now complete and two-sided
  — a consumer reading at high dG has neither squatters nor
  recombined channels (everything starves); a consumer at low dG
  has both, in stack form, and the d4 census names them
  (`lock_stack_channels`, `vacancy_relay_stacks`, tick 34).
- The d4 stack-class report is therefore the right emit-time
  artifact: it enumerates the cooperative classes the one-site
  census cannot see, with the measured context (0.141 block /
  0.155 fill at dG 0.5; both → 0 by dG 4) quoted so severity is
  read against numbers.

Open follow-ups: none on this question — the glue-scope study line
is fully closed through its kinetic arm. Next avenues live in
designs/004 (glue-CLASS boundary kinetic test) and the
founder-gated collaborator/venue shortlist.
