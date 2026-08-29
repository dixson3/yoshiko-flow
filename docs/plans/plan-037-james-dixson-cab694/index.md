---
okf_version: 0.1
---

# plan-037-james-dixson-cab694

> Reconcile user-scope yf-* installs with main: refresh stale installs, upstream the configurable plan-roots patch (#107) on the canonical .yf/ idiom, and import yf-herdr into the repo

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [references/](references/) - Inlined upstream issue bodies (`upstream-<N>.md`), one per non-excluded Upstream Issues row. Snapshots, not live — the issues this plan addresses.
- [reviews/](reviews/) - Reviewer verdicts (`pass-<N>.md`), one per review cycle. What reviewers flagged and how it was resolved.
- [findings/](findings/) - Investigation experiment results (if any).
- [REDEPLOY-HANDOFF.md](REDEPLOY-HANDOFF.md)
- [decisions/](decisions/)
- [scripts/](scripts/)
- [upstream-triage.md](upstream-triage.md)
- [decisions/config-tier.md](decisions/config-tier.md) - Decision: `plans-root` / `incubator-root` are a shared, committed decision
- [findings/5.2-superset-verification.md](findings/5.2-superset-verification.md) - Issue 5.2 — the repo is a superset of user scope
- [findings/exp-01-divergence-classification.md](findings/exp-01-divergence-classification.md) - Experiment 1: Classify every user-scope ↔ repo divergence
- [findings/exp-02-plan-manager-config-reality.md](findings/exp-02-plan-manager-config-reality.md) - Experiment 2: The `plan_manager.py` local patch and the canonical-config reality
- [findings/exp-03-herdr-import-surface.md](findings/exp-03-herdr-import-surface.md) - Experiment 3: What importing `yf-herdr` into the repo actually touches
- [reviews/pass-1.md](reviews/pass-1.md)
- [reviews/pass-2.md](reviews/pass-2.md)
- [reviews/pass-3.md](reviews/pass-3.md)
- [scripts/superset_check.py](scripts/superset_check.py)
