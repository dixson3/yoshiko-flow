---
okf_version: 0.1
---

# plan-046-james-dixson-aabefa

> OKF group — reconcile OKF-BASELINE to v0.2 (#141), make bundle index structure generated rather than asserted (#140, retargeted at the bundle root), reconcile #92 as superseded with named carve-outs, and fix the stale plan-folder orientation docs (#118).

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [references/](references/) - Inlined upstream issue bodies (`upstream-<N>.md`), one per non-excluded Upstream Issues row. Snapshots, not live — the issues this plan addresses.
- [reviews/](reviews/) - Reviewer verdicts (`pass-<N>.md`), one per review cycle. What reviewers flagged and how it was resolved.
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/](findings/) - The four investigation experiments. **exp-003 refuted the originally-approved nested-index backfill and exp-004 weakened the #92 supersede** — read these before trusting plan.md's scope.
- [assets/](assets/) - Attachments and other generated artifacts (not diagrams — those live in `diagrams/`).
- [plan-retrospective.md](plan-retrospective.md)
- [findings/exec-001-full-tier-executed.md](findings/exec-001-full-tier-executed.md) - exec-001 — The FULL tier, EXECUTED (plan-046 Issue 1.6)
- [findings/exec-002-v01-verbatim-delta.md](findings/exec-002-v01-verbatim-delta.md) - exec-002 — The v0.1↔v0.2 delta, measured against BOTH verbatim specs (plan-046 Issue 2.1)
- [findings/exec-003-sc3-unsatisfiable.md](findings/exec-003-sc3-unsatisfiable.md) - exec-003 — SC3's mechanical check is unsatisfiable as written (plan-046, Epic 2)
- [findings/exec-004-audit-measured.md](findings/exec-004-audit-measured.md) - exec-004 — D-12 measured by EXECUTION, not by reading (plan-046 Issue 3.8, SC8)
- [findings/exec-005-corpus-prestate.md](findings/exec-005-corpus-prestate.md) - exec-005 — The corpus pre-state, measured (plan-046 Issue 4.1)
- [findings/exp-001-okf-blast-radius.md](findings/exp-001-okf-blast-radius.md) - exp-001 — The `_shared/okf.py` blast radius, and what actually guards it
- [findings/exp-002-okf-v02-delta.md](findings/exp-002-okf-v02-delta.md) - exp-002 — The v0.1→v0.2 delta, and where v0.2 meets yf's private vocabulary
- [findings/exp-003-reindex-and-corpus-backfill.md](findings/exp-003-reindex-and-corpus-backfill.md) - exp-003 — Is a generated nested-`index.md` backfill mechanically sound?
- [findings/exp-004-92-supersede-evidence.md](findings/exp-004-92-supersede-evidence.md) - exp-004 — Is #92 superseded? (and the true extent of #118)
- [references/okf-spec-v0.1.md](references/okf-spec-v0.1.md) - Reference: Open Knowledge Format (OKF) SPEC v0.1 — verbatim upstream copy
- [references/okf-spec-v0.2.md](references/okf-spec-v0.2.md) - Reference: Open Knowledge Format (OKF) SPEC v0.2 — verbatim upstream copy
- [references/upstream-118.md](references/upstream-118.md) - Upstream #118: yf-plan README.md stale: still lists README.md as plan-folder orientation file (pre-OKF), contradicts index.md/log.md in SPEC REQ-PLAN-010 + SKILL.md
- [references/upstream-140.md](references/upstream-140.md) - Upstream #140: yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model
- [references/upstream-141.md](references/upstream-141.md) - Upstream #141: yf-okf: reconcile OKF-BASELINE from v0.1 to OKF v0.2 (supersedes #128)
- [references/upstream-167.md](references/upstream-167.md) - Upstream #167: plan-046-james-dixson-aabefa execution tracking
- [references/upstream-92.md](references/upstream-92.md) - Upstream #92: OKF export-emit integration for yf-plan/research/incubator (deferred)
- [reviews/pass-1.md](reviews/pass-1.md) - Red-Team Pass 1 — plan-046-james-dixson-aabefa
- [reviews/pass-2.md](reviews/pass-2.md) - Red-Team Pass 2 — plan-046-james-dixson-aabefa
- [reviews/pass-3.md](reviews/pass-3.md) - Red-Team Pass 3 — plan-046-james-dixson-aabefa
- [reviews/pass-4.md](reviews/pass-4.md) - Red-Team Pass 4 — plan-046-james-dixson-aabefa
- [reviews/pass-5.md](reviews/pass-5.md) - Red-Team Pass 5 — plan-046-james-dixson-aabefa
