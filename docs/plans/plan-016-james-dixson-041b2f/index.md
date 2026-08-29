---
okf_version: '0.2'
---

# plan-016-james-dixson-041b2f

> Bundle: PEP-723 shared-helper consolidation (#15), bdplan audit invalid-JSON-on-control-chars fix (#36), beads auto-canonicalize yf projects on preflight/init (#39)

This bundle is **portable** — a cold reader understands its purpose, environment and history from the files below alone, without the drafting conversation.

- [context.md](context.md) - Project Environment Context
- [findings/exp-001-39-canonicalization-gap.md](findings/exp-001-39-canonicalization-gap.md) - Exp 001 — #39 canonicalization gap (auto-vs-propose)
- [findings/exp-002-15-helper-inventory-arch.md](findings/exp-002-15-helper-inventory-arch.md) - Exp 002 — #15 duplicated-helper inventory + yf-owned-asset architecture
- [findings/exp-003-36-audit-json-bug.md](findings/exp-003-36-audit-json-bug.md) - Exp 003 — #36 audit invalid-JSON-on-control-chars: bug repro + fix site
- [plan.md](plan.md) - Plan: Bundle: PEP-723 shared-helper consolidation (#15), bdplan audit invalid-JSON-on-control-chars fix (#36), beads auto-canonicalize yf projects on preflight/init (#39)
- [references/upstream-15.md](references/upstream-15.md) - Upstream #15: Consolidate duplicated Python helpers across skills (PEP 723 shared package route)
- [references/upstream-36.md](references/upstream-36.md) - Upstream #36: bdplan audit --json-output emits invalid JSON on control chars in findings
- [references/upstream-39.md](references/upstream-39.md) - Upstream #39: beads: auto-canonicalize yf projects on preflight/init (strip stray hooks, untrack runtime jsonl) — upstream sink is the only knob
- [reviews/pass-1.md](reviews/pass-1.md) - Review pass 1 — plan-016
- [upstream-triage.md](upstream-triage.md) - Upstream Issue Triage: shared helpers audit json canonicalize
