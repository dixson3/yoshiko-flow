---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #365 - plan-065-james-dixson-7c8cd4 execution tracking'
---
# Upstream #365: plan-065-james-dixson-7c8cd4 execution tracking

- **Number:** 365
- **Title:** plan-065-james-dixson-7c8cd4 execution tracking
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Coarse tracking issue for **plan-065**, per this repo's one-issue-per-plan convention.

**Plan bundle:** [`docs/plans/plan-065-james-dixson-7c8cd4/`](https://github.com/dixson3/yoshiko-flow/tree/main/docs/plans/plan-065-james-dixson-7c8cd4)

## Objective

Run the yf-okf-hygiene corpus backfill on the repaired engine — the last 8 legacy-readme bundles to
the reserved `index.md` + `log.md` model.

## Upstream dispositions

| Issue | Disposition | Note |
| :-- | :-- | :-- |
| #359 | include | Primary. Carries #316's four acceptance criteria verbatim. |
| #316 | include | Parent; closes with #359. |
| #295 | **partial** | **SC19 only** (these same 8 halts). SC24 is out of scope — #295 stays open. |
| #362, #361, #322 | exclude | Reasoned in the plan's `upstream-triage.md`. |

## Shape

6 epics / 37 issues / 49 edges / 5 gates / 15 success criteria / 10 risks. Four red-team cycles
(pass-4 APPROVE). **The plan changes no engine code** — every defect it finds is filed, not fixed.

## What the review cycles found

Two of the four cycles found defects in the *remediations*, not the original draft:

- **A fourth silent data-loss path in `restore`**, discovered because a pass-1 fix introduced the
  sequence that reaches it. Committing the backfill removes `README.md` from `HEAD`; `restore
  --bundle --apply` then returns `verdict: pass, exit: 0` while leaving the bundle with **no
  README, no index, no log**. Root cause: the `git checkout` at `okf_hygiene.py:1371-1372` has its
  return code **never checked**. Reproduced twice, with a control. Recorded in
  `findings/exp-003-post-commit-restore-loss.md`; filed as one of Epic 6's four defects.
- **The plan-030 halt is a detector artifact, not data loss.** `okf.py:1292` skips the entire log
  reconciliation when a `log.md` already exists, so the transform never moves *or* strips the phase
  log — while the guard compares against a staged `log.md` it did not write.
- **Plan bloat as a defect in itself.** Cycle 3 measured 44 issues with 70% named by no criterion;
  ten one-shot checkers were consolidated into one script with subcommands (37 issues, coverage up).

## Ordering constraints that are load-bearing

- `restore` runs on the **uncommitted** post-apply tree; the commit follows. Post-commit the
  reversal verb is `git revert`, never `restore`.
- Pre-transform data capture precedes every mutating issue — the before-counts and the FALSE
  reports are irrecoverable once Epics 1-2 land.

Execution begins in a separate session per the yf-plan session-boundary rule.

