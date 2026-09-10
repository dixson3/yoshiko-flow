---
type: Reference
okf_spec: OKF-PLAN
description: Disposition of each candidate upstream issue, with the reasoning behind
  it — the triage record behind plan.md's Upstream Issues table.
---
# Upstream Issue Triage: land close chain repair

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #349 — The land --apply executor frame is outside both REQ-LAND-030's wrapper and the test suite

> ## Shared cause

`REQ-LAND-030` (plan-063) made landing step dispatch fail-closed: an exception raised by a `LAND_EXECUTOR` step is caught and returned as a halting `inconclusive` row rather than a tr...

**Disposition:**
**Notes:**

## #331 — `land` is incompatible with `execute.worktree: false` — no execute branch is ever created
Labels: bug
> ## What

Under `{"execute.worktree": false}`, `/yf-plan execute` takes the in-place fallback and
**no execute branch is ever created**. `_worktree_ensure` returns
`{"viable": false, "reason": "opted-o...

**Disposition:**
**Notes:**

## #334 — `_land_tty_gate(allow_list=[None])` opens the consent gate unconditionally, and its test is vacuous
Labels: bug
> ## Two defects, one site

### 1. `allow_list=[None]` is a total bypass

`_land_tty_gate` decides the escape with:

```python
if not allowed and allow_list and record.get("tty") in allow_list:
    allo...

**Disposition:**
**Notes:**

## #326 — `land`'s `draft_body_path` posts bundle files verbatim, but OKF requires them to carry frontmatter
Labels: bug, deferred
> ## The conflict

Two requirements apply to the same file and cannot both be satisfied:

1. **`land` L7 posts the file verbatim.** `_land_l7_reconcile_writes` runs
   `gh issue comment <n> --body-file ...

**Disposition:**
**Notes:**

## #360 — plan_manager land --apply ignores a validated 'skip' adjudication (l11_recheck_criteria) and halts on it AFTER the merge and push

> ## Summary

`plan_manager.py land --apply` **executes a landing step that the decision document adjudicated
`skip`**, and halts on it — *after* the merge and push have already completed and been pushe...

**Disposition:**
**Notes:**

## #352 — land --dry-run never checks that a draft body satisfies requires_mention, so the failure surfaces only after the writes are public

> **Found by plan-063's own landing (RE-004). Cost: a mid-landing halt with six issues already
written, plus six additional public comments to recover.**

`land --dry-run` enumerates every upstream row ...

**Disposition:**
**Notes:**

## #304 — The self-authorization residue #301 does not close: the lander cannot forge the ARTIFACT, but the main session still causes the ACT
Labels: type::bug, priority::high
> Filed by **plan-060** (the `land` verb) from EXP-005, so that
[#301](https://github.com/dixson3/yoshiko-flow/issues/301) is not closed claiming a fix it does not
deliver. This is the same **collapsed-...

**Disposition:**
**Notes:**

## #348 — The landing close chain bypasses ctx.run: bare subprocess.run gives L8-L15 the wrong cwd and no injection seam

> ## Shared cause

Two findings from plan-063 that are one omission with two faces: the landing close chain (L8-L15) calls `subprocess.run` directly instead of routing through `LandingContext.run`. That...

**Disposition:**
**Notes:**

## #353 — LAND_DIGEST_EXCLUDED omits resolved_target_tip and merge_preview, which L4/L6 self-mutate: every resume at or after L_VALIDATED is a guaranteed digest mismatch

> **Found by plan-063's own landing (RE-005). Every resume at or after `L_VALIDATED` is a guaranteed
digest mismatch — the landing halts on a change it made itself.**

`REQ-LAND-036` (plan-063) introduc...

**Disposition:**
**Notes:**

## #350 — A measurement that failed is reported as a green number (L16 laundered unpushed count, check_amendment_log under-counted n_impl)

> ## Shared cause

Two instances of one defect class: **an emitted number that is not the measured number.** One launders an *unreadable* count into the literal `0`, so a failed measurement reads as gre...

**Disposition:**
**Notes:**
