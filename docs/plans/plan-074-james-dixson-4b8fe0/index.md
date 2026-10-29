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
- [assets/](assets/) - Immutable native current/historical pours, pinned source excerpts, versions/digests, held-H0 reproduction and upstream readbacks. Captured scripts are archival inputs, not commands to execute in place.
- [diagrams/roles.browser-check.json](diagrams/roles.browser-check.json) - Automated real-browser layout checks; no perceptual review claimed.
- [diagrams/roles.delivery.json](diagrams/roles.delivery.json) - Artifact delivery and provenance receipt.
- [diagrams/roles.finalize-summary.json](diagrams/roles.finalize-summary.json) - Compact passing Archify validation/delivery/browser summary.
- [diagrams/roles.finalize.json](diagrams/roles.finalize.json) - Full automated diagram receipt.
- [diagrams/roles.html](diagrams/roles.html) - Explorable proposed identity boundary, distinct from consent and bootstrap authority.
- [diagrams/roles.json](diagrams/roles.json) - Editable Archify source for the proposal, not an implementation diagram.
- [findings/exp-001-native-roles.md](findings/exp-001-native-roles.md) - Native bd 1.3.1 makes a gate wrapper while 1.1.0 makes a task; pour mapping, not persisted source fields, supplies role identity.
- [findings/exp-002-self-hosting.md](findings/exp-002-self-hosting.md) - Self-hosting needs explicit operator bootstrap authority and a disposable recovery rehearsal; a session boundary alone is insufficient.
- [findings/exp-003-held-h0-reproduction.md](findings/exp-003-held-h0-reproduction.md) - A portable 18-node H0 snapshot reproduces exit 1 solely on the extra wrapper gate count; installed and source scripts match.
- [references/bootstrap-proposal.md](references/bootstrap-proposal.md) - Unapproved plan-specific early-promotion exception with exact-tree validation, sandbox rehearsal and fresh operator landing decisions.
- [references/compatibility-contract.md](references/compatibility-contract.md) - Proposed receipt-bound gate roles distinguish native wrappers from real gates and reject ambiguous lookalikes without inferring consent.
- [references/upstream-417.md](references/upstream-417.md) - Upstream issue #417 - yf-plan: resolve-start-gate can't find the Begin: wrapper under bd 1.3.0 (poured as issue_type gate, not task)
- [references/upstream-scan.json](references/upstream-scan.json) - Full original #417 query result used for triage.
- [reviews/conformance.md](reviews/conformance.md) - Independent six-item mechanical PASS; not adversarial approval.
- [reviews/pass-1.md](reviews/pass-1.md) - Independent REVISE found a missing own-intake bridge; resolved in the unapproved B0 proposal and re-reviewed.
- [reviews/pass-2.md](reviews/pass-2.md) - Independent reading APPROVE verifies the revised allocation, not bootstrap feasibility or operator consent.
- [reviews/pass-3.md](reviews/pass-3.md) - Independent execution-mode APPROVE; checks and prior resolution re-run, future implementation/authority not claimed.
- [references/reproduction.md](references/reproduction.md) - Portable offline baseline reproduction, genuine native fixture controls and artifact-provenance limits.
- [references/readiness.md](references/readiness.md) - Exact reviewed hashes, mechanical readiness, unapproved B0/B1/B2 decisions and no-authority handoff.
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).
- [references/operator-decisions.json](references/operator-decisions.json) - Exact later operator approval, accepted B0, conditional B1 and external-only B2; live PIM writes/resumption remain forbidden.
- [references/upstream-456.md](references/upstream-456.md) - Full verified OPEN coarse tracker body; intake mirror is not an execution epic.
- [references/intake-handoff.md](references/intake-handoff.md) - Approved intake, tracker #456, unchanged fingerprint and master-only fresh-executor handoff. Read this after the historical readiness report.
- [references/publication-exception.json](references/publication-exception.json) - Exact operator answer authorizing only plan-bundle publication with FULL still INCONCLUSIVE.
- [references/publication-exception.md](references/publication-exception.md) - Invocation/timeout provenance, preserved receipts, required publication checks and explicit non-waivers.
