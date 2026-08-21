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

REQ-DATA-018: Each row of a plan.md `## Success Criteria` table shall carry a **stable id** in a
leading `#` column, matching `SC[0-9]+[a-z]?`, unique within the plan, and **insertable without
renumbering** — a criterion added between `SC1` and `SC2` is `SC1b`, never a renumbering of every
later row (plans 039/040 already use `SC1b`/`SC5b`; 6 plans reference criteria positionally
because they have no id to reference). The table columns are fixed:
`| # | Criterion | Verification | Discharged-by |`. `Discharged-by` names the issue id(s) that
discharge the criterion, and the mapping shall be **bidirectionally complete**: every criterion
names at least one issue, and every issue in `## Epics` is named by at least one criterion. The
sibling `## Risks & Mitigations` table columns are likewise fixed:
`| # | Risk | Severity | Mitigation |` (the shape plans 039–043 converged on, preserving the
`Severity` column that 7 of 8 measured lossy-residue items carry).

This requirement is an **addition, not a codification**. Precedent at the time of writing is 31
of 367 criteria in **2 of 47** plans; the other 45 have no key for a criterion↔issue join at
all. `Discharged-by` is **mandatory for new plans and backfilled for none**: plan-047 EXP-002
measured that the edge cannot be recovered from history — only 13.3% of criteria mention an issue
id, the strongest signal is ~73% precise, and combined yield is ≈10%, because *a mention is not a
discharge*. Shipping inferred edges would be worse than an empty mapping, since nothing
downstream could distinguish an inferred edge from a declared one.
Rationale: the criterion↔issue mapping is the join key every downstream consumer needs — #174's
falsify-every-criterion cross-check matrix cannot be built without it, and "every issue is
discharged by at least one criterion" is unverifiable without stable ids. Insertability matters
because renumbering silently invalidates every existing citation of a criterion.
Verification: `_shared/plan_template.py` `CRITERIA_TABLE_HEADER` / `RISKS_TABLE_HEADER` are the
columns `seed_plan_md` writes and `_shared/sync.py` emits into SKILL.md's fenced skeleton
(REQ-DATA-024's `plan.md` schema asserts both column sets and the id grammar); a fresh `init`
emits both headers.

REQ-DATA-019: A gate's `- Blocks:` value shall be drawn from a closed **referent alphabet**: a
comma-separated list of `issue-id` tokens (`N.M[a-z]`), the explicit `epic:<N>` form, and the
reserved sentinel `reconcile step`. Wildcards (`Issue 2.x / 3.x`), prose referents, and a
trailing parenthetical on the sentinel are **forbidden** — a parenthetical's content belongs in
`Instructions:`. `depends-on` is likewise a bare comma-separated id list: a value carrying a
prose tail is forbidden, and the rationale moves to the issue body.

Like REQ-DATA-018 this is legislated rather than observed: only **12 of 72** historical `Blocks:`
values parse as a pure id list, across 10 distinct shapes. The `epic:<N>` form is introduced for
**future plans only** — nothing parses `Blocks:` today, and the only form the pour is documented
to handle is an explicit issue-id list.
**AUTHORING grammar vs READING grammar (plan-048 D-4 / Issue 0.2).** Everything above is the
**authoring** grammar: what a *new* plan shall write, and what the schema rejects. The
**reading** grammar the extractor implements is deliberately **wider**, because plan-048 elected
to widen the reader rather than rewrite 48 historical documents. The extractor shall additionally
**recover** these four historical forms, normalizing each to the canonical alphabet above:

| Historical form | Normalizes to | Why it is unambiguous |
| :-- | :-- | :-- |
| `Issue N.M` prefix inside a `Blocks:` value | the bare `N.M` id | the prefix is a noise word; the id is complete without it |
| `Epic N` as a `Blocks:` referent | `epic:N` | the canonical form's only spelling difference |
| `depends-on` / `resolves-upstream` written at **column 0** | the two-space-indented sub-key | attaches to the immediately preceding issue bullet; no other referent is possible |
| a title parenthetical before the colon, e.g. `- Issue 1.2 (optional): …` | the id `1.2`, parenthetical dropped from the id | the parenthetical never carries an id |

Recovery is **normalization, never repair**: the reader emits the canonical edge and **no
document is modified**. Two classes shall be **REFUSED**, reported with line numbers rather than
recovered — a `depends-on` value carrying a **prose tail** (the tail may or may not be a referent
and no rule distinguishes the cases), and a **dangling target** (a referent naming no issue in
the plan). Refusing is the conservative direction: an edge recovered *wrongly* is worse than an
edge not recovered, because a wrong edge silently reorders execution while a missing one is
visible in `unparsed[]`.

**Disposition alphabet (plan-048 D-7).** A `resolves-upstream` disposition and an `## Upstream
Issues` table `Disposition` cell shall be drawn from the closed set
`include | exclude | partial | supersede | deferred | tracker`. `deferred` means *in scope
later* — genuinely distinct from `exclude`, which means *not in scope at all*. Cells shall be
**normalized before matching**: surrounding emphasis markers (`**bold**`, `_italic_`) are
stripped and the value is lowercased, so `**partial**` and `partial` are the same literal.
Without that normalization a bolded cell parses as the unrecognised literal `'**partial**'` and
silently escapes verification — measured live on plan-023, which carries two such cells.
Rationale: `Blocks:` is the gate→work edge of the plan DAG. A referent no parser can resolve
makes the edge invisible, which is how a gate silently blocks nothing; a closed alphabet is what
lets the extractor report an unresolvable referent as an error instead of dropping it. The
authoring/reading split exists because the two grammars answer different questions — "what may
be written" is a standard, "what can be understood" is a compatibility surface — and collapsing
them forces a choice between rejecting history and legitimizing ambiguity.
Verification: REQ-DATA-024's `plan.md` schema rejects a `Blocks:` value outside the alphabet and
a `depends-on` value with a prose tail; plan-047 Issue 0.4 states the introduction scope;
plan-048 Issue 1.3 implements the four recoveries, 1.4 the two refusals, and 1.4a ships a
**negative** mutant asserting a naive widening's wrong recovery is refused.


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

## Document Conformance (`document_types/` schemas, linter, normalizer, extractor)

REQ-DATA-024: Every in-scope yf artifact document type shall be described by a **declarative
schema** at `document_types/<type>.toml`, read by a single linter engine. A schema comes in one
of two flavours, split by **producer class**:

- `derive_from = "<producer function>"` — for a **code-generated** type, the schema derives its
  required structure from the function that writes the type, so the two cannot diverge;
- an **inline declared schema** — for an **agent-written** type, a standalone artifact the
  producing agent file references.

The split is measured, not stylistic: every enforced code-generated type measures **0%** drift
and every unenforced agent-written type measures **14–95%**. One uniform format for both would
re-introduce, at the template layer, the hand-maintained-duplicate problem `_shared/sync.py`
exists to eliminate.

The **engine contract**:

- **Verdict vocabulary is `PASS | FAIL | INCONCLUSIVE`.** `INCOMPLETE` is the *reviewer agent's*
  vocabulary and shall not appear in a linter verdict.
- **Three severities**, and only one is an error: `E` (structural — the document does not have
  the shape its type declares), `W` (completeness — a required section is present but unfilled),
  and `R` (report-only — recorded in `findings[]`, counted in `report_only`, printed only under
  `--show-report-only`). Only `E` sets a non-zero exit code. `R` is both a **declarable** schema
  severity and the **outcome** of a status demotion (REQ-DATA-053); those are the same value
  reached two ways, not two vocabularies. *(Amended by plan-049 Issue 0.6. This bullet read
  "Two severities" while nine checks across five schemas — `upstream-triage`,
  `upstream-reference`, `finding`, `review`, `plan-retrospective` — had declared `R` directly
  since plan-047, and `doc_lint.py` had accepted it since `ERROR, WARN, REPORT` was written. The
  `e-doclint-spec` drift edge added by the same issue reported it on its first run, which is the
  class of divergence that edge exists to catch.)*
- **`INCONCLUSIVE` means "the linter could not run"** and only that; it maps to **exit 2**.
  "Not finished yet" is expressed as `W` severity **inside a PASS**, so the **lint mode's** exit
  contract stays binary: 0 = no error-severity finding, 1 = at least one, 2 = the harness could
  not run. *(Amended by plan-050 Issue 0.1 (#181). This bullet read "binary at every binding
  point", asserting ONE exit vocabulary for the whole executable. `REQ-DATA-061` adds a second
  MODE — `classify` — to the same executable, whose `0/1/2` means lintable / not-lintable /
  could-not-run. The two vocabularies are **keyed by mode** and neither is "binary at every
  binding point"; a `classify` run over a selected-but-empty document exits **0** while a lint
  run over the same document exits **1** on its 6 `E` findings. Leaving the old wording in place
  would put the spec, the engine banner and `document_types/README.md` in agreement with each
  other and in disagreement with the code — the plan-049 D-9 shape the `e-doclint-spec` edge
  exists to catch. The amendment is scoped to THIS SENTENCE: the **verdict** vocabulary
  (`PASS | FAIL | INCONCLUSIVE`) is closed and unchanged, because `classify` emits a `class`,
  never a verdict.)*
- **Status-aware promotion.** A plan's `status` selects the severity mapping:
  `scoping | investigating | drafting` → `W` findings are informational;
  `review | ready-for-approval` → `W` is **promoted to `E`**;
  `complete` → **report-only, never an error**.
- **Path-keying, never filename-keying.** Type selection keys on the document's path
  (`docs/plans/**/*.md`, `Incubator/*/plans/**/*.md`, `docs/research/**/*.md`), so the engine is
  **inert** in a repo with no yf documents and does not fire on the 17 test-fixture `plan.md`
  files.
Rationale: a step with no exit code is not a step. The corpus's measured defect class is a
process rule that nothing executes; a schema without a non-zero exit is a decorative rule, and a
linter that prints findings and exits 0 reports `pass` — reproduced live. Status-awareness is
what makes an always-on trigger non-hostile to a plan that is still being written; path-keying is
what keeps it silent where it does not apply.
Verification: `_shared/doc_lint.py` exits 1 on a seeded known-bad fixture and 0 on a clean file;
each schema-bearing type rejects a committed malformed fixture under
`tests/fixtures/doclint/<type>/bad.md`; a freshly `init`'d plan reports `errors=0` at every
pre-`review` status.

REQ-DATA-025: The corpus normalizer shall be **hash-neutral**: it recomputes
`_plan_content_fingerprint` **before and after every file it writes**, and **aborts the entire
run** if any hash moves. It shall emit a machine-readable report carrying at minimum the keys
`fingerprints_moved` (int) and `diff_bytes` (int); a gate may assert `fingerprints_moved == 0`.
It shall **refuse to write** any file matching the predicate `status == "complete"` **AND**
`stored fingerprint == current fingerprint` **AND** the path is under a plans root — excluding
`skills/**/fixtures/**`, which is the markup-sensitive ground-truth corpus of
`test_classify_deliverable.py`. Everything hash-changing on a completed plan is **report-only**.
On a `complete` plan carrying **no** stored fingerprint the `stored == current` conjunct is False,
so the refusal does not apply and the hash-neutral transform set still governs; the predicate is
therefore **not** inert on today's corpus, contrary to the plan-047 draft.

Additionally the normalizer shall be **line-count preserving** on every plan cited by
`plan.md:<line>` elsewhere in the repository. The protected set shall be **derived at execution
by a committed script and printed**, never frozen as a literal: two independent sweeps of the
same corpus returned materially different sets (17 plans vs 22), and neither is authoritative.
Trailing-whitespace strip is the only transform that is both hash-neutral and line-count
preserving — blank-line collapse is hash-neutral (the fingerprint ignores blank lines) but shifts
every line below it.
Rationale: REQ-OKF-MIG-003 already *requires* OKF migrate to keep the content fingerprint stable,
so the migrate path is the **precedent for hash-neutrality, not for rewriting**. A hash-changing
sweep would leave all 46 completed plans permanently tagged `⚠ STALE-APPROVED` — reproducing
dixson3/yoshiko-flow#109, closed as not-reproducible — and would silently break 91 measured
`plan.md:<line>` citations plus ≥102 verbatim review quotes.
Verification: before/after hashes are equal for every file written and the run aborts if any
moves; `--idem-check` reports zero non-idempotent plans; the protected set is printed and `wc -l`
is equal before and after for every plan in it; the refusal predicate is exercised on all three
branches (`complete`+fresh-fingerprint, `complete`+no-fingerprint, non-`complete`).

REQ-DATA-026: The pour (SKILL.md §5.2a) shall record the plan issue id in **bead metadata** as
`plan_issue: "<id>"` — never as a title convention — and a **pour-fidelity comparator** verdict
shall be a plan-close gate. The comparator joins the extracted plan DAG to
`bd list --all --include-gates`; `--include-gates` is **mandatory**, since without it 121 gate
beads and every gate edge are invisible **with no error** (#166). It shall report **three
populations separately**: plans with no recoverable plan↔bead mapping, dropped edges among
joinable plans, and invented edges — an aggregate conflates an identity artifact with a real
ordering defect. It shall ship with a **positive control** that runs in CI: deleting an issue
line, a `depends-on`, and a gate block must each make it fail, and it must be silent on an
unmutated copy.
Rationale: measured over 43 comparable plans, **17 carried a pour divergence** — 885 declared
dependency edges against 860 in `bd`, 45 dropped and 20 invented. A dropped `blocks` edge means
the coordinator marked a bead ready *before its declared predecessor*. Bead titles get rewritten;
metadata is the stable carrier. Three plans (006/007/036) have no recoverable mapping at all and
account for 43 of the 45 dropped edges purely as an artifact of missing identity — which is why
the populations must be reported apart. The positive control is the entire reason the 40% figure
is trustworthy.
Verification: a fresh pour writes `plan_issue` on every task bead; the comparator runs at close
and can fail it; the positive control's three mutations each produce a failure and the unmutated
copy is silent.

REQ-DATA-027: **Vendored content** — a file copied verbatim from an external source into a yf
bundle (an upstream issue body, a third-party spec, a salvaged document) — shall carry
`source:` and `retrieved:` frontmatter keys. That frontmatter **is** the exclusion predicate the
linter uses to skip type-schema checks on the file; vendored content is still linted for GFM
validity. **Unmarked vendored content is a linter error, not a silent pass.**
Rationale: at the time of writing only 2 of 6 vendored `references/*.md` files carry the marker;
the three vendored `yf-herdr` copies and `salvaged-docusaurus.md` carry nothing, the latter's only
vendoring signal being an English sentence in prose. The carve-out is therefore **not detectable
today** — it must be *introduced*, and backfilling it is a prerequisite of any fail-closed
binding, because the first such binding would otherwise break on a file it must never read.
Making the absent marker an error (rather than a silent pass) is what stops the exclusion from
becoming a hole that swallows genuinely non-conformant documents.
Verification: all vendored `references/` files match `source:` + `retrieved:`, 0 unmarked; the
linter reports zero findings inside every carved region and a positive control run with the
carve-out globs disabled exits 1.

REQ-DATA-028: `plan_manager.py update-status` shall **refuse** the transition to `approved`
unless `ready-check` (REQ-PLAN-066) is green, exiting non-zero and writing no status. A named
override flag shall exist for the operator to force the transition, and using it shall append a
`deviation` entry to the plan retrospective as well as a `log.md` line stating the override.
Rationale: measured, `update-status <dir> approved` succeeded with **exit 0** on a plan whose
`ready-check` had just exited 3 — `update_status` is a free-form writer by its own docstring, so
**the intake gate is prose obedience, not code**. `spec/cli.md` and `spec/phases.md`
(REQ-STATUS-002) are silent on any gate at the transition, so no existing requirement covers this.
Without it, a fail-closed document-conformance binding does not exist no matter what the linter
returns — the linter's verdict reaches `audit`, `audit` reaches `ready-check`, and `ready-check`
is then simply ignored by the writer.
Verification: driving the real verbs on a non-conformant plan makes `update-status … approved`
exit non-zero; the override path succeeds and logs a deviation under the flag name plan-047
Issue 2.6 selected; `ready-check`-green plans are unaffected.


## Extractor & check-kind contracts

REQ-DATA-043: Every consumer of `_shared/plan_extract.py` shall **gate on `unparsed[]`**: when
`unparsed[] != []` for a document, the consumer shall return **INCONCLUSIVE** — never FAIL — for
every judgement that depends on that document's extracted DAG, and shall name the unparsed
constructs (with line numbers) in its verdict. The consumer set is closed and enumerated:
the **relational checks** (`plan-relations`, REQ-DATA-044), the **pour** (SKILL.md §5.2a), and
**`_shared/pour_fidelity.py`**. A consumer that adds itself to this set adds itself to this
enumeration. The INCONCLUSIVE exit code is **2**, distinct from FAIL's **1** — a caller that
collapses the two has not implemented this requirement.
Rationale: an unparsed construct means the extractor **did not see** part of the plan, so every
downstream conclusion is drawn from a knowably incomplete DAG. FAIL asserts *the plan is wrong*;
the honest claim is *this instrument could not read the plan*. Conflating them manufactures
blockers out of parser limitations — and, worse, a partially-extracted DAG that reports clean
produces a **false-clean** fidelity number, which is strictly more dangerous than a red one.
Verification: plan-048 Issue 1.2 implements the gate in all three consumers; SC4 drives a
relational check with an unparsable construct to exit 2, and SC4b drives the pour and
`pour_fidelity.py` the same way.

REQ-DATA-044: `doc_lint.py` shall support a third check kind, **`plan-relations`**, distinct
from the two per-document schema flavours REQ-DATA-024 declares. A `plan-relations` check calls
`_shared/plan_extract.extract()` and reasons **across sections and across tables** of a single
plan bundle — `## Epics`, `## Gates`, `## Success Criteria` and `## Upstream Issues` — which no
per-document schema check can do, since each of those reads one section in isolation.

- **INCONCLUSIVE path:** a `plan-relations` check on a document with non-empty `unparsed[]`
  returns INCONCLUSIVE per REQ-DATA-043, never FAIL.
- **Severity:** the `R*` rule family ships at severity **`W`**, uniformly.
- **`STATUS_SEVERITY` promotion does NOT apply to this kind.** This is **declared, not
  inherited** — and, since plan-049 Issue 0.2, **implemented**: the schema declares
  `promote = false` and the engine bypasses the map in both directions (REQ-DATA-053). Between
  plan-048 and plan-049 this bullet was true of the prose and false of the code. Were `W → E` to fire at `bundle_status: review`, every future plan would
  hard-fail R1b unless every non-bookkeeping issue were named by a criterion — a bar plan-048
  itself does not clear (it carries four such issues and escapes only by being `executing` when
  the rule lands). A rule that no in-flight plan can satisfy trains authors to write fake
  criteria, which is the exact failure R1b exists to prevent.
- **R1b bookkeeping carve-out:** an epic may declare itself **bookkeeping** with an
  `<!-- epic-kind: bookkeeping -->` marker immediately under its `### Epic N:` heading. Issues
  in a declared-bookkeeping epic are exempt from R1b. The carve-out is **declared, never
  inferred** — an inferred exemption is indistinguishable from an oversight.

**plan-049 is the first plan graded by this kind.** plan-048 lands the rules while already
`executing`, so it is not graded by them; naming the first graded plan explicitly is what stops
that from being an accident.
Rationale: `REQ-DATA-024` declares two schema flavours and a strictly per-document contract. A
check that reads across sections is a third mechanism, not a variant of the first two, and
SPEC-first requires it be declared before it is built.
Verification: plan-048 Issue 3.1 adds the kind, 3.2 implements R1/R1b and the carve-out, 3.3
implements R2a/R2b/R2c; SC4 drives the INCONCLUSIVE path and SC10b drives the carve-out.

REQ-DATA-045: No check may be declared at **`E`** severity on a path **outside a plan bundle**
unless the corpus **already passes it** at declaration time, measured and recorded. Off the
plan-bundle axis — `docs/research/**`, `skills/**`, and any other non-plan path — `bundle_status`
is **null**, so `STATUS_SEVERITY` returns `{}` and an `E` stays `E` with no softening available.
There is no status escape hatch there. A newly instantiated type on such a path shall therefore
ship every check at **`W`** unless the pre-measured corpus pass is recorded alongside the
declaration.
Rationale: on the plan-bundle axis a `W` check that would be disruptive is softened by bundle
status until the bundle reaches `review`, which gives authors a migration window. Off that axis
the window does not exist, so an `E` declared against a non-conforming corpus hard-fails every
run from the moment it lands — converting a lint finding into a repo-wide outage. This was the
single largest hidden cost in the document-type work and is invisible from the type schemas
themselves.
Verification: plan-048 D-10; Issue 2.7 declares every research check at `W`; SC7 drives the
boundary with a mutant, asserting `errors == 0` is not true merely by construction.

REQ-DATA-053: A document-type schema may declare **`promote = false`**, and `doc_lint.py` shall
then bypass `STATUS_SEVERITY` for that schema **in both directions** — a check keeps its
declared severity at every `bundle_status`, neither promoted (`W → E` at `review` /
`ready-for-approval`) nor demoted (`W → R`, `E → R` at `approved`/`executing`/`reconciling`/
`complete`). The key defaults to **`true`**, so every schema that does not declare it is
unaffected. `plan-relations` declares `promote = false`.
Rationale: REQ-DATA-044 already *declares* that promotion does not apply to the `plan-relations`
kind, and the schema file and the engine's own module banner both repeat it — but for a full
plan cycle **nothing implemented it**: `doc_lint.py` applied the map unconditionally to every
schema. plan-049 D-9 measured the same fixture at `executing` → `R`, exit 0, and at `review` →
`E`, exit 1, which would have made plan-049 hard-fail R1b at its own intake. A declaration that
three documents assert and no code enforces is worse than an absent one, because every reader
downstream reasons from it. Making the opt-out a **schema key** rather than a hard-coded kind
guard keeps the rule where the declaration already lives, and makes the next non-promoting
schema a one-line change instead of a second special case in the engine.
Verification: plan-049 Issue 0.2; SC13 drives `tests/fixtures/doclint/plan-relations/
promotion-off-bundle/plan.md` — a **bundle**, so `bundle_status()` resolves to `review` rather
than null — and asserts **exit 1 pre-fix and exit 0 post-fix from the same fixture**, the
pre-fix arm re-running the identical call against a types-dir with the `promote` line stripped.
A flat-file fixture would have exited 0 before any fix and proved nothing.

REQ-DATA-051: A **corpus-write postcondition** shall be expressed as a **four-layer snapshot**
of the plan DAG, taken before a write and re-taken after it, with every layer compared under
**set or multiset containment — never under counts**:

| Layer | Population | Comparison |
| :-- | :-- | :-- |
| **L1** | the set of issue ids per plan | post ⊇ pre (set containment) |
| **L2** | the set of materialised edges `(from, to)` per plan | post ⊇ pre (set containment) |
| **L3** | the **multiset of raw referent tokens literally written** in each `depends-on:` / `resolves-upstream:` declaration, **whether or not the extractor can parse them** | post ⊇ pre (multiset containment) |
| **L4** | gate name → `{type, condition, test, blocks}` | post ⊇ pre per gate, **field by field** |

**L3 is the primary layer.** It is the only one that fires on the emptied-declaration mutant
(mutant A), because a *refused* declaration contributes no issue, no edge and no gate — so
L1, L2 and L4 are all blind to its destruction. Reading the raw token stream rather than the
parsed DAG is what makes the guard independent of the grammar it is guarding.

**L4 is the layer that observes a corpus write.** A relocation moves gate content between
sections; L1–L3 are measurably unchanged by it (EXP-002 mutant C), so a guard asserting only
those would be a no-op over exactly the write it brackets. A gate that loses a field — or is
reduced to a heading with no `Type`/`Condition`/`Test` — is a **loss**, even though the gate
still exists by name.

**Counts are forbidden as the comparison, in every layer.** A reader who implements L1–L4 as
`len(post) >= len(pre)` gets a control that passes the edge-target **substitution** mutant with
totals exactly unchanged, and passes mutant A with the totals moving *favourably*. Containment
is the requirement; a count is a summary of it that discards the identity the guard exists to
check.

The guard shall additionally report the plan content fingerprint as a **note that never changes
the verdict** (REQ-DATA-051's companion, Issue 1.5), and shall exit **2 (INCONCLUSIVE)** — never
1 — when the population itself is unreadable, e.g. a plan present in the pre-snapshot that has
vanished from the post-snapshot.
Rationale: plan-048 shipped an all-or-nothing hash predicate; plan-049 EXP-002 implemented its
successor exactly as worded and drove it with the 23-emptied-declaration replay, measuring
**`PASS`, exit 0** — edges *up* two and residue *down* 22, so the destruction read as an
improvement on both instruments. A postcondition that passes the specific harm it was written
for is not a weak control, it is not a control. Naming the four layers, naming L3 as primary,
and forbidding counts in the requirement text are the three things that stop a re-implementation
from reproducing the blindness.
Verification: plan-049 Issue 1.1 implements `_shared/dag_guard.py`; SC1 drives mutant A to exit 1
with `L3` in `failing_layers`, SC2 drives mutant B and shows a count-only form passes it, SC3
drives a real 48-bundle `okf.py migrate` as the false-positive control, SC11 asserts a non-empty
L4 population on the write phase, SC26 drives all three exit paths, and SC38 drives the
fan-out mutant against the paired upper bound.

REQ-DATA-052: `plan_extract` shall read the **trailing-inline** `depends-on:` form — a
declaration written on the issue bullet's own line or on an indented continuation line rather
than as its own `  - depends-on:` bullet — and shall accept **lettered referents** (`A.1`,
`B.4`) alongside numeric ones. Recovered referents materialise as ordinary L2 edges.

The grammar shall **refuse rather than guess**. A trailing-inline construct is refused, and
reported in `unparsed[]`, whenever the referent it names cannot be resolved unambiguously to an
issue id declared in the same plan — specifically:

- a referent naming an id that no issue in the plan declares;
- a construct whose `depends-on:` token appears inside a fenced block, an inline code span, or
  prose that is not an issue bullet or its continuation;
- a referent list whose separators are ambiguous under the bullet grammar.

A refusal is a **finding, never a silent drop**: refusing must add a residue row, which is why
the widening is required to leave corpus `unparsed[]` no higher than it found it.
Rationale: EXP-001 measured **89 trailing-inline declarations across 5 plans that are invisible
AND uncounted** — `plan-006` and `plan-007` report `0 unparsed, 0 edges` while 20 declarations
go unread, so the residue metric records the loss as perfection. 21 of the 89 use lettered
referents, so a numeric-only widening would silently recover a biased sample. Requiring refusal
over inference is what keeps the widening from *inventing* edges: EXP-001's fan-out mutant
produced **+141 invented edges from 11 lines**, which a loss-only postcondition passes cleanly.
Verification: plan-049 Issues 2.1–2.4; SC5 asserts ≥60 of the 89 recovered with **zero documents
modified**, SC6 drives a mis-attributable form and asserts refusal, SC7 hand-audits ≥20 across
≥4 plans, SC8 asserts `plan-006` and `plan-007` no longer report `0 edges`, and SC31 asserts
corpus `unparsed[]` does not rise above its pre-widening value.

REQ-DATA-054: `doc_lint.py` shall support a **`cell-non-empty`** check kind, asserting that
each named column of a section's first table holds content in every row, and that the table
**has at least one row**. A cell holding only a placeholder — `_tbd_`, `TBD`, `-`, `—`, `n/a`,
`none`, `?`, `todo`, or bare emphasis — counts as **empty**.

Two carve-outs are part of the requirement, not implementation detail:

- **A section with no table at all is NOT this check's finding.** That is `table-columns`'
  business; 44 of the 48 historical plans write `## Success Criteria` as a list, and reporting
  it here would count one defect twice and swamp the signal.
- **A row whose ID cell is itself a placeholder is skipped.** The `| — |  |  |` /
  `| _none_ |  |  |` idiom declares "there is nothing here", which is a correct assertion, not
  an unfilled row. Measured: not skipping it manufactures **58 findings across 29 plans** out
  of an authoring convention working as intended.

Rationale: plan-047's "90-finding exploit" was a table whose required cells were blank — every
existing check passed it, because `table-columns` inspects only the header and `row-id-grammar`
iterates rows. EXP-006 measured the hole still open and **wider** than recorded: a **zero-row**
table also passes both, since iterating nothing raises nothing. Without an instrument that
reddens on those shapes, a plan's own corpus write is unobservable in exactly the way this plan
exists to close.
Verification: plan-049 Issue 3.1; SC9 drives an empty required cell and a zero-row table, each
to exit 1, via `tests/fixtures/doc-checks/`; SC41's false-positive control asserts a conformant
document stays green. Blast radius **re-measured, not cited** (D-7): 0 findings on
`## Success Criteria` and 5 on `## Upstream Issues`, all of them the zero-row shape.

REQ-DATA-055: `doc_lint.py` shall support a **`gate-completeness`** check kind whose predicate
is that a gate block declares **ALL THREE** of `Type`, `Condition` and `Test` absent — a gate
that is a heading and nothing else.

**The predicate is all-three-absent, and the obvious alternative is measurably wrong.** A
`Type` + one-of predicate fires on **79 of the 131 corpus gates** (re-measured here; plan-049
recorded 80 of 137), including **every** Start Gate and the canonical template in
`plan_template.py` and `SKILL.md`. Binding that form fail-closed at intake would leave the next
plan unable to pass its own intake. A `Type: human` + `Approvers: operator` Start Gate is a
**complete** gate — the named approver *is* the condition — so it must not fire.
Rationale: a relocation can reduce a gate to a bare heading while every other gate check still
certifies it clean: the vacuous-gate shape. It is the same loss `REQ-DATA-051`'s L4 layer
catches, approached from the document side rather than the snapshot side.
Verification: plan-049 Issue 3.2; SC10 drives it in **both** directions — a bare gate heading to
exit 1, and the literal canonical Start Gate template (read out of `plan_template.py` by the
fixture builder, so a template change breaks the fixture rather than sliding past it) to exit 0.
Measured corpus firing: **2 gates** — `plan-006`'s `### Reconcile Gate` /
`- Not needed — no upstream issues incorporated`, and `plan-008`'s
`Capability Gate: d2 present (see above)` stub.

**The "declare it not needed" idiom (plan-006), decided explicitly.** It **fires**, and that is
a recorded decision rather than an oversight. `- Not needed — no upstream issues incorporated`
is free prose: no consumer can read it, so the gate is machine-indistinguishable from an
unfinished one. The conformant way to say it is `- Type: auto` plus a `- Condition:` giving the
reason. The idiom is not *exempted*, because an exemption for unstructured prose is an
exemption for anything. Instead both checks ship at **`W`**, so `STATUS_SEVERITY` demotes the
two historical instances to report-only while promoting the rule to `E` at `review` —
enforcement for new plans, no re-judgement of old ones, and no corpus write needed to land it.

REQ-DATA-056: The document linter shall be **vendored into the deployed skill tree with its
full transitive closure**, and shall resolve the repository root **explicitly** rather than
positionally.

- **Closure, not entry point.** `doc_lint.py` loads its schemas from a sibling
  `document_types/` and `resolve_derived()` imports `<module>.py` from its own directory, so
  the unit is `doc_lint.py` + `document_types/*.toml` + `plan_extract.py` + `plan_template.py`.
  Every schema is vendored, enumerated from canonical rather than hand-listed.
- **Root resolution** is `$YF_REPO_ROOT` → `git rev-parse --show-toplevel` → the nearest
  ancestor of the CWD carrying `.git` → the positional guess, last; `--root` overrides all of
  it.

Rationale: EXP-004 measured `find skills -name doc_lint.py` returning **empty** while
`embed.rs` embeds only `../skills` — so the always-on on-edit rule would have referenced an
engine present in **no deployed vault**. And a byte-identical copy would not have fixed it:
positional resolution makes the vendored copy compute its root as the *skill directory*,
matching no `docs/plans/**` glob, so it returns `files_checked: 0` — which is `verdict: PASS`,
exit 0, **indistinguishable from a clean run at every binding point**. A byte-identical vendor
of a root-relative script is not a vendor.
Verification: plan-049 Issue 4.1; SC15 asserts the closure is present and `sync.py --check` is
green; SC42 runs **both** copies over the same finding-producing document and diffs the JSON,
and separately demonstrates the old positional root producing `files_checked: 0` / PASS / exit 0.

REQ-DATA-057: `_audit_plan` shall run the document linter over the plan bundle and fold its
verdict into the audit findings, at **one** call site. The severity mapping is:

| Linter | Audit | Why |
| :-- | :-- | :-- |
| `E` | `fail` | the document does not have the shape its type declares, and intake is where that is caught |
| `W` / `R` | `warn` | informational; never blocks |
| `INCONCLUSIVE` | **`warn`, never `fail`** | see below |

**`Inconclusive` maps to `warn` and this is load-bearing.** INCONCLUSIVE means *the linter
could not run* — a missing schema dir, an unreadable document, an engine that was never
deployed. That is a claim about the instrument, not about the plan. Mapping it to `fail` turns
the linter's own breakage into an **intake outage**; mapping it to `pass` hides a linter that
silently stopped working. `warn` is the only reading that reports it without gating on it.

**One call site, deliberately.** `ready-check` and `audit` both call `_audit_plan` and branch
on its status, so they inherit the binding with their existing exit codes (3 and 1) unchanged,
and `audit_close` stays advisory for free because it ignores the status by contract. Binding
three sites separately produces three slightly different bindings.

**The binding inherits the audit's own grandfather level.** Linter `E` maps to
`okf_missing_level` — already `warn` for a date-grandfathered plan or an un-migrated
OKF-legacy one (no `plan.md` frontmatter), and `fail` only for an OKF-native plan — rather than
to a hard `fail` unconditionally. Without this the binding **re-judges history**: an un-migrated
legacy bundle has no frontmatter, no `## Gates`, no criteria table and a retired in-`plan.md`
phase log, so it fails ten `E`-severity document checks *by construction*. `STATUS_SEVERITY`
rescues the finished ones (a `complete` bundle demotes `E` to `R`), but an in-flight legacy plan
mid-migration would hard-fail its own audit for being what it has always been.

**Two lint calls, both required.** (a) the whole bundle **path-routed**, so `findings/*` is
graded as findings and `reviews/*` as reviews — that reach is the point, since plan-047's
blocking errors lived in `findings/*.md`, not `plan.md`; and (b) `plan.md` **forced** to the
`plan` type, because path routing selects nothing for a bundle outside the configured plans
root and "selected nothing" is `files_checked: 0` — PASS, exit 0, a silent green. Findings are
de-duplicated across the two.
Rationale: plan-047's Epic 9 named this enforcement point and nothing ever wired it, so a
non-conformant NEW plan was caught only by the FAST tier. The fail-closed gate that would have
blocked plan-047 at its own intake did not exist.
Verification: plan-049 Issue 4.2;
`skills/yf-plan/scripts/test_intake_lint_binding.py` drives SC16 — an in-flight bundle with an
injected malformed heading takes `ready-check` from exit **0** to exit **3** — alongside an
unmutated **control** at the same status, so the mutant arm is not satisfied by a binding that
refuses everything, and an absent-engine arm asserting `warn`.

REQ-DATA-058: A schema check may declare **`statuses`** — the list of `bundle_status` values it
applies to. When present, the check **does not run** outside that list.

This is **orthogonal to `STATUS_SEVERITY`**, and the distinction is the requirement: the
severity map changes what a finding *weighs*, `statuses` decides whether the check *runs at
all*. Where both apply, `statuses` is evaluated first.
Rationale: a **producer-version** check — one asserting that a generated document carries
something the *current* producer emits — will fire on every document an *older* producer wrote,
forever, at whatever severity it is declared. Measured: `disposition-alphabet-offered` fired on
**30 of the 31** selected files, the single non-firing file being the triage of the plan taking
the measurement. A rule that fires on essentially everything is a constant, and a constant
carries zero information; demoting it to `R` only makes the noise quieter. Scoping such a check
to in-flight statuses keeps the signal where an author can act on it and drops it where
re-judging a finished document teaches nobody anything.
Verification: plan-049 Issue 4.7; the rule is re-scoped to
`scoping|investigating|drafting|review|ready-for-approval`, taking the measured violation rate
from **30/31 to 0/31** (SC37's strict decrease) while still firing on an in-flight bundle whose
triage omits the alphabet.

REQ-DATA-059: `doc_lint.py` and `plan_extract.py` shall each accept a repeatable
**`--exclude <glob>`**, skipping inputs whose repo-relative path matches. A corpus measurement
taken by a plan **shall exclude that plan** (#135).

- `--exclude` is applied **unconditionally**, including under `doc_lint`'s `--no-exclude`
  positive control. The two are different kinds of thing: a schema's own `exclude` list is a
  carve-out `--no-exclude` deliberately defeats, whereas `--exclude` is the caller stating that
  the measurement is not about those files. A positive control that silently re-admitted the
  measuring plan would reintroduce the self-reference the flag exists to remove.
- The excluded set is **reported**, never silently dropped: an invisible exclusion is
  indistinguishable from an input that was never supplied, which is how a denominator quietly
  shrinks.
Rationale: #135 — a measured literal written into `plan.md` goes stale the moment the plan is
inside its own measured corpus. Deferred twice; plan-048 produced **three live instances**
(47→48 dirs, 112→119 review files, 174→180 `files_checked`), and plan-049 produced two more
during its own drafting. Prior art: plan-048's SC1 already self-excluded by hand.
Verification: plan-049 Issue 5.1; SC19 requires the assertion be **derived, not an era
literal** — run the measurement twice over the live tree and assert
`count(--exclude '<plan>/**') == count(unexcluded) - count(that plan alone)`, for at least two
different plans, with no fixed number anywhere in the assertion.

REQ-DATA-060: `doc_lint.py` shall carry a **`stale-measured-literal`** check reporting a bare
number written adjacent to a corpus-measurement noun (`files_checked`, `plan dirs`,
`report-only findings`, `review files`, `unparsed constructs`, `corpus files`).

It is scoped **hard**, and each scoping rule is earned:

| Rule | Why |
| :-- | :-- |
| runs only when `bundle_status != complete` | a finished plan's measurement is a **historical record** and is *supposed* to be frozen. Re-judging it is the measured-marker failure mode |
| skips `findings/` and `reviews/` | an experiment writeup and a review verdict are point-in-time records **by construction** |
| severity `W`, with **check-level `promote = false`** | a HINT must never hard-fail intake. REQ-DATA-053's schema-level opt-out is generalised to the check level so `plan.toml` can keep promoting `required-sections` — the actual intake gate — while this one stays `W` at every status |

**The blind spot is DENOMINATOR-ONLY, and shall be stated where a reader meets it.** The check
finds a stale **count**; it cannot find a stale **claim about** a count. "the populations
overlap at 144 of 1340" drifts silently when 1340 moves, and "roughly a third" carries no
literal at all. A numerator-drift instance passes green. The statement is required in three
places — the finding text, the schema declaration, and the engine docstring — because a reader
may meet the rule at any of them.
Rationale: upstream #135, deferred twice. plan-048 produced **three live instances**
(47→48 dirs, 112→119 review files, 174→180 `files_checked`) and plan-049 two more while
drafting. EXP-005 measured the naive form — any number near a corpus noun — firing **41 of 41
times with 39 correct-behaviour false positives**; the scoped form measured **2 fires, 2 true
positives, 0 false positives**.
Verification: plan-049 Issues 5.2/5.3; SC20 drives **both** arms — zero findings across the
finished corpus, and ≥2 on the same bundle forced in-flight, so the silence is scoping rather
than a dead rule — and SC21 greps the blind-spot statement in each of its three homes.


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

REQ-DATA-061: `doc_lint.py` shall provide a **`classify` mode** — a *preflight* that runs
**before** the lint and answers whether linting a given input is meaningful at all. It emits a
**`class`**, one of:

| `class` | Meaning | Exit |
| :-- | :-- | --: |
| `selected` | the path is selected by at least one schema's globs and is non-empty | `0` |
| `empty` | the path is selected but its content is empty | `0` |
| `not-selected` | the path exists but **no schema's path globs select it** | `1` |
| `no-such-path` | the path does not exist | `1` |

The exit contract of **this mode** is `0` = lintable, `1` = not lintable, `2` = the classifier
could not run. It does **not** replace the lint mode's contract (REQ-DATA-024 as amended); the
two vocabularies are keyed by mode.

- **`empty` is on the LINTABLE side, deliberately.** A selected-but-empty `plan.md` fails its
  schema, and the lint already says so loudly (measured: 6 `E` findings, exit 1). Skipping it
  would manufacture a new silent green inside the fix for a silent green. `empty` stays a
  distinguishable *class* because the diagnostic value is real; it does not get skip semantics.
- **Callers branch on `class`, never on the exit code alone.** The three non-`selected` classes
  would otherwise collapse into one, reinstating #181's conflation one layer up.
- **`classify` changes nothing about the lint.** No new verdict string, no new lint exit code, no
  change to selection. `--path` remains the explicit override REQ-DATA-024's engine documents.
- **`not-selected` means *not selected by PATH ROUTING*.** A `--type`-forced lint is unaffected:
  `plan_manager.py` deliberately re-lints a bundle's `plan.md` with the type forced, so a path
  `classify` calls `not-selected` *is* lintable by that route.
- `classify` accepts the same `--path` / `--root` inputs as the lint, so the `--root` form — a
  plan bundle **copied outside** `docs/plans/` — is answerable, which is #181's titled scenario.

Rationale: #181. `--path` on a real-but-unselected file and `--path` on a **nonexistent** file
both return `files_checked: 0, verdict: PASS`, exit 0 — byte-identical (EXP-003). Three states,
one verdict. Three earlier scopes were each refuted by measurement, and all three had mutated
the lint's own reporting: a general `files_checked == 0` form breaks `_shared/test_doc_lint.py`'s
SC42, and a `--path`-keyed-always form breaks its SC17 block, which pins an unselected `--path`
to `PASS`/rc 0 and identical to a nonexistent path. A separate preflight touches neither
assertion, so both remain literally true. `DOC-LINT.md`'s on-edit rule — today prose instructing
an agent to parse `files_checked` and reinterpret it — becomes an executed step with an exit
code, which is the whole deliverable: a step with no exit code is not a step.
Verification: `ctl-181-silent-green` drives five scenarios across the four classes and asserts
the exit on the `empty` and `selected` arms as well as the class; `uv run _shared/test_doc_lint.py`
reports `all passed` with the lint path unchanged; the corpus `files_checked` figure is equal
before and after (REQ-DATA-059 self-exclusion), any delta being a failure.

REQ-DATA-062: **Title fidelity.** Every title `plan_extract.py` emits — an epic `name` and an
issue `title` — shall equal its source line's corresponding span **verbatim**, inline code spans
included. The capture shall be taken from the **unmasked** source line by **offset-slicing** the
match (`raw[m.start(<group>):m.end(<group>)]`), which `mask_inline_code`'s documented
length-preservation guarantees correct, and **never** by re-matching `ISSUE`/`EPIC` against
`raw`. `try_trailing`, `SUBKEY`, `EPIC` and `ISSUE` continue to match against the **masked**
line; only the title capture reads `raw`. Both capture sites are in scope — the `EPIC` name and
the `ISSUE` title.
Rationale: #186. `mask_inline_code` blanks `` `code` `` to spaces so a `depends-on:` written
inside a code span is documentation rather than a declaration (`plan_extract.py:142`) — correct,
and preserved. But the title is captured from the *masked* line, so every backticked term is
blanked out of the emitted title, and `--strict` reports `unparsed: []` and exit **0** while the
output is corrupt. §5.2a pours that corruption straight into the bead DAG. Measured upstream: 4
of 35 titles blanked on one plan; 27 of 34 on this one. The naive `ln = raw` repair was measured
at pass 10 producing a **spurious edge to a nonexistent target** and driving `--strict` non-zero
— which is why the requirement names the offset form specifically rather than "read `raw`".
Verification: `ctl-186-masked-title` exits non-zero pre-fix and zero post-fix; a code-span
`depends-on:` still produces no edge (REQ-DATA-062's companion assertion); re-extracting this
plan's own bundle restores the measured title delta.

REQ-DATA-063: **Issue `detail`.** Each issue object `plan_extract.py` emits shall carry a
**`detail`** field: the issue bullet's continuation lines, joined, **minus** the sub-key bullets
the parser already consumes (`depends-on:`, `resolves-upstream:`, in both the two-space-indented
and recovered column-0 forms). An issue with no remaining continuation prose carries an **empty**
`detail`, which is a valid value and not an error.
Rationale: #187. SKILL.md §5.2a instructs an executor to derive the bead DAG mechanically from
`plan_extract.py`'s output and pass `--description=${issue_detail}` — but the extractor emits no
such field, so a mechanical pour yields beads with **empty descriptions** (measured: 35 of 35 on
one plan) while the DAG itself is perfect. This is framing 1 of the issue — make the extractor
honest — rather than framing 2, weakening the documentation to match. The exclusion of the parsed
sub-keys is what makes the field a *schema* addition rather than a raw-text dump: the same bytes
must not be reachable both as a structured edge and as prose.
Verification: `ctl-187-empty-detail` exits non-zero pre-fix and zero post-fix; a bead poured from
the output of a plan whose issues carry continuation prose has a non-empty description; on a plan
whose issues carry none, every `detail` is empty and that is recorded as a negative observation.
