---
type: Asset
okf_spec: OKF-PLAN
description: "The CHANGE-VALIDATION.md rows Issue 0.5 DRAFTS and Issue 8.4b LANDS at land time, post-merge on main. Drafted here rather than landed because a row naming an in-flight plan directory is structurally unsatisfiable from an execute worktree."
id: change-validation-rows
plan: plan-066-james-dixson-e7fadb
created: 2026-09-05
---
# Drafted `CHANGE-VALIDATION.md` rows — Issue 0.5 drafts, Issue 8.4b lands

**These rows are NOT yet in `CHANGE-VALIDATION.md`, and that is deliberate.**

`CHANGE-VALIDATION.md`'s own §1 banner declares a row reading `docs/plans/<in-flight-plan>/`
**structurally unsatisfiable** from an execute worktree, and the existing `gate-plan049-*` rows
are satisfiable only because those plans have LANDED. Adding them earlier would recreate the
unsatisfiable-row class this repository already removed once. The measured case is plan-060's
`gate-plan060-figures`, which the FULL tier caught mid-execution.

Issue 8.4b lands them **post-merge on `main`**, behind a hard guard: halt unless
`git rev-parse --abbrev-ref HEAD` is `main` AND the plan branch is merged. Nothing else enforces
the timing — 8.4b is an ordinary DAG bead a coordinator would otherwise dispatch inside the
execute address space, and the issue is on the deliberately-uncovered list, so no criterion
would detect a mis-timed run.

## §1 — recipe rows (add to BOTH the FAST and FULL tier tables, as the four-plan precedent does)

| Recipe ID | Command |
| :-- | :-- |
| `gate-plan066-amendment` | `uv run scripts/check_amendment_log.py --plan plan-066-james-dixson-e7fadb` |
| `gate-plan066-reqcoverage` | `uv run scripts/checks/check-req-coverage.py --min-issues 30 docs/plans/plan-066-james-dixson-e7fadb` |
| `gate-plan066-closure` | `uv run scripts/checks/check_drift_manifest_closure.py` |

`gate-plan066-closure` is this plan's Epic-0 tagged test. Unlike the other two it names **no
plan directory**, so it is satisfiable from anywhere and is the one row that could have landed
early — it is grouped here only so the three arrive together.

## §3 — trigger-scope rows

| Changed-Path Glob | Recipes |
| :-- | :-- |
| `docs/plans/plan-066-james-dixson-e7fadb/**` | `okf-index-drift`, `gate-plan066-amendment`, `gate-plan066-reqcoverage` |
| `DRIFT-CHECK.md` | `gate-plan066-closure` |
| `skills/yf-drift-check/spec/**` | `gate-plan066-amendment`, `gate-plan066-closure` |

The existing `SPEC.md` row gains `gate-plan066-amendment`:

| Changed-Path Glob | Recipes (amended) |
| :-- | :-- |
| `SPEC.md` | `gate-plan060-amendment`, `gate-plan062-amendment`, `gate-plan063-amendment`, `gate-plan064-amendment`, `gate-plan064-dualhome`, `gate-plan066-amendment` |

## Why `skills/yf-drift-check/spec/**` is in the §3 set

Issue 0.5's mandate names it explicitly. The Epic-0 amendment lives there, so an edit to the
spec must re-run the amendment-log gate — otherwise a later change to `checks.md` could drop a
`REQ-CHECK-*` id that root `SPEC.md`'s log still claims, and nothing would notice.

## Verification at land time

All three commands are green on this branch as of Issue 0.5:

```
uv run scripts/check_amendment_log.py --plan plan-066-james-dixson-e7fadb          -> exit 0
uv run scripts/checks/check-req-coverage.py --min-issues 30 docs/plans/plan-066-…  -> exit 0
uv run scripts/checks/check_drift_manifest_closure.py                              -> exit 0
```

A green here is **not** evidence the rows are landed — that is exactly the distinction 8.4b
exists to hold. It is evidence the rows will be satisfiable when they are.
