# Plan: Create a yf-okf skill and adopt it in yf-plan, yf-research, and yf-incubator as the standard way to construct and manage their artifact folders

**ID:** plan-029-james-dixson-75fd34
**Author:** james-dixson
**Created:** 2026-07-17
**Status:** complete
**Epic:** yf-mol-w21
**Fingerprint:** 6088f15ad7bc49c1cba3a165e3e128788dadfc157f75fd28e85f828e0a8d5fc6
**Phase log:**
- 2026-07-17 scoping: initial scope captured
- 2026-07-17 investigating: 3 experiments identified: plan_manager coupling, shared-engine API surface, OKF type/frontmatter schema
- 2026-07-17 drafting: synthesizing plan from 2 investigations
- 2026-07-17 review: plan v1 presented
- 2026-07-17 review: red-team cycle 2: APPROVE
- 2026-07-17 ready-for-approval: ready-check green — last red-team APPROVE + audit pass
- 2026-07-17 drafting: reframe: OKF-* spec family (BASELINE + YF-EXTENSIONS + per-skill OKF-EXTENSION.md); dual-mode field accessor
- 2026-07-17 review: plan v2 presented (framework reframe)
- 2026-07-17 review: red-team cycle 4: APPROVE
- 2026-07-17 ready-for-approval: ready-check green — cycle-4 APPROVE + audit pass (framework reframe)
- 2026-07-18 drafting: add OKF-* impact-assessment epic + ratification human gate (this repo + Obsidian Primary corpus)
- 2026-07-18 review: plan v3 presented (impact-assessment epic + ratification gate)
- 2026-07-18 review: red-team cycle 6: APPROVE
- 2026-07-18 ready-for-approval: ready-check green — cycle-6 APPROVE + audit pass (assessment epic)
- 2026-07-18 approved: operator approved
- 2026-07-18 intake: epic yf-mol-w21 poured
- 2026-07-18 executing: start gate resolved
- 2026-07-19 reconciling: bead DAG drained; entering land-the-plane
- 2026-07-19 complete: plan complete — OKF-* framework landed at 709a646, #83 closed

## Objective
Create a yf-okf skill and adopt it in yf-plan, yf-research, and yf-incubator as the standard way to construct and manage their artifact folders

## Motivation

The three artifact-producing yf skills — `yf-plan`, `yf-research`, `yf-incubator` — each
hand-roll their own folder layout (filenames, index manifest, change log, metadata form) with
no shared construction engine. Research 001 (`docs/research/001-okf-compliance-delta/`, issue
#91) established that these folders diverge from the **Open Knowledge Format** (OKF v0.1,
`GoogleCloudPlatform/knowledge-catalog`) on two conceptual axes — no YAML frontmatter, and
divergent reserved index filenames (`README.md` / `_index.md` vs OKF `index.md`) — plus the
phase-log-in-`plan.md` vs a reserved `log.md`.

Issue **#83** asks to investigate and integrate OKF for these folders. This plan implements the
integration as an **opinionated framework**: a new **`yf-okf`** skill that is both the shared engine
for *constructing* and *managing* artifact bundles AND the owner of a versioned **OKF-\* spec
family** that says how each kind of yf artifact is structured and annotated. The goal is
"**compatible with** OKF" — adopt OKF's structure/annotation recommendations as a **baseline**, then
**extend** them with the conventions engineering/planning artifacts actually need. Beneficiaries: any
consumer of a yf artifact folder (the emerging OKF linter/validator/MCP-server ecosystem, and Google
Knowledge Catalog ingestion), and — the primary payoff — a firm, shared opinion about how yf skill
artifacts are built and maintained, so every current and future artifact skill inherits one engine
and one spec family instead of re-inventing folder layout.

### The OKF-\* spec family (framework model)

- **`yf-okf/spec/OKF-BASELINE.md`** — the upstream OKF v0.1 rules/recommendations, distilled from
  research 001 (verbatim what OKF says). The baseline we are compatible *with*.
- **`yf-okf/spec/OKF-YF-EXTENSIONS.md`** — the yoshiko-flow extensions layered on the baseline:
  extension-key namespacing, the dual **frontmatter + `**Field:**`** field model, the `log.md`
  format choice, and reserved-file/subdir conventions beyond OKF.
- **Per-artifact-type extension specs, bundled with the skill that leverages them**, at a
  discovery-by-convention path so yf-okf finds them without configuration:
  `skills/yf-plan/OKF-EXTENSION.md` (= **OKF-PLAN**), `skills/yf-research/OKF-EXTENSION.md`
  (**OKF-RESEARCH**), `skills/yf-incubator/OKF-EXTENSION.md` (**OKF-INCUBATOR**). An internal
  `okf_spec:` identifier names the member. **OKF-SPECIFICATION** (for engineering `SPEC.md` files) is
  a **reserved** family name, deferred to a follow-on.
