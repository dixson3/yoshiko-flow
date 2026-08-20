---
type: Review
okf_spec: OKF-PLAN
pass: 3
---
# Red-team pass 3 — plan-049-james-dixson-725bc0

## Verdict: REVISE

## Part A — pass-2 resolutions

**12 of 14 landed.** D2 **partial** (SC12 fixed; Issue 3.4, R4 and `context.md` still say "nine", and
D-2a carries no annotation). D7 landed structurally but SC39's severity literal is wrong (M1).
All others verified against the artifact.

## Part B — mechanical verification

7 epics, **42 issues**, **58 edges**, 6 gates, **40 criteria**, `unparsed: []`; zero cycles, zero
dangling, no duplicate ids, `0.1` the only unnamed issue. `okf.py check` OK; `audit` all-pass;
`markdown_lint` clean on all 21 files; `doc_lint` PASS.

**Premises reproduced:** corpus `unparsed[]` **exactly 81** across **24 of 49**; the 89 declarations
reproduce exactly (006=8, 007=12, 009=15, 010=33, 012=21) with ~101 of 120 referents resolving, so
**SC5's floor of 60 is comfortably derivable**. Every code anchor is line-exact.

> **SC23's floor of 73 is exact, simulated end-to-end.** plan-015: the de-bold takes it **4 → 1**
> (cascade precisely −3). plan-008: relocation takes it **8 → 3** — 7 removed, exactly 2 new.
> 81 − 7 + 2 − 3 = **73**. *"The first target in this lineage that survives independent reproduction."*

## Strengths

- The 73 derivation reproduces to the entry, including plan-008's counter-intuitive +2.
- **Gate reachability and frontloading clean**, re-derived by ancestor set; both gate wrappers are
  ancestors of everything the gates block, so the scripts exist before evaluation.
- **The instrument-first discipline is real** — SC2 and SC38 both require the *weaker* implementation
  to be shown passing.
- **Every recommendation in all six findings is scheduled or explicitly declined** — checked one by
  one across EXP-001..006. Nothing silently deferred at the findings layer.
- The anti-vacuity clauses on SC7, SC29, SC37, SC11 each name the cheap fake that would discharge them.

## Concerns

| # | Sev | Concern |
| :-- | :-- | :-- |
| H1 | **high** | **Issue 3.2's predicate fires on 49 of 49 Start Gates — including this plan's own and the canonical template** (`plan_template.py:134`, `SKILL.md:451` are `Type` + `Approvers`, no Condition, no Test). Measured **80 of 137 corpus gates fail it**. Issue 4.2 binds the linter fail-closed at intake, so **plan-050 could not pass its own intake.** Verbatim the failure `plan-relations.toml:11` warns of and that D-3 rescoped #135 to avoid. **SC10 already states the safe predicate** (all three absent), which fires on plan-008's stub and nothing else |
| H2 | **high** | **D2's fix landed in SC12 and nowhere else** — Issue 3.4, R4 and `context.md` still say "nine", while `context.md` names plan-015's de-bold as one of the two documents the plan **writes**. An executor produces a record that fails its own criterion. Third consecutive cycle of sibling-file drift |
| H3 | **high** | **The SPEC is authored one layer short of the implementation.** Issue 0.4 and D-4 say **three**-layer; Issue 1.1 implements **four** with L4 gate content; SC11 is written entirely on L4; and **SC32 — discharged by 0.4 — requires the text to name all four.** The SPEC would omit the only layer that observes the corpus write |
| M1 | med | **SC13 and SC39 assert incompatible severities.** Measured: R1b is `E` at review, `R` at executing/complete — **never `W`**. Only the bypass-both-directions reading yields SC39's `W`, under which SC13's "stay `R`" is wrong |
| M2 | med | **The Reconcile Gate is green today with zero beads** — the instrument changed correctly but the vacuity did not close. A plan-id typo in the pour yields a permanently green gate |
| L1–L9 | low | `log.md` carries only v1 counts; Motivation says "24 of 48" vs 49; SC27's grep is unscoped; the Instructions mis-state exit 2 (INCONCLUSIVE leaves a gate **unresolved**, per `SKILL.md:1140`); pass-1/2 review files lack `Strengths`/`Missing`; 4.7 says 30/30 vs measured 30/31; SC25 lacks the documented no-op-rebuild caveat; 0.1 and 4.3 name no target file; 1.1 imports a skill-layer symbol into `_shared/` |

## Missing

**A false-positive control on the two new document checks.** Epic 1 has mutant D; Epic 3 has none —
neither 3.1 nor 3.2 must demonstrate it does *not* fire on a conformant document, and **H1 is exactly
what that omission lets through.** Also: Issue 3.1's blast radius is never measured despite the plan
citing "plan-047's 90-finding exploit" — D-7 says re-measure, never cite.

## Gate Assessment

Clean, re-derived independently. All three capability gates draw evidence strictly from ancestors
outside their `Blocks` set; both wrappers precede everything they gate; both human gates correctly
red. **Residual: M2 and the exit-2 wording (L4).** No frontloading misses.

## Upstream Assessment

**Sound and consistent across all three surfaces** — extractor, table, and triage agree on all eight
rows with full titles. Both `partial` rows are specific about IN/OUT and route the OUT half to a
named successor or a recording issue. **Nothing silently deferred upstream.**

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 | high | Issue 3.2's predicate aligned to SC10's **all-three-absent** form, with an explicit note that `Type` + `Approvers` (the canonical Start Gate) must NOT fire; **SC10 extended with the false-positive control** asserting it does not fire on the template | `main-session` | resolved |
| H2 | high | Issue 3.4, R4 and `context.md` corrected to **eight**, each naming plan-015 as moved in-scope; D-2a annotated with the move | `main-session` | resolved |
| H3 | high | Issue 0.4 and D-4 restated as the **four**-layer form with L4 = gate content, keeping "L3 primary" as the mutant-A claim | `main-session` | resolved |
| M1 | med | Issue 0.2 states `promote = false` **bypasses the mapping in both directions**; SC13 changed to "stay at their declared `W`" | `main-session` | resolved |
| M2 | med | The Reconcile Gate's Test gains a **population assertion** — the closed-count must be zero **and** the plan's bead count must be > 0 | `main-session` | resolved |
| Missing | med | **Issue 3.2b added**: a false-positive control for both new document checks, asserting neither fires on a conformant document; and Issue 3.1 must **measure** its blast radius rather than cite plan-047's figure. SC41 covers both | `main-session` | resolved |
| L1–L9 | low | log counts derived; "24 of 49"; SC27's grep scoped to the preamble; the exit-2 wording corrected to "leaves the gate UNRESOLVED"; 4.7's rate corrected to 30/31; SC25 carries the no-op-rebuild caveat; 0.1 and 4.3 name their targets; 1.1's layering note added | `main-session` | resolved |
