---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: review loop bead representation, success criteria end-state re-check, evidence-bearing close-out

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #198 — yf-plan Phase 3: give the review loop a bead representation — dispatch→record ordering, and why the loop cannot live in the formula

> Split out of **plan-051** by operator decision: the content was drafted after that plan's approving red-team pass, so rather than ship it unreviewed it goes here with its measurements intact.

## Two ...

**Disposition:**
**Notes:**

## #199 — yf-plan: nothing re-checks plan.md Success Criteria at completion — a criterion discharged mid-plan rots silently

> Split out of the **plan-051** session by operator decision, alongside #198. Related to #198 (both are "a stage a script could own"), but a **different trigger**: #198 fires inside the review loop, thi...

**Disposition:**
**Notes:**

## #205 — Close-out is manual and the closable signal is wrong in BOTH directions — make verify-then-close a mechanical step at land-the-plane / tab-teardown / deploy

> Filed at operator direction after a hand sweep of the backlog closed #200, #164 and #153 — three issues that a mechanical close-out step should have surfaced, and that between them expose the whole de...

**Disposition:**
**Notes:**

## #194 — yf-plan Phase 3 has no bead representation: fan out the red-team into parallel review lenses via a per-cycle plan-review wisp
Labels: type::feature, priority::high
> DEFERRED FROM plan-051 (which scopes #184's serial-self-review half only).

FINDING. Phase 3 (PLAN/REVIEW) is the ONLY yf-plan phase with no bead representation.
Phase 2 = wisp (plan-investigate), Pha...

**Disposition:**
**Notes:**

## #197 — formula aspects: make the classify -> lint -> verify obligation a bead that must be closed, not a paragraph an agent may skip
Labels: type::feature, priority::medium
> UNVERIFIED PREMISE — stated as such. beads.gascity.com/workflows/formulas lists "Aspects:
cross-cutting transformations applied to matching steps" among formula constructs. It was
NOT confirmed agains...

**Disposition:**
**Notes:**

## #196 — retrospective prevention: fields are prose that nothing executes — use bd mol distill to make a remediation shape pourable
Labels: type::feature, priority::high
> This is the strongest available answer to "why do planning sessions keep generating the
same follow-on issues", and it is an instance of #149's own M5 complaint (process rules
that nothing executes) t...

**Disposition:**
**Notes:**

## #174 — yf-plan: a review-phase validation pass — falsify every criterion, and cross-check every claim against the code that scores it

> **Proposes the mechanism for the defect family #173 diagnoses.** #173 records *what went wrong and why five red-team cycles missed it*, under an explicit "record, do not fix" instruction. This issue p...

**Disposition:**
**Notes:**

## #173 — yf-plan: success criteria and upstream dispositions are never checked against the engine that enforces them

> Filed from plan-046 execution, at operator instruction: **record, do not fix**.

## Two concrete defects, one family

### 1. A plan instruction contradicted the engine that enforces it

plan-046 Issue...

**Disposition:**
**Notes:**

## #177 — yf-plan red-team: no check that a numeric target is derivable from the plan's own scope rules

> ## A numeric target can be fixed-at-approval, falsifiable, and still contradict the plan's own rules

Every red-team pass in plan-047 verified that its residue target was **fixed at approval** — the
p...

**Disposition:**
**Notes:**

## #191 — yf-plan: scaffold reviews/pass-N.md instead of hand-typing it — the shape check already fires, the authoring is what is missing

> ## The check already exists and works. That is the point.

`doc_lint`'s `required-sections` rule catches `## Missing (all now closed)` **every single time** — it fired on `pass-6.md`, on `pass-7.md`, ...

**Disposition:**
**Notes:**

## #145 — New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract

> > **Written to be read cold.** The evidence below was gathered in one session (2026-08-16) and this issue is the only record of it. Nothing here requires that conversation.

## Proposal

A new **`yf-r...

**Disposition:**
**Notes:**

## #188 — Test suites assert output STRUCTURE and never payload FIDELITY — the blind spot #186/#187 lived in

> ## The defect class

Our test suites assert the **shape** of a tool's output and never the **fidelity of its content**. A tool can therefore corrupt every value it carries while every assertion stays ...

**Disposition:**
**Notes:**

## #190 — Require plans to ship tests for code they write, at >= 80% coverage of that code — with a recipe row that enforces it

> ## Proposed policy

**Code written as part of a plan ships with tests, at >= 80% coverage of the code that plan wrote.**

Today this is convention, unevenly applied, and enforced by nothing. #189 meas...

**Disposition:**
**Notes:**

## #149 — M5/M9: process rules that nothing executes, and remediation edges that exist only in prose
Labels: type::task, priority::high
> Filed from research 004 (docs/research/004-plan-process-defect-mining, epic yf-mol-fsp, commit 2adad77).

Two defect classes that share one root cause: a step with no exit code is not a step.

M9 (ran...

**Disposition:**
**Notes:**

## #150 — research 004: process-defect mining across 83 plan bundles
Labels: priority::medium
> Coarse tracking issue for research 004 (precedent: #146 for research 003).

Bundle: docs/research/004-plan-process-defect-mining/ — commit 2adad77 on main.

QUESTION: across 83 plan bundles in five re...

**Disposition:**
**Notes:**

## #165 — SPEC `Verification:` lines are prose shaped like commands — a FULL tier can be all-green while a spec's own stated verification is false

> Follow-on from plan-045 (#162). Observed during execution; the specific instance was fixed, the class was not.

## What happened

plan-045 Epic 6 reported a green final sweep, measured: `cargo test` 4...

**Disposition:**
**Notes:**

## #201 — change_validation.py: repeated --changed silently drops all but the last path

> ## The defect

`change_validation.py` declares `--changed` with `nargs="*"` and **no** `action="append"`, so a
caller passing the flag more than once silently keeps **only the last occurrence**. Every...

**Disposition:**
**Notes:**

## #202 — bd mol burn: a cancelled burn exits 0, so a scripted burn cannot detect it

> ## The defect

A cancelled `bd mol burn` **exits 0**. A scripted caller reading the exit code concludes the burn
succeeded when nothing was burned.

Without `--force`, `bd mol burn` prompts `Continue?...

**Disposition:**
**Notes:**

## #203 — Exit-code discipline: five instruments report failure in output and success in $? — promote the 0/1/2 contract repo-wide

> Filed by operator decision from the **plan-051** session. Related: #199, #198, #202, #173.

## The class

**An instrument reports failure in its OUTPUT and success in its EXIT CODE.** A scripted calle...

**Disposition:**
**Notes:**

## #204 — yf-herdr: no teardown contract — a completed plan's subordinate tab is never closed, and only harvest-before-prune makes closing safe

> Filed by operator decision from the **plan-051** session. Related: #198 (the harvest→prune hazard, same ordering constraint), #203 (structural verification of an operation's result).

## The gap, meas...

**Disposition:**
**Notes:**
