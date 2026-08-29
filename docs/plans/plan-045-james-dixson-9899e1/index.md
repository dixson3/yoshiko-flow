---
okf_version: 0.1
---

# plan-045-james-dixson-9899e1

> Make plan execution and review autonomous by default, with human gates frontloaded: self-resolving review cycles, a non-stopping coordinator loop, an execute-start gate sweep, and push-based herdr delegation

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [references/](references/) - Inlined upstream issue bodies (`upstream-<N>.md`), one per non-excluded Upstream Issues row. Snapshots, not live — the issues this plan addresses.
- [reviews/](reviews/) - Reviewer verdicts (`pass-<N>.md`), one per review cycle. What reviewers flagged and how it was resolved.
- [findings/](findings/) - Investigation experiment results (if any).
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).
- [upstream-triage.md](upstream-triage.md)
- [findings/exp-001-config-and-override-plumbing.md](findings/exp-001-config-and-override-plumbing.md) - exp-001 — Config plumbing and the per-invocation override (D-1)
- [findings/exp-002-attempt-counter-storage.md](findings/exp-002-attempt-counter-storage.md) - exp-002 — Where a per-bead attempt counter can live (D-3)
- [findings/exp-003-gate-sweep-feasibility.md](findings/exp-003-gate-sweep-feasibility.md) - exp-003 — Gate-sweep feasibility (D-4) — REFUTES the scoped design
- [findings/exp-004-retrospective-schema.md](findings/exp-004-retrospective-schema.md) - exp-004 — `plan-retrospective.md`: schema, portability, and #145 consumability (D-6)
- [findings/exp-005-herdr-push-verification.md](findings/exp-005-herdr-push-verification.md) - exp-005 — Live verification of the herdr child→parent push contract (D-5)
- [findings/exp-006-spec-amendment-surface.md](findings/exp-006-spec-amendment-surface.md) - exp-006 — The SPEC amendment surface and validation consequences
- [findings/exp-007-self-report-vs-verification.md](findings/exp-007-self-report-vs-verification.md) - exp-007 — Self-report is not verification (observed, not designed)
- [references/upstream-110.md](references/upstream-110.md) - Upstream #110: herdr: leverage `herdr agent *` to launch and monitor agent sessions from a primary session
- [references/upstream-113.md](references/upstream-113.md) - Upstream #113: yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state)
- [references/upstream-145.md](references/upstream-145.md) - Upstream #145: New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract
- [references/upstream-149.md](references/upstream-149.md) - Upstream #149: M5/M9: process rules that nothing executes, and remediation edges that exist only in prose
- [references/upstream-162.md](references/upstream-162.md) - Upstream #162 — plan-045-james-dixson-9899e1 execution tracking
- [reviews/pass-1.md](reviews/pass-1.md) - Red-Team Pass 1 — plan-045-james-dixson-9899e1
- [reviews/pass-2.md](reviews/pass-2.md) - Red-Team Pass 2 — plan-045-james-dixson-9899e1
- [reviews/pass-3.md](reviews/pass-3.md) - Red-Team Pass 3 — plan-045-james-dixson-9899e1
- [reviews/pass-4.md](reviews/pass-4.md) - Red-Team Pass 4 — plan-045-james-dixson-9899e1

## Note on `scope-answers.md`

This bundle has **no `scope-answers.md`**. Scoping was conducted interactively rather than via the
questionnaire path, and the resulting decisions are recorded as the **D-1…D-8 table** in `plan.md`
§Approach, which supersedes it. Recorded here so a cold reader does not read the absence as a gap
(pass-2 concern I).
