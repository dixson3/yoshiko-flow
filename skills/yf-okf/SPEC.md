# SPEC — Open Knowledge Format engine (`yf-okf`)

> **Status: Draft (plan-029, Epic 1).** Per-skill SPEC for the shared bundle engine and the owner of
> the OKF-\* spec family. Requirements use RFC-2119 "shall"; composed by the root `SPEC.md` macro
> spec. This is the **SPEC-first anchor** for plan-029 — it lands before the engine code (Issue 1.4)
> and before the three consumer integrations (Epics 3–5).

## 1. Purpose & scope

`yf-okf` is a repo-agnostic engine that **constructs, manages, and conformance-checks** the artifact
folders ("bundles") that the yf artifact-producing skills emit (`yf-plan`, `yf-research`,
`yf-incubator`, and future consumers). It makes those bundles **compatible with** the Open Knowledge
Format (OKF v0.2, `GoogleCloudPlatform/knowledge-catalog`): an opinionated framework that adopts the
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
`migrate`) is specified here and implemented in Issue 1.4.

**Out of scope:** authoring OKF tooling (third-party linters / validators / MCP servers) — `yf-okf`
is a **producer/manager**, not a third-party validator, though a conformance self-check
(§ REQ-OKF-CHK-\*) is in scope. The OKF `# Citations` heading convention (a SHOULD-level guideline —
research `sources.md` keeps its GFM citation links) is a non-goal. **OKF-SPECIFICATION** — the
reserved family member for engineering `SPEC.md` files — is a **reserved name, deferred** to a
follow-on (REQ-OKF-FAM-004); it is neither authored nor applied here. Index/log *rendering* adapters
are per-skill (the three current models genuinely differ) and are specified in each consumer's
`spec/` amendments (Epics 3–5), not here.

## 2. Requirements (`REQ-OKF-NNN`)

> **Identifier allocation (plan-046 Issue 2.2).** The `NNN` blocks are **id ranges, not section
> bindings** — this SPEC has never stated a block↔section correspondence, and `reindex` (§2.10)
> deliberately spans the bundle-model, frontmatter, foreign-corpus-survival and check concerns.
> The ids below were allocated from the block-local next-free set, each **measured collision-free
> against this file** at allocation time:
>
> | id | allocated to | lands in |
> | :-- | :-- | :-- |
> | `REQ-OKF-004` | the bundle-root predicate | §2.1 (Issue 3.1) |
> | `REQ-OKF-011` | the `reindex` verb, its verdicts and exit codes | §2.10 (Issue 3.1) |
> | `REQ-OKF-032` | `okf_version` frontmatter only on a bundle-**root** `index.md` | §2.4 (Issue 3.2) |
> | `REQ-OKF-072` | prose preservation across index regeneration | §2.10, co-located with `reindex` (Issue 3.4) |
> | `REQ-OKF-CHK-002` | index-drift findings (`ghost`/`missing`) at **warning** level | §2.8 (Issue 3.6) |
> | `REQ-OKF-CHK-003` | member-declared path exclusion, applied at every walk site | §2.8 (plan-056 Issue 0.3) |
> | `REQ-OKF-CHK-004` | the corpus index-drift driver + its `CHANGE-VALIDATION` binding | §2.8 (plan-056 Issue 0.9) |
> | `REQ-OKF-FAM-005` | the OKF **v0.2** baseline pin | §2.5 (below) |
>
> **Unallocated but reserved by the same measurement** — still free for a later plan:
> `REQ-OKF-022`, `REQ-OKF-051`, `REQ-OKF-061`, `REQ-OKF-MIG-006`.

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
  (the sole OKF MUST). `index.md` and `log.md` are reserved and exempt (REQ-OKF-031).
  *(plan-046 Issue 1.1: this cross-reference read `REQ-OKF-034`, an id **never defined at any
  revision of this SPEC** — `git blame` places it in the introducing commit `aaf2b6c` (plan-029),
  so it was dangling from birth and provenance cannot confirm the author's intent. It is resolved
  to `REQ-OKF-031` on semantic grounds — that is the only requirement in this SPEC stating the
  reserved-file exemption — and the residual uncertainty is recorded here rather than resolved
  silently.)*

