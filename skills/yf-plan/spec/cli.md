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

The enumeration (currently **32**): `json-get`, `init`, `scope`, `triage`, `list`, `parked`, `update-status`, `stamp-tracker`, `record-epic`, `set-deliverable-class`, `classify-deliverable`, `attest-validation`, `complete-gate`, `verify-reconcile`, `commit-plan`, `validate-merged`, `resume-scan`, `audit`, `close-reconcile-step`, `audit-close`, `ready-check`, `config-resolve` (REQ-CLI-021), `retrospective-append` (REQ-CLI-022), `retrospective-report` (REQ-CLI-022), `review-loop-check` (REQ-CLI-023), `resolve-start-gate` (REQ-PLAN-077), `grant` (REQ-CLI-025), `ownership-report` (REQ-DATA-071), `recheck-criteria` (REQ-PLAN-080), `gate-consistency` (#113), `verify-beads` (#197), `clear-epic` (REQ-CLI-027).

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
  `update-status` writes **ten** different statuses, so a bare `--force` there would not say
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

REQ-CLI-013: `plan_manager.py resume-scan <plan-dir> [--json-output|--json]` resolves the plan's epic (plan.md `epic` frontmatter key, then `**Epic:**` header line, then `metadata.plan_dir` fallback — REQ-DATA-015) and returns `{plan_dir, epic_id, epic_source (plan_md|bd_metadata|none), found, epic_resolves, epic_state, epic_status, epic_plan_dir, counts, total, stuck, open_work_remaining}`.

**`epic_state`** *(plan-053, #207)* is the **six-valued** field the execute path shall branch on:

| `epic_state` | Means | What EXECUTE does |
| :-- | :-- | :-- |
| `none` | the plan records no epic | **pour** — the normal first execution |
| `present` | the epic resolves and has open work | **resume** |
| `complete` | the epic resolves and all its work is terminal | resume (nothing left to do) — never re-pour |
| `stale` | the plan records an id that resolves to **nothing** (the burned/dangling ref) | **pour** — the recorded pointer is dead, so there is nothing to resume |
| `foreign` | the epic resolves but its `metadata.plan_dir` names a **different** bundle | **halt** for an operator decision — a copied bundle must never silently resume another plan's epic |
| `unknown` | the state could not be determined (`bd` unavailable or unreadable) | **halt as INCONCLUSIVE** — never pour |

`epic_state` exists because **`found` is one boolean carrying two facts** — "a pointer is
recorded" and "that pointer is live" — and the two have opposite handling. That is the same
conflation as `doc_lint`'s `not-selected` vs `no-such-path` (#181), and the remedy is the same:
**add a field that names the state and branch on it, never on the flag.** `epic_status` is the
epic bead's own `status` (or `null`), and `epic_plan_dir` is the `metadata.plan_dir` the epic
carries (or `null`) — the two signals `foreign` is derived from, surfaced so a caller can report
*why* rather than only *that*.

**`found` and `epic_resolves` keep their existing meanings verbatim**, unchanged and still
emitted, so every existing consumer is unaffected. `epic_state` is additive: it is derived from
signals already in hand, and shall **not** re-implement the existence check `epic_resolves`
already performs.

`unknown` is a first-class value and **not** a synonym for "gone". An unreachable tracker looks
exactly like a burned epic, and guessing "gone" produces the duplicate pour REQ-RESUME-004 exists
to prevent. **`epic_resolves`** *(plan-044, #143)* is `true` when the resolved epic id actually **exists in `bd`**, and `false` when the plan records an id that resolves to nothing — the **dangling-ref** case. This is the distinction the execute path turns on: a dangling ref yields `found: true, total: 0`, which is indistinguishable from a legitimately completed plan, so execute reads "no open work" and **skips the plan entirely** — a silent false success. `resume-scan` is the only verb the execute path consults, which is why the signal belongs here and not solely in `audit`. `stuck` lists `in_progress`/claimed descendant beads. bd JSON is parsed defensively (multi-document tolerant). Default output is a human-readable summary; `--json`/`--json-output` emits the structured object.
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


REQ-CLI-026: **`update-status` shall WARN on an unrecognised status, on stderr, and still exit
0.** When the status argument is not in REQ-STATUS-001's vocabulary, `update-status` shall write
the status as asked and emit a warning to **stderr only** naming (a) the value written, (b) the
full recognised vocabulary, and (c) the three known consequences of writing outside it — the plan
is invisible to `list`'s status filters, `_is_parked` will not classify it, and `doc_lint`'s
`STATUS_SEVERITY` treats it fail-closed (REQ-DATA-072).

**The exit code stays 0, and that is the requirement, not an omission.** `update-status` is not a
gate; refusing the write would strand a plan whose operator has a reason this vocabulary does not
yet cover, which is the failure mode #208 was filed about in the first place. The warning removes
the *silence*, which is the actual defect — the write was accepted with no signal whatsoever, so
an invented status looked exactly like a supported one. `scripts/test_update_status_gate.py`
asserts exit **0** for every non-`approved` status, so a non-zero exit here would flip a passing
assertion on a behaviour that is deliberate.

Warning on **stderr only** is what keeps the verb composable: `--json` consumers parse stdout, and
a warning on stdout would corrupt every one of them.
Rationale: #208. An operator with no legal state for "approved but deliberately not executing"
invented one, and `update-status` accepted it without a word. D-1 takes the widest remedy — the
vocabulary gains a real value for that case (`abandoned`, REQ-STATUS-001), the write warns instead
of being silent, and the linter stops treating an unknown status as permissive.
Verification: `scripts/test_update_status_gate.py` asserts an unrecognised status writes, warns on
stderr, and exits 0, and that `abandoned` is accepted with **no** warning.

REQ-CLI-027: *(plan-053, #207)* `plan_manager.py clear-epic <plan-dir> [-m REASON] [--force]
[--json]` shall clear a plan's recorded epic pointer — removing **both** dual-written surfaces
(REQ-DATA-015): the `epic` frontmatter key **and** the `**Epic:**` header line. It shall **keep**
the existing `- intake: epic <id> poured` history bullet in `log.md` and **append** a
`- pointer cleared` bullet, so the record of what was poured survives the clearing of the pointer
to it. Both bullets are inert tokens: neither advances `status`, and neither matches the
`review:` or `scoping:` audit regexes, so REQ-PORT-006's count-equality is untouched.

The verb is **idempotent** (clearing an already-clear plan is a reported no-op at exit 0) and
**refuses without `--force`** when `epic_state` is `present` or `unknown` — clearing a live
pointer strands real work, and clearing one whose state could not be determined is that same act
performed blind.

It shall report **`metadata_fallback_remains`**. Measured: clearing the two plan.md surfaces does
**not** on its own reopen the pour path, because `_resume_scan` falls back to the epic bead's
`metadata.plan_dir` stamp (REQ-CLI-013), so a surviving epic bead is still found. A verb that
appears to succeed and changes nothing is the silent-success class this plan exists to close, so
the residual fallback is **reported**, never silently tolerated.
Rationale: #207. A plan whose epic was burned records a pointer to nothing and has no supported
way to drop it — the operator's only recourse was hand-editing plan.md, which reliably updates one
of the two dual-written surfaces and leaves the other.
Verification: `scripts/test_epic_ref_audit.py` asserts both surfaces are removed, the `intake:`
bullet survives, a `pointer cleared` bullet is appended, a second run is a no-op, `present` and
`unknown` refuse without `--force`, and `metadata_fallback_remains` is reported when the epic bead
still carries a matching `metadata.plan_dir`.

REQ-CLI-028: *(added plan-056 Issue 0.11)* **The test-invocation guard.** A criterion, recipe row,
or check that asserts "a named test ran and passed" shall invoke the test through an instrument that
guarantees two properties. Both are stated because each was violated in this repository, separately.

**(1) Arguments shall be FORWARDED.** A Python test entrypoint invoked as `uv run <test_file.py>
-k <selector>` in this repo **discards `sys.argv`**: every hand-rolled `__main__` block calls
`pytest.main([])` or runs its own loop, so the selector is silently dropped and the whole file runs.
A criterion written in that form therefore asserts *"some test in this file passed"*, not *"the named
test passed"* — and it stays green when the named function is deleted.

**The vacuity is form-specific, and the scope of this rule is exactly that form.** It is **not** true
that pytest exits 0 on a selector matching nothing: measured, module-form
`python -m pytest -k <no-match>` exits **5** (`N deselected`) and `pytest <missing-file>` exits **4**.
`CHANGE-VALIDATION.md` already recorded this, and the repo's own recipe rows use the module form.
The defect lives **only** in the direct-file form, which the recipe never uses and criteria did.

**(2) A selector matching nothing shall FAIL, never pass.** The instrument shall first assert the
named function exists (a `def <name>` grep against the target), then run it, then require a
**non-zero passed count** — three separate assertions, because each of the three failure modes
(function renamed away, file moved, collection error) produces a different wrong answer under the
other two.

**PEP 723 dependencies shall be parsed from the TARGET and forwarded.** Measured:
`uv run --with pytest python -m pytest _shared/test_okf.py` dies at **collection with exit 2**,
because module form makes `python` the entrypoint and the target's own inline dependency header is
never read — while `test_cli_enumeration.py` happens to need nothing and passes. The per-file
dependency set is heterogeneous, so a fixed `--with` list is a guess that is right by luck. Either
parse the target's `dependencies` and forward them, or invoke via `uv run --script`.

**A hand-rolled non-pytest entrypoint shall yield INCONCLUSIVE, never PASS.** Measured:
`_shared/test_doc_lint.py` carries **0** `def test` functions, no pytest import and no `__main__`;
**15** repo test files carry no `__main__` at all. Reporting a green on a file the instrument cannot
drive is the "a check that cannot fail" defect one level up from the check.

**The INCONCLUSIVE code is `2`**, per `scripts/checks/_common.sh` (REQ-CLI-029) — the contract every
instrument in that directory already follows. It is **not** `3`: `redcheck.sh record-red-check`
**refuses to bank a `2`** precisely because a `2` is not a red observation, whereas an invented `3`
would be banked as one, converting "the instrument could not run" into "the criterion was measured
false".

**Codes `126` and `127` remain reserved to the shell.** Returning either would make every criterion
routed through the instrument permanently unfailable, since a caller cannot distinguish the
instrument's verdict from the shell's report that it could not execute the instrument at all.

**Explicitly OUT OF SCOPE: rewriting the repository's `pytest.main` call sites.** The wrapper closes
the gap on its own, and a repo-wide refactor touching every skill does not belong on the critical
path of the criteria that invoke it.
Rationale: three consecutive red-team passes of plan-056 found the criteria layer vacuous, each time
through a different one of the mechanisms above. A criterion that cannot fail is not weaker
evidence; it is no evidence, and it is worse than none because it reads as evidence.
Verification: `scripts/checks/check-pytest-ran.sh <file> <test-name>` exits non-zero for a name that
does not exist in the file and zero for one that does — a pair of exits that differ, so a missing
instrument cannot satisfy the criterion.

REQ-CLI-029: *(added plan-056 Issue 0.14)* **The check-harness contract for `scripts/checks/`.**
Every executable check in `scripts/checks/` shall honour the three-valued exit contract its shared
preamble `_common.sh` already declares — **`0` the criterion holds · `1` it does not · `2` the check
could NOT RUN** — and shall additionally satisfy the three properties below, which `_common.sh` does
not yet state.

**(a) Two-branch where it asserts a failure code.** A check whose criterion is "X returns a
*different* exit than Y" shall assert **both** exits and that they **differ**. A check asserting only
"X returns non-zero" is satisfied by X being **absent**: `uv run <missing>.py` itself exits 2, which
silently satisfied two criteria in an earlier draft of this plan. The pair is what distinguishes
*correct* from *merely absent*.

**(b) Fail loudly on an empty inspection.** A check that enumerates its own input set shall report
how many items it inspected and shall return non-zero when that count is below a declared floor. A
check that inspected nothing exits 0 on every rule it applies; without a floor, "clean" and "not
read" are the same observation. `--min-roots N` (REQ-OKF-CHK-004) and `--require N` are the two
shipped spellings.

**(c) `126` and `127` are reserved to the CALLER.** No check shall return either. They are the
shell's report that the check could not be executed — a bad shebang, a missing file, a lost
executable bit — and a check that returns them makes its own absence indistinguishable from its
verdict.

**Self-enumeration shall be BY NAME, never by glob.** A harness that enumerates the checks it
verifies shall list them explicitly. Measured on this plan's own ten instruments: they span three
naming conventions and two languages, `redcheck.sh`'s `cmd_verify_red_checks` iterates `check-*.sh`,
and `record-red-check` hard-rejects any other name — so a glob-based enumerator reaches **6 of 10**
and reports success. Dispatch shall be per extension (`bash` for `.sh`, `uv run` for `.py`).

**A selftest excludes ITSELF from its own count.** A selftest cannot be its own RED fixture, so its
`--require N` is one below the instrument total; the criterion asserting all N+1 exist is a separate,
presence-only check.

Rationale: plan-055 landed `_common.sh` plus three checks in `scripts/checks/`; this plan lands eight
more. That makes the directory a real repo surface, and SPEC-first requires the surface be declared
before it is populated — otherwise the epic that enforces SPEC-first would itself violate it.
Verification: `scripts/checks/harness-selftest.sh --require 9` — every instrument returns non-zero
on a deliberately broken input, and the selftest reports how many it checked, so a selftest covering
2 of 10 is distinguishable from one covering 10.
