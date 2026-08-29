---
okf_version: 0.2
---

# plan-053-james-dixson-4015d3

> Fix the yf-plan execution engine's silent data loss and plan-stranding defects: plan_extract drops detail lines (#206), pour_fidelity.py is unshipped (#210), beads carry no plan_dir (#209), resume-scan reports found on a burned epic (#207), update-status accepts out-of-vocabulary statuses (#208), REQ-PLAN-073 id collision (#214)

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).
- [assets/](assets/) - The driven-red harness and its evidence: `checks/` (the criterion instruments), `controls.txt`, the planted edge-scope mutation, the full-tier record, the deferred-defect list, and `fixtures/` — a deliberate NON-CONFORMANT corpus that is carved out of every OKF walk (#233).
- [findings/](findings/) - The six investigation findings this plan's decisions rest on — the extractor drop, pour-fidelity correctness, the shipped-path class, the status vocabulary, resume-scan's state model, and bead provenance.
- [references/](references/) - One file per triaged upstream issue (#188, #189, #206-#209, #214...), each with the full untruncated body, URL, labels and state, so the upstream context survives without network access.
- [reviews/](reviews/) - Red-team verdicts, one file per review cycle (`pass-1` through `pass-5`), each with its concerns and their per-concern resolutions.
- [scope-answers.md](scope-answers.md) - The filled scoping questionnaire — the operator's answers that set this plan's boundaries, retained because several of them are the only record of why a defect was scoped OUT.