- **REQ-OKF-004** *(testable)* the engine shall have an explicit notion of **bundle root**, because
  `okf_version` frontmatter (REQ-OKF-032) and the `reindex` verb (REQ-OKF-011) are both root-scoped
  while `index.md` is reserved at *any* level (REQ-OKF-001). **Root-ness is a property of the
  INVOCATION, not of the filesystem:** the directory a caller names *is* the bundle root, and every
  directory below it is non-root. Library entry points shall accept an explicit `root: bool` (default
  `True` for a named bundle, `False` for a recursed child) rather than inferring.
  **Why not the alternatives.** Sniffing for a marker file (`plan.md`) or testing membership of a
  configured `plans-root`/`research-root` would both require `_shared/okf.py` — the **baseline**
  engine — to know consumer-specific facts, inverting the baseline/extensions separation
  (`spec/OKF-BASELINE.md` vs `spec/OKF-YF-EXTENSIONS.md`). That is the same layering argument that
  decided the presence-optional case in favour of fixing the producer.
  A bundle-root `index.md`'s `okf_version` key MAY be used to *classify an existing index* after the
  root is known; it shall never be used to *locate* the root, which would be circular for a bundle
  that has no index at all.

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

- **REQ-OKF-032** *(testable)* `okf_version` frontmatter shall be emitted **only on a bundle-root
  `index.md`** (REQ-OKF-004). v0.2 §8 states index files carry no frontmatter *"with one exception: a
  bundle-root `index.md` MAY carry an `okf_version` key"*, so emitting it on a nested `index.md` is a
  baseline violation. This is a **latent-defect fix**: no live producer path emits a nested index
  today (nested indexes are deferred, `spec/OKF-YF-EXTENSIONS.md`), so it is a conformance violation
  waiting on the first caller rather than an active one.

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
- **REQ-OKF-FAM-005** *(testable)* the baked-in baseline (REQ-OKF-FAM-002) shall be pinned to
  **OKF v0.2**, and the engine's `okf_version` constant shall read `"0.2"` in `_shared/okf.py` and in
  every vendored copy. `spec/OKF-BASELINE.md` shall record v0.2 **verbatim**, with every `(§N)`
  cross-reference reading its **v0.2** section number. The pin is a single fact with **two
  surfaces** — the human-readable baseline document and the in-code constant — and they shall agree;
  a `DRIFT-CHECK.md` edge (Issue 2.8) encodes that agreement, which was previously unencoded, so a
  v0.1→v0.2 edit fired nothing that inspected `okf_version`.
  **Rationale.** Upstream OKF §13 states v0.2 *"supersedes OKF v0.1"*. yoshiko-flow's exposure to
  both declared breaking changes is **exactly zero** (it emits `timestamp` 0 times and `# Citations`
  0 times), so the pin is a documentation edit plus a constant — **not** a corpus migration, which
  is explicitly out of scope (plan-046 D-2).

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

