# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`beads-skills` (published as `dixson3/yoshiko-flow`) is a collection of beads-backed Claude
Code skills (the `yf-*` family) plus the **`yf` Rust CLI** (Cargo workspace, single member
`yf/`) that installs/manages those skills and runs preflight/doctor checks. Skills live under
`skills/<name>/` (each with `SKILL.md`, optional `SPEC.md`, `scripts/`, `protocols/`). The Rust
crate is `yf/` (clap v4 derive; key sources: `cmd/doctor.rs`, `preflight.rs`, `beads_init.rs`,
`cmd/common.rs`). Releases are cut via cargo-dist on a SemVer git tag, which also publishes the
Homebrew formula to `dixson3/homebrew-tap`. The repo tracks issues **upstream via GitHub**
(`gh issue`, repo `dixson3/yoshiko-flow`), coarse granularity — there is no local `.beads/` Dolt
DB in this checkout. Build/test via `cd yf && cargo test && cargo clippy --all-targets -- -D
warnings && cargo fmt --check` (the `.bdplan.local.json` `validate-cmd`).

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-06-23 -->

- `bd`: bd version 1.0.5 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.23 (Homebrew 2026-06-19 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.95.0 (2026-06-17)
- `glab`: glab 1.103.0 (c724bea5)
- `claude`: 2.1.186 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/beads-skills`
- Working directory at plan creation: `/Users/james/workspace/dixson3/beads-skills`
- Plan directory: `docs/plans/plan-012-james-dixson-a99822`

## Operator identity

- Git user: `james-dixson` (James Dixson, GitHub `dixson3`)
- Contact: james@yoshikostudios.com · Organization: Yoshiko Studios LLC
- Authority scope: repo owner / maintainer — sole approver for plan gates, upstream issue
  dispositions, and the (out-of-scope) release decision.

## Runtime assumptions

- OS/shell: macOS (Darwin, `d3-mbp-m5.local`), zsh. Tooling per the inventory above; the Rust
  toolchain (cargo/clippy/rustfmt) is available for the `yf` crate.
- Network/credentials: `gh` authenticated against `dixson3/yoshiko-flow` (needed for upstream
  reconcile). No Dolt remote in this repo (GitHub-tracked, no local `.beads/`).
- Side effects: Epics A/B edit Rust source under `yf/src/`; Epic C authors a new skill under
  `skills/yf-beads-hygiene/` and edits `skills/yf-beads-extra/`; Epic D adds
  `docs/recommended-settings.md`. The #31 cruft-cleanup work itself mutates repo files (hooks,
  instruction files) — exercise it in a throwaway dir, never against this repo.
- Execution worktree: `/.worktrees/` (yf-plan default-on worktree execute).

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
