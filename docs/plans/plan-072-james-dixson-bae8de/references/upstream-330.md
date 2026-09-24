---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #330 - plan-062-james-dixson-c3e98f execution tracking'
---
# Upstream #330: plan-062-james-dixson-c3e98f execution tracking

- **Number:** 330
- **Title:** plan-062-james-dixson-c3e98f execution tracking
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Coarse tracking issue for **plan-062-james-dixson-c3e98f**.

- **Plan:** [`docs/plans/plan-062-james-dixson-c3e98f/`](https://github.com/dixson3/yoshiko-flow/tree/main/docs/plans/plan-062-james-dixson-c3e98f)
- **Fingerprint:** `3d9a163b…`
- **Landed at:** `794cc2d` (merge), `a019b41` (plan bundle)

## What it does

Wires `land --apply` to the fully-implemented-but-uncalled `_land_execute` (**#327**), and fixes
the `_land_execute` resume no-op that wiring would otherwise make reachable.

**The resume fix lands FIRST.** Ordering is not atomicity: seam-first would leave a window in
which `--apply` works and a resume still re-executes `l6_push_one` and `l7_reconcile_writes` —
measured in a sandbox as re-running all fifteen steps from L0, re-posting every reconcile comment.
The resume fix is inert until something calls the engine, so resume-first has no such window.

## Scope, deliberately narrow

Narrowed by operator decision after red-team pass 4. **Only two defects are fixed.** Everything
else these passes surfaced is filed rather than fixed (Issue 5.1):

| | |
| :-- | :-- |
| **#326** | `draft_body_path` vs OKF frontmatter — re-labelled `deferred`; the complete verified fix design, with a 7/7 spike, is preserved in `findings/exp-003` |
| new | `land` is incompatible with `execute.worktree: false` — no execute branch is created, so `--dry-run` halts `execute-branch-missing` |
| new | `assets/upstream-drafts/` is undocumented in every yf-plan `.md` (zero grep hits outside `plan_manager.py:7936`) |
| new | a decision file written inside the tree halts the landing at L16, past the irreversible boundary |
| new | `allow_list=[None]` opens the tty gate unconditionally; its test at `:384` is vacuous |

Also carried as `partial`: **#266** (the `## Gates` grammar cannot express `test_class`/`cwd` —
worked around at pour, not closed) and **#304** (the self-authorization residue — design input,
stays open).

## Review record

**Seven red-team passes, 57 concerns**, all resolved. The most transferable finding is about
authoring rather than about `land`: **in four of five middle rounds, a fix for a vacuity concern
introduced a new vacuity.** An escaped pipe that made a regex match nothing; an unescaped one that
made a criterion parse as prose and never be evaluated; a gate hoist that recreated the cycle it
was fixing; a `--all` that converted a guaranteed false-fail into a permanent true. Every one was
silent, and every one was caught by re-extracting and re-running the criteria rather than by
reading them.

A related near-miss: a reviewer's line-number "correction" was applied without re-measurement and
would have instructed the implementing issue to delete the tty gate's `sys.exit(3)`.

## Execution precondition

This plan **must** execute with `execute.worktree: false`, written **before** `/yf-plan execute`
is invoked — `_land_assert_primary_checkout` refuses any cwd but the primary, which under worktree
mode still carries the stub. Issue 0.7 then creates the execute branch explicitly, because
in-place mode alone leaves `land` with no branch to merge.

