# CLI Specification

## Skill Invocation

REQ-CLI-001: The skill provides 7 subcommands: `init`, `<objective>` (new plan), `continue`, `capture`, `execute`, `status`, `list`.
Rationale: Each subcommand maps to a distinct user intent; missing any leaves a gap in the workflow. `capture` was added in the portability contract work to let operators audit and repair a plan folder mid-drafting without advancing status.
Verification: SKILL.md Invocation section lists all 7.

REQ-CLI-002: The skill triggers on `/yf-plan` and on planning-intent language ("let's design", "let's plan", "how should we build", "let's architect").
Rationale: Users should not need to remember the exact command; natural language triggers lower friction.
Verification: SKILL.md TRIGGER line.

REQ-CLI-003: The skill overrides native plan mode. `EnterPlanMode`/`ExitPlanMode` must never be used.
Rationale: Two competing plan systems produce conflicting state; yf-plan is the sole planning mechanism.
Verification: SKILL.md OVERRIDE line.

## Pre-flight

REQ-CLI-004: Every invocation except `init` runs `plan_manager.py check` and stops (directing to `init`) on any non-`ok`/`ignored` status.
Rationale: Running the skill without prerequisites produces confusing failures; init must run first.
Verification: SKILL.md Pre-flight section.

REQ-CLI-005: If `.yf-plan.local.json` contains `"ignore-skill": true`, the skill exits silently and falls back to native plan mode.
Rationale: Projects that can't satisfy prerequisites need a clean opt-out without repeated error messages.
Verification: SKILL.md Pre-flight bullet 2; `_check_prerequisites()` in plan_manager.py returns `{"status":"ignored"}`.

## plan_manager.py CLI

