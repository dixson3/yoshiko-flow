# SPEC — Yoshiko Flow (`yf`)

> **Status: SEALED — Gate G0 (2026-06-14, operator).** Macro spec for `yf`, frozen at plan-010
> INTAKE; changes require a new PLAN revision (no in-execution edits). Requirements use RFC-2119
> "shall". The per-skill `skills/<skill>/SPEC.md` it composes remain DRAFT until finalized by
> plan-010 Issue 3.8.

## 1. Purpose & scope

Yoshiko Flow is a family of portable, cross-harness agent **skills** plus a single compiled CLI,
**`yf`**, that installs, upgrades, verifies, and preflights those skills and the toolchain they
depend on. 

**In scope:** skill install/upgrade/remove/status lifecycle; embedded skill payload + integrity
markers; the shared preflight/config kernel (tool/version checks, companion-rule hash verification,
local config + state, beads-init verify/repair); `doctor`; Homebrew/cargo-dist distribution.

**Out of scope:** see `GUARDRAILS.md`. `yf` does **not** run skills, track issues (that is `bd`),
or render markdown/diagrams (those are skills).

## 2. Composition model (macro spec ← per-skill specs)

This root SPEC is the **macro spec**. It owns the `yf` tool requirements (`REQ-YF-*`) and
**composes** the per-skill specs by reference. Every skill ships its own
`skills/<skill>/SPEC.md` with `REQ-<SKILL>-NNN` requirements (see `skills/SPEC-TEMPLATE.md`). The
macro spec is *inferred* from this root plus the union of per-skill specs — no behavioral
requirement lives only in code (GUARDRAILS GR-010).

- **Authority:** a per-skill SPEC is authoritative for that skill's behavior; the macro spec is
  authoritative for `yf` and for cross-skill invariants (naming, install surface, portability).
- **Verification:** every `REQ-…` marked *(testable)* is the anchor a later integration/system test
  names (forward coverage enforced by plan-010 Issue 6.5). Tests cite the REQ id; the spec, not the
  code, is the reference.
- **Drift:** `SPEC.md ↔ GUARDRAILS.md ↔ README.md` is a drift-check edge (plan-010 Issue 5.4);
  per-skill `SPEC.md ↔ SKILL.md` SHOULD be a per-skill drift edge.

## 3. `yf` tool requirements

### 3.1 CLI surface (`REQ-YF-CLI`)

- **REQ-YF-CLI-001** *(testable)* `yf` shall expose subcommands `skills` (with
  `install|upgrade|remove|status`), `doctor`, `preflight`, and `version`.
- **REQ-YF-CLI-002** *(testable)* `skills` subcommands shall accept `--scope {user,project}`
  (default `user`), `--surface {claude,agents}` (default `claude`), `--target <path>`, and
  `--dry-run`.
- **REQ-YF-CLI-003** *(testable)* every subcommand shall support `--json` for machine-readable
  output and shall exit non-zero on failure.
- **REQ-YF-CLI-004** *(testable)* `yf version` shall print the semver version (and build metadata
  when available).

### 3.2 Embedding (`REQ-YF-EMBED`)

- **REQ-YF-EMBED-001** *(testable)* the binary shall embed the entire `skills/` tree at build time
  (no network or repo clone required to install).
- **REQ-YF-EMBED-002** *(testable)* `yf` shall enumerate embedded skill names and per-skill file
  lists, and read any embedded file, from the binary alone.

### 3.3 Install / groups / dependency closure (`REQ-YF-INSTALL`)

- **REQ-YF-INSTALL-001** *(testable)* `yf skills install` shall copy a skill's tree to the resolved
  destination and surface its companion rules (`protocols/*.md`) into the sibling `rules/` surface
  as a **single aggregated `YOSHIKO_FLOW.md`** (one fenced section per protocol), not as per-file
  standalone rules (see `REQ-YF-FLOW-001`).
- **REQ-YF-INSTALL-002** *(testable)* destination resolution shall match: `--target` wins; else
  `<anchor>/.<surface>/skills`, anchor = `$HOME` (user) or git-root/cwd (project); rules →
  `<anchor>/.<surface>/rules`.
- **REQ-YF-INSTALL-003** *(testable)* `yf` shall parse SKILL.md frontmatter (`name`, `skill-group`,
  `depends-on-tool`, `depends-on-skill`, `user-invocable`) and compute install groups from
  `skill-group` (current: `beads`, `utility`, `markdown`).
