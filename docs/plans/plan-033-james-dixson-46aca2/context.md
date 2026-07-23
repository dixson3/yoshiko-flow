---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (working dir name `beads-skills`) is the source repo for the **yf** toolchain: a
Rust CLI (`yf/`, Cargo, embeds skills + profiles via `rust-embed`) plus a family of Claude Code
skills under `skills/yf-*` (each with a `SKILL.md`, `protocols/*.md`, and Python helpers run via
`uv run` with PEP 723 inline deps). The macro contract lives in `SPEC.md` (`REQ-*` ids); each skill
has its own `skills/<name>/SPEC.md`. Task tracking is **beads** (`bd`, Dolt-backed, local-only — no
Dolt remote; JSONL export gitignored). This plan touches the Rust CLI's `yf/src/cmd/harness/*`
module (the `yf harness tune` feature from plan-032) and `yf/profiles/`. Build: `cargo build`/
`cargo test` in `yf/`. The installed `yf` binary at `~/.local/bin/yf` may lag the source tree
(rebuild via `yf self dev-install` or `cargo` to exercise new subcommands).

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-22 -->

- `bd`: bd version 1.1.0 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.26 (396ef7ce4 2026-06-30 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.96.0 (2026-07-02)
- `glab`: glab 1.106.0 (fc1869c7)
- `claude`: 2.1.201 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-033-james-dixson-46aca2`

## Operator identity

- Git user: `james-dixson` (James Dixson, GitHub `dixson3`).
- Attribution: sole maintainer of this repo; authority to approve plans, land to `main`, and
  authorize upstream pushes. LICENSE/attribution default MIT, current year, per the user's global
  attribution rules.

## Runtime assumptions

- **OS/shell:** macOS (Darwin, `arm64`), `zsh`. Rust toolchain + Cargo present for `yf/`.
- **Build/test:** `cargo build` / `cargo test` run in `yf/`; new Cargo deps (`toml`, `toml_edit`)
  are ordinary crates.io additions (network access for the first `cargo fetch`).
- **Beads:** `bd` >= 1.1.0, local-only (no Dolt remote — never `bd dolt push`); JSONL export
  gitignored.
- **Side effects:** the feature writes to per-harness config/rule files under `$HOME` (e.g.
  `~/.codex/config.toml`, `~/.config/opencode/opencode.json`, `~/.codex/AGENTS.md`) and a sidecar
  `.yf/harness-tune-manifest.json`. Tests must use a **sandboxed `HOME`** (project `TESTING.md`
  Tier-2 discipline) — never touch the real `$HOME`.
- **Git authority:** conservative — commit locally on a non-`main` branch; push only on explicit
  operator authorization. Upstream issue tracking is coarse GitHub (`dixson3/yoshiko-flow`).

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
