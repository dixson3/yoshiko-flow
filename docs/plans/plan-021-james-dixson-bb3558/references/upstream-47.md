# Upstream #47: yf-plan: consistent, predictable branch/worktree model (no branch-of-a-branch, intake at execute)

- **Number:** 47
- **Title:** yf-plan: consistent, predictable branch/worktree model (no branch-of-a-branch, intake at execute)
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement, type::feature, priority::medium

## Body

## Summary

`yf-plan`'s branch/worktree handling is **inconsistent and unpredictable** across runs. Depending on
the state of the working copy when planning starts, the same protocol produces at least three
different topologies — and one of them ("branch of a branch of `main`") forces an error-prone
**double merge/push dance** to get changes back to `main` and into the default clone.

This issue proposes a single, predictable model: **worktrees are the default place changes happen**,
with explicit per-phase branch names, intake deferred to `execute`, and a clear, consistent set of
landing options — plus a project-config switch for a `main` vs `feature-branch` default strategy.

## Observed behavior (the inconsistency)

Across recent executions, planning has landed in one of three different shapes:

1. **Branch-of-a-branch → double merge/push.** `yf-plan` creates a plan branch in the current
   workspace to generate plan artifacts + run beads intake, then makes a worktree **off the planning
   branch** (so: a branch of a branch of `main`). Execution happens in the worktree, then we have to
   merge worktree → planning-branch → `main`, and push, to get everything home. Two merges, two
   pushes, easy to get wrong.
2. **Artifacts on `main`, code in a worktree off `main`.** All plan artifacts/beads are committed on
   `main` in the default workspace; the plan's *work* happens in a worktree branched from local
   `main`, merged back to local `main` at land-the-plane, then pushed. (Clean — this is close to what
   we want.)
3. **Everything in local `main`.** No worktree at all; all work happens directly in the default
   workspace on `main`.

I don't understand the conditions that select between these, and the lack of predictability is the
core problem.

### Concrete examples

**plan-002** (Claude session `c4977e90-1c45-4883-aee0-73672826fe29`, repo `dixson3/blog`):
- Planning/intake happened on branch `plan-002-blog-publishing-intake`.
- A worktree was created on a *different* branch, `plan-002-james-dixson-62a38d`, shadowing the
  intake branch.
- Landing was: `worktree teardown` merged `plan-002-james-dixson-62a38d` → `plan-002-blog-publishing-intake`,
  then separately `git checkout main` → `git merge --no-ff plan-002-blog-publishing-intake` → `git push origin main`
  → delete local **and** remote branch. A branch-of-a-branch and a two-step merge to `main`.

**plan-003** (current session, repo `dixson3/blog`):
- Intake (the `bd mol pour`) had already happened in a **prior** session — at `execute` time the plan
  was already `approved` with the epic poured. (This alone contradicts "intake at execute".)
