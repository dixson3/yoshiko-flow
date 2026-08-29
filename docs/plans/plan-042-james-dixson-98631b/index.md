---
okf_version: 0.1
---

# plan-042-james-dixson-98631b

> Install-time sync: make yf self install and yf self update deploy skills, rules, and harness config, with a consent-safe split between the idempotent half and the permissions-bearing half (split from plan-041)

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [references/](references/) - Inlined upstream issue bodies (`upstream-<N>.md`), one per non-excluded Upstream Issues row. Snapshots, not live — the issues this plan addresses.
- [reviews/](reviews/) - Reviewer verdicts (`pass-<N>.md`), one per review cycle. What reviewers flagged and how it was resolved.
- [findings/](findings/) - Investigation experiment results (if any).
- [findings/exp-001-self-install-paths.md](findings/exp-001-self-install-paths.md) - E1 — What `yf self install` actually does today
- [findings/exp-004-harness-tune-safety.md](findings/exp-004-harness-tune-safety.md) - E4 — Is `yf harness tune` safe to auto-invoke?
- [findings/exp-005-upgrade-vs-install.md](findings/exp-005-upgrade-vs-install.md) - E5 — `skills upgrade` vs `skills install` for the shared sync
- [references/upstream-157.md](references/upstream-157.md) - Upstream #157 — plan-042 execution tracking: install-time sync
- [reviews/pass-1.md](reviews/pass-1.md) - Review pass 1 — adversarial (red-team)
- [reviews/pass-2.md](reviews/pass-2.md) - Review pass 2 — adversarial (red-team)
- [reviews/pass-3.md](reviews/pass-3.md) - Review pass 3 — adversarial (red-team)
