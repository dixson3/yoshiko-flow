---
okf_version: 0.2
---

# plan-054-james-dixson-535968

> Release readiness for yf v0.5.0: SKILL_DIR harness resolution, shipped silent-failure defects, changelog reconstruction, doc+website accuracy, and a pi/opencode regression

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/](findings/) - The six investigation write-ups (EXP-001..EXP-006). Three refuted or corrected a scoping premise; plan.md's Investigation Findings table summarises them and cites each by id.
- [references/](references/) - Full, untruncated bodies of every triaged upstream issue, one file per issue. Regenerated on re-triage; do not hand-edit.
- [reviews/](reviews/) - Red-team pass reports, one per review cycle, each frozen once its concerns are resolved. The verdict history behind the plan's readiness.
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).

- [assets/](assets/) - The driven-red harness and its records: `checks/` (the criterion instruments this repo later promoted to `scripts/checks/`), the allowlist with per-entry reasons, `controls.txt`, the harness smoke transcript, the deferred-defect list, and `fixtures/`.
- [findings/exp-001-yf-skill-dir-design.md](findings/exp-001-yf-skill-dir-design.md) - EXP-001 — design probe for a top-level `yf skill-dir <name>` lookup
- [findings/exp-002-live-harness-walk.md](findings/exp-002-live-harness-walk.md) - EXP-002 — do yf skills actually load and run inside real pi and opencode sessions?
- [findings/exp-003-opencode-config-precedence.md](findings/exp-003-opencode-config-precedence.md) - EXP-003 — does opencode read the opencode.json yf writes, or the operator's opencode.jsonc?
- [findings/exp-004-changelog-reconstruction.md](findings/exp-004-changelog-reconstruction.md) - EXP-004 — can the v0.5.0 CHANGELOG be reconstructed mechanically from the plan bundles?
- [findings/exp-005-stale-issue-verification.md](findings/exp-005-stale-issue-verification.md) - EXP-005 — do the six apparently-delivered issues' deliverables actually satisfy their asks?
- [findings/exp-006-symlink-revert-spike.md](findings/exp-006-symlink-revert-spike.md) - EXP-006 — does `yf harness tune --revert` behave correctly through symlinks into a git-tracked dotfiles repo?
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1 (first independent, dispatched via Agent) — plan-054
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2 (second independent, via Agent) — plan-054
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3 (third independent, via Agent) — plan-054
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4 (fourth independent, via Agent) — plan-054
- [reviews/pass-5.md](reviews/pass-5.md) - Red-team pass 5 (fifth independent, via Agent) — plan-054; loop bound reached
- [reviews/pass-6.md](reviews/pass-6.md) - Red-team pass 6 (sixth independent, via Agent) — plan-054; APPROVE
