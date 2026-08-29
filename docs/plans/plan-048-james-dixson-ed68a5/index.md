---
okf_version: 0.2
---

# plan-048-james-dixson-ed68a5

> Make the historical plan corpus machine-readable by widening the extractor grammar, and instantiate the plan-047 document-conformance engine across the remaining yf artifact types. First half of a split taken at approval (D-13); the corpus migration and enforcement binding are **plan-049**.

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/](findings/) - The six investigation findings this plan's decisions rest on. Every measured figure in plan.md originates here; per D-5 nothing is inherited from plan-047 without re-measurement.
  - [exp-001-unparsed-taxonomy.md](findings/exp-001-unparsed-taxonomy.md) - Unparsed-construct taxonomy; refutes plan-047's "300" as 150, and proves no construct sits in a fingerprint-excluded section.
  - [exp-002-document-type-census.md](findings/exp-002-document-type-census.md) - Census of ~30 artifact types; what each schema must require and which have no consumer.
  - [exp-003-report-only-distribution.md](findings/exp-003-report-only-distribution.md) - The 610 report-only findings split 371 structural / 239 content; status explains 100% of the classification.
  - [exp-004-enforcement-binding.md](findings/exp-004-enforcement-binding.md) - What is bound, what is not, two unreported live vacuities, and why a fail-closed intake gate would have blocked plan-047 itself.
  - [exp-005-issue-173-feasibility.md](findings/exp-005-issue-173-feasibility.md) - #173 is structurally checkable; the era mechanism already exists; two extractor defects are prerequisites.
  - [exp-006-hash-neutrality-proof.md](findings/exp-006-hash-neutrality-proof.md) - The fingerprint exclusion set from code, and the measurement that refuted D-4 as originally written.
- [references/](references/) - One file per triaged upstream issue, with the full untruncated body, URL, labels and state — so the upstream context survives without network access.
- [reviews/](reviews/) - Red-team and conformance review records, one file per cycle, with the verdict and per-concern resolutions.
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).
- [assets/](assets/) - The measurement record: the drift-edge audit, the free-REQ-id survey that allocated this plan's ids, the pre/post gate measurements, and the residue analysis with its mutant.
- [scripts/](scripts/) - The plan's executable gates — `gate-grammar.sh` and `gate-relations.sh` over `_common.sh`, driven by `gate-run.sh`.
