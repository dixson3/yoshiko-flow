---
okf_version: 0.2
---

# plan-051-james-dixson-2f499f

> Land the descoped plan-050 work: the red-team sandbox-spike rule (#182), sub-agent dispatch for review (#184), and M9 remediation-edge attribution (#149) — each from plan-050's measured evidence

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [reviews/](reviews/) - The red-team review records, one per cycle, each with its Concerns table and resolutions. The review history behind the plan's current shape.
- [findings/](findings/) - The five investigation records this plan's decisions rest on. EXP-001 (what #184's Verification can honestly assert), EXP-002 (#182's 7-file blast radius), EXP-003 (executable-Verification prior art), EXP-004 (control-harness reuse, and the refutation of plan-050's D-8), EXP-005 (the review wisp: buildable, unevidenced).
- [references/](references/) - Full untruncated bodies of the eleven candidate upstream issues, so a cold reader can judge each disposition without network access.
