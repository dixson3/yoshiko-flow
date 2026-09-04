---
type: Record
okf_spec: OKF-PLAN
title: '`land` is incompatible with `execute.worktree: false` — no execute branch is ever created'
upstream_action: gh issue create
plan: plan-062-james-dixson-c3e98f
discharges: 5.1
status: filed
upstream_url: https://github.com/dixson3/yoshiko-flow/issues/331
description: 'Draft body for a NEW upstream issue: under execute.worktree false no execute branch is ever created, so _land_manifest halts execute-branch-missing with resolvable_by_agent false and land cannot run at all. Records the Issue 0.7 hand-created-branch workaround and two candidate fixes.'
---
# Upstream filing draft — `land` is incompatible with `execute.worktree: false` — no execute branch is ever created

> **FILED** — https://github.com/dixson3/yoshiko-flow/issues/331
>
> Issue 5.1 of plan-062. The operator reviewed this draft on disk
> and authorized the write; the posted body was verified BYTE-EXACT by `gh issue view`
> read-back, not by exit code. Action taken:
> `gh issue create` against `dixson3/yoshiko-flow`. The title above is the intended issue title.

## What

Under `{"execute.worktree": false}`, `/yf-plan execute` takes the in-place fallback and
**no execute branch is ever created**. `_worktree_ensure` returns
`{"viable": false, "reason": "opted-out"}` **before any branch creation**.

`_land_manifest` (`skills/yf-plan/scripts/plan_manager.py:8005`) then appends a halt:

```
{"code": "execute-branch-missing", ...}
```

with `resolvable_by_agent: false`, so `land --dry-run` cannot produce a manifest and
`land --apply` cannot run at all. **In-place mode and `land` are mutually exclusive as
shipped.**

## Why it matters

The two features are individually reasonable and jointly unusable. A plan that must execute
in-place — because its own deliverable is the `plan_manager.py` the landing runs from, which
is exactly plan-062's situation — cannot use the landing capability that plan-062 just
finished wiring.

## Measured

plan-062 pass-4 C37, and again during execution. The workaround was Issue 0.7: create the
branch by hand in the primary checkout, `git checkout -b <plan-id>-execute main`, immediately
after the in-place fallback. That works, and it is a workaround, not a fix — nothing in
`SKILL.md` tells an operator it is needed, and the failure appears only at land time, long
after the choice that caused it.

## Suggested fix

Either:

- **`_worktree_ensure` creates the branch even when opted out of the worktree.** The branch
  and the worktree are separable; only the worktree was opted out of. This is the smaller fix
  and matches what Issue 0.7 did by hand.
- **or** `land`'s manifest treats "in-place mode, branch absent" as a distinct, *resolvable*
  finding with the `git checkout -b` remediation attached, rather than an unresolvable halt.

The first is preferable: it removes the failure instead of documenting it.

Found while executing plan-062 (`docs/plans/plan-062-james-dixson-c3e98f`).
