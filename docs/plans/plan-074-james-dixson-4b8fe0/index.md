---
okf_version: 0.2
---

# plan-074-james-dixson-4b8fe0

> Gate-wrapper compatibility for start resolution and pour fidelity

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [escalations.md](escalations.md) - Open questions raised to the upstream controller during execution (`## ESC-NNN` entries), each with its alternatives, its recommended default, and what happens if no answer arrives. PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding of any severity (REQ-PORT-ACT-ESCALATION).
- [diagrams/roles.browser-check.json](diagrams/roles.browser-check.json)
- [diagrams/roles.delivery.json](diagrams/roles.delivery.json)
- [diagrams/roles.finalize-summary.json](diagrams/roles.finalize-summary.json)
- [diagrams/roles.finalize.json](diagrams/roles.finalize.json)
- [diagrams/roles.html](diagrams/roles.html)
- [diagrams/roles.json](diagrams/roles.json)
- [findings/exp-001-native-roles.md](findings/exp-001-native-roles.md) - Native bd 1.3.1 makes a gate wrapper while 1.1.0 makes a task; pour mapping, not persisted source fields, supplies role identity.
- [findings/exp-002-self-hosting.md](findings/exp-002-self-hosting.md) - Self-hosting needs explicit operator bootstrap authority and a disposable recovery rehearsal; a session boundary alone is insufficient.
- [findings/exp-003-held-h0-reproduction.md](findings/exp-003-held-h0-reproduction.md) - A portable 18-node H0 snapshot reproduces exit 1 solely on the extra wrapper gate count; installed and source scripts match.
- [references/bootstrap-proposal.md](references/bootstrap-proposal.md) - Unapproved plan-specific early-promotion exception with exact-tree validation, sandbox rehearsal and fresh operator landing decisions.
- [references/compatibility-contract.md](references/compatibility-contract.md) - Proposed receipt-bound gate roles distinguish native wrappers from real gates and reject ambiguous lookalikes without inferring consent.
- [references/upstream-417.md](references/upstream-417.md) - Upstream issue #417 - yf-plan: resolve-start-gate can't find the Begin: wrapper under bd 1.3.0 (poured as issue_type gate, not task)
- [references/upstream-scan.json](references/upstream-scan.json)
