---
okf_version: 0.1
---

# plan-044-james-dixson-f6fdbd

> Retire the beads-integrity and deploy-path defect clusters: local-only Dolt remote enforcement (#159, #160), YOSHIKO_FLOW.md tune safety and surface routing (#154, #156, #155), and upstream-reconcile correctness (#144, #142, #143)

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [references/](references/) - Inlined upstream issue bodies (`upstream-<N>.md`), one per non-excluded Upstream Issues row. Snapshots, not live — the issues this plan addresses.
- [reviews/](reviews/) - Reviewer verdicts (`pass-<N>.md`), one per review cycle. What reviewers flagged and how it was resolved.
- [findings/](findings/) - Investigation experiment results (if any).
- [upstream-triage.md](upstream-triage.md)
- [findings/exp-001-rules-aggregate-write-path.md](findings/exp-001-rules-aggregate-write-path.md) - exp-001 — The YOSHIKO_FLOW.md rules-aggregate write path (#154, #156)
- [findings/exp-002-dolt-remote-local-only.md](findings/exp-002-dolt-remote-local-only.md) - exp-002 — The Dolt-remote / local-only two-layer model (#159, #160)
- [findings/exp-003-upstream-reconcile-surface.md](findings/exp-003-upstream-reconcile-surface.md) - exp-003 — The upstream reconcile/closable surface (#144, #142)
- [findings/exp-004-install-prune-gap.md](findings/exp-004-install-prune-gap.md) - exp-004 — The skills install/upgrade prune gap (#155)
- [findings/exp-005-dangling-epics-and-158.md](findings/exp-005-dangling-epics-and-158.md) - exp-005 — Dangling `**Epic:**` refs (#143) and the #158 verdict
- [findings/exp-006-spec-and-validation-surface.md](findings/exp-006-spec-and-validation-surface.md) - exp-006 — SPEC-first and validation machinery (reference)
- [findings/exp-007-160-init-ordering-probe.md](findings/exp-007-160-init-ordering-probe.md) - exp-007 — The #160 init-ordering hypothesis: CONFIRMED
- [findings/exp-008-agents-rule-target-probe.md](findings/exp-008-agents-rule-target-probe.md) - exp-008 — What does the `agents` surface actually load? (D-11 probe)
- [reviews/pass-1.md](reviews/pass-1.md) - Red-Team Pass 1 — plan-044-james-dixson-f6fdbd
- [reviews/pass-2.md](reviews/pass-2.md) - Red-Team Pass 2 — plan-044-james-dixson-f6fdbd
- [reviews/pass-3.md](reviews/pass-3.md) - Red-Team Pass 3 — plan-044-james-dixson-f6fdbd
