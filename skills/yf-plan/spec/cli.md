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

REQ-CLI-005: If the operator config contains `"ignore-skill": true`, the skill exits silently and falls back to native plan mode. Canonical config is `.yf/plan/config.local.json`; the manager script currently reads only the legacy root `.yf-plan.local.json` (canonical-first read tracked in `dixson3/yoshiko-flow#100`), which remains a supported fallback.
Rationale: Projects that can't satisfy prerequisites need a clean opt-out without repeated error messages.
Verification: SKILL.md Pre-flight bullet 2; `_check_prerequisites()` in plan_manager.py returns `{"status":"ignored"}`.

## plan_manager.py CLI

REQ-CLI-006: `plan_manager.py` exposes 10 subcommands: `check`, `json-get`, `init`, `scope`, `triage`, `list`, `update-status`, `record-epic`, `resume-scan`, `audit`. *(plan-044: no subcommand is added — the `**Epic:**` resolution check lands as audit check #9 inside the existing `audit`/`audit-close` verbs (REQ-CLI-020) and as an added output key on the existing `resume-scan` (REQ-CLI-013), so this enumeration is unchanged. Recorded explicitly because the amendment was considered and found unnecessary, not overlooked.)*
Rationale: These are the mechanical operations SKILL.md delegates; missing any breaks the wiring. `audit` was added to support the portability precondition check at intake and the `/yf-plan capture` maintenance subcommand. `record-epic` and `resume-scan` were added for coordinator crash recovery (#2): the first persists the plan↔epic linkage at intake, the second reports it back for the resume guard. The companion rule is installed by the repo installer (`install.sh`), not by `init`, so no `rules-dir` subcommand is needed; preflight locates the installed rule internally via `_rule_candidates()`/`_check_rule()`.
Verification: `grep '@cli.command' skills/yf-plan/scripts/plan_manager.py` returns 10 matches.

REQ-CLI-012: `plan_manager.py record-epic <plan-dir> <epic-id>` persists the plan↔epic linkage in the bundle: the epic id in plan.md's header metadata — dual-written as the `epic` frontmatter key **and** the `**Epic:** <id>` header line (REQ-DATA-015; inserted after `**Status:**`, updated in place if present) — and an inert `- intake: epic <id> poured` entry appended to `log.md` under the current date heading (REQ-DATA-012). It is idempotent and the intake entry matches neither the `review:` nor `scoping:` audit tokens.
Rationale: The resume guard needs a deterministic epic pointer that survives a crash. The inert `log.md` entry records the linkage without perturbing the review/scoping counts the portability audit keys on.
Verification: `record_epic` in plan_manager.py writes both the `epic` frontmatter key and the `**Epic:**` header line and the `log.md` `intake:` entry; SKILL.md §4.2 invokes it after the pour.

REQ-CLI-013: `plan_manager.py resume-scan <plan-dir> [--json-output|--json]` resolves the plan's epic (plan.md `epic` frontmatter key, then `**Epic:**` header line, then `metadata.plan_dir` fallback — REQ-DATA-015) and returns `{plan_dir, epic_id, epic_source (plan_md|bd_metadata|none), found, epic_resolves, counts, total, stuck, open_work_remaining}`. **`epic_resolves`** *(plan-044, #143)* is `true` when the resolved epic id actually **exists in `bd`**, and `false` when the plan records an id that resolves to nothing — the **dangling-ref** case. This is the distinction the execute path turns on: a dangling ref yields `found: true, total: 0`, which is indistinguishable from a legitimately completed plan, so execute reads "no open work" and **skips the plan entirely** — a silent false success. `resume-scan` is the only verb the execute path consults, which is why the signal belongs here and not solely in `audit`. `stuck` lists `in_progress`/claimed descendant beads. bd JSON is parsed defensively (multi-document tolerant). Default output is a human-readable summary; `--json`/`--json-output` emits the structured object.
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

REQ-CLI-020: *(plan-044, #143)* `_audit_plan` shall carry a **check #9**: a plan.md `**Epic:**` reference **shall resolve** via `bd`. A recorded id that resolves to nothing is a **`fail`** finding, raised at **`missing_level`** — explicitly **not** `okf_missing_level`, which would downgrade every legacy bundle to `warn` and thereby suppress the exact 14 dangling refs this check exists to surface. When **`bd` is unavailable** the finding is **`warn`**, not `fail`: a plan bundle is portable by contract and must not hard-fail merely for being read on a machine with no beads database. One implementation serves **both** consumers — the halting `audit` gate (REQ-CLI-011) and the advisory `audit-close` (REQ-CLI-019) — so the two can never disagree about whether a ref resolves.

REQ-CLI-014: `plan_manager.py ready-check <plan-dir> [--json-output|--json]` gates the approval prompt (REQ-PLAN-066). It verifies BOTH preconditions — the **last recorded** red-team verdict (highest `reviews/pass-N.md`, parsed from its `## Verdict:` line) is `APPROVE`, and the portability `audit` passes — and emits `{ready, reasons, verdict, review_pass, audit_status}`. Exit code is `0` when ready and `3` when not ready (a gate signal distinct from the `1` audit-fail/crash code).
Rationale: SKILL.md Phase 3 runs `ready-check` before soliciting operator approval so approval is consent to an already-verified plan, never "approve, then verify". Keying on the *last* verdict (not any earlier APPROVE) enforces the mandatory red-team re-run after a REVISE. Exit 3 lets the SKILL branch on a gate-not-ready distinctly from a script error.
Verification: `ready_check` in plan_manager.py calls `_latest_review_verdict` + `_audit_plan`, builds `{ready, reasons, ...}`, and `sys.exit(0 if ready else 3)`; `test_worktree.py` covers not-ready-on-REVISE, not-ready-on-audit-fail, ready-on-both-green, and the exit-code contract.

REQ-CLI-015: `plan_manager.py classify-deliverable <plan-dir> [--changed <path>]... [--json-output|--json]` (REQ-PLAN-069a) returns `{suggested_class, signals, confidence, evidence}` and is a pure read (no mutation). Its contract:

- **Scan region.** Prose matching is restricted to the plan's **Epics**, **Upstream Issues**, and **Success Criteria** sections — not the whole file. The H1/title, Objective, Motivation, Approach, Investigation Findings, and Risks sections are out of region.
- **Code is not prose.** Fenced code blocks and inline code spans are stripped from the scan region before matching: a trigger word inside a command, a regex, or a quoted example is not a claim that the plan ships releases.
- **Negative-context guards.** A known-incomplete blocklist suppresses demonstrated collisions (`self-signed`, `signed certificate`, upstream release cadence, `(metrics|logs|traces) pipeline`, `deployed by`). It carries a **stop rule**: no pattern is added without a corpus re-measurement showing it moves `FP`.
- **A `ci-release` suggestion requires a high-tier signal.** Low-tier-only matches are reported in `signals` as informational with `suggested_class: standard`.
- **`confidence` and `evidence` are honest.** `confidence: high` is reserved for the `.github/workflows/**` path marker (the only non-prose signal); prose-only matches are `low`. Because `--changed` is empty at intake (SKILL.md §4.1.5), `confidence` is effectively constant there, so `evidence` reports the basis — `path-backed` | `prose-only` — and is what SKILL.md surfaces to the operator.

`set-deliverable-class <plan-dir> <ci-release|standard>` writes the operator-confirmed value via the REQ-DATA-015 dual-write field writer (idempotent).
Rationale: detection is suggest-then-confirm — the heuristic nudges, the operator decides — but a suggestion that is always the same value carries no information. Measured across 53 real plans, the unrestricted keyword scan suggested `ci-release` on 40, and on **all 17** plans carrying an operator-confirmed class it was wrong 16 times with **zero** correct negatives, while reporting `confidence: high`. The four contract corrections above were each measured for their individual effect, with `FN=0` (no genuine `ci-release` plan misclassified) preserved at every step — recall is the safety-critical direction, since a false positive costs an operator seconds at intake while a false negative silently disables a completion gate. `evidence` exists because `confidence` alone cannot be honest at the point it is read.
Verification: `scripts/test_complete_gate.py` asserts signal detection, the `standard` default, and `high`/`low` confidence; `scripts/test_classify_deliverable.py` runs the vendored labeled-plan fixture corpus, asserting `FN=0` and non-increasing `FP` at every step plus a dedicated fixture pinning the code-span/fenced-block exclusion; a round-trip test writes `deliverable_class`, calls `update-status`, and asserts the field survives the field-block rewrite (REQ-DATA-015).

REQ-CLI-016: `plan_manager.py complete-gate <plan-dir> [--json-output|--json]` (REQ-PLAN-069) is a **`halting`** step of the §6.4 chain with **`command`** remediation-kind, and honours the REQ-COMPLETE-003 verdict envelope. It reads `deliverable_class`; for `ci-release` it passes iff a `log.md` `- validated:` bullet exists (REQ-DATA-016) OR an open out-of-tree bead with label `deferred-validation` + metadata `{"plan":"<plan-id>"}` exists (via `bd list --label deferred-validation`), else it fail-louds. For `standard`/absent it is a clean pass (`verdict: "pass"`, `noop: true`). A missing `plan.md` is `verdict: "fail"` (halting) — the answer is definite, not undeterminable, so a typo'd `plan-dir` must not sail through to `set complete`.

**The verdict JSON goes to STDOUT on EVERY path, including failure** — this requirement previously *claimed* the verb mirrored `close_cascade.py` while both of its failing paths in fact wrote to **stderr**. That was a measured live defect, not a documentation nit: SKILL.md §6.4 captures the verb with `GATE=$(…)`, which captures stdout only, so `echo "$GATE"` printed an **empty string** on exactly the path an operator needs to read. The mirroring claim is now true rather than aspirational. Exit code `0` on pass, non-zero on halt.
Rationale: the gate is the machine-checkable hard precondition RECONCILE §6.4 halts on; a non-zero exit lets SKILL.md branch exactly as it does on the cascade-close block. A verdict the documented capture idiom cannot see is equivalent to no verdict at all, which is the same "green while a step silently did not run" shape §6.4 exists to prevent.
Verification: `scripts/test_complete_gate.py` covers ci-release halt-with-neither (non-zero), pass-with-`validated:`-bullet, pass-with-out-of-tree-deferred-bead, and no-op-for-standard/absent; and asserts an out-of-tree deferred bead is not seen as a plan-tree open child by cascade-close (dry-run). `scripts/test_close_contract.py` asserts the **failing** path yields a non-empty, envelope-conformant capture under the documented `X=$(…)` idiom — the check that failed before this amendment.

REQ-CLI-018: `plan_manager.py verify-reconcile <plan-dir> [--json-output|--json]` (REQ-PLAN-074) is a **`halting`** §6.4 step with **`command`** remediation-kind. It parses plan.md's `## Upstream Issues` table via the shared `parse_upstream_rows` and, for every **non-`exclude`** row, queries `gh issue view <n> --json state,stateReason,comments,title` under a bounded timeout, asserting the per-disposition end state of REQ-PLAN-074. The envelope carries `rows: [{issue, disposition, verdict, detail}]` plus the REQ-COMPLETE-003 keys, emitted as JSON **to stdout on every path**. Aggregate: any row `fail` → `fail` (exit non-zero); else any row `inconclusive` → `inconclusive` (exit **0** — it never halts); else `pass`. A `tracker` row is `inconclusive` by construction: the coarse tracker is closed by the land-the-plane sweep, not by reconciliation, so it carries no end-state contract.
Rationale: an `include` row silently left OPEN is invisible to every other close-step check — the cascade sees a closed bead tree, the completion gate is a no-op for a `standard` plan, and `set complete` asks nothing. Exit-code asymmetry between `fail` and `inconclusive` is the whole point: it makes a GitHub outage cost a report rather than a blocked completion.
Verification: `scripts/test_verify_reconcile.py` (mocked `gh`, no network) — per-disposition pass/fail, the state-OK-but-no-mention failure, `exclude` skipped, checker-error → `inconclusive` at exit 0, mixed `fail`+`inconclusive` → `fail`, and `[#N]`/`#N` row-shape variants.

REQ-CLI-019: `plan_manager.py audit-close <plan-dir> [--json-output|--json]` (REQ-PLAN-075) is an **`advisory`** §6.4 step with **`prose`** remediation-kind. It runs the same `_audit_plan` engine as `audit` and emits `{verdict, passed, advisory: true, audit_status, findings, fail_count, warn_count, grandfathered, reason, remediation}` as JSON **to stdout on every path**. It **exits 0 unconditionally** — including when `verdict` is `fail`. Its `remediation` recommends `/yf-plan capture <plan-id>` and never asserts a halt.
Rationale: the halting difference from `audit` (which exits non-zero on `fail`, correctly, as a pre-INTAKE gate) is expressed as a **separate verb rather than a flag**, so an author cannot wire the halting variant into the close chain by passing the wrong option. Reusing `_audit_plan` rather than reimplementing it keeps close-time and plan-time findings identical by construction.
Verification: `scripts/test_audit_close.py` — failing bundle exits 0; verdict never halting for any finding set; findings identical to `audit`'s; envelope conformance; and the §6.4 ordering assertion parsed from SKILL.md.

REQ-CLI-017: `plan_manager.py attest-validation <plan-dir> <run-url-or-id> [--note <text>]` appends a well-formed `- validated: <run> — <note>` bullet to `log.md` under the current date heading via `okf.append_log` (REQ-DATA-016). A hand-written bullet is equally valid; this verb is a convenience that guarantees the recognized form.
Rationale: gives the operator a one-command way to record the green-execution attestation in the canonical `log.md` shape complete-gate matches, without hand-editing.
Verification: `scripts/test_complete_gate.py` asserts the appended bullet matches the `- validated:` form and that it perturbs neither `_plan_review_line_count` nor the grandfather-date parser (REQ-DATA-016 non-status token).

REQ-CLI-010: `plan_manager.py` is invoked via `uv run` with inline script metadata, not installed as a package.
Rationale: Keeps the skill self-contained with no build step; `uv` resolves dependencies from the script header.
Verification: Script begins with `# /// script` PEP 723 metadata block.
