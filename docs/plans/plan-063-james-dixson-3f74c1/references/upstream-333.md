---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #333 - A decision file written inside the tree halts
  the landing at L16, past the irreversible boundary'
---
# Upstream #333: A decision file written inside the tree halts the landing at L16, past the irreversible boundary

- **Number:** 333
- **Title:** A decision file written inside the tree halts the landing at L16, past the irreversible boundary
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

## What

`land --apply <decision.json> <plan_dir>` accepts any path for the decision document. If that
path is **inside the repository tree** and outside `<plan_dir>`, it is an untracked file that
`_land_l16_commit_and_push_two` never stages (it runs `git add -- <plan_dir>` only), so L16's
**post-condition** — `git status --porcelain` clean — fails and the step halts.

## Why it matters

**L16 is past the irreversible boundary.** By the time it runs:

- L6 has pushed (`L_PUSHED_1`),
- L7 has posted the reconcile comments (`L_RECONCILED`),
- L12 has closed the bead tree, L15 has written `status: complete` (`L_CLOSED`).

L16's own docstring states the contract as **retry-after-rebase, NEVER REVERT**, because
reverting would contradict outward statements already made. So the operator is left mid-
landing, with public writes already performed, halted on a file they were never told to put
somewhere specific.

The failure is entirely avoidable and is caused by an argument the CLI accepts without
comment.

## Suggested fix

Refuse **at the top of `--apply`**, before the tty gate and before any write: if the decision
path resolves inside the repository worktree, halt with `halt_class` mechanical and the
remediation "write the decision document outside the tree (e.g. under `$TMPDIR`)". A pre-write
refusal costs nothing; the same condition discovered at L16 is expensive and public.

Note this is cheap to check and cheap to test — `Path.resolve().is_relative_to(repo_root)`.

Found while executing plan-062 (`docs/plans/plan-062-james-dixson-c3e98f`). The plan's own
seam tests write their decision to `tmp_path` for exactly this reason, with the constraint
recorded in a comment — which is documentation of a trap rather than removal of it.

