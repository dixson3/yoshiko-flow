---
okf_version: 0.2
---

# plan-065-james-dixson-7c8cd4

> Run the yf-okf-hygiene corpus backfill on the repaired engine — 8 legacy-readme bundles to the reserved index.md + log.md model

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/exp-001-objective-divergence-classification.md](findings/exp-001-objective-divergence-classification.md) - exp-001 - does adopting plan.md H1 discard real information across the 7 objective-divergence bundles
- [findings/exp-002-plan-030-phase-log-loss.md](findings/exp-002-plan-030-phase-log-loss.md) - exp-002 - plan-030 phase-log-loss is a detector artifact, and the repair is the move migrate skipped
- [references/upstream-295.md](references/upstream-295.md) - Upstream issue #295 - plan-057 follow-on: 8 unresolved backfill halts (SC19) and 4 ungranted reconcile comments (SC24)
- [references/upstream-316.md](references/upstream-316.md) - Upstream issue #316 - Plan 2/3: run the yf-okf-hygiene corpus backfill — 8 legacy-readme bundles to the reserved index.md + log.md model
- [references/upstream-322.md](references/upstream-322.md) - Upstream issue #322 - docs yf-okf-hygiene SKILL.md: the "31 legacy, 7 halt" figure reads as repo-agnostic and mis-sized a real plan 3.5x
- [references/upstream-359.md](references/upstream-359.md) - Upstream issue #359 - Plan 2/3 (part 2): run the yf-okf-hygiene corpus backfill — 8 legacy-readme bundles, on the repaired engine
- [references/upstream-361.md](references/upstream-361.md) - Upstream issue #361 - plan_extract.py --strict validates neither self-edges nor cycles in the plan DAG
- [references/upstream-362.md](references/upstream-362.md) - Upstream issue #362 - yf-okf-hygiene: the _index.md legacy-variant transform route manufactures a hybrid under the yf-plan member
- [findings/exp-003-post-commit-restore-loss.md](findings/exp-003-post-commit-restore-loss.md) - exp-003 - restore --apply after the backfill is committed causes silent total loss, a fourth data-loss path
- [reviews/pass-1.md](reviews/pass-1.md) - Review pass-1 - plan-065 red-team, verdict REVISE, 14 concerns
- [reviews/pass-2.md](reviews/pass-2.md) - Review pass-2 - plan-065 red-team cycle 2, verdict REVISE, 16 concerns, one high-severity data-loss path introduced by pass-1 remediation
- [reviews/pass-3.md](reviews/pass-3.md) - Review pass-3 - plan-065 red-team cycle 3, verdict REVISE, 15 concerns, no high; plan size flagged as a risk in itself
- [reviews/pass-4.md](reviews/pass-4.md) - Review pass-4 - plan-065 red-team cycle 4, verdict APPROVE, 10 concerns none high, converged
