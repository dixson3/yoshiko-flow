---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: execution engine silent data loss

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #206 — CRITICAL: plan_extract.py still silently drops detail lines — inline-code-only continuations and fenced blocks vanish with unparsed: 0 (same family as #186/#187)
Labels: type::bug, priority::critical
> ## Summary

`plan_extract.py` still silently discards issue-detail content — the same failure family as #186 / #187, which are closed. Two line shapes are dropped **whole**, and both are reported as `...

**Disposition:**
**Notes:**

## #210 — pour_fidelity.py is not shipped to the skill dir — SKILL.md 6.4's completion fidelity gate is unrunnable in every repo but this one
Labels: type::bug, priority::high
> ## Summary

`SKILL.md` §6.4 runs the completion pour-fidelity gate as:

```bash
FIDELITY=$(uv run _shared/pour_fidelity.py /tmp/yf-beads.json "${plan_dir}" --strict --plan "${plan_id}")
```

`_shared/...

**Disposition:**
**Notes:**

## #209 — Issue beads carry no plan_dir, so poured descriptions cite EXP-NNN / SC-N evidence an executor cannot locate (21 of 35 in one plan)
Labels: priority::medium, type::bug
> ## Summary

Since #187, an issue bead's description is the plan's per-issue `detail` **verbatim**. That text routinely cites evidence by identifier — `EXP-001`, `SC8`, `R11`, a bundle-relative filenam...

**Disposition:**
**Notes:**

## #207 — resume-scan reports found: true for a BURNED epic, making the plan permanently unpourable (both SKILL.md 5.2 branches dead-end)
Labels: type::bug, priority::high
> ## Summary

`resume-scan` reads the plan's epic id from `plan.md`'s `**Epic:**` field and **never checks whether that epic still exists in the tracker**. If the epic has been deleted (`bd mol burn`), ...

**Disposition:**
**Notes:**

## #208 — update-status accepts out-of-vocabulary statuses silently — strands the plan AND relaxes doc_lint (STATUS_SEVERITY fails open)
Labels: type::bug, priority::high
> ## Summary

`update-status` accepts **any** string as a plan status with no validation. Writing an out-of-vocabulary value strands the plan: it becomes invisible to `parked`, ineligible for `execute`,...

**Disposition:**
**Notes:**

## #214 — yf-plan: `REQ-PLAN-073` id collision — two different requirements share one id
Labels: priority::medium, type::bug
> **Measured:** plan-052, D-18. Re-confirmed on the tree at execution time.

Two different requirements are both numbered `REQ-PLAN-073`:

- `skills/yf-plan/SPEC.md:345` — *"the plan and incubator roots...

**Disposition:**
**Notes:**

## #189 — Six shipped scripts have no tests at all — including two CHANGE-VALIDATION checks and the beads repair engine

> ## Summary

Six shipped scripts have **no test file and are referenced by no test anywhere in the repo**. This is the coverage half of the problem; the blind-spot half — suites that exist but assert o...

**Disposition:**
**Notes:**

## #188 — Test suites assert output STRUCTURE and never payload FIDELITY — the blind spot #186/#187 lived in

> ## The defect class

Our test suites assert the **shape** of a tool's output and never the **fidelity of its content**. A tool can therefore corrupt every value it carries while every assertion stays ...

**Disposition:**
**Notes:**
