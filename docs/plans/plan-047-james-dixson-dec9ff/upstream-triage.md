---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: document templates linters extractor plan parsing

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #174 — yf-plan: a review-phase validation pass — falsify every criterion, and cross-check every claim against the code that scores it

> **Proposes the mechanism for the defect family #173 diagnoses.** #173 records *what went wrong and why five red-team cycles missed it*, under an explicit "record, do not fix" instruction. This issue p...

**Disposition:** partial
**Notes:** Both halves need the plan's assertions machine-readable. Templates additionally add the criterion ids its matrix joins on. The two checks themselves stay open. **Resolved by:** Issue 0.3, 5.1.

## #173 — yf-plan: success criteria and upstream dispositions are never checked against the engine that enforces them

> Filed from plan-046 execution, at operator instruction: **record, do not fix**.

## Two concrete defects, one family

### 1. A plan instruction contradicted the engine that enforces it

plan-046 Issue...

**Disposition:** exclude
**Notes:** The evidence record for #174, deliberately kept open.

## #172 — yf-plan README.md File Layout block is stale — 29 omissions including SPEC.md, OKF-EXTENSION.md, and test-harness/

> Split out of #118 by plan-046 Issue 5.4. Same file, different defect — folding it into #118 would have made #118 unreviewable.

#118 was about `README.md` still naming `README.md` as the plan-folder o...

**Disposition:** exclude
**Notes:** The skill-dir README, not a bundle document type.

## #165 — SPEC `Verification:` lines are prose shaped like commands — a FULL tier can be all-green while a spec's own stated verification is false

> Follow-on from plan-045 (#162). Observed during execution; the specific instance was fixed, the class was not.

## What happened

plan-045 Epic 6 reported a green final sweep, measured: `cargo test` 4...

**Disposition:** include
**Notes:** SPEC.md is an in-scope document type; this is the spec-linter's headline rule. **Resolved by:** Issue 7.2.

## #150 — research 004: process-defect mining across 83 plan bundles
Labels: priority::medium
> Coarse tracking issue for research 004 (precedent: #146 for research 003).

Bundle: docs/research/004-plan-process-defect-mining/ — commit 2adad77 on main.

QUESTION: across 83 plan bundles in five re...

**Disposition:** exclude
**Notes:** Coarse research tracker and evidence source, not work.

## #149 — M5/M9: process rules that nothing executes, and remediation edges that exist only in prose
Labels: type::task, priority::high
> Filed from research 004 (docs/research/004-plan-process-defect-mining, epic yf-mol-fsp, commit 2adad77).

Two defect classes that share one root cause: a step with no exit code is not a step.

M9 (ran...

**Disposition:** partial
**Notes:** M9 becomes a template field (a bundle declares what it fixes) plus a linter check. M5 as a class is not closed here. **Resolved by:** Issue 0.3, 0.4.

## #145 — New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract

> > **Written to be read cold.** The evidence below was gathered in one session (2026-08-16) and this issue is the only record of it. Nothing here requires that conversation.

## Proposal

A new **`yf-r...

**Disposition:** exclude
**Notes:** Adjacent (escape-rate measurement), separate deliverable.

## #135 — yf-plan: a measured literal in plan.md goes stale when the plan is inside its own measured corpus

> ## The pattern

A plan states a **measured number** as a literal in `plan.md` — a baseline, a corpus count, a signal count, an expected test tuple. The number then goes stale, because the corpus it wa...

**Disposition:** partial
**Notes:** A linter can flag hand-maintained counts in an authored document; it cannot solve corpus self-inclusion. **Resolved by:** Issue 7.3.

## #125 — yf-plan: optional status-enum hardening for update-status (currently free-form, no validation)
Labels: type::task, priority::low, follow-on
> Follow-on from plan-035 (5.2 honesty fix). plan_manager.py update-status is a free-form writer with no enum guard — a typo'd status writes silently; the 9-value vocabulary (scoping..complete) is doc/s...

**Disposition:** include
**Notes:** The documented 9-value vocabulary becomes a linted enum rather than doc/spec/test-enforced only. **Resolved by:** Issue 2.5.

## #113 — yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state)

> ## Observation

Across `d3-pxe` plan-013, four real defects were found in review. **All four are the same class**, and one escaped every pass:

| Found by | Defect |
| :-- | :-- |
| Conformance | Issu...

**Disposition:** partial
**Notes:** This plan delivers the extractor the walk requires. The walk itself stays open — its own re-open trigger (two consecutive plans with structural escapes) is **not** met; plan-046's two escapes were claims-class, not ordering-class. **Resolved by:** Issue 5.3.

## #62 — Propose yf-spec skill: build & manage specifications; yf-plan SPEC-first integration

> ## Proposal

Introduce a new **`yf-spec`** skill dedicated to building and managing specifications (the `SPEC.md` requirements surface: `REQ-*` ids, testable/non-testable classification, the living-am...

**Disposition:** partial
**Notes:** This plan delivers the spec-linter half. Whether a full `yf-spec` skill follows stays open. **Resolved by:** Issue 7.5.