- **REQ-OKF-CHK-002** *(testable)* `check` shall additionally report index-drift findings —
  `missing` and `ghost` (REQ-OKF-011) — at **`warning`** level.
  **Warning, not error, and the reason is not the one an earlier draft gave.** The audit's promotion
  filter (`plan_manager.py`) is an **allowlist** of four requirement ids, not a fold over all
  error-level findings, so a newly allocated req is outside it *by construction* — there is no action
  to take and nothing to opt out of. Warning level is chosen anyway on the ground that relying on an
  allowlist's **silence** is itself an implicit guarantee no test asserts: a future edit widening the
  allowlist would resurrect the risk invisibly. Promotion to error is a separate, later change, gated
  on a green corpus.

  **Promotion to `error`: RECORDED, DELIBERATELY NOT EXECUTED (plan-046 Issue 4.5).** The
  precondition is now met — `reindex --check` is clean across all 19 bundles carrying a root
  `index.md`, the other 31 return `no-index` (exit `2`), and `markdown_lint --rules ML003` is clean
  over the same glob. Promotion is nevertheless **not** performed here, for one reason: landing it in
  the same pass would enforce against a corpus whose greenness was established **minutes earlier by
  the same session**, with no independent run in between. A gate that has never observed a red state
  it did not itself create has not been tested.

  What a future promotion must do, so it does not have to re-derive this:
  1. flip the level from `warning` to `error` in `check_conformance`;
  2. decide *explicitly* whether `REQ-OKF-CHK-002` joins the audit's promotion allowlist — it is
     outside it **by construction** today (plan-046 exec-004 measured this: three error-level
     findings reached the engine and `audit` still exited `0`), so promoting the level alone changes
     `check`'s exit code and **not** `audit`'s;
  3. re-run the corpus sweep **from a clean checkout**, in a different session from the one that
     produced the green state.

