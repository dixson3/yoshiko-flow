---
type: Note
okf_spec: OKF-PLAN
description: "SECOND HALT. plan-066's close chain now clears verify-reconcile but stops at close-reconcile-step, because Issue 8.4b is open and its hard guard requires HEAD on main. Nothing forced; the decision is the operator's."
id: halt-2-plan066-8-4b
plan: plan-066-james-dixson-e7fadb
created: 2026-09-09
---
# HALT 2 — plan-066 cannot reach `complete` on this branch, by its own design

**The first halt is cleared.** `verify-reconcile` returns **PASS, 7 of 7**. Issue 8.5 is closed.

The chain now stops one step later, at **`close-reconcile-step` (exit 1)**:

> the reconcile gate `yf-mol-a927.14` is not resolved — §6.4's gate-before-close ordering
> constraint (`REQ-COMPLETE-004`) forbids closing the reconcile bead against incomplete execution

## The single root cause

**Issue 8.4b (`yf-mol-a927.9.5`) is open**, so the reconcile gate — *auto, all execution beads
closed* — cannot resolve. It is the only remaining execution bead.

8.4b adds the `gate-plan066-amendment` and req-coverage rows that Issue 0.5 drafted, and it
carries a **HARD GUARD** (pass-4 C2):

> halt unless `git rev-parse --abbrev-ref HEAD` is `main` **AND** the plan branch is merged.

Measured against that guard, right now:

| Clause | State |
| :-- | :-- |
| the plan branch is merged | **TRUE** — `plan-066-james-dixson-e7fadb-execute` is in `git branch --merged main`, and plan-066's bundle and commits are on `main` |
| `HEAD` is `main` | **FALSE** — `HEAD` is `plan-067-james-dixson-de852a-execute`, 24 ahead of `main`, 0 behind |

**So plan-066 completes at LAND, not before. That is not a defect — it is what 8.4b says.**

## One fact that complicates it, stated because it cuts toward acting

The guard's *rationale* is about **worktrees**: the rows name `docs/plans/plan-066-*/`, which
`CHANGE-VALIDATION.md` declares structurally unsatisfiable from a worktree, with plan-060's
`gate-plan060-figures` as the measured case.

**We are not in a worktree.** `git rev-parse --git-dir` returns `.git` — this is the primary
checkout, and `execute.worktree` is `false` for this project. plan-066's bundle is present both on
`main` and in this tree, so the rows would be **satisfiable** if added here.

## Two resolutions, and I am not choosing between them

**A — land first, then run 8.4b on `main`.** Merge plan-067's branch, run 8.4b there, and
plan-066's chain clears. Cost: plan-067's work reaches `main` **before** plan-066 reads
`complete`, inverting the requested sequence (plan-066 → `#372` → plan-067 → `#379`). Nothing
stated forbids it, but it is a real reordering and the tracker rule still holds — `#372` and
`#379` stay shut until their own plans complete.

**B — run 8.4b now, on the grounds that its purpose is met.** The satisfiability hazard the guard
exists to prevent is genuinely absent here.

**The honest warning about B**, since it is the tempting one: *"the purpose is satisfied, so the
literal condition need not hold"* is precisely the reasoning a hard guard exists to resist. Pass-4
C2 made this guard hard on the observation that **no criterion would detect a mis-timed run** —
8.4b is on the deliberately-uncovered list. Reasoning past it here would be safe on the facts and
would also be the exact habit that makes the next guard easier to reason past.

That is why this is reported rather than decided.

## What is done, and what is untouched

Done: 8.5 closed, `Resolved By` filled on all seven rows, `verify-reconcile` PASS 7/7, and the
three advisory observers clean (`audit-close` pass, retrospective present, judgement-report pass).

Untouched: **nothing posted this turn.** `#372` and `#379` remain OPEN; plan-066 and plan-067 both
remain `executing`; 8.4b is open and **not** force-closed.

One note for whoever resumes: `classify-deliverable` re-run on the merged-tree paths suggests
`ci-release` on **`prose-only`** evidence at **low** confidence. That is the documented
self-reference case — a plan whose subject is validation recipes matches those keywords in its own
prose — so the stored `standard` class was **not** changed. `evidence: path-backed` is the only
combination that carries weight here, and it did not occur.
