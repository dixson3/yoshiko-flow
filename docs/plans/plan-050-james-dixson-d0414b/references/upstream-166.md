---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #166: yf-beads-extra: document that `bd ready` silently excludes whole categories — two loops have already been built on the assumption it does not

- **Number:** 166
- **Title:** yf-beads-extra: document that `bd ready` silently excludes whole categories — two loops have already been built on the assumption it does not
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Follow-on from plan-045 (#162). A generalization the plan fixed twice, instance-by-instance, without naming the class.

## The behaviour

`bd ready --help` states it plainly:

> Excludes in_progress, **blocked**, deferred, and hooked issues.

There are `--include-deferred` and `--include-ephemeral` flags. There is **no `--include-blocked`**, and `--include-gates` exists on `bd list` but **not** on `bd ready` (`bd ready --include-gates` exits 1).

So `bd ready` is a narrow view with no general widening flag, and any loop built on it silently drops whatever it excludes.

## Two instances, both real, both found the hard way

| | Excluded | Consequence |
| :-- | :-- | :-- |
| **plan-045 D-7** (found in planning) | gate beads | `agents/coordinator.md` loop step 2 reads *"For gate-type beads: read description, run test command"* — over a list that has **never** contained a gate. Dead since it was written. |
| **plan-045 Epic 2** (found in execution) | blocked beads | The plan prescribed marking a failed bead `blocked`. Implemented literally, every failed bead would have become permanently invisible to the loop and the DAG would drain to "empty" — reported as completion. A failure branch built to stop silent success would have manufactured a new one. |

The second was caught only because the executing agent ran `bd ready --help` instead of trusting the plan. It had passed four red-team passes.

## Proposed

Add a `bd ready` section to `yf-beads-extra` (the direct-CLI-gotcha home) stating:

- exactly what `bd ready` excludes;
- that `--include-gates` is a `bd list` flag, not a `bd ready` one;
- that there is no `--include-blocked` at all;
- the consequence: **a loop that drives work from `bd ready` must enumerate excluded categories explicitly**, or it silently drops them.

`in_progress`, `deferred` and `hooked` are the remaining untested corners — same trap, not yet hit.

## Why here

`yf-beads-extra`'s stated remit is "advanced/gotcha layer for using the `bd` CLI directly … issue-type semantics, gate semantics, defensive JSON parsing". This is squarely that, and it is the kind of fact that is cheap to write once and expensive to rediscover — twice, so far, both times inside the same plan.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