- **REQ-YF-INSTALL-004** *(testable)* installing a skill shall transitively include its
  `depends-on-skill` closure; unresolved/external deps shall be logged, not fatal.
- **REQ-YF-INSTALL-005** *(testable)* `--group <g>`, explicit positional skill names, and `--strict`
  (fail on missing `depends-on-tool`) shall behave as in the retired `install.py`. `--force` shall
  **no longer overwrite rule content**: the aggregated ruleset is a fully `yf`-managed artifact whose
  acted-on sections are **always** regenerated to the embedded source (`REQ-YF-FLOW-004`), so
  `--force` is inert on the rule axis (M2; supersedes the old "overwrite existing rules" behavior).
- **REQ-YF-INSTALL-006** *(superseded by `REQ-YF-FLOW-004`)* the legacy "companion-rule install shall
  preserve an existing rule unless `--force`" no longer holds: under the aggregated ruleset there is
  no hand-edit tolerance (S3) — acted-on sections are always rewritten to the embedded source.

### 3.3.1 Aggregated ruleset (`REQ-YF-FLOW`)

`yf` surfaces every rule-bearing skill's companion protocol as **one** operator-facing file in the
rules dir, `YOSHIKO_FLOW.md`, instead of a scatter of standalone `*.md` files. The format is owned
end-to-end by the `flow` module (as `marker` owns the SKILL.md marker).

- **REQ-YF-FLOW-001** *(testable)* the aggregate file shall carry a fixed do-not-edit banner, a
  deterministic `yf`-version generated-on note (never a wall-clock timestamp), and one HTML-comment
  fenced section per protocol — `<!-- yf-flow: skill=… protocol=… version=… sha256=… -->` … body …
  `<!-- yf-flow:end protocol=… -->` — ordered alphabetically by `protocol`. Each section body is the
  protocol file **verbatim**, so its `sha256` equals the `manifest.json` file sha256. `version` is
  omitted for a manifest-less protocol.
- **REQ-YF-FLOW-002** *(testable)* every write shall **reconcile-prune**: a section whose
  `(skill, protocol)` is no longer embedded, or whose manifest entry is `deprecated:true`, is dropped;
  a section for a skill merely **not selected** this run is retained (reconcile keys on the embedded
  set, never on the invocation selection).
- **REQ-YF-FLOW-003** *(testable)* on **any** install/upgrade write, every `yf`-owned standalone rule
  file present in the rules dir — including protocols for skills **not** named this run — shall be
  folded into `YOSHIKO_FLOW.md` and the standalone deleted (C4a migration); non-`yf` files are never
  touched; the fold is idempotent and preserves a folded standalone's bytes.
- **REQ-YF-FLOW-004** *(testable)* the aggregate is a fully `yf`-managed artifact (S3, no hand-edit
  tolerance): acted-on sections are **always** rewritten to the embedded source (no `--force` gate);
  `remove` drops the named skills' sections **unconditionally** (even a drifted section) and deletes
  `YOSHIKO_FLOW.md` when its last section is removed (S6).
- **REQ-YF-FLOW-005** *(testable)* `doctor` and `preflight` shall read a protocol's installed content
  from the aggregate **section body** when `YOSHIKO_FLOW.md` is present (authoritative), falling back
  to a legacy standalone file only when the aggregate is absent (transition release, S5). `doctor`'s
  axis stays presence + content-hash vs embedded (`rule_missing`/`rule_drift`/ok); `preflight`'s axis
  preserves **all seven** outcomes (`ok | update_available | drift | deprecated | missing |
  manifest_schema_unknown | manifest_missing`) by feeding the section body through the unchanged
  `manifest.json` semver machinery.
- **REQ-YF-FLOW-006** *(testable)* serialization shall be deterministic: `serialize → parse →
  serialize` is byte-stable (the generated-on note carries the `yf` version, not a timestamp), and
  section sha256 is over the body only, so header churn never perturbs a doctor/preflight verdict.

### 3.4 Integrity marker & up-to-date detection (`REQ-YF-MARK`)

