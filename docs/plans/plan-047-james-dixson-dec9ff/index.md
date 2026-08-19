---
okf_version: 0.2
---

# plan-047-james-dixson-dec9ff

> Make yf artifact documents mechanically parseable: formal templates per document type, per-type linters, a corpus normalizer, and a common plan extractor that machine-reads the epic/issue DAG

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/](findings/) - The six investigation findings (EXP-001…006). **Every measured figure the plan cites originates here**, each with its reproduction command. Read these before trusting any number in plan.md.
- [references/](references/) - Full untruncated bodies of the 11 triaged upstream issues, plus drafted upstream comments (`comment-*.md`) awaiting the Upstream-write gate. The only in-bundle copies of the upstream context.
- [reviews/](reviews/) - Red-team pass records, newest last. Each carries its verdict, concerns with severity, and an Operator Resolutions table filled as each concern is resolved.
