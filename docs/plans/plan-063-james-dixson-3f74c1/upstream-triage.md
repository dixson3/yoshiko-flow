---
type: Reference
okf_spec: OKF-PLAN
description: Disposition of each candidate upstream issue, with the reasoning behind
  it — the triage record behind plan.md's Upstream Issues table.
---
# Upstream Issue Triage: make landings stick

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #331 — `land` is incompatible with `execute.worktree: false` — no execute branch is ever created
Labels: bug
> ## What

Under `{"execute.worktree": false}`, `/yf-plan execute` takes the in-place fallback and
**no execute branch is ever created**. `_worktree_ensure` returns
`{"viable": false, "reason": "opted-o...

**Disposition:**
**Notes:**

## #332 — `assets/upstream-drafts/` is undocumented in every yf-plan `.md`
Labels: bug
> ## What

`_land_upstream_rows` expects per-issue draft bodies at:

```
<plan_dir>/assets/upstream-drafts/<issue-number>.md
```

(`skills/yf-plan/scripts/plan_manager.py:7936` and `:7948`.)

That path ...

**Disposition:**
**Notes:**

## #333 — A decision file written inside the tree halts the landing at L16, past the irreversible boundary
Labels: bug
> ## What

`land --apply <decision.json> <plan_dir>` accepts any path for the decision document. If that
path is **inside the repository tree** and outside `<plan_dir>`, it is an untracked file that
`_l...

**Disposition:**
**Notes:**

## #340 — L18 crashes with a TypeError on every landing: _land_l18_prune calls _worktree_teardown with one arg, signature needs two
Labels: bug
> ## The defect

`_land_l18_prune` calls `_worktree_teardown` with one argument; the function requires two.

```python
# skills/yf-plan/scripts/plan_manager.py:9512
wt = _worktree_teardown(ctx.plan_dir)...

**Disposition:**
**Notes:**

## #341 — land --dry-run's worktree_dirty can never report dirty: bool() of a 2-tuple is always True, so  only ever means 'no worktree'
Labels: bug
> ## The defect

The landing manifest's `worktree_dirty` field can **never report a dirty tree**, and its `false`
does not mean what a reader takes it to mean.

```python
# skills/yf-plan/scripts/plan_m...

**Disposition:**
**Notes:**

## #342 — L16 commits the WHOLE INDEX: a pre-staged unrelated file is pushed to origin under the plan's commit message, and L16 reports pass
Labels: bug
> ## The defect

L16 stages the plan folder, then commits **the whole index**:

```python
# skills/yf-plan/scripts/plan_manager.py:9352
add = ctx.run("git", ["add", "--", ctx.plan_dir.as_posix()], cwd=c...

**Disposition:**
**Notes:**

## #343 — L16's journal filter is a substring match: it misses land-beads.json and a collapsed '?? .yf/', so it does not even exempt the journal
Labels: bug
> ## The defect

L16's post-condition filters the landing journal out of `git status --porcelain` with a
**substring match on one constant**:

```python
# skills/yf-plan/scripts/plan_manager.py:8544
LAN...

**Disposition:**
**Notes:**