- **REQ-YF-MARK-001** *(testable)* `yf` shall compute a per-skill **tree hash** = SHA256 over each
  file (sorted by relpath) as `relpath-bytes ++ file-bytes`, with `SKILL.md` **marker-stripped
  before hashing**, so a deployed marked copy hashes identically to the embedded source.
- **REQ-YF-MARK-002** *(testable)* on install/upgrade `yf` shall inject a single marker into the
  deployed `SKILL.md` after the YAML frontmatter: `<!-- yf-skills: v=<version> tree=<sha256> -->`.
- **REQ-YF-MARK-003** *(testable)* `yf skills status` shall report per skill: `installed`,
  `up-to-date` (deployed marker hash == embedded tree hash), `complete` (all embedded files
  present), `unmodified` (recomputed deployed hash, marker-stripped, == embedded).
- **REQ-YF-MARK-004** *(testable)* `yf skills upgrade` shall rewrite files, re-inject the marker,
  and **prune** deployed files absent from the embedded tree.

### 3.5 Preflight/config kernel (`REQ-YF-PRE`)

- **REQ-YF-PRE-001** *(testable)* `yf preflight <skill> --json` shall return a status from the
  superset schema `ok | ignored | system_deps_missing | bd_not_initialized | rule_missing |
  rule_drift | rule_deprecated | manifest_*`, plus `scaffold_added` and `instructions`, matching the
  legacy per-skill Python `check` output.
- **REQ-YF-PRE-002** *(testable)* the kernel shall detect required tools and enforce a minimum `bd`
  version (≥ 1.0.5).
- **REQ-YF-PRE-003** *(testable)* the kernel shall verify a companion rule against the skill's
  embedded `manifest.json` (sha256 + semver). The installed content is read from the aggregate
  `YOSHIKO_FLOW.md` **section body** when present, with a legacy standalone fallback when it is absent
  (`REQ-YF-FLOW-005`). All seven outcomes are preserved — `ok | update_available | drift | deprecated |
  missing | manifest_schema_unknown | manifest_missing` — so a section body matching a
  `previous_versions[].sha256` still yields `update_available`, a `deprecated:true` entry yields
  `deprecated`, and an unknown `schema_version` yields `manifest_schema_unknown`. This per-rule axis is
  **distinct** from the §3.4 whole-tree marker.
- **REQ-YF-PRE-004** *(testable)* the kernel shall read per-skill config `.yf-<skill>.local.json`
  (including `ignore-skill`) and maintain runtime state under `.yf/<skill>/`.
- **REQ-YF-PRE-005** *(testable)* the kernel shall scaffold gitignore anchors (`/.yf/`) idempotently.
- **REQ-YF-PRE-006** *(testable)* beads-init **verify** shall classify a repo by parsing
  `bd status --json` for an `error` **key** (not exit code), distinguishing `not_initialized` from a
  wedged-but-initialized `corrupted` repo.
- **REQ-YF-PRE-007** beads-init **repair** shall apply the idempotent sequence (`bd dolt stop →
  bd migrate schema → bd migrate`; gitignore/hooks/perms/JSONL hardening; local-only assertion).

### 3.6 Doctor (`REQ-YF-DOCTOR`)

- **REQ-YF-DOCTOR-001** *(testable)* `yf doctor` shall check, per axis: `version`, `bd`
  (present + ≥ 1.0.5), `uv`, `git`, each `skills:<name>` (via §3.4 marker comparison →
  `not installed`/`outdated`/`incomplete`/`modified`), and companion-rule presence/hash.
- **REQ-YF-DOCTOR-002** *(testable)* `yf doctor` shall support `--json` and exit non-zero if any
  axis fails.

### 3.7 Distribution (`REQ-YF-DIST`)

- **REQ-YF-DIST-001** *(testable)* `yf` shall be released via cargo-dist for `{darwin,linux} ×
  {amd64,arm64}` with checksums and semver derived from git tags.
- **REQ-YF-DIST-002** *(testable)* the release shall publish/update a Homebrew formula in
  `dixson3/homebrew-tap` that declares `depends_on "beads"` and `depends_on "uv"`.
- **REQ-YF-DIST-003** *(WAIVED — operator-ratified 2026-06-16)* the cargo-dist-generated Homebrew
  formula carries **no** `test do` block: cargo-dist (`dist` 0.32.0) emits a minimal formula and
  exposes no test-block knob, so `brew test yf` is not provided. `yf`'s behavior is verified
  instead by the crate test suite and the G1 install round-trip (build + `yf skills install` +
  `yf skills status`). Adding a test block would require a post-publish formula patch, intentionally
  not adopted (keeps the formula fully cargo-dist-managed).

