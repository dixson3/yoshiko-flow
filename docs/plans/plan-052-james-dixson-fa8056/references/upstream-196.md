---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #196: retrospective prevention: fields are prose that nothing executes — use bd mol distill to make a remediation shape pourable

- **Number:** 196
- **Title:** retrospective prevention: fields are prose that nothing executes — use bd mol distill to make a remediation shape pourable
- **URL:** 
- **State:** OPEN
- **Labels:** type::feature, priority::high

## Body

This is the strongest available answer to "why do planning sessions keep generating the
same follow-on issues", and it is an instance of #149's own M5 complaint (process rules
that nothing executes) turned on the retrospective schema itself.

MEASURED. plan-retrospective.md entries carry a `prevention` field. Two recent ones are
general, correct, reusable — and inert:

- plan-050 RE-002: "when N successive fixes to one defect are each refuted BY THE SAME
  MECHANISM, stop iterating on the fix and put a check IN FRONT of the failing
  component." Confirmed by execution at RE-008.
- plan-050 RE-003: "for every extractor, assert that a field carried through unchanged
  EQUALS its source; for every filter, assert the selected set is non-empty on a
  known-positive input" — plus the measurement that 5 of 20 script directories have NO
  test file at all.

Nothing consumes either. They are read by whoever happens to open the file.

PROPOSAL. `bd mol distill <epic> <formula-name>` extracts a formula from an ad-hoc epic.
So the FIRST epic that performs a recurring remediation shape can be distilled once, and
thereafter poured or wisped whenever a retrospective's `prevention` names that shape.
Worked example: a "failure-mode pass over a script directory" formula — write the
round-trip / non-empty-selection assertion, run it, record the result — distilled from
the epic that first does it, then poured per directory.

That converts a prose prevention into an artifact with an exit code, which is the exact
transformation #149 asks for.

VERIFIED. `bd mol distill` exists in installed bd 1.1.2. It is referenced once in this
repo (skills/yf-beads-authoring/SKILL.md:252, "optionally distill") and used ZERO times
in any execution path.

RELATED. #145 (yf-retrospective skill) is the consumer side of the same gap; that issue
notes the corpus is still thin. This one is narrower and buildable now: it needs one
distilled formula and a `prevention` field that can name it, not a measurement skill.
