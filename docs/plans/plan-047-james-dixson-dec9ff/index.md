---
okf_version: 0.2
---

# plan-047-james-dixson-dec9ff

> Make yf artifact documents mechanically parseable: formal templates per document type, per-type linters, a corpus normalizer, and a common plan extractor that machine-reads the epic/issue DAG

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/](findings/) - The six investigation findings (EXP-001…006). **Every measured figure the plan cites originates here**, each with its reproduction command. Read these before trusting any number in plan.md.
- [references/](references/) - Full untruncated bodies of the 11 triaged upstream issues, plus drafted upstream comments (`comment-*.md`) awaiting the Upstream-write gate. The only in-bundle copies of the upstream context.
- [reviews/](reviews/) - Red-team pass records, newest last. Each carries its verdict, concerns with severity, and an Operator Resolutions table filled as each concern is resolved.
- [plan-retrospective.md](plan-retrospective.md) - Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE).
- [assets/](assets/) - Measurement records and spikes behind the plan's claims: the carve-out mutant set, the gate-falsification matrix, the pre-work gate baselines, the full-tier run record, and the spiked `extract_plan.py` / `pour_fidelity.py` drafts.
- [scripts/](scripts/) - The plan's own executable gates (`gate-carveouts.sh`, `gate-doclint.sh`, `gate-normalizer.sh`, `gate-upstream.sh`) over the shared `_common.sh` preamble, plus the split proposal generator.
- [findings/exp-001-anchor-derivation.md](findings/exp-001-anchor-derivation.md) - EXP-001 — Canonical grammar for `plan.md`, derived from the 47-plan corpus + declared templates
- [findings/exp-002-normalizability.md](findings/exp-002-normalizability.md) - EXP-002 — How much of the historical corpus can be mechanically normalized?
- [findings/exp-003-extractor-pour-fidelity.md](findings/exp-003-extractor-pour-fidelity.md) - EXP-003 — Prototype extractor, and the first measurement of pour fidelity
- [findings/exp-004-type-surface.md](findings/exp-004-type-surface.md) - EXP-004 — The definitive document-type surface, its producers, and the carve-outs
- [findings/exp-005-enforcement-wiring.md](findings/exp-005-enforcement-wiring.md) - EXP-005 — Can per-type linters bind as real exit-code gates at intake, in CHANGE-VALIDATION, and always-on on-edit?
- [findings/exp-006-normalization-blast-radius.md](findings/exp-006-normalization-blast-radius.md) - EXP-006 — Blast radius of rewriting historical `plan.md` files in place (tests D-2)
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1 — plan-047-james-dixson-dec9ff
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2 — plan-047-james-dixson-dec9ff
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3 — plan-047-james-dixson-dec9ff
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4 — plan-047-james-dixson-dec9ff
- [scripts/_common.sh](scripts/_common.sh)
- [scripts/gate-carveouts.sh](scripts/gate-carveouts.sh)
- [scripts/gate-doclint.sh](scripts/gate-doclint.sh)
- [scripts/gate-normalizer.sh](scripts/gate-normalizer.sh)
- [scripts/gate-upstream.sh](scripts/gate-upstream.sh)
- [scripts/split-proposal.sh](scripts/split-proposal.sh)
