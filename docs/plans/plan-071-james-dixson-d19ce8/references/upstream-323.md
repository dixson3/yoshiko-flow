---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #323 - yf-plan red-team: EXECUTE each success criterion
  at review time — reviewing a criterion is not executing it'
---
# Upstream #323: yf-plan red-team: EXECUTE each success criterion at review time — reviewing a criterion is not executing it

- **Number:** 323
- **Title:** yf-plan red-team: EXECUTE each success criterion at review time — reviewing a criterion is not executing it
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## The gap

`yf-plan`'s red-team verifies that a success criterion is **well-formed and non-vacuous**. It does not verify that the criterion is **satisfiable**, or that it **survives the plan's own mutations**. Those are different properties, and the difference is measurable.

Measured on `dixson3/writing` plan-012 (OKF corpus backfill, completed 2026-08-30): **five** criteria/pass-conditions were mis-encoded. Four adversarial red-team cycles caught two. The remaining three were caught only by *running* them — two of those had survived **every** review pass.

## The five, and who caught each

| # | Defect | Caught by |
| :-- | :-- | :-- |
| 1 | `SC4` asserted `b['operations']` — a key of `cmd_restore`'s **output**, absent from the backfill record. Exit 1 on a fully successful run | red-team cycle 2 |
| 2 | `SC6` called `set()` on `markdown_lint.py --format json` output, a list of **dicts** → `TypeError` even when before == after | red-team cycle 2 |
| 3 | Issue 3.4 asserted `after.verdict != fail` on four **yf-research** bundles, but `audit_verdict()` shells `plan_manager.py audit` — a yf-**plan** audit — which returns `plan.md missing; cannot audit` ⇒ `fail` **before and after**. Unsatisfiable by construction | **execution** (ESC-001) |
| 4 | `SC6` keyed violations as `<file>:<line>:<message>` in a plan whose entire purpose is to **insert frontmatter**, shifting every subsequent line by 4-6. Same unbroken link, different string. Multiset measured identical 287/287 | **execution** (ESC-002) |
| 5 | `SC8` keyed on `git merge-base main HEAD != HEAD` — a window the plan's **own merge** collapses. Exit 0 pre-merge, exit 1 post-merge, with the underlying property unchanged | **close chain** (`recheck-criteria`) |

Note the two classes are distinct:

- **1, 2, 3 — unsatisfiable by construction.** Could never pass, in any state.
- **4, 5 — satisfiable but self-defeating.** Correct at authoring time, broken by a mutation the plan itself declares.

Class 2 is the more interesting one: those criteria measured the *right* property. Nothing about reading them reveals the defect, because the defect is an interaction between the criterion's encoding and the plan's declared effects.

## Why review cannot catch these

A red-team pass reads a criterion and asks "is this well-formed, non-vacuous, and does it assert the right thing?" All five passed that bar. What none of them survives is **execution** — and for 4 and 5, execution *at the right moment*, since both were green when first written.

`recheck-criteria` already encodes this insight at the completion end (REQ-PLAN-080: "a criterion is only as good as the last time something re-ran it"). The proposal is to apply the same reasoning at the **review** end, where it is far cheaper — plan-012 halted its close chain on defects that a review-time execution would have surfaced days earlier.

## Proposed fix — two prompt-level additions to `agents/red-team.md`

Both are cheap, need no new machinery, and are checkable.

**1. Execute every criterion; require it to fail for the RIGHT REASON.**

At review time a not-yet-discharged criterion *should* fail. The question is how. A criterion failing with `FileNotFoundError`, `TypeError`, `unrecognized arguments`, an `error:` from the wrong tool, or a wrong-tool verdict is a **defect**, not a pending task. A criterion failing with a clean, meaningful exit 1 is fine.

This alone catches 1, 2 and 3.

**2. Check each criterion's key against the plan's own declared mutations.**

If the plan inserts or removes lines, a **line-keyed** criterion is self-defeating. If the plan merges a branch, a **merge-base-keyed** criterion is self-defeating. If the plan renames files, a **path-keyed** criterion needs care.

Mechanically: for each criterion, name what it is keyed on, then check that key against the plan's Approach/Epics for a mutation that changes it.

This catches 4 and 5.

## Suggested wording

Add to the red-team's checklist, alongside the existing non-vacuity check:

> **Execute every success criterion and pass condition.** Do not merely read them. At review time an undischarged criterion should fail *cleanly* — a meaningful non-zero exit. A criterion that fails with a traceback, a parse error, an `unrecognized arguments`, or a verdict from a tool that cannot read the artifact is **mis-encoded**, and that is a defect to report now, not work pending.
>
> **Then name what each criterion is KEYED on** — a line number, a git range, a path, a JSON key — and check that key against the plan's own declared mutations. A plan that inserts frontmatter defeats a line-keyed criterion; a plan that merges a branch defeats a merge-base-keyed one. A criterion the plan will break by doing its job is mis-encoded even though it is correct today.

## Evidence

Full trail in `dixson3/writing`, plan bundle `docs/plans/plan-012-james-dixson-c324be/`:

- `reviews/pass-1.md` … `pass-4.md` — the four cycles (REVISE ×3, APPROVE)
- `escalations.md` — ESC-001 and ESC-002, each with measured evidence
- `log.md` — the close-chain halt at `recheck-criteria` and the two encoding amendments

Both amendments preserved each criterion's **assertion** and changed only its **encoding**; `SC8` was independently confirmed exit 0 *pre*-merge, so neither was a retrofitted pass.

Filed from the plan-012 execution as an observed process defect, not a one-off.
