---
type: Reference
okf_spec: OKF-PLAN
description: Disposition of each candidate upstream issue, with the reasoning behind
  it — the triage record behind plan.md's Upstream Issues table.
---
# Upstream Issue Triage: wire land --apply

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #327 — `land --apply` is an unconditional stub — the fully-implemented `_land_execute` has no caller, so no plan can land
Labels: bug
> ## The defect

`land --apply` can never execute a landing. The CLI performs its two safety checks and then
falls into an **unconditional stub**, at `plan_manager.py:8305-8310`:

```python
where = _lan...

**Disposition:** include
**Notes:** The plan's reason for existing. Closed when the seam is wired, the resume is fixed, and both are covered by a test PROVEN to discriminate (the capability gate requires it to fail against the unwired build).

## #326 — `land`'s `draft_body_path` posts bundle files verbatim, but OKF requires them to carry frontmatter
Labels: bug
> ## The conflict

Two requirements apply to the same file and cannot both be satisfied:

1. **`land` L7 posts the file verbatim.** `_land_l7_reconcile_writes` runs
   `gh issue comment <n> --body-file ...

**Disposition:** deferred
**Notes:** CUT at pass 4 by operator decision — plan-062 narrowed to seam + resume only. The complete verified fix design survives in findings/exp-003 (strip + temp file + compare-the-stripped-text, reusing okf.read_frontmatter, 7/7 spike), so a later plan starts from a solved design. `deferred` sets requires_mention False, so no draft body is authored for this row.

## #304 — The self-authorization residue #301 does not close: the lander cannot forge the ARTIFACT, but the main session still causes the ACT
Labels: type::bug, priority::high
> Filed by **plan-060** (the `land` verb) from EXP-005, so that
[#301](https://github.com/dixson3/yoshiko-flow/issues/301) is not closed claiming a fix it does not
deliver. This is the same **collapsed-...

**Disposition:** partial
**Notes:** Design input, not a deliverable — it is why the seam test adds no production-reachable bypass. The record it promises is findings/exp-001. Stays OPEN; this plan declines to widen the residue rather than closing it.

## #266 — CRITICAL: the plan.md Gates grammar cannot express test_class or cwd, so every capability gate defaults to a class that is never run
Labels: type::bug, priority::critical
> Plan: plan-056-james-dixson-473dba | Bundle: docs/plans/plan-056-james-dixson-473dba (repo-relative)

A capability gate declared in `plan.md` cannot say which class it belongs to, and the default is t...

**Disposition:** partial
**Notes:** This plan structurally depends on the grammar gap and does not close it. Issue 0.0 SETS the gate metadata directly at pour as a workaround; plan_extract.py's grammar is untouched. Recorded so the dependency is on the record rather than discovered at execution (pass-2 C17).