- yf-okf's engine (`scaffold`/`check`/`migrate`) is parameterized by
  **OKF-BASELINE ∪ OKF-YF-EXTENSIONS ∪ the resolved per-skill OKF-EXTENSION**.

**Override of the research recommendation (explicit).** Research 001's *primary* recommendation was
the **export-emit / least-regret** path and it cautioned that full-native frontmatter is high-cost
against a v0.1 *draft* standard with thin (Google-only) adoption, and that moving the phase log to
`log.md` disturbs `plan_manager.py`'s in-`plan.md` review reconciliation. The operator chose
**native OKF-compatible construction** at scoping anyway: the bet is that a firm opinionated framework
(native structure + an owned, extensible spec family) is the durable "standard way to construct and
manage" the objective asks for. The research's concern that OKF is a moving draft is answered by the
BASELINE/EXTENSIONS split — we pin and own our extension layer, so upstream OKF drift touches only
`OKF-BASELINE.md`, not the artifacts. The risks research flagged (R1/R2 below) are carried as
first-class, gated risks rather than dismissed.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|
| #83 | Investigate OKF compliance + integration for yf-plan / yf-research folders | include | This plan is the integration #83 asks for | plan-029 (all epics) |
| #91 | research 001: OKF compliance-delta (research record) | exclude | Completed research record whose least-regret recommendation this plan deliberately **overrides** (see Motivation); referenced as the source being overridden, not resolved | — |

## Scope Decisions

Captured at scoping + the framework-reframe follow-up (operator answers, 2026-07-17):

1. **Architecture — shared construction engine + owned spec family.** `yf-okf` owns folder
   scaffolding + `index.md` / `log.md` / frontmatter management AND the **OKF-\* spec family**
   (OKF-BASELINE, OKF-YF-EXTENSIONS, and per-skill OKF-EXTENSION resolution — see Motivation).
   `yf-plan` / `yf-research` / `yf-incubator` delegate construction/management to it and each bundle
   their own `OKF-EXTENSION.md`. yf-okf is the single source of truth for how yf artifacts are
   structured and annotated.
2. **On-disk form — native OKF-compatible (baseline + extensions).** Folders adopt the OKF baseline
   (reserved `index.md` replacing `README.md` / `_index.md`; reserved `log.md` replacing the
   in-`plan.md` `**Phase log:**` and yf-research phase log; YAML frontmatter with a non-empty `type`
   on every non-reserved `.md`) **and** the yoshiko-flow extensions. Requires reworking each skill's
   layout AND `plan_manager.py`'s heading-based audit (README→index.md, phase-log→log.md).
3. **Field storage — dual-write frontmatter + `**Field:**`.** New artifacts write BOTH a YAML
   frontmatter block (machine / OKF surface) and the human-readable `**Field:**` lines, kept in sync
   by a single writer. `plan_manager.py` is **properly factored into a dual-mode field accessor**:
   read frontmatter-first, fall back to legacy `**Field:**` (so un-migrated plans keep working). This
   replaces the earlier "keep `**Field:**`, add only `type:`" note.
4. **Spec family scope — BASELINE + YF-EXTENSIONS + 3 consumers.** Author the resolver mechanism,
   `OKF-BASELINE.md`, `OKF-YF-EXTENSIONS.md`, and the three consumer `OKF-EXTENSION.md`
   (OKF-PLAN / OKF-RESEARCH / OKF-INCUBATOR). **OKF-SPECIFICATION** is a reserved family name,
   **deferred** to a follow-on (not authored or applied to `SPEC.md` files here).
5. **Assess-then-ratify before implementation.** Once the OKF-\* specs are drafted, a dedicated epic
   assesses their impact — via `yf-okf check` + `migrate --dry-run` — against **two real corpora**:
   this repo's plans/research/incubators AND the `~/Documents/Obsidian/Primary` vault's
   plans/research/incubators. The assessment produces impact reports (how each directory would change
   under full baseline conversion) and sample **test migrations on copies**, which feed back into
   re-deriving/refactoring the OKF-\* specs. A **human OKF-\* Ratification Gate** reviews the refactored
   proposals + reports + samples before any implementation epic starts. The external vault is treated
   read-only (never mutated).
6. **Migration — opt-in command.** Ship `yf-okf migrate <dir>`; run per-folder on demand. Existing
   ~28 plan folders + research 001 + incubators are **grandfathered** (precedent: the portability
   activation date in `plan_manager.py`), not bulk-rewritten.
7. **Sequencing — skill + all three integrations in one plan.** SPEC-first `yf-okf` skill + spec
   family, then the impact-assessment/ratification epic, then `yf-plan`, `yf-research`, `yf-incubator`
   integration epics, landing as one coherent change. *Optional interior checkpoint:* Epic 1
   (foundation) + Epic 2 (ratification) + Epic 3 (highest-risk axis, capability gates cleared) form a
   natural landing point; Epics 4/5 are independent integrations that could land incrementally if the
   execute branch ages.

