---
okf_version: 0.1
---

# plan-046-james-dixson-aabefa

> OKF group — reconcile OKF-BASELINE to v0.2 (#141), make bundle index structure generated rather than asserted (#140, retargeted at the bundle root), reconcile #92 as superseded with named carve-outs, and fix the stale plan-folder orientation docs (#118).

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [references/](references/) - Inlined upstream issue bodies (`upstream-<N>.md`), one per non-excluded Upstream Issues row. Snapshots, not live — the issues this plan addresses.
- [reviews/](reviews/) - Reviewer verdicts (`pass-<N>.md`), one per review cycle. What reviewers flagged and how it was resolved.
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/](findings/) - The four investigation experiments. **exp-003 refuted the originally-approved nested-index backfill and exp-004 weakened the #92 supersede** — read these before trusting plan.md's scope.
- [assets/](assets/) - Attachments and other generated artifacts (not diagrams — those live in `diagrams/`).
- [plan-retrospective.md](plan-retrospective.md)
