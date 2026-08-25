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

REQ-CLI-005: If the operator config contains `"ignore-skill": true`, the skill exits silently and falls back to native plan mode. Canonical config is `.yf/plan/config.local.json`. The canonical-first read is **delivered** (#100, closed): `_read_config()` merges the three tiers key-by-key with `.yf/plan/config.local.json` > `.yf/plan/config.json` > the legacy root `.yf-plan.local.json`, which remains a supported fallback and is never removed. *(This sentence previously said the script "currently reads only the legacy root" — that was true before #100 landed and has been stale since.)*
Rationale: Projects that can't satisfy prerequisites need a clean opt-out without repeated error messages.
Verification: SKILL.md Pre-flight bullet 2; `_check_prerequisites()` in plan_manager.py returns `{"status":"ignored"}`.

## plan_manager.py CLI

REQ-CLI-006: `plan_manager.py` exposes its subcommands **flat** — one `@cli.command("<name>")`-decorated function per verb. The **normative requirement is a self-consistency invariant, not a number**:

> the set of verbs enumerated in this REQ **equals** the set of `@cli.command` names in `skills/yf-plan/scripts/plan_manager.py`.

The enumeration (currently **29**): `json-get`, `init`, `scope`, `triage`, `list`, `parked`, `update-status`, `stamp-tracker`, `record-epic`, `set-deliverable-class`, `classify-deliverable`, `attest-validation`, `complete-gate`, `verify-reconcile`, `commit-plan`, `validate-merged`, `resume-scan`, `audit`, `close-reconcile-step`, `audit-close`, `ready-check`, `config-resolve` (REQ-CLI-021), `retrospective-append` (REQ-CLI-022), `retrospective-report` (REQ-CLI-022), `review-loop-check` (REQ-CLI-023), `resolve-start-gate` (REQ-PLAN-077), `grant` (REQ-CLI-025), `ownership-report` (REQ-DATA-071), `recheck-criteria` (REQ-PLAN-080).

Adding a verb **requires** adding it here. The count is written as *currently N* precisely because it is a **derived** fact: the invariant is the set equality, and the number is a convenience that the executing check re-derives. Separately, `plan_manager.py` also exposes the click **groups** `fingerprint`, `worktree` and `landing-lock`, whose subcommands are registered on the group (`@fingerprint.command`, etc.) and are therefore **outside** both the enumeration and the check — which is why REQ-CLI-021 mandates the flat form.
Rationale: These are the mechanical operations SKILL.md delegates; missing any breaks the wiring. This REQ has drifted **three times**: it read 10 while the script carried 21; plan-045 corrected it to 23, then to 24 when `review-loop-check` landed; and it was *still* wrong at 25 because `retrospective-report` was added in the same epic that fixed the previous drift. Each fix bumped a hardcoded literal, which is a repair that re-breaks on the very next verb.

The third drift is the instructive one: it survived a full green sweep because **nothing executed the Verification line** — it was prose shaped like a command, so the FULL validation tier passed 33/33 while this REQ asserted something false. That is exactly the defect class `dixson3/yoshiko-flow#149` names (a process rule nothing executes), reproduced inside the spec of the plan that cites #149. Hence both changes here: the requirement is restated as a set equality that cannot go stale by arithmetic, **and** the verification was moved into a test that actually runs. `audit` was added to support the portability precondition check at intake and the `/yf-plan capture` maintenance subcommand. `record-epic` and `resume-scan` were added for coordinator crash recovery (#2): the first persists the plan↔epic linkage at intake, the second reports it back for the resume guard. The companion rule is installed by the repo installer (`install.sh`), not by `init`, so no `rules-dir` subcommand is needed; preflight locates the installed rule internally via `_rule_candidates()`/`_check_rule()`.
Verification: **executed**, not asserted — `skills/yf-plan/scripts/test_cli_enumeration.py` parses this REQ's enumeration and the `@cli.command` names from `plan_manager.py` and asserts the two **sets** are equal, naming any verb missing from either side. It is registered as CHANGE-VALIDATION id `uv-yf-cli-enum` and fires on edits to both `skills/yf-plan/scripts/**` and `skills/yf-plan/spec/cli.md`, so adding a verb without amending this REQ is a hard failure at the point of the change. The former hand-run `grep -c '^@cli.command' … returns N` is retained only as the human-readable form of the same check.

REQ-CLI-024: `update-status` shall accept the override flag **`--override-ready-check`** —
**not** a bare `--force` — to authorize the `approved` transition on a red `ready-check`
(REQ-DATA-028). Using it shall write the status **and** append both a `log.md` override line
and a `retrospective-append --kind deviation` entry naming the flag.

**The name was decided BEFORE the implementation** (plan-047 Issue 2.6), because the drafted
plan claimed a collision with "the existing stale-approval `--force`" and the red-team measured
that `update_status` has **no options besides `-m`**: the existing `--force` overrides are a
**prose convention** (SKILL.md's deviation table: *"Every `--force` override (stale-approval,
audit bypass)"*), not a flag on this verb. So there was no flag to collide with — but there is a
real deviation-vocabulary overlap, and that is what the choice turns on:

- **A distinct name, because `--force` is already overloaded on other verbs and means different
  things on each**: file overwrite on `capture`, stale-approval bypass on `execute`, lock
  stealing on `landing-lock release`, dirty-tree override on `worktree teardown`.
  `update-status` writes **nine** different statuses, so a bare `--force` there would not say
  *what* it forces — and the one thing it must never be read as forcing is a status the plan has
  not earned.
- **It stays in the `--force` deviation FAMILY** for retrospective purposes: the entry is
  recorded exactly like the other overrides, so the vocabulary overlap is resolved at the name
  and not at the audit trail.
- It is greppable: `--override-ready-check` has exactly one meaning repo-wide.

Rationale: an override that does not name what it overrides is how a bypass becomes routine.
Verification: `scripts/test_update_status_gate.py` asserts the flag name, that the transition is
refused without it, that it succeeds with it, and that the deviation entry names it.

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

REQ-CLI-021: `plan_manager.py config-resolve [--json]` reports each autonomy-relevant config key's **effective value and its `source`**, where `source` is one of `flag`, `config.local`, `config.json`, `legacy`, or `default` — the resolution precedence in order. It is registered **flat** as `@cli.command("config-resolve")`, never as a `config` click group with a `resolve` subcommand. It is a pure read: it exits `0`, mutates nothing, and emits JSON on stdout on every path **including failure** (REQ-CLI-016). It accepts `--json` and `--json-output` as aliases.
Rationale: A resolved value alone is undebuggable — the recurring question is not *what is autonomy set to* but *which of the five tiers won*, and a value without its source cannot answer it. The flat registration is required, not stylistic: REQ-CLI-006's Verification greps `@cli.command`, which does not match a group-registered subcommand, so a `config` group would make the enumeration and its verification disagree by construction. Nothing in the existing three-tier reader forces a group.
Verification: `plan_manager.py config-resolve --json` emits an object whose every key carries both `value` and `source`; `test_cli_enumeration.py` asserts it is present in the REQ-CLI-006 enumeration; invoking it against an unreadable config still emits JSON and exits 0.

REQ-CLI-022: `plan_manager.py retrospective-append <plan-dir> [--json]` appends one `## RE-NNN` entry to the bundle's `plan-retrospective.md`, creating the file (with `type: Retrospective` + `okf_spec: OKF-PLAN` frontmatter) when absent, and adding it to the reserved `index.md` listing. The append is **idempotent** on entry identity and allocates `RE-NNN` monotonically without reusing or renumbering an existing id. It is registered flat as `@cli.command("retrospective-append")`.
Rationale: Mirrors `okf.append_log`'s create-if-absent + idempotence contract, which is the established shape for a reserved-member writer in this bundle. It is implemented **locally** rather than by generalizing `append_log`, which is vendored in four byte-identical copies behind `e-okf-copy-*` drift edges — generalizing it would require changing all four in lockstep. Adding the `index.md` listing entry in the same verb keeps the bundle's cold-reader contract intact: a member absent from the listing is exactly the portability gap the file exists to help close.
Verification: appending to a bundle with no `plan-retrospective.md` creates a conformant file listed in `index.md`; appending twice with the same entry yields one entry; ids increase monotonically across appends; `test_cli_enumeration.py` asserts it is present in the REQ-CLI-006 enumeration.

REQ-CLI-023: `plan_manager.py review-loop-check <plan-dir> [--max-review-cycles <n>] [--json]` bounds the autonomous review loop (2.4a). It exits `3` when the loop must escalate and `0` otherwise, emitting `{"escalates", "cycles", "limit", "stop_class", "autonomy", "raised", "remediation"}`. The cycle count is `len(glob('reviews/pass-*.md'))`. `--max-review-cycles` raises the bound **for that invocation only** and echoes the raise to `log.md`. Registered flat as `@cli.command("review-loop-check")`.
Rationale: Issue 2.4 grants the review loop autonomy in **Phase 3 — before intake, before the pour, before any bead exists** — so `yf_attempts` (bd metadata, incremented in the coordinator loop) structurally cannot bound it. Without a second, plan-phase counter the headline autonomy change would be unbounded, which is the shape D-8 forbids. The count reads pass **files** rather than `log.md` **bullets** because those are different numbers that can and do diverge, and a bound keyed on the wrong one would escalate on a bookkeeping artifact. The counter is monotonic and deliberately does **not** auto-reset: a plan that has burned `N` review cycles should not silently resume, so the per-invocation raise is the only exit and is recorded.
Verification: a bundle with `N` pass files exits `3`; the same bundle with `--max-review-cycles N+1` exits `0` and appends a `log.md` entry; removing the raise re-escalates immediately; `test_cli_enumeration.py` asserts it is present in the REQ-CLI-006 enumeration.

REQ-CLI-025: `plan_manager.py grant <plan-dir> [--json]` **generates** the upstream-write
authorization grant from the plan's own **Upstream Issues** table — the set of upstream actions
the plan's dispositions require, enumerated per row — and emits it as a **proposal**. It:

- **never writes** the authorization file and never performs an upstream write;
- **requires no network** to generate, so it is runnable before any `gh` call;
- reads its per-disposition requirement from the **one shared table** keyed by the
  `UPSTREAM_DISPOSITIONS` literals that `_verify_row` also reads, so generator and verifier
  cannot disagree about what a disposition requires;
- covers **every** literal in `UPSTREAM_DISPOSITIONS`, including `exclude`, `deferred` and
  `tracker` — a generator that silently omits a disposition is #181's defect class in a new
  place;
- honours the REQ-COMPLETE-003 envelope and is registered **flat** as `@cli.command("grant")`
  (REQ-CLI-021), so REQ-CLI-006's set-equality check sees it.

Rationale: #178. plan-048 **halted its own reconcile** on an omitted `include` close: the grant
was derived by hand from the table, one row was missed, and the omission surfaced only at
`verify-reconcile` — a late halt after the outward-facing writes had begun. plan-049 avoided it
only because the operator re-derived the grant by hand a second time. The two readers of the
disposition→end-state map (what the grant asks for, and what the verifier requires) were separate
prose derivations of the same rule; making them one table read is what removes the class rather
than the instance. The extraction is a **separate step** from the generator because `_verify_row`
as it stands cannot serve as the source: it returns no `required_action`, is network-bound
(`gh issue view` per row), and returns `fail` on an `exclude` row handed to it directly — a
literal that IS in the frozenset (measured, pass-3 C12).
Verification: `ctl-178-grant` replays plan-048's **actual recorded grant with the `#172` close
omitted** and drives the round-trip check non-zero; the shared read is asserted **behaviorally** —
mutate one entry in a throwaway copy of the table, re-run `grant` and `_verify_row` with
`_gh_issue_view` stubbed to a fixed payload, and assert **both** verdicts change; every literal
in `UPSTREAM_DISPOSITIONS` has exactly one table entry; `test_cli_enumeration.py` asserts `grant`
is present in the REQ-CLI-006 enumeration.

