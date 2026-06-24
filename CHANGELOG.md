# Changelog

All notable changes to Yoshiko Flow (`yf`) are documented here. The version source
of truth is the `yf` crate version in `yf/Cargo.toml`; releases are cut by pushing a
matching `v<semver>` git tag (cargo-dist builds the artifacts and GitHub release).

## Unreleased

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
