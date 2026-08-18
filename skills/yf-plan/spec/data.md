# Data Contracts Specification

## Plan Identity

REQ-DATA-001: Plan IDs follow the format `plan-NNN-<user>-<hash>` where NNN is a zero-padded 3-digit index, user is the normalized git username, and hash is a 6-character hex string.
Rationale: Predictable, sortable IDs enable listing and selection; the hash prevents collisions when multiple plans share an index.
Verification: `make_plan_id` in plan_manager.py; SKILL.md Phase 3 plan.md template shows `plan-NNN-user-hash`.

REQ-DATA-002: Plan directories are stored under one of two roots — either `docs/plans/<plan-id>/` (vault-default) or `Incubator/<slug>/plans/<plan-id>/` (incubator-scoped). Both roots use the same per-plan layout: subdirectories `findings/`, `diagrams/` (d2 source + PNG renders authored per the `diagram-authoring` skill), `assets/` (attachments/generated artifacts, not diagrams), `references/`, and `reviews/`, plus root files `plan.md`, the OKF-reserved `index.md` and `log.md`, and `context.md` (seeded at init time by the portability contract). The bundle is an OKF-PLAN dir-form bundle (OKF-EXTENSION.md): `index.md` is the reserved listing (replacing the legacy `README.md`, REQ-PORT-001), `log.md` is the reserved update history (replacing the in-`plan.md` phase log, REQ-DATA-012), and every non-reserved `.md` carries `type` + `okf_spec: OKF-PLAN` frontmatter (REQ-PORT-050). A bundle **may** additionally carry the root file `plan-retrospective.md` (`type: Retrospective`), which records stops and deviations during execution; it is **presence-optional** — its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE) — and when present it conforms to REQ-PORT-051/052. Plan numbering (the `NNN` in plan IDs) is global across all roots.
Rationale: Versioned in git, reviewable in PRs, co-located with the code they describe. Incubator-scoped placement keeps plan artifacts adjacent to the incubator they belong to (matching deep-research's per-incubator routing); the global numbering preserves unambiguous cross-references. `references/` and `reviews/` carry portability scaffolding (spec/portability.md REQ-PORT-005/006); `index.md` / `log.md` are the OKF-reserved bundle files.
Verification: `resolve_plans_dir(incubator)` returns the appropriate root; `make_plan_dir(plan_id, plans_dir)` creates findings/, assets/, and diagrams/ under it; `seed_portability_scaffolding` creates references/ and reviews/ plus `index.md`, `log.md`, and context.md; `init` command invokes both. `list_plan_roots` enumerates every root for listing and global numbering.

## plan.md Schema

REQ-DATA-010: Every plan.md carries these required identity fields: ID, Author, Created, Status — each dual-represented as a YAML frontmatter key and a `**Field:**` header line (REQ-DATA-015). The phase history is **no longer an in-`plan.md` field**: it lives in the reserved bundle-root `log.md` (REQ-DATA-012). A resumable bundle therefore requires the four identity fields on `plan.md` **plus** `log.md`.
Rationale: These fields enable cold resume (`/yf-plan continue`) — a plan.md missing any of them cannot be reliably resumed. Relocating the phase log to `log.md` (the OKF reserved update history) keeps plan.md's body fingerprint-stable (REQ-PORT-040) without losing resume-critical history.
Verification: `seed_plan_md` in plan_manager.py writes the four identity fields (dual frontmatter + `**Field:**`) and seeds `log.md`; SKILL.md Phase 3 template includes the four fields and the reserved `log.md`.

REQ-DATA-011: Every plan.md contains these required sections: Objective, Motivation, Upstream Issues, Investigation Findings, Approach, Epics, Gates, Risks & Mitigations, Success Criteria. Motivation may alternatively live in a sibling `motivation.md` file (see REQ-PORT-004).
Rationale: These sections are the planner agent's output contract and the coordinator's input contract. Motivation is required by the portability contract so cold readers can answer "why does this plan exist?" without the drafting conversation.
Verification: SKILL.md Phase 3 plan.md structure template includes §Motivation; `seed_plan_md` in plan_manager.py writes a §Motivation placeholder; `_audit_plan` enforces non-placeholder content.

REQ-DATA-012: The plan phase history is the OKF-reserved `log.md` at the plan-bundle root — it **replaces** the legacy in-`plan.md` `**Phase log:**` block (SPEC REQ-OKF-002, OKF-EXTENSION.md §3). `log.md` is append-only and **newest-first**: entries are grouped under ISO-8601 (`YYYY-MM-DD`) date headings, newest date first, and each entry is a `- <status>: <message>` bullet that retains its `<status>:` token (`scoping:`, `review:`, `approved:`, `intake:`, …) so the review-count (REQ-PORT-006), grandfather-date (REQ-PORT-ACT), and append parsers keep resolving from `log.md` instead of the phase log. Being an OKF **reserved** file, `log.md` carries **no `type` and no `okf_spec`** (SPEC REQ-OKF-031).

REQ-DATA-016: The **green-execution attestation** (REQ-PLAN-069b) is a `log.md` bullet of the form `- validated: <run URL/id> — <note>` under the current `## YYYY-MM-DD` heading, appended via `okf.append_log` (helper verb `attest-validation`; a hand-written bullet is equally valid). `validated:` is a recognized **non-status** `log.md` token — like `intake:`, it is inert to the lifecycle: **no** review-count (REQ-PORT-006), grandfather-date (REQ-PORT-ACT), or status parser keys on it, and it never advances `status`. `complete-gate` (REQ-PLAN-069) reads `log.md` and matches the `- validated:` bullet form, falling back to the plan.md `**Phase log:**` block only for un-migrated bundles. The **deferred-validation bead** that alternatively satisfies REQ-PLAN-069 lives **outside the plan molecule tree**: a standalone `bd` issue (no `--parent` into the plan epic) with label `deferred-validation` and metadata `{"plan":"<plan-id>"}`, discovered by a `bd list --label deferred-validation` filter — never by walking the plan tree — so `close_cascade` (REQ-PLAN-067) does not fail-loud on it as an open plan-tree child.
Rationale: An append-only, newest-first log preserves the full phase-transition history for audit and debugging; moving it out of `plan.md` into the reserved `log.md` keeps plan.md's body (from the first `## `) fingerprint-stable (REQ-PORT-040) and matches the OKF update-history convention (which OKF leaves format-silent — yf pins newest-first ISO-8601 date headings).
Verification: `update_status` / the `append_log` op in plan_manager.py append newest-first without removing prior entries; migrate lifts the legacy `**Phase log:**` block into `log.md` preserving the first `scoping:` date in machine-readable form (SPEC REQ-OKF-MIG-002). **Tension for Issues 3.2–3.7 to resolve:** the legacy count/date parsers matched the inline-date line form `^- \d{4}-\d{2}-\d{2} <status>:`; under `log.md`'s heading-grouped form the date moves to the enclosing `## YYYY-MM-DD` heading, so `_plan_review_line_count` and `_plan_first_scoping_date` must rebind to the heading+bullet shape (count `- review:` bullets; read the oldest date heading bearing a `scoping:` entry).

REQ-DATA-017: `update-status` shall be **idempotent per (date, status-token)** when appending to `log.md`: re-running the §6.4 close step shall leave exactly **one** `- complete:` bullet under the current date heading, not one per run. Re-running §6.4 is a **documented recovery path** — the fail-loud banners on the halting steps explicitly instruct the operator to resolve and re-run — so duplicate bullets are produced by the normal remediation flow, not by misuse. They are not cosmetic: `log.md` bullets are what the status, review-count (REQ-PORT-006) and grandfather-date parsers read, so a duplicated status bullet corrupts the record those parsers derive their answers from. Idempotence is scoped to an exact `(date heading, status token, message)` match: a genuinely new entry for the same status on a **later date**, or with a **different message**, is still appended — the requirement suppresses re-emission, not history.
Rationale: no §6.4 step may append to `log.md` unguarded. A new chain step should be a pure read or dedupe its own write, and the terminal status writer is the one place this was already being violated.
Verification: `scripts/test_update_status_idempotent.py` — two consecutive `update-status complete` calls leave exactly one `- complete:` bullet; a different message or a later date still appends; the review-count and grandfather-date parsers are unperturbed.

REQ-DATA-014: At intake (after the pour), the plan↔epic linkage is persisted two ways: the epic id in plan.md's header metadata — dual-written as the `epic` frontmatter key **and** the `**Epic:** <id>` header line (REQ-DATA-015) — and a `metadata.plan_dir` stamp on the poured epic bead. The epic field is absent before intake (no epic exists yet) and is therefore not in the REQ-DATA-010 always-required set. The metadata stamp is the fallback for plans intaken before the field existed.
Rationale: Crash recovery (#2) needs a deterministic pointer from a plan folder to its epic. Two independent records (plan.md field + bead metadata) make the resume guard robust to either being absent.
Verification: `record_epic` in plan_manager.py writes both the `epic` frontmatter key and the `**Epic:**` header line; SKILL.md §4.2 stamps `bd update ${EPIC} --metadata` and invokes `record-epic`; `_resume_scan` reads the epic frontmatter-first with `**Epic:**` fallback, plus the metadata stamp.

REQ-DATA-015: plan.md header metadata shall be **dual-represented** — a YAML frontmatter block **and** the human-readable `**Field:**` header lines — emitted by a single writer from one in-memory model (SPEC REQ-OKF-020). The dual set is `id`↔`**ID:**`, `author`↔`**Author:**`, `created`↔`**Created:**`, `status`↔`**Status:**`, `deliverable_class`↔`**Deliverable-class:**`, `epic`↔`**Epic:**`, `fingerprint`↔`**Fingerprint:**` (OKF-EXTENSION.md §4). `deliverable_class` (REQ-PLAN-069a; values `ci-release` | `standard`, default `standard` when absent) is positioned in `PLAN_FIELD_ORDER` **immediately after `status`**; being a registered field it survives every `_rebuild_field_block` rewrite (which re-emits only registered fields), unlike a raw header line which would be silently dropped on the next `update-status`/`record-epic` write. **Reads are frontmatter-first with `**Field:**` fallback** (SPEC REQ-OKF-021): a reader takes the frontmatter value when the key is present and falls back to the legacy `**Field:**` line when it is absent, so un-migrated (frontmatter-free) plans keep resolving. **Writes are dual-write** — the consistency invariant: there is no path that writes one representation without the other; the two surfaces are never authored independently (SPEC REQ-OKF-020). Both blocks sit above the first `## ` heading (REQ-PORT-040 / SPEC REQ-OKF-010), so neither perturbs the content fingerprint.
Rationale: Preserving the human `**Field:**` surface while adding the machine/OKF frontmatter surface avoids a lossy cutover and keeps `/yf-plan continue` working on legacy plans; single-writer dual-write is the anti-divergence guarantee (one writer, one model, both representations always in sync).
Verification: a shared field accessor reads frontmatter-first and falls back to `**Field:**`; `seed_plan_md`, `record-epic`, and `fingerprint write` each emit both representations from one model; a test asserts no writer emits one surface without the other and that a frontmatter value overrides a stale `**Field:**` line on read. Amendment-log entry: root `SPEC.md` `plan-029` (OKF-PLAN adoption — this requirement is added by plan-029 Issue 3.1).

REQ-DATA-013: The Upstream Issues table has columns: Issue, Title, Disposition, Notes, Resolved By.
Rationale: The reconciler reads this table to determine what action to take on each upstream issue after execution.
Verification: SKILL.md Phase 3 plan.md template; reconciler.md Execute step 1.

## Configuration & State (Skill Surface Convention)

REQ-DATA-020: Operator config and runtime state are separate buckets per the Surface Convention (skill-authoring). The canonical layout — the `yf` binary's ground truth — is short-name (`<short>` = `plan`): config at `.yf/plan/config.local.json` and state at `.yf/plan/preflight.json`. The legacy root dotfile `.yf-plan.local.json` survives only as a read-time config fallback (declared by the `config-basename` descriptor). `yf migrate` moves legacy → canonical; preflight does **not** auto-migrate.

`plan_manager.py` is **aligned to the binary as of #100** (plan-037 Issue 2.2). Both readers now resolve the same three tiers, merged **key by key** with the highest present tier winning each key (REQ-YF-PRE-004):

| Tier | Path | Committed? |
|:--|:--|:--|
| 1 | `.yf/plan/config.local.json` | no — gitignored, machine-specific |
| 2 | `.yf/plan/config.json` | **yes** — shared, repo-carried (REQ-YF-PRE-004a) |
| 3 | `.yf-plan.local.json` | no — legacy root dotfile, read-only fallback |

`plan_manager.py`'s own state (e.g. `landing.lock`) now lands in the short-name `.yf/plan/` directory, matching where the preflight kernel writes `preflight.json`; state written by an earlier version under the full-name `.yf/yf-plan/` is migrated on first use.

Rationale: Config = operator decisions a fresh clone would need; state = caches/derived values tied to one checkout. Conflating them commits machine-specific state or loses operator intent. The committed tier exists because some of those decisions — the plan/incubator roots — are properties of the repository, not of a checkout: plan-id numbering is global across roots, so two clones disagreeing about the root silently fragments it.
Verification: plan_manager.py `_read_config()` (three-tier merge) and `STATE_DIR` (short-name `.yf/plan/`); `yf/src/preflight.rs` `read_config` / `state_path`; `scripts/test_config_tiers.py` (Tier-1, tagged REQ-YF-PRE-004/-004a, REQ-PLAN-073); SKILL.md Pre-flight section.

REQ-DATA-021: The config/state split is by **role, not by count**. **Config** is operator decision: `ignore-skill`, `plans-root`, `incubator-root`, `execute.worktree`, `validate-cmd`, `landing-strategy`, `autonomy`, `sweep-gates`, `max-attempts`, `max-review-cycles` — **ten** keys as of plan-045, and the set grows. **State** is runtime cache: `prereqs-present` (deps cache) and `scaffold-ensured` (scaffold-version marker). *(This REQ previously read "`ignore-skill` … is the only config key", which was true when written and has been false since; a REQ stated as a count goes stale on the next key added, so it is restated as the distinguishing rule.)*
Rationale: Minimal config surface; the only operator decision is whether to opt out. Both state keys are recomputable caches, so they are state.
Verification: every config key is read through plan_manager.py `_read_config()` (and reported by `config-resolve --json`, REQ-CLI-021), while `_read_state()`/`_update_state()` carry only `prereqs-present` and `scaffold-ensured`; SKILL.md Pre-flight.

REQ-DATA-022: A single anchored entry `/.yf/` is present in `.gitignore` (no globs), ensured by preflight, not by `/yf-plan init`. It covers both config (`.yf/plan/config.local.json`) and state (`.yf/plan/preflight.json`); the legacy per-skill dotfile and `/.state/` anchors are no longer scaffolded. **One carve-out** (plan-037, REQ-YF-PRE-004a): the committed tier `.yf/<short>/config.json` is un-ignored — everything else under `.yf/`, including all state and every `*.local.json`, stays ignored.
Rationale: Machine-specific config and all runtime state must not be committed; one anchor keeps `.gitignore` auditable and collapses the old per-skill dotfile + `/.state/` pair. Folding the ensure into preflight makes it self-healing rather than dependent on init having been run. The write is additive-only and gated by `scaffold-ensured` so it runs once per scaffold version (Surface Convention §7).
Verification: `yf/src/preflight.rs` scaffold (single `/.yf/` anchor, additive append, scaffold-version gate), run on the `ok` path; SKILL.md Pre-flight `ok` bullet.

REQ-DATA-023: The companion rule `protocols/PLANS.md` is installed by the repo installer (`install.sh`) — not by `/yf-plan init` — to a rules dir anchored by install scope and surface: user-scope → `~/.<surface>/rules/PLANS.md`, project-scope → `<git-root>/.<surface>/rules/PLANS.md` (`.claude` or `.agents`). Preflight resolves the installed rule across locations in precedence order — the user/global `~/.<surface>/rules` copy before the project copy — and hash-checks it against `protocols/manifest.json` (schema_version 1). A correct user-scope copy satisfies every project; `install.sh --force` overwrites an existing rule.
Rationale: A manifest hash detects drift/stale/deprecated installed rules; matching the surface keeps a `.claude` install from polluting an unrelated `.agents/` tree (and vice versa); anchoring by scope puts a user-scope rule at `~/.<surface>/rules` (shared by every project) and a project-scope rule at the git root. Installing at install time (not init) means the rule is present the moment the skill is. Both `.claude/rules/` and `.agents/rules/` are auto-loaded.
Verification: `install.sh` rule-copy step (`install_rules`); plan_manager.py `_skill_surface()` + `_skill_scope()` + `_git_root()` + `_rules_dir()` + `_rule_candidates()` + `_check_rule()` (preflight hash check).

## Upstream Tracking

REQ-DATA-030: Upstream tracking configuration is persisted to `CLAUDE.md` under a `## Upstream Tracking` section.
Rationale: CLAUDE.md is loaded into every session; upstream config must be available without extra file reads.
Verification: SKILL.md Phase 0.4.

REQ-DATA-031: Upstream tracking supports: GitHub Issues (`gh`), GitLab Issues (`glab`), or none.
Rationale: These are the platforms with CLI support for automated reconciliation. Jira/Linear are mentioned in the discovery prompt but require manual reconciliation.
Verification: SKILL.md Phase 0.1 auto-detect and 0.3 operator confirmation.

## Formulas

REQ-DATA-040: The `plan-execute` formula creates a start gate with `type = "human"`.
Rationale: Enforces the session boundary — execution cannot begin without operator resolution.
Verification: plan-execute.formula.toml `[steps.gate]`.

REQ-DATA-041: The `plan-investigate` formula uses `phase = "vapor"` (wisp lifecycle: create, inject, execute, burn).
Rationale: Investigation beads are ephemeral — findings are captured in markdown, then the wisp is burned. No permanent bead trail for experiments.
Verification: plan-investigate.formula.toml `phase = "vapor"`.

REQ-DATA-042: Both formulas require variables `objective` and `plan_dir`.
Rationale: These are the two values that link a formula instance to a specific plan.
Verification: Both `.formula.toml` files have `[vars.objective]` and `[vars.plan_dir]` with `required = true`.
