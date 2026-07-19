# SPEC — Open Knowledge Format engine (`yf-okf`)

> **Status: Draft (plan-029, Epic 1).** Per-skill SPEC for the shared bundle engine and the owner of
> the OKF-\* spec family. Requirements use RFC-2119 "shall"; composed by the root `SPEC.md` macro
> spec. This is the **SPEC-first anchor** for plan-029 — it lands before the engine code (Issue 1.4)
> and before the three consumer integrations (Epics 3–5).

## 1. Purpose & scope

`yf-okf` is a repo-agnostic engine that **constructs, manages, and conformance-checks** the artifact
folders ("bundles") that the yf artifact-producing skills emit (`yf-plan`, `yf-research`,
`yf-incubator`, and future consumers). It makes those bundles **compatible with** the Open Knowledge
Format (OKF v0.1, `GoogleCloudPlatform/knowledge-catalog`): an opinionated framework that adopts the
OKF baseline (reserved `index.md`, reserved `log.md`, YAML frontmatter with a non-empty `type` on
every non-reserved `.md`) and layers the yoshiko-flow extensions on top (a dual **frontmatter +
`**Field:**`** field model, an `okf_spec:` member key, per-skill extension specs). `yf-okf` is also
the **owner of the OKF-\* spec family** — the versioned ruleset that says how each kind of yf artifact
is structured and annotated.

**In scope:** the bundle model (reserved files, the frontmatter+`type` invariant, the fingerprint-safe
placement invariant); the dual field model; the `okf_spec:` member key; the OKF-\* family and the
per-skill `OKF-EXTENSION.md` discovery/composition contract (BASELINE ∪ YF-EXTENSIONS ∪ per-skill);
the single-file-bundle exemption; the non-`.md` exclusion; the two foreign-corpus survival guarantees
(merge-and-preserve, report-only/crash-safe); the `check` conformance self-test; the opt-in `migrate`
semantics (grandfather preservation, fingerprint stability). The engine API surface
(`scaffold_bundle`, `write_fields`/`read_fields`, `write_frontmatter`/`read_frontmatter`,
`render_index`/`add_index_entry`, `append_log`, `resolve_extension`, `check_conformance`,
`emit_conformant_copy`, `migrate`) is specified here and implemented in Issue 1.4.

**Out of scope:** authoring OKF tooling (third-party linters / validators / MCP servers) — `yf-okf`
is a **producer/manager**, not a third-party validator, though a conformance self-check
(§ REQ-OKF-CHK-\*) is in scope. The OKF `# Citations` heading convention (a SHOULD-level guideline —
research `sources.md` keeps its GFM citation links) is a non-goal. **OKF-SPECIFICATION** — the
reserved family member for engineering `SPEC.md` files — is a **reserved name, deferred** to a
follow-on (REQ-OKF-FAM-004); it is neither authored nor applied here. Index/log *rendering* adapters
are per-skill (the three current models genuinely differ) and are specified in each consumer's
`spec/` amendments (Epics 3–5), not here.

## 2. Requirements (`REQ-OKF-NNN`)

### 2.1 Bundle model (see `spec/OKF-BASELINE.md`, `spec/OKF-YF-EXTENSIONS.md`)

- **REQ-OKF-001** *(testable)* a **bundle** is an OKF-compatible directory. Each dir-form bundle shall
  carry a reserved **`index.md`** — a progressive-disclosure listing (`#` heading + `- description`
  bullets, no frontmatter except a bundle-root `okf_version`) — that replaces the legacy `README.md`
  (yf-plan, yf-incubator) and `_index.md` (yf-research) reserved index files.
- **REQ-OKF-002** *(testable)* each dir-form bundle shall carry a reserved **`log.md`** whose entries
  are **newest-first, under ISO-8601 (`YYYY-MM-DD`) date headings**, replacing the legacy in-`plan.md`
  `**Phase log:**` block (yf-plan), the timestamped `_index.md` ledger (yf-research), and the
  `## Decision log` body section (yf-incubator).
- **REQ-OKF-003** *(testable)* every **non-reserved `.md`** file in a bundle shall carry a parseable
  YAML frontmatter block delimited by `---`, and that block shall contain a **non-empty `type`** field
  (the sole OKF MUST). `index.md` and `log.md` are reserved and exempt (REQ-OKF-034).

