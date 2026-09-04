---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #341 - land --dry-run''s worktree_dirty can never report
  dirty: bool() of a 2-tuple is always True, so  only ever means ''no worktree'''
---
# Upstream #341: land --dry-run's worktree_dirty can never report dirty: bool() of a 2-tuple is always True, so  only ever means 'no worktree'

- **Number:** 341
- **Title:** land --dry-run's worktree_dirty can never report dirty: bool() of a 2-tuple is always True, so  only ever means 'no worktree'
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

## The defect

The landing manifest's `worktree_dirty` field can **never report a dirty tree**, and its `false`
does not mean what a reader takes it to mean.

```python
# skills/yf-plan/scripts/plan_manager.py:8043
"worktree_dirty": bool(_worktree_dirty(wt)) if wt.is_dir() else False,

# skills/yf-plan/scripts/plan_manager.py:4211
def _worktree_dirty(wt_abs: Path) -> tuple[bool, list[str]]:
```

`_worktree_dirty` returns a **2-tuple** `(dirty, porcelain_lines)`. A non-empty tuple is always
truthy:

```
>>> bool((False, []))
True
```

So the field is broken in **both** directions:

- **If the worktree exists** → `bool(<2-tuple>)` is **unconditionally `True`**. It would report
  `dirty` on a perfectly clean worktree.
- **If the worktree does not exist** → the `else` branch returns `False`. That is the *absence of
  a directory*, not a clean tree.

The only way the field can read `false` is the else-branch. **It never observes a tree.**

## Measured, on plan-062's landing

plan-062 ran with `execute.worktree: false`, so `.worktrees/plan-062-james-dixson-c3e98f` was
never created. The manifest reported:

```
worktree_dirty: false
worktree_path:  .worktrees/plan-062-james-dixson-c3e98f     <- does not exist
```

while `git status --porcelain` in the real checkout showed **two modified files**. A reviewer
reading `worktree_dirty: false` would have concluded the tree was clean.

## Why that mattered

Those two files would have failed **L16**, which stages only its own `plan_dir` and then asserts
a clean **whole-repo** porcelain:

```python
add = ctx.run("git", ["add", "--", ctx.plan_dir.as_posix()], cwd=ctx.root)
...
porcelain = "\n".join(ln for ln in raw.splitlines() if ln.strip() and LAND_JOURNAL_DIR not in ln)
if porcelain or unpushed not in ("0", ""):
    return _step("l16_commit_and_push_two", "fail", ...)
```

L16 runs **after the L6 push and after the L7 outward writes**, so the landing would have posted
three public comments, closed an issue, and then halted. It was caught only because the `lander`
sub-agent checked the working tree by a separate route instead of trusting the field.

## This is the vacuous-check class

A field whose failure mode is a reassuring value, computed from an expression that cannot
express the failure. Same family as #263, #181, #207 — and as #334, filed the same day, where a
test's `or` fallback guaranteed a non-match.

## Suggested direction (not prescriptive)

- Fix the expression: `_worktree_dirty(wt)[0]`.
- **The `else` branch needs a third value, not `False`.** "No worktree" is not "clean" — under
  in-place execution there is no worktree by design, and the real tree is `ctx.root`. Consider
  `null`/`"n/a"`, or point the check at the primary checkout when the worktree is absent.
- Whatever the field ends up meaning, **the landing should assert the condition L16 actually
  enforces** — a clean whole-repo porcelain in the checkout the landing will run in — rather than
  a proxy for it. Ideally as a `--dry-run` halt, since L16's own failure lands past the
  irreversible boundary.

## Provenance

Found by the `lander` sub-agent while adjudicating **plan-062**'s landing
(`plan-062-james-dixson-c3e98f`, tracker #330), and independently re-measured. Adjacent to #333
(a decision file inside the tree fails the same L16 post-condition by a different route) and
#340 (L18's TypeError, in the same step chain).

