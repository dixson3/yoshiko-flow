---
okf_version: 0.1
---

# plan-038-james-dixson-1ce25a

> Make yf-beads-upstream enforce its own never-hand-run-bd invariant (#106) and add a closable verb closing the write-only gap (#117)

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [references/](references/) - Inlined upstream issue bodies (`upstream-<N>.md`), one per non-excluded Upstream Issues row. Snapshots, not live — the issues this plan addresses.
- [reviews/](reviews/) - Reviewer verdicts (`pass-<N>.md`), one per review cycle. What reviewers flagged and how it was resolved.
- [findings/](findings/) - Investigation experiment results (if any).
- [upstream-triage.md](upstream-triage.md)
- [findings/exp-01-prescriptive-vs-descriptive.md](findings/exp-01-prescriptive-vs-descriptive.md) - Experiment 1: Which `bd <backend>` mentions in SKILL.md are the bug?
- [findings/exp-02-machinery-and-closable-limits.md](findings/exp-02-machinery-and-closable-limits.md) - Experiment 2: What machinery exists, and what `closable` can actually detect
- [findings/exp-03-hoist-separator-defect.md](findings/exp-03-hoist-separator-defect.md) - Experiment 3: Does `hoist` already cover the plain-push case?
- [reviews/pass-1.md](reviews/pass-1.md)
- [reviews/pass-2.md](reviews/pass-2.md)
