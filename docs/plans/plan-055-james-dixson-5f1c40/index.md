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
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).
- [assets/](assets/) - The measurement record: the §5.2 drive-verify transcript, the migration dry-run JSON, and the Issue 1.1 red baseline.
- [assets/drive-verify-5.2.md](assets/drive-verify-5.2.md) - Drive-verify — Issue 5.2 (SC17 / SC17b evidence)
- [assets/migration-dryrun.json](assets/migration-dryrun.json)
- [assets/red-baseline-1.1.md](assets/red-baseline-1.1.md) - RED baseline — Issue 1.1
- [findings/exp-001-claude-code-agents-root.md](findings/exp-001-claude-code-agents-root.md) - Does claude-code read .agents/skills with no additional configuration? (D-4's hinge)
- [findings/exp-002-pi-opencode-agents-root.md](findings/exp-002-pi-opencode-agents-root.md) - Do pi and opencode load skills from .agents/skills in both scopes, and does pi require its name transform?
- [findings/exp-003-harness-env-vars.md](findings/exp-003-harness-env-vars.md) - What CODEX_HOME / OPENCODE_CONFIG_DIR / XDG_CONFIG_HOME do to each installed harness's skills and config lookup (#238)
- [findings/exp-004-skills-ownership-and-dedup.md](findings/exp-004-skills-ownership-and-dedup.md) - Does an ownership manifest cover the SKILLS surface, and how does install behave on duplicate destinations?
- [findings/exp-005-pi-trust-gate.md](findings/exp-005-pi-trust-gate.md) - What pi does with a skills bundle in an untrusted project directory (#239)
- [findings/exp-006-smoke-state-model.md](findings/exp-006-smoke-state-model.md) - check-harness-smoke.sh's current state model, per-harness consent states, and where the fix belongs
- [findings/exp-007-live-tree-classification.md](findings/exp-007-live-tree-classification.md) - Does a live deployed skill copy actually classify owned-and-unmodified? (pass-2 M7 falsifier)
- [references/upstream-121.md](references/upstream-121.md) - Upstream #121: Pi config tuning re-verification (plan-033 deferral REQ-YF-TUNE-017)
- [references/upstream-238.md](references/upstream-238.md) - Upstream #238: yf ignores XDG_CONFIG_HOME / CODEX_HOME / OPENCODE_CONFIG_DIR when resolving harness directories
- [references/upstream-239.md](references/upstream-239.md) - Upstream #239: pi's project-trust gate is unexercised by any test or smoke
- [references/upstream-240.md](references/upstream-240.md) - Upstream #240: codex budget check models ONE AGENTS.md; codex concatenates several against the same cap
- [references/upstream-243.md](references/upstream-243.md) - Upstream #243: Successor to #154: harness tune OVERWRITES a pre-existing rules aggregate with no backup
- [references/upstream-255.md](references/upstream-255.md) - Upstream #255: Cut the v0.5.0 release: push the tag (deferred from plan-054, everything else staged and green)
- [references/upstream-256.md](references/upstream-256.md) - Upstream #256: check-harness-smoke: the state model is missing 'installed but consent-gated' — codex reaches INCONCLUSIVE for the wrong reason
- [references/upstream-257.md](references/upstream-257.md) - Upstream #257: Deploy skills ONCE to .agents/skills for every harness that reads it; keep only config/hooks/extensions harness-specific
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1 — verdict REVISE, 12 concerns (5 high)
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2 — verdict REVISE, resolution verification plus 17 concerns (8 high)
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3 — verdict REVISE, 12 concerns (2 high); 15 of 17 pass-2 resolutions verified genuine
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4 — verdict REVISE, 13 concerns (1 high); all 12 pass-3 resolutions verified genuine
- [reviews/pass-5.md](reviews/pass-5.md) - Red-team pass 5 — verdict REVISE (bound reached), 5 concerns (1 high); reviewer recommends against a sixth cycle
- [reviews/pass-6.md](reviews/pass-6.md) - Red-team pass 6 — verification pass; verdict REVISE, 3 concerns (1 high); behaviour set confirmed closed
- [reviews/pass-7.md](reviews/pass-7.md) - Red-team pass 7 — verdict APPROVE; C1 independently recomputed and confirmed closed