### 2.2 Placement invariant — fingerprint safety (see `spec/OKF-YF-EXTENSIONS.md`)

- **REQ-OKF-010** *(testable)* in any artifact that carries them, **both** the YAML frontmatter block
  **and** the human-readable `**Field:**` block shall sit **above the first `## ` heading** of the
  document. Rationale: yf-plan's content fingerprint excludes everything before the first `## `
  (positional exclusion — exp-001 `_plan_content_sections` / `_plan_content_fingerprint`), so neither
  block enters the fingerprint. The engine shall enforce this on emit, so that adding frontmatter and
  removing an in-`plan.md` phase log are both **hash-neutral by construction**.

### 2.3 Dual field model (see `spec/OKF-YF-EXTENSIONS.md`)

- **REQ-OKF-020** *(testable)* header metadata shall be **dual-written**: a single writer, from a
  single in-memory model, shall emit **both** a YAML frontmatter block (the machine / OKF surface)
  **and** the human-readable `**Field:**` lines. The two representations shall never be authored
  independently (the anti-divergence invariant, R7). **On migration**, existing human `**Field:**`
  header lines (`**ID:**`, `**Status:**`, …) shall be **mirrored into frontmatter** (both surfaces
  kept in sync), so the dual model is *established by migration*, not left frontmatter-only.
- **REQ-OKF-021** *(testable)* reads shall be **frontmatter-first with `**Field:**` fallback**: when
  a key is present in frontmatter the frontmatter value wins; when absent, the reader shall fall back
  to the legacy `**Field:**` line, so un-migrated artifacts keep working.

### 2.4 The `okf_spec:` member key (see `spec/OKF-YF-EXTENSIONS.md`)

- **REQ-OKF-030** *(testable)* each **non-reserved** artifact shall carry an `okf_spec:` frontmatter
  key naming the OKF-\* extension member it conforms to (e.g. `okf_spec: OKF-PLAN`,
  `okf_spec: OKF-RESEARCH`, `okf_spec: OKF-INCUBATOR`).
- **REQ-OKF-031** *(testable)* the reserved `index.md` and `log.md` shall carry **no `type` and no
  `okf_spec`** key (they are structural files, not typed concept documents); `index.md` at a bundle
  root MAY carry only an `okf_version` key.

### 2.5 OKF-\* family + per-skill `OKF-EXTENSION.md` discovery/composition

- **REQ-OKF-FAM-001** *(testable)* the **effective ruleset** the engine enforces against a bundle
  shall be the composition **OKF-BASELINE ∪ OKF-YF-EXTENSIONS ∪ resolved-per-skill-OKF-EXTENSION**.
- **REQ-OKF-FAM-002** *(testable)* the machine-readable **BASELINE + YF-EXTENSIONS** ruleset shall be
  **baked into `okf.py`** (no cross-skill file read at runtime). The human-readable
  `spec/OKF-BASELINE.md` and `spec/OKF-YF-EXTENSIONS.md` docs are the authored spec, kept **in
  agreement** with the in-code ruleset by a `yf-drift-check` edge — they are documentation the engine
  does not parse at runtime.
- **REQ-OKF-FAM-003** *(testable)* `resolve_extension(skill)` shall discover a consumer's per-skill
  extension **by convention** at `skills/<skill>/OKF-EXTENSION.md`, resolved **`__file__`-relative**
  to the running (vendored) `okf.py` — each skill bundles its own `OKF-EXTENSION.md` beside its
  vendored `okf.py`. This guarantees full `check_conformance` composition runs from **any** vendored
  copy in **both** the worktree and installed address spaces, with no sibling skill required on disk.
- **REQ-OKF-FAM-004** the family name **`OKF-SPECIFICATION`** (for engineering `SPEC.md` files) shall
  be **reserved and deferred** — declared as a stub in `spec/OKF-YF-EXTENSIONS.md`, not authored here
  and not applied to any `SPEC.md` in this plan.

### 2.6 Single-file-bundle exemption & non-`.md` exclusion

