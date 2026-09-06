---
okf_version: 0.2
---

# plan-065-james-dixson-7c8cd4

> Run the yf-okf-hygiene corpus backfill on the repaired engine — 8 legacy-readme bundles to the reserved index.md + log.md model

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [findings/exp-001-objective-divergence-classification.md](findings/exp-001-objective-divergence-classification.md) - exp-001 - does adopting plan.md H1 discard real information across the 7 objective-divergence bundles
- [findings/exp-002-plan-030-phase-log-loss.md](findings/exp-002-plan-030-phase-log-loss.md) - exp-002 - plan-030 phase-log-loss is a detector artifact, and the repair is the move migrate skipped
- [references/upstream-295.md](references/upstream-295.md) - Upstream issue #295 - plan-057 follow-on: 8 unresolved backfill halts (SC19) and 4 ungranted reconcile comments (SC24)
- [references/upstream-316.md](references/upstream-316.md) - Upstream issue #316 - Plan 2/3: run the yf-okf-hygiene corpus backfill — 8 legacy-readme bundles to the reserved index.md + log.md model
- [references/upstream-322.md](references/upstream-322.md) - Upstream issue #322 - docs yf-okf-hygiene SKILL.md: the "31 legacy, 7 halt" figure reads as repo-agnostic and mis-sized a real plan 3.5x
- [references/upstream-359.md](references/upstream-359.md) - Upstream issue #359 - Plan 2/3 (part 2): run the yf-okf-hygiene corpus backfill — 8 legacy-readme bundles, on the repaired engine
- [references/upstream-361.md](references/upstream-361.md) - Upstream issue #361 - plan_extract.py --strict validates neither self-edges nor cycles in the plan DAG
- [references/upstream-362.md](references/upstream-362.md) - Upstream issue #362 - yf-okf-hygiene: the _index.md legacy-variant transform route manufactures a hybrid under the yf-plan member
- [findings/exp-003-post-commit-restore-loss.md](findings/exp-003-post-commit-restore-loss.md) - exp-003 - restore --apply after the backfill is committed causes silent total loss, a fourth data-loss path
- [reviews/pass-1.md](reviews/pass-1.md) - Review pass-1 - plan-065 red-team, verdict REVISE, 14 concerns
- [reviews/pass-2.md](reviews/pass-2.md) - Review pass-2 - plan-065 red-team cycle 2, verdict REVISE, 16 concerns, one high-severity data-loss path introduced by pass-1 remediation
- [reviews/pass-3.md](reviews/pass-3.md) - Review pass-3 - plan-065 red-team cycle 3, verdict REVISE, 15 concerns, no high; plan size flagged as a risk in itself
- [reviews/pass-4.md](reviews/pass-4.md) - Review pass-4 - plan-065 red-team cycle 4, verdict APPROVE, 10 concerns none high, converged
- [findings/negative-controls.md](findings/negative-controls.md) - Prose companion to `negative-controls.json` — why each of the eleven controls is the RIGHT control, and the Issue 0.5 pre-transform FALSE reports (SC13, SC14).
- [findings/negative-controls.json](findings/negative-controls.json) - Machine record of the eleven negative controls (all exit 1) plus the four tree-property FALSE reports against the pre-transform tree. Consumed by `plan065_checks.py negative-controls`.
- [findings/finding-counts-before.json](findings/finding-counts-before.json) - Per-bundle OKF finding counts for the 8 targets BEFORE the transform (114 total). Irrecoverable once Epics 1-2 land; the baseline D6's comparison needs.
- [findings/diff-base.txt](findings/diff-base.txt) - The pinned diff base (`git merge-base origin/main HEAD`). A checker diffing an unpinned base is vacuously green at Epic 0.
- [findings/dryrun-post-epic1.json](findings/dryrun-post-epic1.json) - Backfill dry run after the two H1 pre-merges — 7 would-backfill, plan-030 still halting; the byte-for-byte reconciled-objective evidence for Issue 1.4.
- [findings/dryrun-post-epic2.json](findings/dryrun-post-epic2.json) - Backfill dry run after plan-030's repair — 8 would-backfill, 0 halted (Issue 2.5).
- [findings/rehearsal-result.json](findings/rehearsal-result.json) - The sandbox rehearsal artifact the capability gate's Test reads: `legacy_before`, `transformed`, `halted`, `roundtrip_identical`, plus per-bundle hashes (Issue 3.4).
- [findings/apply-result.json](findings/apply-result.json) - The real-corpus `backfill --apply` run JSON — 8 transformed, 0 halted, 70 checked, exactly 8 rows with `action == backfilled` (Issue 4.3).
- [findings/restore-roundtrip.json](findings/restore-roundtrip.json) - Per-file sha256 for plan-030 across pre-backfill / post-backfill / post-reversal / post-reapply, discharging #359's restore-on-a-real-bundle criterion (Issue 4.4).
- [findings/backfill-record.json](findings/backfill-record.json) - The `--record` from the real-corpus apply (Issue 4.2) — per-path operations for all 8 bundles, `schema_version: 1`. The input `restore` reads; RELOCATED here from a repo-root `findings/` so the record lives with the plan it belongs to.
- [findings/reapply-record.json](findings/reapply-record.json) - The SECOND record, from Issue 4.4's re-apply after the plan-030 restore. A separate path is required: `backfill` has no per-bundle selector, so overwriting 4.2's record would leave the other seven with no record-driven reversal.
- [findings/fingerprints-all-eight.txt](findings/fingerprints-all-eight.txt) - Issue 5.4's measurement that the stored `**Fingerprint:**` of all EIGHT targets is byte-identical at the pinned base and after the transform.
- [findings/upstream-drafts.md](findings/upstream-drafts.md) - The SIX drafted engine-defect issue bodies and the exact close set (#359 close, #316 close, #295 partial), written for the Epic 6 operator gate to authorize against. Nothing here is filed.
- [findings/full-tier-result.json](findings/full-tier-result.json) - The FULL change-validation tier over the merged tree — 73/73 commands executed and passed, including both new plan065 rows.
- [escalations.md](escalations.md) - Open questions raised to the upstream controller during execution (`## ESC-NNN` entries), each with its alternatives, its recommended default, and what happens if no answer arrives. PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding of any severity (REQ-PORT-ACT-ESCALATION).
- [assets/](assets/) - Negative-control fixtures for `plan065_checks.py` (Issue 0.4) — synthesized `--input` JSON/markdown and a fixture bundle tree, each reproducing the exact failure shape one subcommand claims to detect. Collapsed to one bullet by OKF rule D (>10 files reachable recursively).
