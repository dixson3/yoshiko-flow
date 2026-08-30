---
okf_version: 0.2
---

# plan-060-james-dixson-6a6ac9

> Plan-landing capability: a plan_manager.py land verb (--dry-run enumerates facts, --apply <decision.json> is the only writer) plus a read-only lander agent producing a decision document, so authorizing merge-back authorizes the whole landing in one informed consent grant

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/exp-001-cli-surface.md](findings/exp-001-cli-surface.md) - EXP-001 — the plan_manager.py CLI surface a land verb must slot into: verb inventory, exit-code contract, verdict envelope, and the measured absence of any merge or push code.
- [findings/exp-002-spec-surface.md](findings/exp-002-spec-surface.md) - EXP-002 — the SPEC-first surface: REQ-prefix ownership, next-free ids, the living amendment log, requirement anatomy, the coverage gate, and the read-only agent template.
- [findings/exp-003-landing-tooling.md](findings/exp-003-landing-tooling.md) - EXP-003 — inventory of the tooling land must call: yf-beads-upstream, the reconcile contract, the FULL tier, the redeploy consent gate, herdr teardown, and the strongest prior art.
- [findings/exp-004-landing-order.md](findings/exp-004-landing-order.md) - EXP-004 — the landing order. Measured: neither SKILL.md's Phase 6 nor issue #301's six-step order is correct, and no single-push order satisfies all four constraints.
- [assets/decision-schema.md](assets/decision-schema.md) - Draft schema for the landing manifest and the landing decision document — the two data structures carrying the three-layer split.
- [findings/exp-005-consent-model.md](findings/exp-005-consent-model.md) - EXP-005 — the consent model. Measured: no purely local artifact is unmintable, and #301's structural claim is overstated.
- [references/](references/)
- [diagrams/landing-three-layers.png](diagrams/landing-three-layers.png) - Diagram: the three-layer landing split — facts, judgement, execution — and where the session stops.
- [diagrams/landing-three-layers.d2](diagrams/landing-three-layers.d2) - d2 source for the three-layer landing diagram.
- [findings/exp-006-conflict-handling.md](findings/exp-006-conflict-handling.md) - EXP-006 — apply-path conflict behaviour, measured: a clean preview does not guarantee a clean apply, and the manifest digest already detects the drift.
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1 — REVISE, 14 concerns (3 high), all resolved in place.
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2 — REVISE (narrowly), 11 concerns (2 high), all resolved in place.
- [assets/criteria-validation.md](assets/criteria-validation.md) - Execution record for every criterion whose command exists today, run under bash -c.
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3 — REVISE (narrowly), 7 concerns, zero high, all resolved in place.
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4 — REVISE, one high (tracked-blindness), all 5 concerns resolved.
- [reviews/pass-5.md](reviews/pass-5.md) - Red-team pass 5 — REVISE, one high (the enumeration fix was itself gitignore-blind), all 4 resolved.
- [escalations.md](escalations.md) - Open questions raised to the upstream controller during execution (`## ESC-NNN` entries), each with its alternatives, its recommended default, and what happens if no answer arrives. PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding of any severity (REQ-PORT-ACT-ESCALATION).
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).
- [reviews/pass-6.md](reviews/pass-6.md) - Red-team pass 6 — REVISE, one high (--others is a tracked-ness filter), all 6 resolved.
- [assets/enumeration-spike.md](assets/enumeration-spike.md) - EXP-007 — the enumeration spike: every candidate against a fixture holding both tracked-ness states inside and outside a gitignored worktree, from both cwds.
- [reviews/pass-7.md](reviews/pass-7.md) - Red-team pass 7 — APPROVE, no high; six prose concerns all resolved.
