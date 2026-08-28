---
okf_version: 0.2
---

# plan-055-james-dixson-5f1c40

> Deploy skills once to the shared .agents/skills root for every harness that reads it; keep only config/hooks/extensions/rules harness-specific

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/](findings/) - Seven investigation write-ups (EXP-001 … EXP-007), each measured against installed binaries with versions pinned and a Confidence section separating **measured** from **inferred**. The evidence behind every scoping decision in plan.md.
- [references/](references/) - One file per triaged upstream issue, carrying the full untruncated body, URL, labels and state. Regenerated on every re-triage; do not hand-edit.
- [reviews/](reviews/) - One `pass-N.md` per red-team cycle, each with its verdict, concerns and a Resolutions table. Written at presentation, updated in place, then frozen.
