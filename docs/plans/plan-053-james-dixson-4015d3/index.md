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
- [findings/exp-001-extractor-drop-fix.md](findings/exp-001-extractor-drop-fix.md) - EXP-001: can #206 be fixed without breaking the masking invariant?
- [findings/exp-002-pour-fidelity-correctness.md](findings/exp-002-pour-fidelity-correctness.md) - Is pour_fidelity.py correct before we ship it? The join is sound; --strict has three silent-pass holes
- [findings/exp-003-shipped-path-class.md](findings/exp-003-shipped-path-class.md) - Sizing the unshipped-script-path class and designing the check that closes it
- [findings/exp-004-status-vocabulary.md](findings/exp-004-status-vocabulary.md) - The 16-site change-set for adding a plan status, why `incomplete` is disqualified, and the vacuous drift edge that was supposed to protect it
- [findings/exp-005-resume-scan-state-model.md](findings/exp-005-resume-scan-state-model.md) - The resume-scan tri-state and clear-epic verb — the bd check already exists, SKILL.md just never reads it, and there are six states not three
- [findings/exp-006-bead-provenance.md](findings/exp-006-bead-provenance.md) - Both
- [findings/exp-007-req-plan-073-collision.md](findings/exp-007-req-plan-073-collision.md) - Which side of the REQ-PLAN-073 collision to renumber, measured by live citation count
- [references/upstream-188.md](references/upstream-188.md) - Upstream #188: Test suites assert output STRUCTURE and never payload FIDELITY — the blind spot #186/#187 lived in
- [references/upstream-189.md](references/upstream-189.md) - Upstream #189: Six shipped scripts have no tests at all — including two CHANGE-VALIDATION checks and the beads repair engine
- [references/upstream-206.md](references/upstream-206.md) - Upstream #206: CRITICAL: plan_extract.py still silently drops detail lines — inline-code-only continuations and fenced blocks vanish with unparsed: 0 (same family as #186/#187)
- [references/upstream-207.md](references/upstream-207.md) - Upstream #207: resume-scan reports found: true for a BURNED epic, making the plan permanently unpourable (both SKILL.md 5.2 branches dead-end)
- [references/upstream-208.md](references/upstream-208.md) - Upstream #208: update-status accepts out-of-vocabulary statuses silently — strands the plan AND relaxes doc_lint (STATUS_SEVERITY fails open)
- [references/upstream-209.md](references/upstream-209.md) - Upstream #209: Issue beads carry no plan_dir, so poured descriptions cite EXP-NNN / SC-N evidence an executor cannot locate (21 of 35 in one plan)
- [references/upstream-210.md](references/upstream-210.md) - Upstream #210: pour_fidelity.py is not shipped to the skill dir — SKILL.md 6.4's completion fidelity gate is unrunnable in every repo but this one
- [references/upstream-214.md](references/upstream-214.md) - Upstream #214: yf-plan: `REQ-PLAN-073` id collision — two different requirements share one id
- [references/upstream-231.md](references/upstream-231.md) - The coarse upstream tracking issue for plan-053
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1 (independent, via Agent) — REVISE, 14 concerns, 6 high
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2 (second independent, via Agent) — REVISE, 15 concerns, 6 high; 9 of 14 pass-1 resolutions reproduced by execution
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3 (third independent, via Agent) — REVISE, 14 concerns, 4 high; 9 of 15 reproduced, and three failures were re-broken by pass-2's own remedies
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4 (fourth independent, via Agent) — REVISE, 10 concerns, 2 high; 7 of 14 reproduced (50%), and pass-3's structural remedy was itself applied site-by-site
- [reviews/pass-5.md](reviews/pass-5.md) - Red-team pass 5 (fifth independent, CONFIRMING) — APPROVE; 9 of 10 reproduced (90%), six of six verification commands pass
