---
type: Plan
okf_spec: OKF-PLAN
id: plan-051-james-dixson-2f499f
author: james-dixson
created: '2026-08-21'
status: drafting
---
# Plan: Land the descoped plan-050 work: the red-team sandbox-spike rule (#182), sub-agent dispatch for review (#184), and M9 remediation-edge attribution (#149) — each from plan-050's measured evidence

**ID:** plan-051-james-dixson-2f499f
**Author:** james-dixson
**Created:** 2026-08-21
**Status:** drafting

## Objective

Ship the **review contract** into the yf-plan skill, where it currently does not exist, and correct
one upstream issue whose premise this repo has already measured false.

Three pieces, in descending order of evidence:

1. **#184 — dispatch the red-team as a sub-agent.** `SKILL.md:315` (§2 INVESTIGATE) says **spawn**;
   `SKILL.md:489` (§3 REVIEW) says **perform**. Following §3 literally produces a main-session
   self-review — the drafter reviewing its own draft.
2. **#182 — authorize the sandbox spike.** `red-team.md:63` says only *"Read-only — never writes
   files"*. It never forbade a spike; the prohibition is a reasonable reading of silence. The defect
   is **under-specification**, which is why the fix is a clarification rather than a reversal.
3. **#149 — correct the record.** Comment only. exp-004 measured the issue's premise false and
   plan-050 never posted the correction.

**The policy is already ratified — it just does not ship.** `AGENTS.md` carries both halves and
this session exercised them hard. What is missing is the SPEC requirement and the skill text, so
every other consumer still gets the self-review.

