---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #342 - L16 commits the WHOLE INDEX: a pre-staged unrelated
  file is pushed to origin under the plan''s commit message, and L16 reports pass'
---
# Upstream #342: L16 commits the WHOLE INDEX: a pre-staged unrelated file is pushed to origin under the plan's commit message, and L16 reports pass

- **Number:** 342
- **Title:** L16 commits the WHOLE INDEX: a pre-staged unrelated file is pushed to origin under the plan's commit message, and L16 reports pass
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

## The defect

L16 stages the plan folder, then commits **the whole index**:

```python
# skills/yf-plan/scripts/plan_manager.py:9352
add = ctx.run("git", ["add", "--", ctx.plan_dir.as_posix()], cwd=ctx.root)
...
# :9360
c = ctx.run("git", ["commit", "-m", ...])          # no -o / --only
```

`git commit -m` commits everything staged, not only what the preceding `git add` staged. So any
file **already in the index** when the landing starts is swept into the plan's commit — and then
pushed to `origin/<target>` by the same step.

## Measured

In a sandbox with a bare `origin`, driving the **real** `_land_l16_commit_and_push_two`:

```
porcelain before L16: 'M docs/plans/plan-999-x/plan.md\nM  other.txt'
REAL L16 verdict: pass
files in the commit L16 made:
    docs/plans/plan-999-x/plan.md
    other.txt              <- unrelated, pre-staged, NOT under plan_dir
```

`other.txt` was committed under the plan's commit message and pushed to `origin/main`.

## Why it reports success

L16's post-condition is a whole-repo `git status --porcelain` check. By the time it runs, the
unrelated file has been **committed** — so the porcelain is clean and the step reports `pass`.

**The check cannot see the defect because the step itself removed the evidence.** That is what
makes this worse than a missed check: it is a silent, successful, outward write of work nobody
authorized as part of this landing.

## Blast radius

- Unrelated work reaches `origin/<target>` under a misleading commit message, attributed to a
  plan that did not contain it.
- It is invisible in the landing verdict, the journal, and the decision document.
- It happens at **L16**, past the irreversible boundary — after the L6 push and after L7's public
  comments — so even noticing it later does not offer a clean revert. L16's own recovery contract
  is *"retry-after-rebase, NEVER REVERT"* (`:9345-9347`).

Note the interaction with **#341**: the manifest field an operator would consult to check for a
dirty tree can never report one, so nothing warns beforehand either.

## Distinguish from the neighbouring bugs

This is **not** fixed by a dry-run halt on a dirty tree. A pre-*staged* file and a pre-*modified*
file are different states: a dry-run check catches the second; only path-scoping the commit
catches the first. #333 and #341 are about L16's *check*; this is about L16's *commit*.

## Suggested direction (not prescriptive)

- Path-scope the commit to match the add: `git commit -o -- <plan_dir> -m ...` (or
  `--only`), so L16 can only ever commit what it staged.
- Consider whether L16 should **refuse** on a non-empty pre-existing index rather than commit
  around it — a staged file at landing time is an operator state the landing should not silently
  absorb in either direction.
- Add a Tier-1 test that pre-stages an unrelated file and asserts it is **not** in the commit L16
  makes. The existing suite cannot catch this because it never pre-stages anything.

## Provenance

Found while investigating **plan-063** (`plan-063-james-dixson-3f74c1`) — a sandbox spike driving
the real L16 against an injected `origin`, ~120 lines, no network. Adjacent to #333 and #341 (the
same step, its check rather than its commit) and #340 (the next step in the chain).

