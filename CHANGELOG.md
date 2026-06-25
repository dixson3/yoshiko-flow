# Changelog

All notable changes to Yoshiko Flow (`yf`) are documented here. The version source
of truth is the `yf` crate version in `yf/Cargo.toml`; releases are cut by pushing a
matching `v<semver>` git tag (cargo-dist builds the artifacts and GitHub release).

## Unreleased

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
