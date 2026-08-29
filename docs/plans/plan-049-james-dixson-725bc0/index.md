---
okf_version: 0.2
---

# plan-049-james-dixson-725bc0

> Rewrite the historical plan corpus so the constructs plan-048 refuses become readable, and bind the document linter at the two enforcement points that were never wired

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/](findings/) - The six investigation findings this plan's decisions rest on. Two of them refuted the plan's own scope decisions (D-2's target population and D-4's safety postcondition) before any code was written.
  - [exp-001-adjudication-taxonomy.md](findings/exp-001-adjudication-taxonomy.md) - The 65 are 51 adjudications yielding ~35 archival edges; and 89 inline declarations are invisible AND uncounted.
  - [exp-002-dag-invariance-design.md](findings/exp-002-dag-invariance-design.md) - D-4 as worded PASSES the replay it was written for; the three-layer form with L3 primary is what fires (the plan adopts a fourth layer, L4 gate content).
  - [exp-003-intake-binding-blast-radius.md](findings/exp-003-intake-binding-blast-radius.md) - The findings blocker is gone by demotion, not conformance; "conform by construction" is n=0.
  - [exp-004-unbound-enforcement-surface.md](findings/exp-004-unbound-enforcement-surface.md) - The engine is vendored into no skill; promotion-off is declared twice and implemented never.
  - [exp-005-stale-literal-detectability.md](findings/exp-005-stale-literal-detectability.md) - A naive #135 check fires 41/41 with 39 correct-behaviour false positives.
  - [exp-006-linter-distribution.md](findings/exp-006-linter-distribution.md) - 610 is wrong by 2.2x; the populations overlap at 144 of 1340; the migration moves the count +41.
- [references/](references/) - One file per triaged upstream issue, with the full untruncated body, so the upstream context survives without network access.
  - [handoff-050.md](references/handoff-050.md) - Everything this plan leaves for its successor: unmet `Discharged-by` criteria, the `deferred`/`partial` upstream rows, the two missed numeric targets with the reason the target was misderived, and the instruments plan-050 inherits. **Generated** from plan.md's own tables and diffed against a hand list.
- [reviews/](reviews/) - Red-team review records, one file per cycle, each with its verdict and a per-concern resolutions table.
- [scripts/](scripts/) - The executable capability-gate harness this plan authors for itself: `gate-run.sh` (the 0/1/2 exit-discipline wrapper) plus the two gate scripts it wraps. Listed only now that the directory exists — an index entry for an absent directory is an OKF ghost.
  - [gate-run.sh](scripts/gate-run.sh) - Maps any exit outside {0,1,2} — notably bash's 127 for a missing script — to an explicit 2 with a harness-failure message, so a never-authored gate reads as a repairable harness fault rather than a stall.
  - [gate-dagguard.sh](scripts/gate-dagguard.sh) - Capability gate: the DAG guard exits 1 on mutants A and B and 0 on mutant D. A claim about the instrument, not the corpus.
  - [gate-cellcheck.sh](scripts/gate-cellcheck.sh) - Capability gate: the empty-cell and gate-completeness checks fire on three mutants and on neither control, including the canonical Start Gate template.
- [assets/](assets/) - Measured artifacts produced during execution: the free REQ-id list, the two gate/drift evidence records, the edge audit, the proposed write diff, and the two operator authorization records.
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).
- [references/upstream-102.md](references/upstream-102.md) - Upstream #102: .markdown-lint-on-edit -> .yf/markdown-lint-on-edit: gitignore semantics + migrate.rs rename
- [references/upstream-113.md](references/upstream-113.md) - Upstream #113: yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state)
- [references/upstream-135.md](references/upstream-135.md) - Upstream #135: yf-plan: a measured literal in plan.md goes stale when the plan is inside its own measured corpus
- [references/upstream-140.md](references/upstream-140.md) - Upstream #140: yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model
- [references/upstream-145.md](references/upstream-145.md) - Upstream #145: New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract
- [references/upstream-149.md](references/upstream-149.md) - Upstream #149: M5/M9: process rules that nothing executes, and remediation edges that exist only in prose
- [references/upstream-171.md](references/upstream-171.md) - Upstream #171: yf-okf: nested index.md generation, deferred behind a `description:` producer change (plan-046 D-9)
- [references/upstream-174.md](references/upstream-174.md) - Upstream #174: yf-plan: a review-phase validation pass — falsify every criterion, and cross-check every claim against the code that scores it
- [references/upstream-183.md](references/upstream-183.md) - Upstream #183: plan-049-james-dixson-725bc0 execution tracking
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1 — plan-049-james-dixson-725bc0
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2 — plan-049-james-dixson-725bc0
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3 — plan-049-james-dixson-725bc0
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4 — plan-049-james-dixson-725bc0
- [reviews/pass-5.md](reviews/pass-5.md) - Red-team pass 5 — plan-049-james-dixson-725bc0
