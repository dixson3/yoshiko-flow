---
type: Finding
okf_spec: OKF-PLAN
description: "Fidelity baseline over plans 060–070 (plan-071 Issue 1.3): 5 of 8 intaken plans flipped a Success Criterion after approval (14 flips: 9 added, 2 amended, 8 FALSE at landing); halts post-L6 are `no-record` for every bundle because the `landing-halt:` bullet postdates them; 4 plans FAIL and 3 are INCONCLUSIVE under `recheck-criteria --timeout 10`"
plan: plan-071-james-dixson-d19ce8
issue: "1.3"
date: 2026-09-12
---
# Fidelity baseline — plans 060 through 070

The first data set for the approval-to-landing fidelity metric (REQ-PLAN-084), derived by
`plan_manager.py retrospective-report --fidelity <plan_dir> --timeout 10 --json` over every
bundle from plan-060 to plan-070 on 2026-09-12, at commit `62f6b23` of the
`plan-071-james-dixson-d19ce8-execute` branch. Nothing was recorded into any bundle's
retrospective (`--record` was not passed); this file is the record.

**How to read the columns.**

- **Approval commit** — the latest commit whose subject is `<plan-id>: INTAKE approved (awaiting
  /yf-plan execute)`, found by `git log --grep`. `none` means the plan was never intaken through
  `commit-plan` and the `Verification` diff has no baseline; the flip count is then `no-record`.
- **SC flipped** — rows whose `Verification` cell differs between the approval commit and the
  working `plan.md` (`amended`, `converted-to-manual`, `added-after-approval`,
  `removed-after-approval`), plus rows the fresh `recheck-criteria` run reports FALSE
  (`false-at-landing`). A row counted under both is counted once.
- **Halts post-L6** — `- landing-halt:` bullets in `log.md` at or after `L_PUSHED_1`. **Every
  bundle here predates the bullet** (it is written by `land --apply` from plan-071 Issue 1.2
  onward), so every cell is `no-record`, never a zero. The retrospectives of 062, 063 and 068
  narrate post-push halts in prose, but prose is not the instrument this column reads.
- **recheck verdict** — the EXP-002 rot signal, re-measured: `recheck-criteria --advisory
  --timeout 10` on today's tree. `FAIL` means a criterion that was green at discharge is FALSE
  now (rot vs. noise is **not adjudicated here** — that is a later plan's question).
  `INCONCLUSIVE` means no clause-form criterion existed to run.
- **Source** — which artifact each number came from.

| Plan | Approval commit | SC flipped | Halts post-L6 | recheck verdict | Source | Detail |
| :-- | :-- | --: | :-- | :-- | :-- | :-- |
| plan-060-james-dixson-6a6ac9 | `4480739c4e5b` | 0 | no-record | PASS | no-record / intake commit | — |
| plan-061-james-dixson-6d8c97 | `e5d1135d6857` | 1 | no-record | PASS | no-record / intake commit | SC6 (amended) |
| plan-062-james-dixson-c3e98f | `a019b4187e7f` | 2 | no-record | FAIL | no-record / intake commit | SC0b (false-at-landing), SC13 (false-at-landing) |
| plan-063-james-dixson-3f74c1 | `89778b6e0269` | 3 | no-record | FAIL | no-record / intake commit | SC0 (false-at-landing), SC2 (false-at-landing), SC9 (false-at-landing) |
| plan-064-james-dixson-a0b7fa | `f0dcb6a61103` | 1 | no-record | FAIL | no-record / intake commit | SC5 (false-at-landing) |
| plan-065-james-dixson-7c8cd4 | `b9486e1b949d` | 3 | no-record | FAIL | no-record / intake commit | SC10 (amended), SC3 (false-at-landing), SC12 (false-at-landing) |
| plan-066-james-dixson-e7fadb | `19921edb941d` | 0 | no-record | PASS | no-record / intake commit | — |
| plan-067-james-dixson-de852a | `114286a3f91c` | 9 | no-record | PASS | no-record / intake commit | SC27b (added-after-approval), SC27c (added-after-approval), SC28 (added-after-approval), SC29 (added-after-approval), SC30 (added-after-approval), SC31 (added-after-approval), SC32 (added-after-approval), SC33 (added-after-approval), SC34 (added-after-approval) |
| plan-068-james-dixson-8ae0e1 | `1e34f72fd442` | 0 | no-record | INCONCLUSIVE | no-record / intake commit | 16 rows, 0 clause-form (prose `Verification` cells) |
| plan-069-james-dixson-9d2878 | `none` | no-record | no-record | INCONCLUSIVE | no-record / no intake commit | no `## Success Criteria` table; seeded by plan-068, never intaken |
| plan-070-james-dixson-810177 | `none` | no-record | no-record | INCONCLUSIVE | no-record / no intake commit | 15 rows, 0 clause-form; deferred by operator decision, never intaken |

## Totals

| Measure | Value |
| :-- | --: |
| Bundles measured | 11 |
| Bundles with an intake commit | 8 |
| Bundles with ≥ 1 flip | 5 of 8 |
| Flips, total | 14 (9 added-after-approval, 2 amended, 8 false-at-landing; 5 overlap-free) |
| Bundles FALSE at `--timeout 10` | 4 (062, 063, 064, 065) |
| Bundles INCONCLUSIVE | 3 (068: prose criteria; 069: no table; 070: prose criteria, deferred) |
| Halts post-L6 with a mechanical record | 0 of 11 (`no-record` everywhere) |

## What this baseline does and does not establish

- **measured:** the flip count is real and reproducible from `git show <commit>:plan.md`; the
  commands above regenerate every row.
- **measured:** plan-067's nine flips are all `added-after-approval` — criteria SC27b–SC34 were
  appended to the table after intake. Whether that was an amendment under review or a silent
  widening is not visible from the diff; it is visible from `reviews/pass-*.md` and is left to
  adjudication.
- **inferred:** the `false-at-landing` rows are the EXP-002 rot signal. Four plans' criteria are
  FALSE today; they were green at the issue that discharged them. The baseline does not say
  which are regressions and which are criteria that asserted world state (#358).
- **absence is the finding for the halts column:** no bundle in this range can report
  `halts_post_irreversible` as a number. The metric's second number starts being recorded with
  this plan's own landing (D-6).
