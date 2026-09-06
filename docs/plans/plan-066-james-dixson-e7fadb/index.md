---
okf_version: 0.2
---

# plan-066-james-dixson-e7fadb

> Regenerate user-facing website/docs (#317): unbreak the pelican build, repair Class-A content defects at every site, and close the Class-B harvest/generation-pipeline defects

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/exp-001-checkability-census.md](findings/exp-001-checkability-census.md) - Census of the Class-A claim classes in issue 317: 7 CHECKABLE, 5 PARTIAL, 2 PROSE-ONLY. D1 corroborated; the issue undercounts rows 4-6 from about 4 sites to 15.
- [findings/exp-002-classb-reproduction.md](findings/exp-002-classb-reproduction.md) - All six Class-B defects reproduce; three diagnoses in issue 317 are wrong and two remedies are no-ops. Defect 5 is a DISPATCH gap, not a manifest gap.
- [findings/exp-003-build-reality.md](findings/exp-003-build-reality.md) - Nothing is behind the first build error, so the P0 is one file. But the guard is existence-only (an empty file passes) and piping through tail masks the pelican exit code.
- [findings/exp-004-diagram-pipeline.md](findings/exp-004-diagram-pipeline.md) - Diagram repair is achievable and no committed PNG is content-stale. Byte comparison works within a pinned d2 version, not across versions.
- [references/upstream-104.md](references/upstream-104.md) - Upstream issue #104 - web: prevent runaway Pelican devservers + add clean teardown (port naba#21)
- [references/upstream-127.md](references/upstream-127.md) - Upstream issue #127 - web/concepts: define idiomatic workflow terms (pouring beads, landing the plane, red-team, etc.)
- [references/upstream-247.md](references/upstream-247.md) - Upstream issue #247 - Drift findings no edge covers: the manifest's own diagram is 22 edges stale, and install.sh/install.py do not exist
- [references/upstream-263.md](references/upstream-263.md) - Upstream issue #263 - META: 'two facts, one signal' is one architectural gap with 11+ instances — investigate the class before fixing another instance
- [references/upstream-273.md](references/upstream-273.md) - Upstream issue #273 - The command-vs-obligation law: prose naming a COMMAND is followed more reliably than prose naming an OBLIGATION — one mechanism behind #264, #270, #145's finding 4, and retrospective_fields.py
- [references/upstream-312.md](references/upstream-312.md) - Upstream issue #312 - Process-audit stage: amend the poured DAG so the retrospective write, the landing protocol and preflight are BEADS, not paragraphs
- [references/upstream-317.md](references/upstream-317.md) - Upstream issue #317 - Plan 3/3: regenerate user-facing docs (the site does not currently BUILD) and separate content defects from harvest/generation-process defects
- [references/upstream-322.md](references/upstream-322.md) - Upstream issue #322 - docs yf-okf-hygiene SKILL.md: the "31 legacy, 7 halt" figure reads as repo-agnostic and mis-sized a real plan 3.5x
- [references/upstream-363.md](references/upstream-363.md) - Upstream issue #363 - OKF-EXTENSION.md documentation remediation: 3 stale DRAFT banners, 2 dangling symbols, 2 shipped-but-open decisions (#247)
- [references/upstream-365.md](references/upstream-365.md) - Upstream issue #365 - plan-065-james-dixson-7c8cd4 execution tracking
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1: REVISE, 16 concerns (5 high). All resolved.
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2: REVISE, 15 concerns (5 high), five introduced by the pass-1 remediation. All resolved.
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3: REVISE, 11 concerns. Caught two PHANTOM RESOLUTIONS from pass 2 — edits asserted by four documents but never made.
- [reviews/pass-4.md](reviews/pass-4.md) - Red-team pass 4: APPROVE with one medium-high must-fix. Phantom streak broken; all 11 pass-3 resolutions verified in the artifact.
- [escalations.md](escalations.md) - Open questions raised to the upstream controller during execution (`## ESC-NNN` entries), each with its alternatives, its recommended default, and what happens if no answer arrives. PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding of any severity (REQ-PORT-ACT-ESCALATION).
- [assets/change-validation-rows.md](assets/change-validation-rows.md) - The CHANGE-VALIDATION.md §1 recipe and §3 trigger rows Issue 0.5 DRAFTS and Issue 8.4b LANDS post-merge on main — a row naming an in-flight plan directory is structurally unsatisfiable from an execute address space.
- [findings/class-a-inventory.md](findings/class-a-inventory.md) - The Class-A defect inventory, DERIVED MECHANICALLY by running the four Epic-2 checkers: 40 findings across 10 files. This, not #317's table, is what Epic 4 repairs.
- [findings/negative-control-evidence.md](findings/negative-control-evidence.md) - Evidence for the code-side negative-control convention: two measured instances where a control caught a false green that reasoning missed.