- **REQ-OKF-050** *(testable)* a **single-file bundle** — an artifact that is a single `.md` file with
  no owning directory (e.g. a single-file incubator, `Incubator/<slug>.md`) — shall be **exempt** from
  the reserved `index.md`/`log.md` requirement (REQ-OKF-001, REQ-OKF-002); it carries only its own
  frontmatter+`type`. A bundle counts as single-file iff it is one `.md` with no dedicated bundle
  directory. When such a bundle gains substructure it is **promoted to dir-form**, at which point its
  body `## Files` / `## Decision log` sections map to reserved `index.md` / `log.md` respectively.
- **REQ-OKF-060** *(testable)* **non-`.md`** files (e.g. yf-research's `plan.yaml`, `sources.json`)
  shall be **excluded** from the frontmatter-`type` rule (REQ-OKF-003); `check_conformance` shall not
  flag them for missing frontmatter.

### 2.7 Foreign-corpus survival (see `spec/OKF-YF-EXTENSIONS.md`)

- **REQ-OKF-070** *(testable)* **merge-and-preserve** — `write_frontmatter` and `migrate` shall add
  only yf keys (`type:`, `okf_spec:`, and other yf-owned keys) and shall **never drop or overwrite** a
  pre-existing frontmatter key. A file carrying foreign frontmatter (e.g. Obsidian `tags`, `aliases`,
  `cssclass`) shall retain every such key byte-for-byte after a write or migrate.
- **REQ-OKF-071** *(testable)* **report-only and crash-safe** — `check` and `migrate --dry-run` run
  over non-conforming, malformed, or otherwise unexpected input (unparseable YAML, missing files,
  binary content) shall **record a finding and continue**, and shall **never raise**. A scan of a
  messy foreign corpus returns a findings report, not a stack trace.

### 2.8 Conformance self-check (`check`)

- **REQ-OKF-CHK-001** *(testable)* `yf-okf check <bundle>` shall verify the **composed** effective
  ruleset (REQ-OKF-FAM-001) holds over the bundle: reserved `index.md`/`log.md` well-formed
  (REQ-OKF-001, REQ-OKF-002), frontmatter+non-empty-`type` on every non-reserved `.md`
  (REQ-OKF-003), the placement invariant (REQ-OKF-010), the `okf_spec:` member key (REQ-OKF-030), the
  single-file exemption (REQ-OKF-050), and the non-`.md` exclusion (REQ-OKF-060). It reports findings
  and is report-only (REQ-OKF-071) — it never mutates the bundle. **Error vs. warning split.** The
  OKF baseline MUSTs (parseable frontmatter + non-empty `type`), `okf_spec` (REQ-OKF-030), placement
  (REQ-OKF-010), and reserved-file presence (REQ-OKF-001/002) are **errors** (the base engine
  guarantees them, so a base `migrate` yields an error-free bundle). A composed member's **extra
  required keys** (§2 beyond `type`/`okf_spec`) and **type-vocabulary** membership are **warnings**,
  scoped to docs of the member's **main type** — backfilling member-specific keys from legacy
  prose/`**Field:**` surfaces is the per-skill adapter's responsibility (Epics 3/4/5), not the base
  engine's. The placement (REQ-OKF-010) below-`## ` scan flags only a bold `**Label:**` line whose
  normalized label is a **known metadata key** (the yf baseline dual-field set ∪ the member's §4
  labels ∪ its required keys) with a non-empty value — a bold prose lead-in
  (`**Recommendation:** …`) is never false-flagged.

### 2.9 Migration semantics (`migrate`)

- **REQ-OKF-MIG-001** *(testable)* `yf-okf migrate <dir>` shall convert a legacy folder **in place**
  to the OKF-compatible model, and shall be **opt-in** (run per-folder on demand; existing completed
  folders are grandfathered, never bulk-rewritten). `migrate --dry-run` shall emit the change plan
  without mutating the folder (and is the mode Epic 2's impact assessment relies on).
- **REQ-OKF-MIG-002** *(testable)* migration shall **preserve the first `scoping:` date** into
  `log.md` in a machine-readable form, so that a downstream grandfather clause (yf-plan's
  `_plan_first_scoping_date`) still resolves and a migrated legacy plan does not lose its grandfather
  warn-downgrade. This is migration's single most dangerous step (exp-001). Migration of a
  block-form (dated-bullet) phase log shall further **transcribe every dated bullet** — each
  `<status>:` line, `review:` lines included — preserving its status token, so a downstream
  count-equality invariant (yf-plan's REQ-PORT-006: `log.md` `review:` entries == `reviews/pass-*.md`)
  survives migration; only an inline/semicolon-form log with no dated bullets falls back to the
  single-`scoping:` transcription.
- **REQ-OKF-MIG-003** *(testable)* migration shall **keep the content fingerprint stable** — because
  frontmatter is placed above the first `## ` (REQ-OKF-010) and the phase-log move is a positional
  no-op for the hash, a migrated **approved** plan shall not go **stale-approved**.
- **REQ-OKF-MIG-004** *(testable)* migration shall assign each non-reserved `.md` a `type` from the
  composed member's **role → type map** (an ordered path-glob → type table in its `OKF-EXTENSION.md`;
  first match wins), not a blanket `Concept`. A file matching no rule shall fall back to the member
  default (`Concept` unless the member declares otherwise) and the fallback shall be **recorded** in
  the change plan (`type_source: default-fallback`) — migration never silently mislabels a role.
- **REQ-OKF-MIG-005** *(testable)* migration's reserved-file reconciliation shall be **member-driven**:
  the composed member declares which legacy file becomes `index.md` (e.g. OKF-PLAN/OKF-INCUBATOR
  `README.md`, OKF-RESEARCH `_index.md`, or `scaffold`) and the `log.md` source (an in-body
  `**Phase log:**` block via `extract-log`, or `scaffold`). Where a member declares no source, a
  **conformant skeleton** shall be synthesized so that `check` on the migrated bundle **passes**
  (REQ-OKF-001/002) for that member. The `extract-log` op carries `source_kept: true` — the phase-log
  source file (e.g. `plan.md`) is **not** renamed, only its block is lifted (I-3 legibility). Fine
  per-skill index/log *rendering* stays a per-skill adapter concern (Epics 3/4/5); the base engine
  guarantees only a conformant skeleton.

## 3. Interfaces

- **CLI / scripts:** canonical `_shared/okf.py`, whole-file-vendored into each consumer's
  `scripts/okf.py` via `_shared/sync.py` (the `manifest_update.py` precedent — no cross-skill imports;
  independent-installability preserved). PEP-723 inline deps (`pyyaml`). Engine API surface (Issue
  1.4):

  | Function | Purpose |
  |:--|:--|
  | `scaffold_bundle(dir, *, subdirs, reserved=True)` | mkdir + reserved `index.md`/`log.md` |
  | `write_frontmatter(path, *, type, meta)` / `read_frontmatter(path)` | OKF frontmatter I/O; merge-and-preserve on write (REQ-OKF-070) |
  | `write_fields(...)` / `read_fields(...)` | dual-mode field accessor (REQ-OKF-020/021) |
  | `render_index(dir)` / `add_index_entry(dir, path, desc, *, phase, ts)` | `index.md` listing (per-skill adapters) |
  | `append_log(dir, entry, *, date=None)` | newest-first ISO-8601 `log.md` entry (REQ-OKF-002) |
  | `resolve_extension(skill)` | `__file__`-relative find+parse of `skills/<skill>/OKF-EXTENSION.md` (REQ-OKF-FAM-003) |
  | `check_conformance(dir)` | composed-ruleset conformance report (REQ-OKF-CHK-001); report-only/crash-safe |
  | `emit_conformant_copy(dir)` | non-destructive conformant projection |
  | `migrate(dir, *, dry_run=True)` | opt-in in-place migration (REQ-OKF-MIG-\*) |

- **Operator surface:** `/yf-okf init | migrate | check | assess` (SKILL.md, Issue 1.5).
- **Companion rule / config / state:** the OKF-\* family reference docs
  (`spec/OKF-BASELINE.md`, `spec/OKF-YF-EXTENSIONS.md`, Issue 1.2) and per-skill
  `skills/<skill>/OKF-EXTENSION.md` (Issue 1.3). No `.local.json` / `.yf/` state. The
  baseline is pinned `okf_version: 0.1`; upstream OKF drift is isolated to `OKF-BASELINE.md` + the
  baked-in ruleset.

## 4. Guardrails (`GR-OKF-NNN`)

- **GR-OKF-001** *Drift:* becoming a third-party OKF **validator** / linter. *Rule:* `yf-okf` is a
  **producer/manager** of yf bundles plus a **conformance self-check** — it does not re-implement the
  ecosystem's validators. *Why:* the ecosystem already ships linters/MCP servers (research 001); the
  yf value is a shared construction engine and an owned spec family.
- **GR-OKF-002** *Drift:* clobbering a foreign corpus. *Rule:* writes are **merge-and-preserve**
  (REQ-OKF-070) and scans are **report-only / crash-safe** (REQ-OKF-071); the engine never drops an
  existing key and never raises on messy input. *Why:* Epic 2 runs the engine over a real Obsidian
  vault (a copy); a clobber or crash would corrupt the impact report the ratification gate depends on
  (R8, R10).
- **GR-OKF-003** *Drift:* a runtime cross-skill file read to compose the ruleset. *Rule:* BASELINE +
  YF-EXTENSIONS are **baked into `okf.py`**; only the per-skill `OKF-EXTENSION.md` is resolved, and
  only `__file__`-relative (REQ-OKF-FAM-002/003). *Why:* a skill cannot assume another skill is
  installed; composition must run from any vendored copy in both address spaces.
- **GR-OKF-004** *Drift:* silently breaking the fingerprint or the grandfather clause on migrate.
  *Rule:* frontmatter above the first `## ` (REQ-OKF-010), first-`scoping:` date preserved into
  `log.md` (REQ-OKF-MIG-002), fingerprint asserted stable (REQ-OKF-MIG-003). *Why:* these are the
  high-severity migration risks (R1, R2).

## 5. Verification

- Bundle-model, placement, dual-field, `okf_spec`, exemption, and exclusion invariants
  (REQ-OKF-001..003, 010, 020..021, 030..031, 050, 060) are checked by tagged unit tests over
  synthetic bundle fixtures (a greenfield bundle, a `**Field:**`-only legacy artifact, a
  frontmatter-only artifact, a dual artifact, a single-file incubator, a bundle with `plan.yaml`).
- The composition contract (REQ-OKF-FAM-001..003) is checked by the **resolver-composition unit test**
  (Issue 1.4) using a **synthetic fixture `OKF-EXTENSION.md`**, run in a **simulated installed address
  space** (script + bundled `OKF-EXTENSION.md` only, no sibling skills present) — the Epic-1
  extension-resolver Capability Gate.
- Foreign-corpus survival (REQ-OKF-070..071) is checked by messy-input fixtures: a file with
  pre-existing Obsidian frontmatter (`tags`/`aliases`) round-trips every key; malformed YAML /
  missing files / binary content yield findings, never exceptions.
- Migration safety (REQ-OKF-MIG-001..003) is checked by migrating a copy of a real pre-activation
  plan folder and asserting the grandfather status, REQ-PORT-006 count-equality, and content
  fingerprint are all preserved (the Epic-3 migrated-legacy-plan Capability Gate; Issue 3.6 tests).
- Each *(testable)* REQ is the anchor a tagged test names.

## 6. References

- `skills/yf-okf/SKILL.md` (operator surface; on discrepancy, `spec/` + this SPEC win) — Issue 1.5.
- `skills/yf-okf/spec/OKF-BASELINE.md` (upstream OKF v0.1 rules distilled from research 001) and
  `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` (the yoshiko-flow extension layer; reserves
  OKF-SPECIFICATION) — Issue 1.2.
- Per-skill extensions `skills/yf-plan/OKF-EXTENSION.md` (OKF-PLAN),
  `skills/yf-research/OKF-EXTENSION.md` (OKF-RESEARCH), `skills/yf-incubator/OKF-EXTENSION.md`
  (OKF-INCUBATOR) — Issue 1.3; discovered by `resolve_extension` (REQ-OKF-FAM-003).
- `_shared/okf.py` (canonical engine) + vendored `skills/<skill>/scripts/okf.py` — Issues 1.4/1.6.
- `docs/research/001-okf-compliance-delta/Summary.md` (the OKF baseline facts this SPEC pins).
- `docs/plans/plan-029-james-dixson-75fd34/findings/exp-001-plan-manager-okf-coupling.md`
  (fingerprint positional-exclusion fact; migration surface) and `exp-002-shared-engine-api-surface.md`
  (the engine API surface; `_shared/` vendoring).
- Root `SPEC.md` §4 (OKF catalog entry) and `GUARDRAILS.md`.
