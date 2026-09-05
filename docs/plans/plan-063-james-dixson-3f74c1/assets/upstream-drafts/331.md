**#331 is depended upon by a THIRD consecutive plan and remains open. This issue records the
accumulating residue rather than the original defect.**

Under `execute.worktree: false`, `worktree ensure` returns `viable: false / reason: opted-out` and
**no execute branch is ever created**. But `land --dry-run` halts with `execute-branch-missing`,
so the landing route is unreachable in in-place mode.

Every affected plan has worked around it the same way — a hand-cut branch, as an explicit numbered
issue in its own Epic 0:

| Plan | Workaround |
| :-- | :-- |
| plan-061 | hand-cut `<plan-id>-execute` |
| plan-062 | hand-cut `<plan-id>-execute` |
| plan-063 | hand-cut `<plan-id>-execute` (Issue 0.7) |

**Why in-place mode is not an edge case.** All three plans *edit `plan_manager.py` itself* — the
file the landing runs from. Under worktree mode the primary checkout stays on `main` carrying the
unfixed code, and the landing crashes at the prune. That is not a hypothetical: it is exactly what
plan-062's landing did. So the plans most likely to need the landing capability are precisely the
ones that cannot use worktree mode.

**Why this is worth its own issue.** A workaround repeated three times is no longer a workaround;
it is an undocumented step in the flow that every future in-place plan must rediscover. And each
repetition is a chance to get it wrong — the branch must be cut **before any commit**, or the
first commit lands on `main` and escapes the merge L3 validates.

**Proposed fix.** `worktree ensure` should create the execute **branch** even when it declines to
create the worktree: the two are separable, and in-place mode needs the branch for exactly the same
reason worktree mode does.