### Constraints & non-goals

- **SPEC-first (AGENTS.md).** The `yf-okf` `SPEC.md` requirement lands before implementation; each
  behavior change is tagged to a `REQ-*` id.
- **Grandfather, don't break.** Existing completed folders must keep passing their audits; the
  full-native rework applies going forward + via opt-in migrate.
- **Conservative git authority.** Execution reports a push handoff; no auto-push.
- **Non-goal:** authoring OKF tooling (linters/validators) — those exist in the ecosystem; yf-okf
  is a *producer/manager*, not a third-party validator (though a conformance self-check is in scope).
- **Non-goal:** the OKF `# Citations` heading convention (SPEC §8, a SHOULD-level guideline).
  Research `sources.md` already uses GFM citation links; normalizing to OKF's numbered `# Citations`
  form is out of scope for this plan (soft guidance, not a conformance requirement).
- **Non-goal (deferred):** **OKF-SPECIFICATION** and retrofitting the skills' engineering `SPEC.md`
  files. The family name is reserved in `OKF-YF-EXTENSIONS.md`, but authoring the member and applying
  it to `SPEC.md` files is a follow-on, not this plan.

## Investigation Findings

Two read-only code-mapping investigations (see `findings/`):

- **exp-001 — plan_manager.py OKF coupling.** README→index.md is a *rework* (the OKF listing
  format is incompatible with the current `File map`/`Reading order` heading check), not a rename.
  The phase-log move is the **high-risk axis**: three plan.md-text parsers
  (`_plan_review_line_count` → REQ-PORT-006 count-equality; `_plan_first_scoping_date` →
  grandfather clause; the `update_status`/`record_epic` appenders) silently break when the phase
  log leaves plan.md. The **fingerprint is safe by construction** — its exclusion is positional
  (everything before the first `## ` is dropped), so removing the phase log and adding frontmatter
  *above the first `## `* are both hash-neutral. Frontmatter is greenfield (zero existing
  parse/emit). Recommend keeping `**Field:**` header lines and adding only `type:`.
- **exp-002 — shared-engine API surface.** `_shared/` exists at repo root; skills **cannot import
  each other** (independent-installability invariant) — sharing is by **vendoring** via
  `_shared/sync.py` (fenced-region or whole-file, e.g. `manifest_update.py` copied into 5 skills).
  So yf-okf = a **skill** (user surface: migrate/check) **+ canonical `_shared/okf.py`
  whole-file-vendored** into each consumer's `scripts/okf.py`. Shared ops: `scaffold_bundle`,
  `write/read_frontmatter`, `append_log` (newest-first), `check_conformance`, `migrate`. Index/log
  *rendering* needs per-skill adapters (the three current models genuinely differ). Divergences to
  resolve: research `_index.md` table vs OKF `index.md` listing; single-file incubators have no room
  for reserved files; non-`.md` files (`plan.yaml`/`sources.json`) must be excluded from the
  frontmatter-`type` rule.

## Approach

Build **`yf-okf`** as a shared bundle engine **and** the owner of the OKF-\* spec family, and adopt
it in the three consumer skills, SPEC-first, landing native OKF-compatible construction going forward
with opt-in migration for legacy folders.

1. **Engine + skill + spec family (per exp-002).** Canonical engine lives at `_shared/okf.py`,
   **whole-file-vendored** into each consumer's `scripts/okf.py` via `_shared/sync.py` (the
   `manifest_update.py` precedent), with `yf-drift-check` `value-equal` edges guarding the copies. A
   `skills/yf-okf/` skill provides the operator surface (`/yf-okf init | migrate | check`) and owns
   the family reference docs (`OKF-BASELINE.md`, `OKF-YF-EXTENSIONS.md`). The engine **resolves each
   consumer's `skills/<skill>/OKF-EXTENSION.md` by convention** and composes
   BASELINE ∪ YF-EXTENSIONS ∪ per-skill extension into the effective ruleset. No cross-skill imports.
2. **SPEC-first (AGENTS.md).** Land `skills/yf-okf/SPEC.md` (REQ-OKF-*) + the family reference docs
   *before* engine code, and land each skill's `OKF-EXTENSION.md` + its `spec/` amendments *before*
   that integration's code. The OKF baseline is pinned to `okf_version: 0.1`; upstream OKF drift is
   isolated to `OKF-BASELINE.md`.
3. **Native OKF-compatible on disk, dual-write field model.** Every non-reserved `.md` gets YAML
   frontmatter with a non-empty `type`, placed **above the first `## `** (keeps the fingerprint
   hash-neutral). Reserved `index.md` (progressive-disclosure listing, no frontmatter except a
   bundle-root `okf_version`) replaces `README.md` / `_index.md`; reserved `log.md` (newest-first
   ISO-8601 date headings) replaces the in-`plan.md` phase log and yf-research's timestamp ledger.
   Header metadata is **dual-written**: frontmatter (machine/OKF) **and** the human `**Field:**`
   lines, both emitted by one writer from a single in-memory model. `plan_manager.py`'s six
   `**Field:**` parsers are refactored into **one dual-mode accessor** (read frontmatter-first, fall
   back to `**Field:**`), so un-migrated plans keep working.