- **REQ-OKF-CHK-003** *(testable)* *(added plan-056 / #233)* the engine shall carry a
  **member-declared path-exclusion concept**, and shall apply it at **every walk site**.

  **The declaration.** A per-skill `OKF-EXTENSION.md` MAY carry a **§3b Excluded paths** table whose
  first column is a **bundle-relative glob**. `resolve_extension` shall parse it into
  `ExtensionRuleset.exclude_globs`; an absent §3b yields an **empty list**, which is a legal and
  common state, never an error.

  **The matcher is `fnmatch`, not the engine's `_glob_match`.** `_glob_match` cannot express a
  recursive `**`, and every exclusion this concept exists to declare (`assets/fixtures/**`,
  `findings/okf-migration-samples/**`) is recursive. A matcher that silently cannot express the
  patterns it is handed is a control that cannot fire — this SPEC's own recurring defect class.

  **Every walk site, enumerated, because "the walk" is not one place.** The exclusion shall be
  applied by `okf.py`'s `check_conformance`, `migrate` and `_listing_members`, and by
  `plan_manager.py`'s bundle-conformance walk and its `dangling-refs` scan. Applying it at some
  sites and not others is worse than not having it: a fixture excluded from `check` but still
  reached by `audit-close` produces a finding the operator cannot silence at its declared source.

  **The motivating defect (#233).** `audit-close`'s OKF walk has no carve-out, so a *deliberate*
  migration-fixture corpus — 45 nested `.md` files under `findings/okf-migration-samples/**`, whose
  whole purpose is to be non-conformant — reports as 34 real findings on an unrelated plan's close.
  `doc_lint` had already solved this twice, per-schema, with `exclude` lists; the OKF layer simply
  never grew the concept.

  **Declaration, never derivation** (D-14). The two layers' exclusion lists are **independently
  declared** and share a *mechanism*, not a *source*: they use different coordinate systems
  (repo-relative vs bundle-relative) and different granularities, and deriving one from the other
  would miss `assets/fixtures/**` entirely — `doc_lint` is silent there by **non-selection**, not by
  exclusion, and those are different facts. The mechanism is shared **in both directions**:
  `doc_lint` shall also be able to read a member's §3b, so the relationship between the two lists is
  checkable from either side rather than asserted from one.

  **The overlap invariant, and its non-vacuity guard.** A test shall assert the declared relationship
  between the two lists **and** that **both lists are non-empty**. Without the second half the
  invariant holds trivially when either side is empty — which is precisely the state the concept is
  being introduced from, so the test would ship green and stay green through its own regression.

  **`check` shall expose `--no-exclude`** as the positive control, mirroring `doc_lint`'s flag of the
  same name: removing §3b, or passing `--no-exclude`, shall restore the suppressed findings. An
  exclusion nothing can turn off is indistinguishable from a check that never fired.

- **REQ-OKF-CHK-004** *(testable)* *(added plan-056 / #140, #247)* a **corpus index-drift driver**
  shall exist as an executable check, and shall be **bound into `CHANGE-VALIDATION.md`** in both the
  FAST and FULL tiers.

  **Why a driver, and not `reindex` alone.** `reindex` judges **one** bundle. Measured at scoping:
  `okf.py reindex` appears in **zero** `CHANGE-VALIDATION.md` rows, **zero** CI steps, and is called
  by nothing in `plan_manager.py`. Root-index drift was repaired nine days earlier and had **already
  regressed in 9 of the 30 index-bearing bundles** — every bundle authored after the repair. A verb
  no gate invokes is not enforcement; the driver is what makes REQ-OKF-011 reachable from a gate.

  **Root enumeration shall be a depth-1 glob, never `rglob`.** The roots are
  `docs/plans/*`, `docs/research/*`, `Incubator/*/plans/*` and `Incubator/*/research/*`. `rglob`
  would descend into a bundle's own `findings/okf-migration-samples/**` and treat each nested fixture
  bundle as a corpus root — inflating the count while inspecting fixtures, which is REQ-OKF-CHK-003's
  defect reappearing in the enumerator.

  **The exclusion source is REQ-OKF-CHK-003's §3b**, not a second list. The driver shall additionally
  be **gitignore-aware**, so an untracked scratch directory is never enumerated.

  **Its exit contract is three-valued** and follows `scripts/checks/_common.sh` (REQ-CLI-029):
  `0` clean · `1` drift · `2` INCONCLUSIVE. It shall **hard-error on a nonexistent enumerated root**
  rather than skipping it, so a mistyped path can never be demoted into a clean verdict — this is
  the consumer half of REQ-OKF-011's new `no-such-path`, and without it that new code buys nothing.

  **It shall emit a `bundles_checked` count and support `--min-roots N`, failing when fewer than `N`
  roots were enumerated.** A driver that enumerated nothing exits 0 on every other rule it applies;
  the floor is what makes "the corpus is clean" distinguishable from "the corpus was not read". This
  is the same guard REQ-CLI-029 requires of every check in that directory, stated here because this
  driver is the one whose input set is discovered rather than given.

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

### 2.10 Index generation and drift (`reindex`)

- **REQ-OKF-011** *(testable)* *(amended plan-056 / #140, #247)* the engine shall expose a
  **`reindex`** verb over a bundle **root** (REQ-OKF-004), in two modes, emitting **JSON on every
  path**:
  - **`reindex --check <bundle>`** — report index drift without mutating anything. Three finding
    kinds: **`missing`** (a listing member present on disk but absent from `index.md`), **`ghost`**
    (an entry whose relative target does not resolve — covering dead *files* **and** dead
    *directories*), and **`empty-dir`** (a listed subdirectory containing nothing).
  - **`reindex --write <bundle>`** — regenerate the listing, preserving prose (REQ-OKF-072).

  **Exit codes are a FIVE-way verdict, not a boolean and no longer a three-way one:**

  | exit | verdict | meaning |
  | :-: | :-- | :-- |
  | `0` | `clean` | an `index.md` exists and every entry resolves, with nothing unlisted |
  | `1` | `drift` | an `index.md` exists and at least one `missing` / `ghost` / `empty-dir` finding |
  | `2` | `no-index` | the path **exists and is a directory**, but carries no root `index.md` |
  | `3` | `no-such-path` | the path **does not exist**, or is not a directory |
  | `4` | `inconclusive` | the index exists but **could not be judged** |

  **`no-index` is its own verdict and MUST NOT collapse into either neighbour.** A bundle with no
  index is neither clean nor drifted — there is nothing to be in or out of agreement with. Reporting
  it as `0` would let an index-less bundle be counted as green, which is precisely the "an artifact
  asserting something nothing checks" failure this requirement exists to prevent; reporting it as `1`
  would manufacture drift findings for a file that does not exist.

  **`no-such-path` is a CALLER BUG and MUST NOT collapse into `no-index`.** Both states reach the
  same line today — `index.md` is absent either way — so a **mistyped or moved bundle path was
  reported as `no-index`**, indistinguishable from a real index-less bundle. Any driver that treats
  `no-index` as tolerable (as a corpus sweep over a mixed corpus must, since most bundles have no
  index) therefore reads a typo as a benign skip and certifies a corpus it never inspected. This is
  the same two-facts-one-signal conflation as `doc_lint`'s `not-selected` vs `no-such-path` (#181)
  and `resume-scan`'s `found` (#207), and it is fixed the same way: distinguish the two states and
  give each its own code. `no-such-path` is never demotable — a consumer must surface it as an
  error, because the instrument was pointed at nothing.

  **`inconclusive` is a statement about the INSTRUMENT, not the artifact.** It is returned when the
  index is present but the check cannot be made:
  - an **unbalanced generated-region marker** (REQ-OKF-072) — `--check` shall run `check_markers`
    over the index text. Until this amendment `--check` did not call it at all, so a
    marker-imbalanced index — the one condition REQ-OKF-072 calls *unrecoverable* — was reported
    **`clean`, exit 0**. Certifying it clean is worse than silence: it licenses the `--write` that
    then hard-errors, and it is the only path by which a green `--check` precedes prose loss;
  - an **unreadable** `index.md` (an I/O or decode failure).

  A consumer must treat `4` as "repair the harness, then re-run" — never as clean and never as
  drift, on the same reasoning `REQ-DATA-024` applies to `doc_lint`'s own `2`. **The two exit
  vocabularies deliberately differ in the number they use**, because `reindex`'s `2` was already
  shipped as `no-index` and re-pointing it would silently change the meaning of every existing
  caller's `2`.

  **Codes `126` and `127` are reserved to the shell and MUST NOT be allocated** (REQ-CLI-029), so a
  non-executable or absent engine can never be mistaken for a verdict.

  **Root-only in v1, deliberately.** `reindex` is specified over the bundle root only. Nested
  `index.md` generation is **deferred** behind a producer change that stamps `description:`. **Measured
  2026-08-28 (plan-056 Issue 0.8): 165 of 983 nested files carry one** — up from the plan-046-era
  "0 of 423", which is stale on both terms. Coverage is real but **partial and recent**, confined to
  the twelve newest bundles, so most generated nested entries would still carry no description, and
  **74 of 142 (52%)** of subdirectories would receive a listing of no value. The deferral is recorded
  in `spec/OKF-YF-EXTENSIONS.md` with its measurement and filed upstream, so a future reader inherits
  the evidence rather than the conclusion.

  **No "stale metadata" check.** At the 165/983 coverage measured 2026-08-28 there is too little
  nested metadata for a staleness check to be worth its own requirement, and the entries that do
  exist are the newest in the corpus — the population least likely to have gone stale. Revisit when
  the producer contract (REQ-DATA-075) has run long enough to make coverage the common case.

- **REQ-OKF-072** *(testable)* `reindex --write` shall **preserve author prose**. Generated content is
  delimited by `<!-- intro:start -->` / `<!-- intro:end -->` and `<!-- notes:start -->` /
  `<!-- notes:end -->`; text outside those regions is carried through untouched. Two guards are
  required, and they differ in force **because their failure modes differ**:
  - an **unbalanced marker** (a `:start` with no matching `:end`) is a **hard error** — the region is
    unbounded, so regenerating would discard prose *unrecoverably*;
  - **dropped non-generated lines** are a **warning** — recoverable from git, so a warning is
    proportionate.

  Rationale: the corpus contains hand-written orientation prose a naive regenerator would delete
  (e.g. a `## Note on scope-answers.md` section in a live plan bundle's `index.md`). This requirement
  is the reason the backfill is safe to run at all, and it sits under **foreign-corpus survival**
  (§2.7) because preserving content the engine did not author is exactly that concern.

  **Never invent a description.** An existing description is preserved; a new entry is emitted as a
  bare `- [title](path)`. Emitting a placeholder (`*description pending*`) would write an assertion
  that a description exists when none does — 818 times over, on the 983-nested-file corpus measured
  2026-08-28.

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
  | `reindex(dir, *, write=False)` | root-scoped index generation + drift report; `clean`/`drift`/`no-index`/`no-such-path`/`inconclusive` (REQ-OKF-011) |
  | `append_log(dir, entry, *, date=None)` | newest-first ISO-8601 `log.md` entry (REQ-OKF-002) |
  | `resolve_extension(skill)` | `__file__`-relative find+parse of `skills/<skill>/OKF-EXTENSION.md` (REQ-OKF-FAM-003) |
  | `check_conformance(dir)` | composed-ruleset conformance report (REQ-OKF-CHK-001); report-only/crash-safe |
  | `migrate(dir, *, dry_run=True)` | opt-in in-place migration (REQ-OKF-MIG-\*) |

> **`emit_conformant_copy` was REMOVED (plan-046 Issue 5.2).** It was specified from plan-029 with
> **zero callers, zero tests, and no CLI verb** — measured, not assumed. A spec'd-but-unreachable
> function is worse than an absent one: it lets a future investigator conclude the on-demand export
> projection exists. It was deleted rather than exposed, because exposing it would mean building the
> projection that #92's revisit triggers do not justify — the **adopter** half of trigger (b) has
> fired, the **demand** half has not. The capability is preserved as an upstream follow-on
> ("projection delivery mode"), so removing the code does not erase the record of what was removed.
> `emit_conformant_copy` now appears in neither the code nor this SPEC — the only two outcomes
> plan-046 SC10 permits.

- **Operator surface:** `/yf-okf init | migrate | check | assess | reindex` (SKILL.md). `reindex`
  exits `0` clean / `1` drift / `2` `no-index` / `3` `no-such-path` / `4` `inconclusive`
  (REQ-OKF-011) — the one verb whose exit code is a multi-way verdict rather than a pass/fail.
  `126`/`127` stay reserved to the shell (REQ-CLI-029).
- **Companion rule / config / state:** the OKF-\* family reference docs
  (`spec/OKF-BASELINE.md`, `spec/OKF-YF-EXTENSIONS.md`, Issue 1.2) and per-skill
  `skills/<skill>/OKF-EXTENSION.md` (Issue 1.3). No `.local.json` / `.yf/` state. The
  baseline is pinned `okf_version: 0.2` (`REQ-OKF-FAM-005`); upstream OKF drift is isolated to `OKF-BASELINE.md` + the
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
- Path exclusion (REQ-OKF-CHK-003) is checked by `_shared/test_okf.py::exclude_globs_declared` (a
  synthetic `OKF-EXTENSION.md` carrying a §3b; removing it restores the findings) and
  `::overlap_invariant` (the two declared lists agree, and **both are non-empty** — the non-vacuity
  half), plus `scripts/checks/check-fixture-carveout.sh` over a real bundle.
- The corpus drift driver (REQ-OKF-CHK-004) is checked by
  `scripts/checks/check-drift-driver-contract.sh`, which asserts a **nonexistent enumerated root
  yields a different exit than a clean corpus**, and by `check-recipe-row.sh okf-index-drift`, which
  asserts the row is present in `CHANGE-VALIDATION.md` **and** appears in a FULL-tier run's JSON — a
  bare full-tier run cannot show this, since it already exits 0 before the row exists.
- Each *(testable)* REQ is the anchor a tagged test names.

## 6. References

- `skills/yf-okf/SKILL.md` (operator surface; on discrepancy, `spec/` + this SPEC win) — Issue 1.5.
- `skills/yf-okf/spec/OKF-BASELINE.md` (upstream OKF v0.2 rules, reconciled by plan-046 from the vendored v0.2 spec; research 001 distilled the superseded v0.1) and
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
