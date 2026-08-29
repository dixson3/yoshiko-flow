---
okf_version: 0.1
---

# plan-043-james-dixson-a8afe8

> Settle the Phase 6.4 close-time hook contract once, and land the payloads queued behind it (#136 reconcile verification, #140 bundle conformance at close, #145 escape capture)

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [references/](references/) - Inlined upstream issue bodies (`upstream-<N>.md`) — one per triaged issue, including the `exclude` rows, so a cold reader can check the exclusion rationale against the source. Snapshots, not live — the issues this plan addresses.
- [reviews/](reviews/) - Reviewer verdicts (`pass-<N>.md`), one per review cycle. What reviewers flagged and how it was resolved.
- [findings/](findings/) - Investigation experiment results (if any).
- [upstream-triage.md](upstream-triage.md)
- [findings/exp-001-reconcile-skip-cause.md](findings/exp-001-reconcile-skip-cause.md) - E1 — Why plan-039's reconcile skipped three `include` upstream issues
- [findings/exp-002-phase64-surface.md](findings/exp-002-phase64-surface.md) - E2 — The actual implementation surface of Phase 6.4
- [findings/exp-003-close-time-audit.md](findings/exp-003-close-time-audit.md) - E3 — Close-time bundle audit: fail-loud or propose-only?
- [references/upstream-128.md](references/upstream-128.md) - Upstream #128: yf-okf skill: add reference/link to the Google OKF spec
- [references/upstream-136.md](references/upstream-136.md) - Upstream #136: yf-plan: reconcile silently skipped three mapped 'include' upstream issues while the plan reported complete
- [references/upstream-140.md](references/upstream-140.md) - Upstream #140: yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model
- [references/upstream-141.md](references/upstream-141.md) - Upstream #141: yf-okf: reconcile OKF-BASELINE from v0.1 to OKF v0.2 (supersedes #128)
- [references/upstream-145.md](references/upstream-145.md) - Upstream #145: New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract
- [references/upstream-148.md](references/upstream-148.md) - Upstream #148 — plan-043 execution tracking: Phase 6.4 close-time step contract (+ #136, #140 audit half)
- [reviews/pass-1.md](reviews/pass-1.md) - Review pass 1 — adversarial (red-team)
- [reviews/pass-2.md](reviews/pass-2.md) - Review pass 2 — adversarial (red-team)
- [reviews/pass-3.md](reviews/pass-3.md) - Review pass 3 — adversarial (red-team)
- [reviews/pass-4.md](reviews/pass-4.md) - Review pass 4 — adversarial (red-team)
