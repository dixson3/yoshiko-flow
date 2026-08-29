---
okf_version: 0.1
---

# plan-040-james-dixson-1cabe4

> Replace bd-backend push with gh-direct issue creation across push/hoist/land, and close the coarse-tracker visibility gap

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [references/](references/) - Inlined upstream issue bodies (`upstream-<N>.md`), one per non-excluded Upstream Issues row. Snapshots, not live — the issues this plan addresses.
- [reviews/](reviews/) - Reviewer verdicts (`pass-<N>.md`), one per review cycle. What reviewers flagged and how it was resolved.
- [findings/](findings/) - Investigation experiment results (if any).
- [upstream-triage.md](upstream-triage.md)
- [findings/exp-001-label-mapping-gap.md](findings/exp-001-label-mapping-gap.md) - Finding: What does gh-direct actually have to reimplement, and is "~20 lines" right?
- [findings/exp-002-closable-n-plus-1.md](findings/exp-002-closable-n-plus-1.md) - Finding: `closable` never completes at this repo's scale, and the cause is a removable N+1
- [reviews/pass-1.md](reviews/pass-1.md) - Plan Red-Team: plan-040-james-dixson-1cabe4
- [reviews/pass-2.md](reviews/pass-2.md) - Plan Red-Team: plan-040-james-dixson-1cabe4
- [reviews/pass-3.md](reviews/pass-3.md) - Plan Red-Team: plan-040-james-dixson-1cabe4