Explicitly NOT in scope: M9 itself (#149's substance), the payload-fidelity group (#188/#190), the
corpus-wide `Verification:` sweep (#165 beyond this plan's own two REQs), and #145.

## Motivation

**A rule that lives in one repo's `AGENTS.md` is not a rule the skill has.** Every yf-plan consumer
outside this repository still runs `SKILL.md` §3 as written, which never dispatches. The drafter
reviews its own draft, and a concern the drafter cannot see is a concern the review cannot raise.

The evidence is first-party and unusually direct — plan-050 is the experiment. Its concerns per
review pass ran **5 → 4 → 11 → 17 → 14**, and the discontinuity lands exactly at pass 3, the first
`Agent`-dispatched pass. Passes 1-2 were main-session self-review and advanced the plan to
`ready-for-approval`; three independent passes then returned REVISE.

The spike half has its own instance: plan-050's pass-11 refuted the plan's "single call site" claim
about `plan_extract.py` **by building it**, and execution later confirmed both sites were corrupt.
Reading four passes had not found it.

**And the counter-evidence is recorded here rather than omitted.** Eleven independent red-team
passes found **none** of the three defects that *running a control* found during plan-050's
execution. Independent review is a large improvement over self-review; it is not the strongest lever
measured. This plan ships the improvement it has evidence for and does not overclaim it.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|
| [#184](https://github.com/dixson3/yoshiko-flow/issues/184) | red-team is never dispatched as a sub-agent — the drafter reviews its own draft | include | **D-2.** The §2-vs-§3 asymmetry is verbatim: `SKILL.md:315` says **spawn**, `:489` says **perform**. Measured RED: `Agent` appears **0** times across all 7 `agents/*.md`. Needs a **NEW** `REQ-AGENT-*` — none of 040-048 says who RUNS the review | |
| [#182](https://github.com/dixson3/yoshiko-flow/issues/182) | the read-only rule forbids the sandbox spike that catches specification defects | include | **D-1.** exp-006 **narrows** this issue: `red-team.md:63` says only "never writes files" — it never forbade a spike. Under-specification, not a wrong rule. One line, **plus `spec/agents.md:73`**, whose Verification clause pins the exact string | |
| [#149](https://github.com/dixson3/yoshiko-flow/issues/149) | M5/M9: process rules that nothing executes, and remediation edges that exist only in prose | partial | **D-3.** **IN:** a comment correcting the refuted premise — **26** `discovered-from` edges, **0** attributed on either endpoint, so the relationship exists and only attribution is missing; plus C40 and the no-seam finding. **OUT:** M9 itself | |
| [#165](https://github.com/dixson3/yoshiko-flow/issues/165) | SPEC `Verification:` lines are prose shaped like commands | partial | **D-4.** **IN:** this plan's own new/amended `Verification:` lines must be **executable**. **OUT:** the corpus-wide sweep. Folded in because otherwise this plan ships two requirements nothing executes — the exact M5 defect it exists to fix | |
| [#173](https://github.com/dixson3/yoshiko-flow/issues/173) | criteria and dispositions are never checked against the engine that enforces them | partial | #182's and #184's REQs are checked against the surface that enforces them, as worked instances. The general cross-check stays open | |
| [#174](https://github.com/dixson3/yoshiko-flow/issues/174) | a review-phase validation pass — falsify every criterion | partial | #182 closes a named sub-case: the spike is the technique that catches what reading cannot. The general falsification pass stays open | |
| [#150](https://github.com/dixson3/yoshiko-flow/issues/150) | research 004: process-defect mining across 83 plan bundles | partial | **IN:** two more ranked classes delivered as worked instances. **OUT:** M9, the M11 probe mechanism, the remaining classes | |
| [#177](https://github.com/dixson3/yoshiko-flow/issues/177) | no check that a numeric target is derivable from the plan's own scope rules | exclude | Closed out by plan-050 — the refutation comment was posted and D-6 dropped it on evidence. No action here | |
| [#188](https://github.com/dixson3/yoshiko-flow/issues/188) | test suites assert output STRUCTURE and never payload FIDELITY | deferred | plan-050's headline finding is direct evidence, but payload fidelity is a second independent axis, scoped OUT | |
| [#190](https://github.com/dixson3/yoshiko-flow/issues/190) | require plans to ship tests at >= 80% coverage of code they write | deferred | Same axis as #188 — deferred with it | |
| [#145](https://github.com/dixson3/yoshiko-flow/issues/145) | New skill: yf-retrospective — measure escape rate | deferred | Own plan. The emit side accumulates; a consumer built now reads a thin corpus | |

## Investigation Findings

Four experiments returned. **Two refuted parts of the approach hypothesis and one refuted a decision
this plan was about to inherit.** Full records in `findings/`.

| # | Question | Outcome |
| :-- | :-- | :-- |
| [EXP-001](findings/exp-001-dispatch-verification.md) | What can #184's `Verification:` line assert with an exit code? | **The behavioral claim has none, and cannot.** But `spec/agents.md` has **0 of 26** exit-code-decidable clauses today, and #184 has a real substrate the plan can use |
| [EXP-002](findings/exp-002-182-blast-radius.md) | What is #182's complete edit set? | **exp-006's "one line in one file" is wrong by ~7x** — 7 files minimum, 8 with the reviewer sibling. And the FAST tier passes green on the broken intermediate state |
| [EXP-003](findings/exp-003-executable-verification.md) | Does any SPEC `Verification:` line execute today? | **Yes — 1 of 251.** Prior art exists and is green, so #165 stays in scope. The "no prior art → drop it" branch is refuted |
| [EXP-004](findings/exp-004-redcheck-reuse.md) | Can plan-050's control harness be reused, and is a control possible? | **Reuse as-is, and a control is possible for ALL THREE subjects** — which **refutes plan-050's D-8** as written |

### The four results that change the plan

**1. D-8 is wrong about the edit set, and this plan must not inherit it verbatim.** plan-050's D-8
says #182's fix *"has no exit code and cannot have one."* EXP-004 built the control and ran a
**half-fix arm**: editing `red-team.md:63` alone **breaks** `spec/agents.md:73`, whose `Verification:`
clause pins the literal string — and the fixture catches it with exit 1. D-8 is right about
*behaviour* (no exit code for "a reviewer obeyed a rule") and wrong about *edit-set completeness*.
Carried verbatim, this plan would under-claim and skip a control it can build. **See D-1.**

**2. #182's blast radius is 7 files, and mostly invisible to automation.** EXP-002's spike measured
the decisive case: with `red-team.md` reworded and `spec/agents.md:73` still pinning a string that no
longer exists (`grep -c` → **0**), the FAST tier returns **pass, first_failure None**. FULL is the
same command set, so it does too. Three of the twelve edit steps have **nothing mechanical** behind
them. There is also **no `spec → agent` edge** in `DRIFT-CHECK.md` at all — the same class pass-4's
C24 flagged on plan-050.

**3. Executable-`Verification:` prior art exists — 1 of 251 clauses.** `REQ-CLI-006` /
`test_cli_enumeration.py` is green in 0.02s, wired at `CHANGE-VALIDATION.md:80` with §3 globs on
**both** the script and the spec file. Two further instances sit on the agent-prose axis this plan
needs, one of them (`test_gates.py:349`) already asserting prose in `red-team.md` — the very file
#182 changes. **This plan follows a three-instance precedent; it invents nothing.**

**4. #165's class claim is confirmed by execution, and is larger than this plan.** Ten literal
Verification commands were hand-run; **two are false today in a FULL-tier-green tree** — a stale
`skills/optimal-instructions/` path and a stale `.agents/skills/` path. Those go to #165 as evidence,
not into this plan's scope.

### Re-measured figures (D-5)

| Figure | Value | Note |
| :-- | --: | :-- |
| Exit-code-decidable `Verification:` clauses in `spec/agents.md` | **0 of 26** | the one clause carrying a command exits 0 with a match |
| `Verification:` clauses corpus-wide / of those, executed | **251 / 1** | 0.4% |
| Files in #182's minimum consistent edit set | **7** | 8 including the `reviewer.md` sibling |
| Sites pinning the literal `Read-only — never writes files` | **3** | `red-team.md:63`, `spec/agents.md:73`, **`spec/agents.md:97`** |
| `Agent` occurrences across all 7 `agents/*.md` | **0** | #184's RED |
| Free `REQ-AGENT-*` ids | **049, 052-059** | `050`, `051`, `060`-`064` are taken |
| Harness roots deployed on this machine | **2** | `~/.claude`, `~/.agents`; codex/opencode/pi absent |
| `gate-run.sh` copies in the corpus, materially drifted | **3** | plan-048, -049, -050 |

### Two defects found by the experiments, both out of scope

- **`change_validation.py:946`** declares `--changed` with `nargs="*"` and **no** `action="append"`,
  so `--changed A --changed B` silently validates only `B`. **Confirmed at source**, not taken on
  report. A validation-coverage hole affecting every caller. → file upstream.
- The two false `Verification:` commands above. → evidence on #165.

## Approach
_To be determined after scoping and investigation._

## Epics
_To be determined._

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
