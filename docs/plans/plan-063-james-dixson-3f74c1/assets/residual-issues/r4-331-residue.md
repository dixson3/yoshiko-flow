> **CORRECTION (plan-068 Issue 3.1, measured 2026-09-09).** This note said **three** plans. It
> is **two** — plan-062 and plan-063. **plan-061 ran in WORKTREE mode**, so #331 never applied
> to it: its `context.md:72` reads *"a git worktree at `.worktrees/<plan-id>` on
> `<plan-id>-execute`"*, it has **no Issue 0.7**, it mentions `#331` **zero** times, and its
> down-merge commit `7dd863c` (*"Merge branch 'main' into
> plan-061-james-dixson-6d8c97-execute"*) is the worktree-mode down-merge. The table below is
> corrected; the argument is unaffected, because two consecutive plans hand-cutting the same
> branch is already accumulating residue.
>
> **plan-068 makes it three** — and closes it. See `REQ-BRANCH-001`/`-002` as amended.

**#331 was depended upon by TWO consecutive plans and remained open. This issue records the
accumulating residue rather than the original defect.**

Under `execute.worktree: false`, `worktree ensure` returns `viable: false / reason: opted-out` and
**no execute branch is ever created**. But `land --dry-run` halts with `execute-branch-missing`,
so the landing route is unreachable in in-place mode.

Every affected plan has worked around it the same way — a hand-cut branch, as an explicit numbered
issue in its own Epic 0:

| Plan | Mode | Workaround |
| :-- | :-- | :-- |
| plan-061 | **worktree** | **none — #331 never applied** (corrected, plan-068 Issue 3.1) |
| plan-062 | in-place | hand-cut `<plan-id>-execute` |
| plan-063 | in-place | hand-cut `<plan-id>-execute` (Issue 0.7) |
| plan-068 | in-place | hand-cut `<plan-id>-execute` (Issue 0.1) — **and fixes it** |

**Why in-place mode is not an edge case.** Both in-place plans *edit `plan_manager.py` itself* — the
file the landing runs from. Under worktree mode the primary checkout stays on `main` carrying the
unfixed code, and the landing crashes at the prune. That is not a hypothetical: it is exactly what
plan-062's landing did. So the plans most likely to need the landing capability are precisely the
ones that cannot use worktree mode.

**Why this is worth its own issue.** A workaround repeated twice — three times counting
plan-068 — is no longer a workaround;
it is an undocumented step in the flow that every future in-place plan must rediscover. And each
repetition is a chance to get it wrong — the branch must be cut **before any commit**, or the
first commit lands on `main` and escapes the merge L3 validates.

**Proposed fix.** `worktree ensure` should create the execute **branch** even when it declines to
create the worktree: the two are separable, and in-place mode needs the branch for exactly the same
reason worktree mode does.

> **RESOLVED by plan-068 Epic 2.** `_worktree_ensure_in_place` cuts **and checks out** the branch
> from the strategy-resolved pinned base, as a three-way create/reattach/no-op. The proposed fix
> above was right in substance and **incomplete in one respect**: create-without-checkout is
> silently wrong, because the point is that `ctx.root`'s HEAD *is* the execute branch — without
> that, L1 merges the target into ambient HEAD and reports `Already up to date.` at exit 0
> (`REQ-LAND-002` as amended).
