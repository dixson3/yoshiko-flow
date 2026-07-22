# Changelog

All notable changes to Yoshiko Flow (`yf`) are documented here. The version source
of truth is the `yf` crate version in `yf/Cargo.toml`; releases are cut by pushing a
matching `v<semver>` git tag (cargo-dist builds the artifacts and GitHub release).

## Unreleased

Beads formula-staging kernel hardening (plan-027, #84): preflight now owns
formula staging so beads-backed skills never ship a formula they forget to stage,
and doctor gained static validation + provenance-tracked cleanup of the staging dir.

### Added

- **`yf preflight` owns formula staging (REQ-YF-PRE-011).** On every preflight, the
  kernel copies each beads-backed skill's embedded `formulas/*.formula.toml` into the
  project's (gitignored) `.beads/formulas/`, verifying the destination on every run
  (a destination deleted since a prior stage is re-created — not a source-hash-only
  skip), records provenance in a `.beads/formulas/.yf-staged.json` marker, and anchors
  `/.beads/formulas/` in the root `.gitignore`. `SCAFFOLD_VERSION` bumped 1→2 so
  already-preflighted repos pick up the new anchor. `bd mol pour|wisp <name>` now
  resolves with no per-call `cp`/`rm` staging in the SKILL body.
- **`yf doctor` FormulaCheck axis (REQ-YF-DOCTOR-004).** A static, read-only check over
  the embedded skill tree: every concrete `bd mol pour|wisp <name>` in a runnable bash
  fence of a formula-shipping skill's SKILL.md must have a shipped
  `formulas/<name>.formula.toml` (placeholders/prose/non-bash fences excluded).
- **`yf doctor --prune-formulas`.** A provenance-tracked GC on its own affordance
  (decoupled from `--repair`): removes only `.beads/formulas/` entries the yf-staged
  marker attributes to yf that no currently-embedded skill still declares — never a
  foreign/unmarked proto, and nothing at all when the marker is absent.

### Changed

- **SKILL.md fleet migration.** Removed the per-call `cp`/`rm` `.beads/formulas/`
  staging brackets from `yf-plan` (`plan-execute` pour + `plan-investigate` wisp) and
  `yf-research` (`yf-research` pour); the permanent `--force` on `bd mol burn` is kept.
  `yf-beads-authoring` documents the no-stage canonical pattern; the `e-formula-name`
  drift edge now also flags a hand-staging bracket as drift.
- **`workflows` promoted to a formal install group (`REQ-YF-INSTALL-003/004`).**
  `yf-plan`, `yf-research`, and `yf-incubator` move from `skill-group: beads` to
  `skill-group: workflows`; the `beads` install group is now the five `yf-beads-*`
  support skills. `yf skills install --group workflows` installs those three workflows
  **plus their `depends-on-skill` closure** (the beads skills they need) — a `--group`
  install now closes over its members' dependencies, so groups pull in the groups they
  depend on. `--group beads` installs only the `yf-beads-*` support skills. No engine
  change (the closure already applied to a group base); the frozen `install-parity.json`
  golden and the `computed_groups` / beads-membership unit tests were regenerated.

## v0.4.0 — 2026-07-09

Self-contained vendor install with a full `yf self` update/install/uninstall
lifecycle and XDG dirs; a `yf-plan` lifecycle overhaul (intake-at-execute,
base-pinned branches, fingerprint re-review gate, ready-for-approval gate,
cascade-close on completion); a `.yf/` config namespace with a minimal-local
profile; and bd 1.1.x certification.

### Added

- **Self-contained vendor install + `yf self` lifecycle (#55).** `yf` is now
  primarily distributed via the `curl | sh` installer to `~/.local/bin` (uv-style),
  with Homebrew kept as a secondary path. New `yf self` command surface:
  - `yf self update` — checks the latest GitHub release, downloads the host's
    `yf-<triple>.tar.gz`, verifies its sha256 against the release manifest, extracts
    it (pure-Rust `flate2`+`tar`), and atomically replaces the running binary
    (`self-replace`). **Vendor installs only**: it refuses on a Homebrew (Cellar) copy
    (directing you to `brew upgrade`) and on a from-build/unknown copy unless
    `--force`. `--check` reports availability without swapping.
  - `yf self install --from-build [--release|--debug] [--build] [--force]` — promotes
    a local `cargo build` to `~/.local/bin/yf` for development (suppresses the upgrade
    nudge; `yf self update --force` round-trips back to a vendor release).
  - `yf self uninstall` — removes the binary, the yf-owned XDG dirs, and the
    installer's `PATH` line, never touching installed skills/rules.
- **Post-update skills/rules refresh.** After a successful `yf self update`, the new
  binary re-deploys user-scope skills/rules once per present surface (`~/.claude`,
  `~/.agents`); `--binary-only` skips it. Fail-soft — a refresh failure never rolls
  back the binary swap.
- **Upgrade-detection nudge.** `yf version` / `yf doctor` print a throttled (24h),
  fail-open, **vendor-only** notice when a newer release exists. Opt out with
  `YF_NO_UPDATE_CHECK=1`; auto-skipped under `CI`.
- **XDG directory layout.** `yf` resolves config/cache/data/bin via an XDG layout on
  both Linux and macOS (honoring `XDG_CONFIG_HOME` / `XDG_CACHE_HOME` /
  `XDG_DATA_HOME` / `XDG_BIN_HOME`): receipt → `~/.config/yf`, update-check cache →
  `~/.cache/yf`, binary → `~/.local/bin`.
- **Preflight self-update offer (REQ-YF-PRE-009).** On an `ok` verdict, `yf preflight`
  now folds a `yf self update` offer into `instructions` when a newer release is
  already known — vendor installs only, **cache-only** (it reads the shared
  `~/.cache/yf/update-check.json` the throttled `yf version`/`yf doctor` nudge writes,
  so it adds **no** network latency to a skill invocation and is eventually
  consistent). The offer notes that `yf self update` also refreshes installed skill
  definitions/rules and that you likely need `/reload-skills` afterward. A build from
  a **dirty** working tree (surfaced as a `-dirty` suffix on `yf version`) is the
  first short-circuit and is never offered an update — it signals active local `yf`
  development.
- **Preflight cache version-invalidation (REQ-YF-PRE-008, REQ-YF-SELF-007).** Each
  `.yf/<skill>/preflight.json` is stamped with the generating `yf` version; a mismatch
  (or absent stamp) is a full cache miss that re-probes system deps + `bd` and re-runs
  the scaffold ensure. This is how `yf self update` invalidates preflight — the swapped
  binary reports a new version, so the next preflight re-validates from scratch with no
  explicit cache-clear.
- **`yf-plan` ready-for-approval gate (plan-024, #69).** A `ready-for-approval` status
  plus a `ready-check` verb gate the approval prompt on **last-red-team = APPROVE AND
  audit-pass**, so approval can't be granted over an un-reconciled review or a failing
  portability audit.
- **`yf-plan` cascade-close on completion (plan-024, #73).** A self-contained
  `close_cascade.py` wired into RECONCILE §6.4 closes container/epic beads when a plan
  completes — fail-loud on still-open children, treating a resolved gate as terminal.
- **CONTRIBUTING.md — how to report `yf-*` skill defects (#75).** Documents where to
  file, the report checklist, and anti-patterns (with #74 as the exemplar); linked from
  the README so GitHub surfaces it in the new-issue flow.
- **Claude Code Optimization docs (plan-025, #80).** New README section plus an expanded
  `docs/recommended-settings.md` (permissions block, tool disables, notification/upload/
  connector keys).

### Changed

- **`yf-plan` lifecycle rework — intake-at-execute (plan-021, #47 + #63 + #64).** A
  predictable, worktree-default git model:
  - **Intake-at-execute (#47).** The `plan-execute` molecule is no longer poured at
    INTAKE; INTAKE now writes a content **fingerprint**, auto-commits the plan, and
    lands it. The pour moves to EXECUTE start, where one `resume-scan`-driven
    **pour-once/resume gate** replaces the old duplicate-pour + resume guards (epic
    absent → pour + atomic `record-epic`; present → resume).
  - **Base-pinned named branches (#47).** Planning runs in `<plan-id>-development`,
    execution in `<plan-id>-execute` cut from a **pinned base** (never ambient HEAD),
    with a `landing-strategy` config switch (`main` default | `feature-branch`) that
    drives both the execute base and the §6.1 merge target. Teardown deletes only
    `<plan-id>-execute`, preserving the feature branch under `feature-branch`.
  - **Auto-commit at the plan→execute boundary (#63).** New `commit-plan` verb makes a
    scoped, **local-only** commit (never pushes, refuses the default branch / detached
    HEAD fail-closed) — a `GR-PLAN-003` carve-out so a fresh execute session inherits a
    committed base.
  - **Content-fingerprint re-review gate (#64).** Approval writes a `**Fingerprint:**`
    over the plan's content sections (excluding header fields, phase-log, `reviews/`,
    and `## Upstream Issues`); editing reviewed content marks the plan **stale-approved**
    and blocks execute until re-review (or logged `--force`).
  - SPEC-first: `REQ-PHASE-002`/`REQ-RESUME-001`/`REQ-RESUME-004`, `REQ-BRANCH-001..004`,
    `REQ-PLAN-034/040/054/055/064/065`, `REQ-PORT-040/041`. A scratch-project Tier-2 test
    harness (`skills/yf-plan/test-harness/`) validates the modified skill; the installed
    copy is promoted (`cargo build` → `yf skills install`) only after the scratch smoke.
- **cargo-dist installer retargeted to `~/.local/bin` + `.tar.gz`.** `install-path`
  moved from `~/.cargo/bin` to `~/.local/bin` (XDG), and `unix-archive` flipped from
  `.tar.xz` to `.tar.gz` so `yf self update` extracts with pure-Rust `flate2` — no
  system `tar`/`xz` dependency on minimal Linux/container hosts.
- **Install docs re-sequenced (#54, partial).** README and the website install page
  now lead with `curl | sh` (Homebrew secondary) and document `yf self …`, the XDG
  dirs + env overrides, and the macOS browser-download `xattr` note.
- **Mode-aware `yf-beads-init` wedged-migration repair (plan-020, #56).** The
  wedged-schema-migration fix is now mode-aware. Server mode is unchanged
  (`bd dolt stop` → `bd migrate schema` → `bd migrate`); for **embedded** storage
  (`.beads/embeddeddolt/`, no Dolt server — where `bd dolt stop` errors and
  `bd migrate schema` fails against the dirty on-disk working set) repair now commits
  the working set first via a **data-preserving** native step (raw `dolt add -A && dolt
  commit` in the derived Dolt-repo dir; never `reset --hard`/`--allow-empty`; a clean
  tree is a no-op; falls back to `bd dolt commit` when `dolt` is absent). Mode is
  detected from `.beads/metadata.json` (`dolt_mode`, with a `dolt-server.*` filesystem
  fallback); the Dolt-repo path is **derived** (unique `.dolt/`-parent, guarded against
  zero/multiple candidates), never hardcoded. The `verify` remediation string is
  likewise mode-aware. SPEC: `REQ-BINIT-011`/`REQ-BINIT-016`, `REQ-YF-PRE-007`;
  `BEADS_INIT.md` rule → v1.0.3.
- **bd 1.1.x certification + local-only remote hygiene (plan-022, #68 + #61).** The
  beads skills are certified against `bd` 1.1.x (219 yf tests + 41 upstream tests green,
  FULL merged-state validation passing) and local-only remote handling is hardened.
- **`.yf/` config namespace + minimal-local profile (plan-023, #58 + #67 + #66 + #57).**
  Per-skill config migrated to `.yf/<skill>/config.local.json` (legacy root dotfile
  migrated in, gitignore anchors collapsed; `REQ-YF-MIGRATE-001`, `REQ-YF-PRE-004`);
  read-only profile engine-mode drift detection with `doctor --repair` reporting the
  embedded engine-mode without migrating (`REQ-YF-PRE-010`, `REQ-BINIT-025`);
  `interactions.jsonl` gitignored in the repair top-up (`REQ-BINIT-023`); and the
  `UPSTREAM_TRACKING` Safety-invariant reworded routing-primary (`REQ-BUP-032`).
- **Removed the transitional flat `.yf/<short>.local.json` config tier (#76).** Now that
  the `.yf/<skill>/config.local.json` migration is ubiquitous, config resolution and
  migration drop the flat interim tier end to end — resolution is canonical subdir →
  legacy root dotfile only (revises `REQ-YF-PRE-004`, `REQ-YF-MIGRATE-001`).

### Fixed

- **`yf-plan` `commit-plan` failed on local-only beads repos (#71).** `commit-plan` did
  an unconditional `git add -- "${plan_dir}" .beads`; where `.beads/` is gitignored
  (gh-only interchange), the ignored pathspec made `git add` fail and blocked intake. The
  pathspec is now conditional (`.beads/` added only when it exists and is not gitignored),
  surfacing a `beads_note` when skipped. SPEC: `REQ-PLAN-064` local-only carve-out.
- **change-validation FAST tier missed formatting drift (#45).** The `.rs` FAST tier ran
  only `cargo test`, so `cargo fmt` drift slipped past local validation and failed only in
  CI (bit v0.3.2). A dedicated `cargo-fmt` FAST id (`cargo fmt --all -- --check`) now runs
  on `*.rs`/`Cargo.toml` edits; clippy stays FULL-only.
- **change-validation engine resolver never fired on real installs (#74).** `yf-plan`
  `validate-merged` resolved the `yf-change-validation` engine at one hardcoded in-repo
  path, so every user- or `.claude`/`.agents`-scope install fell through to `engine: none`
  and the layer-(b) cross-plan safety net never ran. Resolution now mirrors the SKILL_DIR
  find precedence (user → project → cwd), searching in-tree source then install surfaces.

## v0.3.2 — 2026-06-24

### Fixes

- **yf-beads-init: stop flagging a phantom "Dolt remote under local-only" (#43).**
  The canonicalization-drift detector read `bd config get sync.remote`'s plain-text
  output, which prints a non-empty `sync.remote (not set in config.yaml)` sentinel at
  **exit 0** for an *unset* key — misclassified as a configured remote, so preflight
  reported an unactionable drift instruction that `--remove-remote` (a clean no-op)
  could never clear. Detection and repair now read the unambiguous `--json` shape
  (`"value": ""` = unset) via a shared `bd_config_value()` helper.
- **yf-markdown-pdf: 16-bit / alpha PNGs no longer render blank (#44).** Such PNGs
  embed but render white under xelatex. The pipeline now detects them by their PNG
  IHDR and renders an 8-bit RGB copy (alpha composited onto white) into a run-scoped
  temp dir prepended to `--resource-path`; source images are never modified.
  `--no-normalize-images` opts out, and absence of the imaging library degrades
  gracefully (originals used, build still succeeds).

## v0.3.1 — 2026-06-24

### Packaging

- **Homebrew formula no longer declares runtime dependencies.** Dropped the
  `[workspace.metadata.dist.dependencies.homebrew]` block (`beads`, `uv`), so the
  generated `dixson3/homebrew-tap` formula emits no `depends_on` lines. `bd` (beads)
  and `uv` are provisioned out-of-band (vendor installers / dotfiles bootstrap)
  rather than pulled in as Homebrew dependencies of `yf`.

## v0.3.0 — 2026-06-24

Adds a renderable-fenced-block pipeline (d2/csv compile-checked in lint and rendered in
PDF), a per-repo change-set validation engine, consolidates shared Python helpers into a
`_shared/` package, and extends `yf-beads-init` repair with native runtime/hook/remote
cleanup.

### Renderable fenced blocks: d2 + csv (plan-017, #33 + #34 + #37)

- **`_shared/renderable_fences.py`** — new canonical registry of renderable fenced-block
  kinds (d2, csv) shared across the lint, PDF, and diagram skills.
- **yf-markdown-lint** — new **ML009** rule: d2 fenced blocks are compile-checked (caught
  malformed diagram source at authoring time, not render time).
- **yf-markdown-pdf** — `scripts/blocks.lua` renders fenced blocks during the PDF pipeline
  (d2 → embedded diagram, csv → table) with a `glyph-fallback.tex` for broad Unicode
  coverage; `--no-render-fences` opts out. `_shared/sync.py` gains a Python→Lua emitter
  that keeps `blocks.lua` mirrored from the canonical registry (DRIFT-CHECK edges enforce it).
- **yf-diagram-authoring** — embed/lift/inline round-trip between a `.d2` source file and an
  inline fenced block.
- **yf-research** — new `record-epic` subcommand and the CLI-spec realignment that goes with it.

### Helper consolidation + `yf-beads-init` native cleanup (plan-016, #15 + #39 + #36)

- **`_shared/`** — two-helper vendoring sweep: `manifest_update.py` (whole-file, byte-identical
  copies across five skills) and `json_extract.py` (defensive JSON extractor, region-vendored
  into `plan_manager.py` + `research_manager.py`; `json-get` gains list int-indexing). New
  DRIFT-CHECK edges and `test_sync.py` coverage. Zero `yf` Rust change for this epic.
- **yf-beads-init** — `repair()` native cleanup: untrack-runtime, content-guarded
  remove-hook-shims, and a confirm-gated remove-remote (`--remove-remote`), wired into
  preflight-converge (the read-only invariant is preserved). Rust tests + SKILL/SPEC docs.
- **audit** — regression test pinning the `audit --json-output` `json.dumps` invariant (bug
  already absent; no production change).

### New: `yf-change-validation` — per-repo change-set validation engine (plan-015, #27 + #25)

- **`yf-change-validation`** — new skill that validates a change set against a per-repo,
  operator-approved `CHANGE-VALIDATION.md` manifest: declared check tiers (`fast`/`full`),
  a changed-path → check-id trigger scope, and a signal fingerprint that detects when the
  manifest itself has gone stale relative to the repo's real test/build surface.
  - `scripts/change_validation.py` — the engine: `infer` (bootstrap a manifest by scanning
    CI workflows, `Cargo.toml`, `test_*.py`, build configs), `run` (execute the tier or
    the trigger-scoped affected subset for a changed path; fail-closed), and `check-drift`
    (re-propose the manifest
    when the signal fingerprint diverges). Self-maintaining: a stale manifest re-proposes
    itself rather than silently passing.
  - `spec/{schema,engine,inference}.md` + `SPEC.md` — the manifest schema, the
    validate/trigger-scope engine, and the inference/bootstrap heuristics.
  - `templates/manifest.md` — the seed `CHANGE-VALIDATION.md` template.
  - `protocols/CHANGE-VALIDATION-TRIGGER.md` — always-loaded companion rule binding the
    on-change trigger a `description` cannot fire (silent no-op unless the repo has an
    **approved** `CHANGE-VALIDATION.md`).
- **yf-plan** — §6.1.5 layer (b) now **delegates** change-set validation to
  `yf-change-validation` when an approved manifest exists; the static `validate-cmd`
  becomes the thin middle fallback and the not-checked notice the floor (3-tier
  precedence, output schema + exit-3 contract preserved).
- **CHANGE-VALIDATION.md** — dogfood manifest for this repo (approved): `fast`/`full` tiers
  wiring the cargo + per-skill `uv`/pytest suites and `_shared/sync.py --check`, with the
  `website` build rows trimmed (deploy-only, not a validation gate) and `yf-drift-check`
  excluded (prose/LLM trigger, not a runnable command).
- **Docs (#25):** added worktree-uv guidance to yf-plan's worktree address-space docs —
  prefix `uv run …` with `env -u VIRTUAL_ENV` inside a plan worktree so uv resolves the
  worktree's own environment, and do not follow uv's `--active` suggestion (it targets the
  primary venv, the wrong address space).

### `_shared/` package — retire the duplicated active-set classifier (plan-014, #15)

- **`_shared/`** — new top-level package (outside the `skills/` embed root, so `yf` never
  treats it as a skill) holding canonical Python helpers shared across skills. Ships **zero**
  `yf` Rust changes: the vendored copies live inside each consuming script and install copies
  them verbatim.
  - `_shared/active_set.py` — the single canonical active-set classifier (`classify_active` +
    `Edge`, `ActiveSetReport`, helpers, and the `ACTIVE_*`/`PARENT_CHILD`/`OPEN`/`IN_PROGRESS`/
    `CLOSED_STATUSES`/`GATE_TYPE` constants), delimited by `BEGIN`/`END` region markers.
  - `_shared/sync.py` — repo-time sync tool that **regenerates the marker-fenced classifier
    region in-place** in each consumer from canonical (no sibling `import`, no new file — each
    script stays self-contained); `--check` mode exits non-zero on divergence (CI/manual backstop).
  - `_shared/README.md` — documents the regenerate-the-fenced-region (vendoring shape (b)) pattern
    and the enforcement point.
- **yf-beads-hygiene / yf-beads-upstream** — the active-set classifier is now a **generated**,
  marker-fenced region in both `beads_hygiene.py` and `upstream.py`, regenerated from
  `_shared/active_set.py`. The plan-013 "do NOT edit one without the other" hand-maintenance
  banner is **gone**; both test suites stay green and the single-file test loaders are untouched.
- **DRIFT-CHECK.md** — migrated the classifier edges: `classifier-canonical` re-pointed to
  `_shared/active_set.py` (fixed authority); the old pairwise `e-classifier-copy` replaced by two
  derived `value-equal` region edges (`e-active-set-copy-hygiene`, `e-active-set-copy-upstream`).
  A tampered region now FAILs the **copy**, never the canonical.

### Reconcile policy: local beads = active work only (plan-013, #38 + #17)

- **yf-beads-upstream** — implements `custom.upstream.granularity` (`coarse`|`granular`,
  default `coarse`; fills the previously-unimplemented REQ-BUP-043) and a default-deny
  `custom.upstream.auto_hoist_followons` knob. Adds a `hoist` operation (per-granularity
  create-or-map via `External:`, dry-run-first, reversible `bd close -r` — never `bd delete`),
  narrow-vs-broad follow-on detection, an `un-hoist`/restore path, and a land-the-plane flow
  that **proposes follow-on hoists with a single confirm by default** (no-prompt only under
  the opt-in key, narrow signal only). `enumerate` now uses the shared active-set definition.
  Companion rule `UPSTREAM_TRACKING.md` 1.0.2 → 1.1.0.
- **yf-beads-hygiene** — new read-only-first `reconcile` pass: classifies the active set
  (in_progress / claimed-open / open ancestors) and lists non-active local beads as hoist
  candidates plus obsolete upstream issues (mechanical delivered signal; flag-for-review
  fallback, never auto-close). Gated `--apply`/`--yes`/`--record` **delegates** the hoist to
  yf-beads-upstream (the carve: hygiene proposes, upstream executes).
- **DRIFT-CHECK.md** — new `e-classifier-copy` edge asserting the active-set classifier
  (authored once in yf-beads-hygiene, copied verbatim into yf-beads-upstream for install
  independence) stays identical across both.

#### yf-beads-init — prune empty `.codex/config.toml` residual (dqo)
- Repair now removes the bare `[features]` residual `bd setup codex --remove` leaves behind,
  deleting `.codex/config.toml` only when effectively empty (then pruning an empty `.codex/`).

## v0.2.0 — 2026-06-24

Hardens the yf/beads runtime, adds a beads-graph hygiene skill, and consolidates the
always-loaded rule surface so skill-owned protocol rules travel with their skills.

### `yf` CLI

#### `yf doctor` — extensible check framework (#32)
- Refactored `yf doctor` from hardcoded axes into a `Check`-trait registry
  (`CheckResult { name, ok, required, detail, remediation }`). Adding a new
  prerequisite is now a one-line registry edit.
- `BinCheck` reports presence + version + **resolved path** + min-version for
  `bd`/`uv`; new non-fatal `HomebrewShadowCheck` warns on a Homebrew-shadowed `uv`.
- Read-only by default; `--repair` is now an explicit opt-in (repair failures still
  error via `bail!`, read-only checks return `Result<ExitCode>`).
- Consolidated 3 duplicate `which` implementations + 2 version parsers into a new
  shared `yf/src/tool.rs` (`resolve_tool` / `tool_version`).

#### yf-beads-init — suppress bd-init cruft (#31)
- Fresh init now runs `bd init --skip-hooks --skip-agents` (+ `dolt.local-only`,
  `doctor.suppress.git-hooks`), so a new repo has no instruction-file boilerplate,
  no `.codex/` / `.agents/skills/beads/`, no beads `settings.json` hook, and leaves
  `core.hooksPath` at the git default.
- Repair no longer force-installs beads git hooks; adds idempotent bd-native cleanup
  for already-dirtied repos (hooks uninstall + `hooksPath` reset;
  `bd setup claude/codex --remove`; marker-scoped CLAUDE/AGENTS strip; entry-scoped
  `settings.json` cleanup that never wholesale-deletes).

### Skills

#### New: `yf-beads-hygiene` (#29)
- Safe, read-only-first audit + gated repair of the beads dependency graph.
- Resolves edge targets via `bd show` over the **full universe** (`--all` +
  `--type gate`) and classifies edges as true-orphan / truly-dangling /
  satisfied-gate / live-gate — live gates are never mistaken for dangling.
- Gated repair proposes only truly-dangling removals, with round-trip restore and a
  post-mutation `bd dep cycles` check; routes to `yf-beads-init` on a wedged DB.
- Regression-tested against the original 11-live-gate-edge false positive.

#### yf-beads-upstream — default `none` + preflight offer
- Unconfigured upstream now resolves to **disabled** everywhere (default-deny:
  anything `!= "true"` is off), so repos initialized before this change fail closed.
- Adds a gated, **one-shot** preflight detect-and-offer: on a github/gitlab origin
  with upstream unconfigured, offers to configure once, then stays silent.

#### yf-beads-extra
- Documented two gotchas: `bd list` hides gate beads and truncates at 50 rows;
  `bd dep cycles` for post-mutation integrity.

### Rules & docs

- **Rule consolidation:** per-skill protocol rules are now installed as a single
  aggregated `YOSHIKO_FLOW.md` with per-protocol hash-bearing fences for selective
  version update/removal.
- **BEADS.md fold:** the orphan, unowned `~/.claude/rules/BEADS.md` is folded
  (selective, deduplicated) into the skill-owned `BEADS_INIT.md` so it ships via
  `yf skills install`; the standalone global rule is retired (manual delete).
- **New doc:** `docs/recommended-settings.md` — recommended Claude `settings.json`
  baseline, each key tied to the rule/contract it supports (`disableWorkflows` and
  `todoFeatureEnabled: false` flagged as highest-impact), with user- vs project-scope
  guidance.
- **yf-markdown-lint:** added ML008 (require explicit table alignment markers);
  converted skill-authoring / optimal-instructions docs to GFM.

### Internal
- Parity golden regenerated for the new skill; preflight version fixtures updated for
  the `BEADS_INIT.md` manifest bump (1.0.1 → 1.0.2).

### Closed issues
- #29 (yf-beads-hygiene), #30 (settings docs), #31 (bd-init cruft), #32 (yf doctor).
- Coarse tracking: #35 (plan-012).

## v0.1.0 — 2026-06-16

First release: skills lifecycle CLI, preflight kernel, and Homebrew distribution
(plan-010).