4. **Opt-in migration, grandfather preserved.** `yf-okf migrate <dir>` converts a folder in place;
   existing completed folders are left untouched and stay grandfathered. Migration's top invariant:
   preserve the first-`scoping:` date into `log.md` so the grandfather clause does not flip to fail,
   and keep the content fingerprint stable so migrated approved plans don't go stale-approved.

**Execution note (two-address-space / installed-copy hazard).** Under the worktree-execute model,
each consumer's vendored `scripts/okf.py` must be **committed on the execute branch (Issue 1.6)
before** the integration Epic 3–5 code invokes it, and all testing drives the **worktree** skill copy — never
the installed rust-embed copy (per `TESTING.md`). `plan_manager.py` edits take effect only through
the worktree checkout, not a `${SKILL_DIR}` that resolves to the installed skill. This is why Epic 1
(engine + vendoring) fully precedes the integration epics.

**Representative `type` vocabulary** (open vocab; each skill's `OKF-EXTENSION.md` owns its set):
OKF-PLAN → `Plan` (plan.md), `Finding` (findings/*), `Review` (reviews/pass-*), `Environment`
(context.md), `Reference` (references/upstream-*); OKF-RESEARCH → `Research Report` (Summary.md),
`Research Artifact` (artifacts/*), `Reference` (sources.md); OKF-INCUBATOR → `Incubator` (state
file). Each artifact also carries an `okf_spec:` frontmatter key naming its extension member (e.g.
`okf_spec: OKF-PLAN`). Reserved `index.md`/`log.md` carry no `type`.

## Epics

### Epic 1: yf-okf SPEC, spec family & engine (foundation)
- Issue 1.1: Write `skills/yf-okf/SPEC.md` — REQ-OKF-* for the bundle model, reserved `index.md`
  (§6 listing) and `log.md` (§7 newest-first) rules, the frontmatter+non-empty-`type` invariant and
  a placement REQ that **both the frontmatter block AND the `**Field:**` block MUST sit above the
  first `## `** (so neither enters the content fingerprint), the dual **frontmatter + `**Field:**`**
  field model, the `okf_spec:` member key, the **OKF-\* family + per-skill `OKF-EXTENSION.md`
  discovery/composition** contract (BASELINE ∪ YF-EXTENSIONS ∪ per-skill), the single-file-bundle
  exemption, the non-`.md` exclusion, the §9 conformance test, and migration semantics.
  **Resolve the independent-installability edge explicitly:** the machine-readable BASELINE +
  YF-EXTENSIONS ruleset is **baked into `okf.py`** (the `OKF-BASELINE.md` / `OKF-YF-EXTENSIONS.md`
  docs are the human-readable spec, kept in agreement with the in-code ruleset by a `yf-drift-check`
  edge — no cross-skill file read); `resolve_extension` finds `skills/<skill>/OKF-EXTENSION.md` via
  `__file__`-relative resolution (each skill bundles its own extension beside its vendored `okf.py`),
  so full `check_conformance` composition runs from any vendored copy in both the worktree and
  installed address spaces. **Two foreign-corpus REQs** (the engine must survive a real external
  vault, not just greenfield yf folders): (a) `write_frontmatter`/`migrate` **merge-and-preserve** —
  add only `type:`/`okf_spec:` (and other yf keys), **never drop or overwrite** a pre-existing
  frontmatter key (e.g. Obsidian `tags`/`aliases`/`cssclass`); (b) `check`/`migrate --dry-run` are
  **report-only and crash-safe** — on non-conforming or unexpected input they record a finding and
  continue, never raising. **(SPEC-first anchor.)**
- Issue 1.2: Author the family reference docs — `skills/yf-okf/spec/OKF-BASELINE.md` (the upstream
  OKF v0.1 rules/recommendations distilled from research 001, verbatim what OKF says) and
  `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` (the yoshiko-flow extension layer: extension-key
  namespacing, dual field model, `log.md` format, reserved subdirs). Reserve the **OKF-SPECIFICATION**
  family name with a "deferred" stub. **(SPEC-first; the reference the engine enforces against.)**
  - depends-on: 1.1
- Issue 1.3: Author the three per-skill extension drafts — `skills/yf-plan/OKF-EXTENSION.md`
  (**OKF-PLAN**: type vocab Plan/Finding/Review/Environment/Reference, required extension keys
  id/author/created/status/epic/fingerprint + upstream dispositions + review passes, reserved subdirs
  findings/reviews/references, the dual field set), `skills/yf-research/OKF-EXTENSION.md`
  (**OKF-RESEARCH**: Research Report / Research Artifact / Reference, the `sources.json`/`plan.yaml`
  non-`.md` exclusion, the research index-body convention), and `skills/yf-incubator/OKF-EXTENSION.md`
  (**OKF-INCUBATOR**: `type: Incubator`, single-file-bundle exemption, dir-form reserved-file mapping).
  These are the **draft** proposals the Epic-2 assessment stress-tests and the ratification gate
  reviews. **(SPEC-first; discovered by the engine's resolver.)**
  - depends-on: 1.1, 1.2
- Issue 1.4: Implement `_shared/okf.py` — the baked-in BASELINE + YF-EXTENSIONS machine-readable
  ruleset, `scaffold_bundle`, `write_fields`/`read_fields` (dual-mode: write frontmatter + `**Field:**`;
  read frontmatter-first with `**Field:**` fallback), `write_frontmatter`/`read_frontmatter`,
  `render_index`/`add_index_entry`, `append_log` (newest-first), `resolve_extension`
  (`__file__`-relative find + parse of `skills/<skill>/OKF-EXTENSION.md`), `check_conformance`
  (parameterized by the composed ruleset), `emit_conformant_copy`, `migrate` (with a **`--dry-run`**
  mode the Epic-2 assessment relies on); implement the two foreign-corpus REQs from 1.1 —
  **merge-and-preserve** frontmatter (never drop existing keys) and **report-only / crash-safe**
  scanning (findings, never exceptions) — with tests over messy-input fixtures (pre-existing
  frontmatter, malformed YAML, non-conforming files). PEP 723 inline deps (pyyaml); tagged tests
  against each REQ-OKF-*. **Include a resolver-composition unit test using a synthetic fixture
  `OKF-EXTENSION.md`** so composition is proven here, before later epics depend on it.
  - depends-on: 1.1, 1.2, 1.3
- Issue 1.5: Author `skills/yf-okf/` — `SKILL.md`, agent(s), `/yf-okf init | migrate | check | assess`
  surface, preflight + `protocols/manifest.json` per yf-skill-authoring; attribution MIT/current-year.
  - depends-on: 1.4
- Issue 1.6: Register `okf.py` in `_shared/sync.py` canonical→copy map; vendor into each consumer's
  `scripts/okf.py`; add `yf-drift-check` `value-equal` edges; confirm `_shared/sync.py --check` clean.
  The vendored copies must be **committed on the execute branch before** the integration Epics 3–5
  invoke them (two-address-space bootstrap — see Approach execution note).
  - depends-on: 1.4, 1.5

### Epic 2: OKF-* impact assessment & ratification (human-gated)
- Issue 2.1: Assess impact on **this repo's** corpus — **discover** every artifact bundle under BOTH
  roots the skills use: the default `docs/plans/*` and `docs/research/*`, AND incubator-scoped
  `Incubator/<slug>/plans/*` and `Incubator/<slug>/research/*`, plus any single-file/dir-form
  incubator. Run `yf-okf check` + `migrate --dry-run` over each and produce
  `findings/okf-impact-this-repo.md`: per-artifact-type, exactly how each directory would change under
  a full baseline conversion (README→index.md, phase-log→log.md, frontmatter/`type` additions) and
  every inconsistency the drafts surface. Read-only; no folder is mutated.
  - depends-on: 1.3, 1.4, 1.5
- Issue 2.2: Assess impact on the **`~/Documents/Obsidian/Primary`** vault corpus — **first snapshot
  the vault to a scratch copy** (it is a live git repo; per R8 all Epic-2 ops run against the copy,
  never the live vault). **Discover** its bundles under the same two-root model (`docs/plans`,
  `docs/research`, and `Incubator/<slug>/{plans,research}`) — do NOT assume top-level `plans/`. Run
  the same `check` + `migrate --dry-run`, producing `findings/okf-impact-primary-vault.md` and noting
  structural differences from this repo: **pre-existing Obsidian frontmatter** (`tags`/`aliases` the
  engine must merge-preserve, not clobber — REQ in 1.1), wikilinks/embeds, single-file incubators, a
  larger real corpus, and the possibility that the vault runs a **different installed yf-flow
  version/layout** (surface as divergence, do not assume vault ≡ this-repo layout).
  - depends-on: 1.3, 1.4, 1.5
- Issue 2.3: Re-derive / refactor the OKF-* proposals — run representative **test migrations on
  copies** of samples from both corpora, work out the inconsistencies the reports surface, and feed
  fixes back into: `OKF-BASELINE.md` (rare), `OKF-YF-EXTENSIONS.md`, the three `OKF-EXTENSION.md`
  drafts, **AND the engine `okf.py` itself** when a finding is engine-level (e.g. a frontmatter-merge
  or crash-safety gap) — an engine finding reopens Issue 1.4, it is not forced into a spec-doc edit.
  Iterate until sample migrations are clean. Output: the refactored specs/engine + a
  `findings/okf-migration-samples/` set of before/after examples for the gate.
  - depends-on: 2.1, 2.2
  - Gated by: **OKF-\* Ratification Gate** (below) — implementation Epics 3–5 do not start until the
    operator reviews and approves the refactored proposals.

### Epic 3: yf-plan integration (highest risk)
- Issue 3.1: SPEC amendments in `skills/yf-plan/spec/` — REQ-PORT-001 (README→index.md + structure
  check), REQ-PORT-006 (review-line source → log.md), REQ-PORT-040 (make phase-log exclusion explicit
  + frontmatter-aware), REQ-PORT-ACT / REQ-DATA-012 (log.md format + location), new REQ for the
  global "every non-reserved `.md` has non-empty `type`" check, and a new REQ for the **dual-mode
  field accessor** (frontmatter-first, `**Field:**` fallback) + the dual-write consistency invariant.
  **(SPEC-first, before 3.2+; consumes the ratified OKF-PLAN extension.)**
  - depends-on: 1.1
  - Gated by: OKF-\* Ratification Gate
- Issue 3.2: Refactor `plan_manager.py` field access into **one dual-mode accessor** — collapse the
  six `**Field:**` parsers (`_read_plan_status`, `_read_plan_epic_field`,
  `_read_plan_fingerprint_field`, and the `update_status`/`record_epic`/`fingerprint write` sites)
  into read frontmatter-first / fall-back-to-`**Field:**`, and a single writer that emits BOTH
  representations in sync. Delegates frontmatter I/O to the vendored engine.
  - depends-on: 1.6, 3.1
- Issue 3.3: Repoint construction to the vendored engine — `seed_readme`→`index.md` (OKF listing),
  dual-write frontmatter + `**Field:**` on plan.md, `type` frontmatter on all non-reserved `.md`.
  Also repoint the **`agents/captor.md`** agent (which authors the file-map/reading-order document)
  to emit the OKF `index.md` listing instead of `README.md`.
  - depends-on: 1.6, 1.3, 3.2
- Issue 3.4: Move the phase log to `log.md` — repoint `update_status`/`record_epic` appenders and the
  audit's `_plan_review_line_count` + `_plan_first_scoping_date` readers to `log.md` (newest-first).
  - depends-on: 3.1, 1.6
- Issue 3.5: Rework the portability audit — checks #1 (index structure), #5 (count-equality from
  log.md), grandfather gate (first-scoping date from log.md), + new `type`-frontmatter check + a
  **frontmatter/`**Field:**` consistency check** (dual-write divergence, R7).
  - depends-on: 3.3, 3.4
- Issue 3.6: Fingerprint-stability + migration + dual-representation tests — assert
  frontmatter-above-`##` and phase-log removal are hash-neutral; the dual-mode accessor reads a
  frontmatter-only, a `**Field:**`-only, and a dual plan identically; a migrated legacy plan
  preserves grandfather status and REQ-PORT-006 count-equality and does not go stale-approved.
  **(Satisfies the Epic-3 capability gate.)**
  - depends-on: 3.5
- Issue 3.7: Update the legacy-layout test fixtures to the OKF model — `scripts/test_worktree.py`
  (seeds `README.md` + `**Phase log:**`) and `test-harness/smoke.sh` (scaffolds `README.md`) so the
  suite exercises `index.md` / `log.md` / dual-write frontmatter.
  - depends-on: 3.3, 3.4

### Epic 4: yf-research integration
- Issue 4.1: SPEC amendment for the research dir layout (`_index.md`→`index.md`; frontmatter+`type`
  on Summary.md / artifacts/*.md / sources.md; `plan.yaml`/`sources.json` excluded as non-`.md`).
  **(SPEC-first; consumes the ratified OKF-RESEARCH extension.)**
  - depends-on: 1.1
  - Gated by: OKF-\* Ratification Gate
- Issue 4.2: Update `index_manager.py` to delegate to the vendored engine — rename `_index.md`→
  `index.md`, reconcile the timestamped table with the OKF listing body (decision locked in 1.3/4.1),
  add `type` frontmatter emit.
  - depends-on: 1.6, 1.3, 4.1
- Issue 4.3: Repoint the rest of the `_index.md` fan-out (the reserved filename is hard-coded beyond
  `index_manager.py`) — `scripts/link_normalizer.py` (`rewrite_index` / `link_index`: the filename
  AND the table-column shape), `agents/packager.md` (step 5 writes the index), the
  `yf-research.formula.toml` step description, `spec/portability.md` REQ-PORT-006, and
  `scripts/test_link_normalizer.py`. Without this the research link-normalization pipeline silently
  breaks on a renamed `index.md`.
  - depends-on: 4.2

### Epic 5: yf-incubator integration
- Issue 5.1: SPEC amendment — add `type` to the existing frontmatter (7→8 keys); `## Decision log`→
  `log.md` for dir-form bundles; per-bundle `## Files`→`index.md` for dir-form; **single-file
  bundles exempt** from reserved files; repo-level `Incubator/INDEX.md` stays (not a bundle index).
  **(SPEC-first; consumes the ratified OKF-INCUBATOR extension.)**
  - depends-on: 1.1
  - Gated by: OKF-\* Ratification Gate
- Issue 5.2: Update the incubator scaffold + `incubator-index.py` `parse_frontmatter` to go through
  the vendored engine; implement the single-file special-case; keep `INDEX.md` generation.
  - depends-on: 1.6, 1.3, 5.1

### Epic 6: Cross-cutting validation, docs & reconcile
- Issue 6.1: Update repo docs/rules referencing folder layout (AGENTS.md, PLANS.md/RESEARCH.md
  protocol copies, any `DRIFT-CHECK.md` / `CHANGE-VALIDATION.md` manifests) to the OKF-native model.
  - depends-on: 3.5, 4.3, 5.2
- Issue 6.2: End-to-end check — create one fresh folder per skill through the engine and confirm
  `yf-okf check` passes and **resolves each skill's `OKF-EXTENSION.md`**; **drive a full yf-research
  cycle's link-normalization against the renamed `index.md`** (guards the Issue 4.3 fan-out); run
  `_shared/sync.py --check` and the full change-validation tier.
  - depends-on: 3.6, 3.7, 4.3, 5.2

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### OKF-\* Ratification Gate (Epic 2 — the operator's spec review)
- Type: human
- Condition: the operator has reviewed the refactored OKF-\* proposals (`OKF-BASELINE.md`,
  `OKF-YF-EXTENSIONS.md`, and the three `OKF-EXTENSION.md`) together with the two impact reports
  (`findings/okf-impact-this-repo.md`, `findings/okf-impact-primary-vault.md`) and the sample
  before/after test migrations (`findings/okf-migration-samples/`), and **approves the proposals**
  (or sends them back for another assessment/refactor pass — a REVISE loop within Epic 2).
- Test: human review; the sample test migrations in `findings/okf-migration-samples/` apply cleanly
  (`yf-okf migrate --dry-run` reports no unresolved inconsistency on the reviewed samples).
- Blocks: Issues 3.1, 4.1, 5.1 — i.e. **all implementation Epics 3–5 start only after ratification**.
- Instructions: walk the impact reports per artifact type; confirm each `OKF-EXTENSION.md` accounts
  for the inconsistencies its corpus surfaced; approve, or loop back to Issue 2.3. **Termination
  lever:** if an artifact type will not converge after a refactor pass, exercise R9 (exempt or
  descope that type) rather than looping indefinitely.

### Capability Gate: extension-resolver composition (Epic 1)
- Type: human
- Condition: the engine resolves a skill's `OKF-EXTENSION.md` by `__file__`-relative path and
  composes BASELINE ∪ YF-EXTENSIONS ∪ per-skill into a single effective ruleset, proven by a unit
  test (synthetic fixture) — before the assessment (Epic 2) and integrations (Epics 3–5) build on it.
- Test: the Issue 1.4 resolver-composition unit test is green; `yf-okf check` on a fixture bundle
  reports the composed ruleset.
- Blocks: Issues 2.1, 2.2 (assessment `check`/`migrate --dry-run` calls the resolver), 3.3, 4.2, 5.2
  (the construction repoints that call the resolver).
- Instructions: run the Issue 1.4 test suite; confirm composition resolves in a simulated installed
  address space (script + bundled `OKF-EXTENSION.md` only, no sibling skills present).

### Capability Gate: migrated-legacy-plan safety (Epic 3)
- Type: human
- Condition: a migrated legacy plan folder passes `plan_manager.py audit` with grandfather status
  and REQ-PORT-006 count-equality preserved, and its content fingerprint is unchanged (not
  stale-approved).
- Test: `uv run skills/yf-plan/scripts/plan_manager.py audit <migrated-legacy-plan> --json-output`
  returns `status: pass`; the fingerprint-stability + dual-representation unit tests (Issue 3.6) are
  green.
- Blocks: Issue 6.2 (end-to-end), and merging Epic 3 to the base.
- Instructions: run the Issue 3.6 test suite against a copy of a real pre-activation plan folder.
- Note: this gate guards the *plan* migration path only; the yf-research `index.md` rename fan-out
  (Issue 4.3) is guarded by the Issue 6.2 link-normalization end-to-end check, not this gate.

### Reconcile Gate (upstream #83 incorporated)
- Type: auto (all execution beads closed)
- Blocks: reconcile step (updates issue #83)

## Risks & Mitigations

| # | Risk | Sev | Mitigation |
|:--|:--|:--|:--|
| R1 | Phase-log move silently breaks REQ-PORT-006 count-equality + the grandfather clause (3 parsers return empty) | high | SPEC-first repoint (3.1/3.4); Epic-3 capability gate + Issue 3.6 test on a real migrated legacy plan |
| R2 | Migrating an approved plan flips its fingerprint → stale-approved, blocking execute | high | Positional exclusion keeps the hash stable (exp-001); frontmatter forced above first `##`; assert with a fingerprint-stability test; migrate is opt-in |
| R3 | OKF v0.1 is a draft and may change | med | The BASELINE/EXTENSIONS split isolates upstream drift to `OKF-BASELINE.md` + the baked-in ruleset; pin `okf_version: 0.1`; the yf extension layer is owned/versioned independently; **follow-on bead** (filed at execution) for a BASELINE re-sync checkpoint keyed to upstream OKF version bumps |
| R7 | Dual-write frontmatter + `**Field:**` diverge (writer bug or hand-edit), so the two representations disagree | med | Single writer emits both from one in-memory model (Issue 3.2); frontmatter-first read precedence; a frontmatter/`**Field:**` consistency check in the audit (Issue 3.5); dual-representation read test (Issue 3.6) |
| R4 | Single-file incubator bundles cannot host reserved `index.md`/`log.md` | med | Explicit single-file exemption in the SPEC (5.1) + OKF-INCUBATOR (1.3); promote to dir-form when they gain substructure |
| R5 | Vendoring drift across 3+ copies of `okf.py` | med | `_shared/sync.py --check` in change-validation + `yf-drift-check` `value-equal` edges (existing precedent) |
| R6 | research `_index.md` rename fans out beyond `index_manager.py` (link_normalizer, packager, formula, spec, tests) — a partial rename silently breaks link-normalization | med | Issue 4.3 enumerates every rename target; Issue 6.2 drives link-normalization against the renamed `index.md`; lock the index body schema in 1.3/4.1 |
| R8 | The assessment touches the live `~/Documents/Obsidian/Primary` vault (real personal corpus, a live git repo) and could mutate or corrupt it | high | **Structural, not procedural:** Issue 2.2 snapshots the vault to a scratch copy first and runs **all** Epic-2 ops (even `check`/`--dry-run`) against the copy, so a mistaken non-dry-run hits the copy, not the vault; the live vault is never written by this plan |
| R9 | The impact assessment reveals full baseline conversion is too disruptive for some artifact type | med | The OKF-\* Ratification Gate is a genuine decision point — the operator can send the proposals back (Epic-2 REVISE loop) or, as the **termination lever**, re-scope an extension or exempt an artifact type before any implementation starts |
| R10 | The external vault carries **pre-existing (Obsidian) frontmatter** the engine could clobber, and `migrate --dry-run` could misreport "add frontmatter" when one exists — corrupting the impact report the ratification gate depends on | high | Merge-and-preserve REQ (Issue 1.1) + engine behavior (1.4): add only `type:`/`okf_spec:`, never drop existing keys; report-only/crash-safe scanning; messy-input fixture tests; engine findings reopen 1.4 via Issue 2.3 |

## Success Criteria

1. `skills/yf-okf/SPEC.md` exists with REQ-OKF-* ids; `OKF-BASELINE.md` + `OKF-YF-EXTENSIONS.md`
   family reference docs exist (OKF-SPECIFICATION reserved as a deferred stub); `_shared/okf.py`
   engine + tagged tests pass.
2. Each consumer skill bundles a `skills/<skill>/OKF-EXTENSION.md`, and `yf-okf check` **resolves and
   composes** BASELINE ∪ YF-EXTENSIONS ∪ per-skill extension for that folder.
3. **Impact reports exist for both corpora** (`findings/okf-impact-this-repo.md`,
   `findings/okf-impact-primary-vault.md`) with sample test migrations, and the operator **ratified**
   the refactored OKF-\* proposals at the human gate before any implementation epic ran.
4. New plan/research/incubator folders constructed through the engine are OKF-compatible — `yf-okf
   check` passes (frontmatter+non-empty `type` on every non-reserved `.md`; reserved `index.md`/
   `log.md` well-formed).
5. Header metadata is **dual-written** (frontmatter + `**Field:**`) and `plan_manager.py`'s dual-mode
   accessor reads a frontmatter-only, a `**Field:**`-only, and a dual plan identically (Issue 3.6).
6. All three skills delegate folder construction/management to the vendored engine (no hand-rolled
   layout remains for the covered operations).
7. `yf-okf migrate <dir>` converts a legacy folder in place; a migrated legacy **plan** still passes
   `plan_manager.py audit` (grandfather + count-equality preserved) and does **not** go stale-approved.
8. Existing completed folders are untouched and still pass their audits (grandfathered).
9. `_shared/sync.py --check` is clean and `yf-drift-check` `value-equal` edges cover every vendored
   `okf.py` copy.
10. Issue #83 is reconciled (updated/closed) at land-the-plane.
