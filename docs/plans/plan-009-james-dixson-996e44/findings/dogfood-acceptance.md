# Dogfood acceptance — bdplan worktree execution (Issue 2.5)

**Result: 23 / 23 PASS** on a fresh `bd init` repo (2026-06-14). This is the named
acceptance checklist that gates the D2 default-on flip (Capability Gate
`beads-skills-mol-bjf.6`). Runnable copy: `dogfood_worktree.sh` (this dir).

## Why a throwaway repo

The merge-back step (§6.1 `git merge --no-ff <plan>`) needs a clean base checkout, but
plan-009's own execution leaves the real repo's working tree dirty (bootstrapping: the
plan modifies `bdplan execute` itself, so its first run is in-place — see plan §Risks).
The checklist therefore runs the full lifecycle against an isolated, `bd init`-ed repo so
the real `bd` shared-DB resolution, merge, and teardown are exercised for real.

## Checklist → Success Criteria

| # | Assertion | SC |
|---|-----------|----|
| 1 | `worktree ensure` → `viable`, `action=created`, `branch=<plan-id>` | SC1 |
| 2 | worktree dir exists; HEAD on the plan branch | SC1 |
| 3 | `/.worktrees/` is gitignored (ensure-managed, Issue 1.2) | SC1 |
| 4 | a commit inside the worktree lands on `<plan>`, **not** the primary checkout | SC1 |
| 5 | `bd create` from inside the worktree succeeds | SC2 |
| 6 | that bead is visible from the **primary** (single shared DB, INV-2) | SC2 |
| 7 | the worktree has **no divergent DB** (no own `.beads/embeddeddolt`; resolves via git-common-dir) | SC2 |
| 8 | `worktree path` returns the repo-relative path; `plan_dir` lives primary-side | address-space (C1/M1) |
| 9 | `git merge --no-ff <plan>` from primary brings the code onto base; merge commit has 2 parents | SC4 |
| 10 | `validate-merged` passes and emits the **cross-plan-not-checked notice** when `validate-cmd` unset | SC4 / C2 |
| 11 | with `validate-cmd` configured, layer-(b) runs and is reflected in the verdict | SC4 |
| 12 | landing-lock acquire records a holder; release frees it | Issue 3.4 |
| 13 | `worktree teardown` removes the worktree + deletes the merged branch | SC6 |
| 14 | opt-out (`execute.worktree:false`) → `viable=false reason=opted-out` (in-place fallback) | SC6 |

## Gating outcome

All SC 1–6 demonstrated end-to-end. Per Issue 2.5 the **D2 default-on flip is unblocked**:
worktree mode ships **default-on** (opt-in via `_worktree_opted_out()` defaulting to
worktree-enabled), with the safe in-place fallback verified (assertion 14). Capability
Gate `beads-skills-mol-bjf.6` is resolved on the strength of this run.

## Bootstrapping note

plan-009 itself executed **in-place** (worktree feature not yet built at its own start —
plan §Risks). Worktree mode applies to the *next* plan executed after this lands and the
installed copy is refreshed.
