---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: red-team sandbox spike, sub-agent dispatch, M9 remediation edges

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #190 — Require plans to ship tests for code they write, at >= 80% coverage of that code — with a recipe row that enforces it

> ## Proposed policy

**Code written as part of a plan ships with tests, at >= 80% coverage of the code that plan wrote.**

Today this is convention, unevenly applied, and enforced by nothing. #189 meas...

**Disposition:** deferred
**Notes:** Same axis as #188 — deferred with it
**Notes:**

## #188 — Test suites assert output STRUCTURE and never payload FIDELITY — the blind spot #186/#187 lived in

> ## The defect class

Our test suites assert the **shape** of a tool's output and never the **fidelity of its content**. A tool can therefore corrupt every value it carries while every assertion stays ...

**Disposition:** deferred
**Notes:** plan-050's headline finding is direct evidence, but payload-fidelity is a second independent axis and was scoped OUT of this plan
**Notes:**

## #184 — yf-plan §3: the red-team is never dispatched as a sub-agent — the drafter reviews its own draft

> ## The defect

`yf-plan` SKILL.md §3 REVIEW never dispatches the red-team as a sub-agent. Compare the two phases:

**§2 INVESTIGATE** (`SKILL.md:315`) — unambiguous:

> Spawn a sub-agent per unknown u...

**Disposition:** include
**Notes:** **D-2.** The §2-vs-§3 asymmetry is verbatim: `SKILL.md:315` says **spawn**, `:489` says **perform**. Measured RED: `Agent` appears **0** times across all 7 `agents/*.md`. Needs a NEW `REQ-AGENT-*` — none of 040-048 says who RUNS the review
**Notes:**

## #182 — yf-plan red-team: the read-only rule forbids the sandbox spike that catches specification defects

> ## The rule as written forbids the one technique that catches specification defects

`skills/yf-plan/agents/red-team.md` makes the reviewer read-only (REQ-AGENT-043), and the
dispatching prose in `SKI...

**Disposition:** include
**Notes:** **D-1.** exp-006 NARROWS this issue: `red-team.md:63` says only "never writes files" — it never forbade a spike anywhere. The defect is UNDER-specification, silence read as prohibition. One line, plus `spec/agents.md:73`'s Verification clause, which pins the exact string
**Notes:**

## #177 — yf-plan red-team: no check that a numeric target is derivable from the plan's own scope rules

> ## A numeric target can be fixed-at-approval, falsifiable, and still contradict the plan's own rules

Every red-team pass in plan-047 verified that its residue target was **fixed at approval** — the
p...

**Disposition:** exclude
**Notes:** Closed out by plan-050: the refutation comment was posted and D-6 dropped it on evidence. No further action here
**Notes:**

## #174 — yf-plan: a review-phase validation pass — falsify every criterion, and cross-check every claim against the code that scores it

> **Proposes the mechanism for the defect family #173 diagnoses.** #173 records *what went wrong and why five red-team cycles missed it*, under an explicit "record, do not fix" instruction. This issue p...

**Disposition:** partial
**Notes:** #182 closes a named sub-case — the spike is the technique that catches what reading cannot. The general review-phase falsification pass stays open
**Notes:**

## #173 — yf-plan: success criteria and upstream dispositions are never checked against the engine that enforces them

> Filed from plan-046 execution, at operator instruction: **record, do not fix**.

## Two concrete defects, one family

### 1. A plan instruction contradicted the engine that enforces it

plan-046 Issue...

**Disposition:** partial
**Notes:** #182's and #184's REQs are checked against the surface that enforces them, as worked instances. The general cross-check stays open
**Notes:**

## #165 — SPEC `Verification:` lines are prose shaped like commands — a FULL tier can be all-green while a spec's own stated verification is false

> Follow-on from plan-045 (#162). Observed during execution; the specific instance was fixed, the class was not.

## What happened

plan-045 Epic 6 reported a green final sweep, measured: `cargo test` 4...

**Disposition:** partial
**Notes:** **D-4.** **IN:** this plan's OWN new/amended `Verification:` lines must be EXECUTABLE, demonstrated on the two REQs it ships. **OUT:** the corpus-wide sweep. Folded in because without it this plan ships two requirements nothing executes — the exact M5 defect it exists to fix
**Notes:**

## #150 — research 004: process-defect mining across 83 plan bundles
Labels: priority::medium
> Coarse tracking issue for research 004 (precedent: #146 for research 003).

Bundle: docs/research/004-plan-process-defect-mining/ — commit 2adad77 on main.

QUESTION: across 83 plan bundles in five re...

**Disposition:** partial
**Notes:** **IN:** two more of the ranked classes delivered as worked instances. **OUT:** M9, the M11 probe mechanism, and the remaining classes
**Notes:**

## #149 — M5/M9: process rules that nothing executes, and remediation edges that exist only in prose
Labels: type::task, priority::high
> Filed from research 004 (docs/research/004-plan-process-defect-mining, epic yf-mol-fsp, commit 2adad77).

Two defect classes that share one root cause: a step with no exit code is not a step.

M9 (ran...

**Disposition:** partial
**Notes:** **D-3.** **IN:** a comment correcting the refuted premise — exp-004 measured **26** `discovered-from` edges with **0** attributed on either endpoint, so the relationship EXISTS and only attribution is missing; plus C40 and the no-seam finding. **OUT:** M9 itself. exp-004's "one seam" recommendation does not survive measurement — `bd create --deps discovered-from:` is instructed by prose in >=7 places across 4 skills and no script creates one, so a stamping rule would be M5 vacuity inside the fix for M5
**Notes:**

## #145 — New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract

> > **Written to be read cold.** The evidence below was gathered in one session (2026-08-16) and this issue is the only record of it. Nothing here requires that conversation.

## Proposal

A new **`yf-r...

**Disposition:** deferred
**Notes:** Own plan. The emit side accumulates; a consumer built now still reads a thin corpus
**Notes:**