REQ-CLI-006: `plan_manager.py` exposes 10 subcommands: `check`, `json-get`, `init`, `scope`, `triage`, `list`, `update-status`, `record-epic`, `resume-scan`, `audit`.
Rationale: These are the mechanical operations SKILL.md delegates; missing any breaks the wiring. `audit` was added to support the portability precondition check at intake and the `/yf-plan capture` maintenance subcommand. `record-epic` and `resume-scan` were added for coordinator crash recovery (#2): the first persists the plan↔epic linkage at intake, the second reports it back for the resume guard. The companion rule is installed by the repo installer (`install.sh`), not by `init`, so no `rules-dir` subcommand is needed; preflight locates the installed rule internally via `_rule_candidates()`/`_check_rule()`.
Verification: `grep '@cli.command' skills/yf-plan/scripts/plan_manager.py` returns 10 matches.

REQ-CLI-012: `plan_manager.py record-epic <plan-dir> <epic-id>` persists the plan↔epic linkage in the bundle: the epic id in plan.md's header metadata — dual-written as the `epic` frontmatter key **and** the `**Epic:** <id>` header line (REQ-DATA-015; inserted after `**Status:**`, updated in place if present) — and an inert `- intake: epic <id> poured` entry appended to `log.md` under the current date heading (REQ-DATA-012). It is idempotent and the intake entry matches neither the `review:` nor `scoping:` audit tokens.
Rationale: The resume guard needs a deterministic epic pointer that survives a crash. The inert `log.md` entry records the linkage without perturbing the review/scoping counts the portability audit keys on.
Verification: `record_epic` in plan_manager.py writes both the `epic` frontmatter key and the `**Epic:**` header line and the `log.md` `intake:` entry; SKILL.md §4.2 invokes it after the pour.

REQ-CLI-013: `plan_manager.py resume-scan <plan-dir> [--json-output|--json]` resolves the plan's epic (plan.md `epic` frontmatter key, then `**Epic:**` header line, then `metadata.plan_dir` fallback — REQ-DATA-015) and returns `{plan_dir, epic_id, epic_source (plan_md|bd_metadata|none), found, counts, total, stuck, open_work_remaining}`. `stuck` lists `in_progress`/claimed descendant beads. bd JSON is parsed defensively (multi-document tolerant). Default output is a human-readable summary; `--json`/`--json-output` emits the structured object.
Rationale: SKILL.md §5.2's resume guard and §4.2's duplicate-pour guard branch on `found`; the coordinator's orphan sweep consumes `stuck`. A machine-readable shape is required for both.
Verification: `_resume_scan`/`resume_scan` in plan_manager.py construct the documented keys; `_parse_bd_json` tolerates concatenated documents; SKILL.md §5.2 and §4.2 consume the JSON via `json-get`.

REQ-CLI-007: All `plan_manager.py` subcommands that produce structured output emit JSON to stdout. `check` and `list` default to human-readable but accept `--json-output` for skill use. `json-get` outputs the extracted value (plain text for scalars, JSON for objects/arrays).
Rationale: SKILL.md parses output via `json-get` or `--json-output` flags — non-JSON in those modes breaks the pipeline.
Verification: Subcommands producing structured output call `click.echo(json.dumps(...))` or `click.echo(data)` for scalar values.

REQ-CLI-008: `plan_manager.py list --json-output` returns an array of objects with keys `id`, `objective`, `status`, `path`.
Rationale: SKILL.md Phase 5.1 and Phase 1.1 filter on `status` to find actionable plans.
Verification: `list_plans` function in plan_manager.py constructs dicts with these 4 keys.

REQ-CLI-009: `plan_manager.py init <objective>` returns JSON with keys `plan_id`, `plan_dir`, `plan_md`, `index_md`, `context_md`, `references_dir`, `reviews_dir`. The orientation surface is the OKF-reserved `index.md` (replacing the legacy `README.md`, REQ-PORT-001), so the key is `index_md`.
Rationale: SKILL.md Phase 1.2 extracts `plan_id` and `plan_dir` for downstream operations. The portability-scaffolding keys let SKILL.md verify all contract seed files were created.
Verification: `init` function in plan_manager.py merges `seed_portability_scaffolding` return into the result dict.

REQ-CLI-011: `plan_manager.py audit <plan-dir> [--json-output] [--retro]` returns structured findings (list of `{item, status, detail}` with status in `pass|fail|warn`) plus an overall `status` (`pass` or `fail`). Exit code is `0` on `pass`, `1` on `fail`. Warn findings do not degrade overall status (grandfather clause). `--retro` is plumbing only (REQ-PORT-033): it surfaces a `"retro"` boolean in the output for the capture orchestration but does not alter the mechanical verdict.
Rationale: SKILL.md Phase 4 inserts the audit between `update-status approved` and `bd mol pour`; it needs a machine-readable shape for the halt decision and a human-readable report for operator display. The `--retro` passthrough keeps the `/yf-plan capture` invocation surface uniform without putting conversation mining in the script.
Verification: `_audit_plan` in plan_manager.py constructs `{status, findings, report, grandfathered}`; the `audit` command adds `result["retro"]` and exits 0/1 based on status.

REQ-CLI-014: `plan_manager.py ready-check <plan-dir> [--json-output|--json]` gates the approval prompt (REQ-PLAN-066). It verifies BOTH preconditions — the **last recorded** red-team verdict (highest `reviews/pass-N.md`, parsed from its `## Verdict:` line) is `APPROVE`, and the portability `audit` passes — and emits `{ready, reasons, verdict, review_pass, audit_status}`. Exit code is `0` when ready and `3` when not ready (a gate signal distinct from the `1` audit-fail/crash code).
Rationale: SKILL.md Phase 3 runs `ready-check` before soliciting operator approval so approval is consent to an already-verified plan, never "approve, then verify". Keying on the *last* verdict (not any earlier APPROVE) enforces the mandatory red-team re-run after a REVISE. Exit 3 lets the SKILL branch on a gate-not-ready distinctly from a script error.
Verification: `ready_check` in plan_manager.py calls `_latest_review_verdict` + `_audit_plan`, builds `{ready, reasons, ...}`, and `sys.exit(0 if ready else 3)`; `test_worktree.py` covers not-ready-on-REVISE, not-ready-on-audit-fail, ready-on-both-green, and the exit-code contract.

REQ-CLI-015: `plan_manager.py classify-deliverable <plan-dir> [--changed <path>]... [--json-output|--json]` (REQ-PLAN-069a) scans the plan's epics/upstream/success-criteria text and any `--changed` merged-tree paths for ci-release signals and returns `{suggested_class, signals, confidence}` — `suggested_class` in `ci-release|standard`, `signals` the matched tokens, `confidence` `high` (a `.github/workflows/**` path or a release/sign/notarize signal) or `low` (keyword-only). It is a pure read (no mutation). `set-deliverable-class <plan-dir> <ci-release|standard>` writes the operator-confirmed value via the REQ-DATA-015 dual-write field writer (idempotent).
Rationale: detection is suggest-then-confirm — the heuristic nudges, the operator decides. A deterministic `{suggested_class, signals, confidence}` contract makes the classifier unit-testable; separating the read (`classify-deliverable`) from the write (`set-deliverable-class`) keeps mutation explicit.
Verification: `scripts/test_complete_gate.py` asserts signal detection, the `standard` default, and `high`/`low` confidence; a round-trip test writes `deliverable_class`, calls `update-status`, and asserts the field survives the field-block rewrite (REQ-DATA-015).

REQ-CLI-016: `plan_manager.py complete-gate <plan-dir> [--json-output|--json]` (REQ-PLAN-069) reads `deliverable_class`; for `ci-release` it passes iff a `log.md` `- validated:` bullet exists (REQ-DATA-016) OR an open out-of-tree bead with label `deferred-validation` + metadata `{"plan":"<plan-id>"}` exists (via `bd list --label deferred-validation`), else it fail-louds (exit non-zero + JSON `{passed:false, reason, remediation}`). For `standard`/absent it is a clean pass (`{passed:true, noop:true}`). Exit code `0` on pass, non-zero on halt — mirroring `close_cascade.py`.
Rationale: the gate is the machine-checkable hard precondition RECONCILE §6.4 halts on; a non-zero exit lets SKILL.md branch exactly as it does on the cascade-close block.
Verification: `scripts/test_complete_gate.py` covers ci-release halt-with-neither (non-zero), pass-with-`validated:`-bullet, pass-with-out-of-tree-deferred-bead, and no-op-for-standard/absent; and asserts an out-of-tree deferred bead is not seen as a plan-tree open child by cascade-close (dry-run).

REQ-CLI-017: `plan_manager.py attest-validation <plan-dir> <run-url-or-id> [--note <text>]` appends a well-formed `- validated: <run> — <note>` bullet to `log.md` under the current date heading via `okf.append_log` (REQ-DATA-016). A hand-written bullet is equally valid; this verb is a convenience that guarantees the recognized form.
Rationale: gives the operator a one-command way to record the green-execution attestation in the canonical `log.md` shape complete-gate matches, without hand-editing.
Verification: `scripts/test_complete_gate.py` asserts the appended bullet matches the `- validated:` form and that it perturbs neither `_plan_review_line_count` nor the grandfather-date parser (REQ-DATA-016 non-status token).

REQ-CLI-010: `plan_manager.py` is invoked via `uv run` with inline script metadata, not installed as a package.
Rationale: Keeps the skill self-contained with no build step; `uv` resolves dependencies from the script header.
Verification: Script begins with `# /// script` PEP 723 metadata block.