### 3.8 Rename invariants (`REQ-YF-RENAME`)

- **REQ-YF-RENAME-001** all skills shall be named `yf-<skill>`; `bdplan → yf-plan`,
  `bdresearch → yf-research`; invocations become `/yf-<skill>`.
- **REQ-YF-RENAME-002 (INV-1)** the rename of the self-driving skills (`yf-plan`, `yf-research`)
  shall be the **last** execution step, performed in an isolated worktree, so the orchestrator
  driving the work runs from the installed copy and is not mutated mid-flight.
- **REQ-YF-RENAME-003** *(testable)* no canonical source shall retain a stale `bdplan`/`bdresearch`
  reference after the rename (drift-check clean).

### 3.9 Legacy migration (`REQ-YF-MIGRATE`)

- **REQ-YF-MIGRATE-001** *(testable)* `yf` shall idempotently migrate legacy `.state/<old>/` and
  `.<old>.local.json` to `.yf/<new>/` and `.<new>.local.json`.

## 4. Skill catalog (per-skill specs)

The macro spec composes these. `REQ-<KEY>-*` ids live in each skill's `SPEC.md`.

| Skill (`yf-`)           | Was                  | Group    | Spec key | Per-skill SPEC                           |
| :---------------------- | :------------------- | :------- | :------- | :--------------------------------------- |
| yf-plan                 | bdplan               | beads    | PLAN     | `skills/yf-plan/SPEC.md`                 |
| yf-research             | bdresearch           | beads    | RESEARCH | `skills/yf-research/SPEC.md`             |
| yf-beads-authoring      | beads-authoring      | beads    | BAUTH    | `skills/yf-beads-authoring/SPEC.md`      |
| yf-beads-extra          | beads-extra          | beads    | BEXTRA   | `skills/yf-beads-extra/SPEC.md`          |
| yf-beads-init           | beads-init           | beads    | BINIT    | `skills/yf-beads-init/SPEC.md`           |
| yf-beads-hygiene        | _(new, #29)_         | beads    | HYG      | `skills/yf-beads-hygiene/SPEC.md`        |
| yf-beads-upstream       | beads-upstream       | beads    | BUP      | `skills/yf-beads-upstream/SPEC.md`       |
| yf-incubator            | incubator            | beads    | INCUB    | `skills/yf-incubator/SPEC.md`            |
| yf-diagram-authoring    | diagram-authoring    | utility  | DIAG     | `skills/yf-diagram-authoring/SPEC.md`    |
| yf-drift-check          | drift-check          | utility  | DRIFT    | `skills/yf-drift-check/SPEC.md`          |
| yf-optimal-instructions | optimal-instructions | utility  | OPTINST  | `skills/yf-optimal-instructions/SPEC.md` |
| yf-skill-authoring      | skill-authoring      | utility  | SKAUTH   | `skills/yf-skill-authoring/SPEC.md`      |
| yf-markdown-lint        | markdown-lint        | markdown | MDLINT   | `skills/yf-markdown-lint/SPEC.md`        |
| yf-markdown-pdf         | markdown-pdf         | markdown | MDPDF    | `skills/yf-markdown-pdf/SPEC.md`         |

> Several skills already ship topical design docs under `skills/<skill>/spec/*.md` (e.g. `cli.md`,
> `data.md`, `phases.md`, `portability.md`). The per-skill `SPEC.md` is the **requirement-numbered**
> contract; it MAY reference those design docs rather than restate them.

## 5. Verification

- Each *(testable)* requirement maps to ≥1 integration/system test naming its REQ id (plan-010
  Epic 6; coverage enforced by Issue 6.5).
- `yf`-tool requirements are verified by the crate test suite; per-skill requirements by that
  skill's own checks/tests where present.

## 6. References

- `GUARDRAILS.md` — the out-of-domain boundaries this spec operates within.
- `docs/plans/plan-010-james-dixson-73eebd/plan.md` — the plan that produces `yf`.
- `skills/SPEC-TEMPLATE.md` — the per-skill SPEC schema.
