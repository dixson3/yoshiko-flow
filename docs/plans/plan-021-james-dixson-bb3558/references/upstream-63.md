# Upstream #63: yf-plan: always commit intake state before offering the plan for execution

- **Number:** 63
- **Title:** yf-plan: always commit intake state before offering the plan for execution
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Proposal

`yf-plan` Phase 4 (INTAKE) should **commit the intake state automatically** as its final step — before the Phase 4.8 handoff that tells the operator to run `/yf-plan execute` in a new session. Today intake leaves the plan folder and `AGENTS.md`/other edits as uncommitted working-tree changes; the operator must remember to commit (or ask), and a fresh execute session inherits a dirty tree.

## Motivation

- **Clean handoff invariant.** Phase 5 (EXECUTE) runs in an isolated git worktree by default and re-attaches on resume; a dirty base tree at handoff muddies the worktree's starting point and the §5.2 dirty-state detection. Committing at end-of-intake gives execute a clean, known base commit.
- **Portability / cold-resume.** The plan folder is meant to be self-contained and resumable from a different session or machine. If intake artifacts (plan.md status `approved`, `reviews/pass-N.md`, the epic linkage in plan.md) live only in an uncommitted tree, a crash or a new clone loses them. A commit is the durable boundary.
- **Observed this session:** intake produced `docs/plans/<id>/` + an `AGENTS.md` rule edit, left uncommitted; the operator had to explicitly ask to commit before execution. That manual step should be the default.

## Scope to investigate

- Where in Phase 4 the commit belongs (after 4.7 burn-wisp, before 4.8 handoff) and the commit-message convention (reuse the `plan-NNN: intake — <objective>` form).
- **Git authority boundary.** yf-plan's stated git authority is *conservative* — it reports a handoff and does not push without authorization. A local **commit** (no push) is a weaker action than a push; confirm that auto-commit-at-intake is consistent with that stance, or make it a confirm-required step. (Recommendation: auto-commit local, never auto-push — the push stays operator-authorized at Phase 6.2.)
- **What to stage.** Plan folder always; but intake sometimes touches sibling files (e.g. an `AGENTS.md` rule, a `CLAUDE.md` index). Decide whether the auto-commit scopes to `<plan_dir>/` only (safest) or a reviewed set, to avoid sweeping unrelated working-tree edits into the intake commit.
- **Beads DB.** The `.beads/*.jsonl` export is gitignored (Dolt-tracked); the beads side commits/pushes via `bd dolt` at land-the-plane, not here. Confirm the git auto-commit and the bd side stay decoupled.
- **Branch.** Whether intake should also ensure it is on a non-default branch first (this repo's convention: never commit intake directly to `main`).
- **Idempotency / dirty-tree handling.** Behavior when the tree already has unrelated uncommitted changes, or when re-running intake.

## Context

- Precedent: plan-019 intake, committed on branch `plan-019-intake` after this was raised.
- Related: the SPEC-first rule added to `AGENTS.md` this session; the `yf-spec` skill proposal (#62).