- The default checkout was left on `plan-002-blog-publishing-intake` (a *previous* plan's branch),
  and the `plan-003-james-dixson-3d2225` branch sat at the plan-002 tip (`8299bf8`) — i.e. branched
  off plan-002, **not** off `main`. The execute worktree was cut from that.
- Landing required: discovering the topology, realizing a naive `merge plan-003 → main` would have
  dragged in plan-002's unmerged commits, a re-fetch after plan-002 was separately landed to `main`,
  then a merge of plan-003 → `main`. The plan artifacts (`findings/`, `plan.md`) were uncommitted in
  the default tree (on the plan-002 branch) while the essays were committed in the worktree on the
  plan-003 branch — work split across two branches **and** two address spaces.

## Root-cause hypotheses

- **Worktree base = "current HEAD".** `worktree ensure` cuts from whatever branch the default
  checkout happens to be on, which may be a prior plan's branch or a planning branch — not `main`.
  Nothing pins the base to a known anchor.
- **Intake timing varies.** Sometimes intake runs during planning (prior session), sometimes at
  execute. The desired invariant ("intake only at execute") isn't enforced.
- **Plan artifacts vs. plan code live in different places.** Artifacts sometimes land on the default
  branch, code in the worktree branch; reconciling them is ad hoc.
- **Leftover branch state.** The default checkout is not returned to a known branch between
  plans, so the next plan inherits a surprising base.

## Proposed model (predictable, worktree-default)

### Planning phase

- When the `yf-plan` protocol triggers, **move all planning work** (investigations, experiments,
  document drafts, plan artifacts, beads scoping) into a **new plan worktree/branch**:
  - branch name: **`<plan-id>-development`**
- Work continues in the session **in that worktree**, all the way through the **portability check**,
  and stops **just before intake**.
- Once portability completes, **always commit the plan.**
- Then offer the operator two options:
  1. **Push the plan branch upstream** into a feature branch named **`<plan-id>`**, then delete the
     local worktree + `<plan-id>-development` branch; **or**
  2. **Merge** the local `<plan-id>-development` branch/worktree into local `main`, push `main`
     upstream, then delete the local worktree + branch.
- In **either** case, create an **upstream tracking issue**: *"Complete execution of `<plan-id>`"*.
  If the plan was spawned/inspired by one or more existing upstream issues, annotate the new issue as
  a **dependency** of those original issue(s).
- Then the operator chooses to **implement now** or **move on**. If implementing, tell them to run
  **`/yf-plan execute <plan-id>`** — in the current session or a new one (**new session recommended
  for large plans** that may exhaust token context).
- **Important invariant: intake does NOT happen until `execute`.**

### Execution phase

- When `execute` starts, **always create a new worktree**:
  - branch name: **`<plan-id>-execute`**
- The execute worktree's **base is determined by how the plan landed**:
  - bound to **`main`** if the plan was merged to `main` (option 2 above);
  - bound to the **upstream feature branch `<plan-id>`** if the plan was pushed there (option 1).
- **Intake proceeds** (now, not earlier), then implementation, gates, etc.

### Completing the execution

- **If `<plan-id>-execute` shadows `main`:** land-the-plane merges changes into local `main`,
  closes/deletes `<plan-id>-execute`, pushes upstream, and closes the upstream tracking issue(s).
- **If `<plan-id>-execute` shadows `<plan-id>` (feature branch):** the operator chooses:
  - **(a) Push & close local** — push changes upstream to `<plan-id>`, delete the local
    `<plan-id>-execute` branch/worktree, and update the upstream tracking issue with development
    status. The operator can resume later elsewhere, or open a PR to merge the upstream branch later.
    *Likely path when the plan has dependencies/gates needing work or validation that can't be done
    locally — multi-platform testing, manual evaluation on an air-gapped system, etc.*
  - **(b) Push & open a PR to `main`** — push changes upstream to `<plan-id>`, open a PR to merge
    into `main`, update the upstream issue(s) appropriately, and delete the local
    `<plan-id>-execute` branch/worktree.

### Project-config strategy switch

- A project-config option to default the `yf-plan` landing strategy to either **`main`** or
  **`feature-branch`**, with **`main` as the default**.

## Goals / invariants

- **Worktrees are the default place changes happen** — but **avoid inconsistent / double branching**
  (no branch-of-a-branch).
- Predictable, named branches per phase: `<plan-id>-development`, feature `<plan-id>`,
  `<plan-id>-execute`.
- Execute worktrees are pinned to a **known base** (`main` or `<plan-id>`), never "whatever HEAD
  happened to be."
- **Intake happens only at `execute`.**
- The default checkout is returned to a known branch between phases so the next plan doesn't inherit a
  surprising base.
- An upstream tracking issue is always created for execution, with dependency links to any inspiring
  upstream issues.

## Acceptance criteria

- [ ] Planning always runs in a `<plan-id>-development` worktree through the portability check.
- [ ] Plan is always committed after portability passes.
- [ ] Post-plan offers exactly the two options (push to feature `<plan-id>`, or merge to `main`),
      both deleting the local dev worktree/branch.
- [ ] An upstream "Complete execution of `<plan-id>`" tracking issue is created, with dependency
      annotations to inspiring issues when applicable.
- [ ] Intake is deferred to `execute` (no pour during planning).
- [ ] `execute` always creates a `<plan-id>-execute` worktree pinned to the correct base (`main` or
      `<plan-id>`) based on how the plan landed.
- [ ] Completion offers the correct option set depending on whether `<plan-id>-execute` shadows
      `main` or `<plan-id>`.
- [ ] A project-config switch selects `main` (default) vs `feature-branch` strategy.
- [ ] No "branch of a branch of `main`" topology is ever produced; no double merge/push dance.

## References

- Current session (plan-003, `dixson3/blog`): branch-of-a-branch topology + intake-before-execute +
  artifacts/code split across branches.
- Claude session `c4977e90-1c45-4883-aee0-73672826fe29` (plan-002, `dixson3/blog`): worktree branch
  `plan-002-james-dixson-62a38d` shadowing intake branch `plan-002-blog-publishing-intake`, landed via
  a two-step merge to `main`.
- Affected skill: `yf-plan` (`SKILL.md` Phases 1/4/5/6; `scripts/plan_manager.py` `worktree
  ensure|teardown`, `landing-lock`, `update-status`; `formulas/plan-execute.formula.toml`).

