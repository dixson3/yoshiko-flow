# Upstream Issue Triage: yf-plan lifecycle rework + yf-spec

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #47 — yf-plan: consistent, predictable branch/worktree model (no branch-of-a-branch, intake at execute)
Labels: enhancement, type::feature, priority::medium
> ## Summary

`yf-plan`'s branch/worktree handling is **inconsistent and unpredictable** across runs. Depending on
the state of the working copy when planning starts, the same protocol produces at least...

**Disposition:**
**Notes:**

## #62 — Propose yf-spec skill: build & manage specifications; yf-plan SPEC-first integration

> ## Proposal

Introduce a new **`yf-spec`** skill dedicated to building and managing specifications (the `SPEC.md` requirements surface: `REQ-*` ids, testable/non-testable classification, the living-am...

**Disposition:**
**Notes:**

## #63 — yf-plan: always commit intake state before offering the plan for execution

> ## Proposal

`yf-plan` Phase 4 (INTAKE) should **commit the intake state automatically** as its final step — before the Phase 4.8 handoff that tells the operator to run `/yf-plan execute` in a new ses...

**Disposition:**
**Notes:**

## #64 — yf-plan: re-review gate — modifying a reviewed/approved plan must re-trigger red-team + conformance + portability audit before re-approval

> ## Proposal

When a plan that has already reached `review` or `approved` status is **modified**, yf-plan should automatically **invalidate the approval** and require a fresh review cycle — conformance...

**Disposition:**
**Notes:**
