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
skills under `skills/yf-*` (each with a `SKILL.md`, `protocols/*.md`, Python helpers run via
`uv run` with PEP 723 inline deps). The macro contract lives in `SPEC.md` (`REQ-*` ids). Task
tracking is **beads** (`bd`, Dolt-backed, local-only — no Dolt remote; JSONL export gitignored;
coarse upstream tracking via `gh issue`). This plan touches the Rust CLI's
`yf/src/cmd/harness/*` and `yf/src/cmd/doctor/*` (the `yf harness tune` + `yf doctor` features
from plan-032/plan-033), the embedded `yf/profiles/`, and the Pelican static site under `web/`
(from plan-031). Build/validate: `cargo fmt --all --check` + `cargo clippy --workspace
--all-targets -- -D warnings` + `cargo test --workspace` (the CI gate), plus the repo's
`CHANGE-VALIDATION.md` full-tier suite (Python skill tests). The installed `yf` binary at
`~/.local/bin/yf` may lag the source tree — rebuild via `cargo`/`yf self dev-install` to exercise
new subcommands.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-23 -->

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
- Plan directory: `docs/plans/plan-034-james-dixson-ac6633`

## Operator identity

- Git user: `james-dixson` (James Dixson, GitHub `dixson3`)
- Role: sole maintainer / author of the yf toolchain; full authority to approve, execute, and
  land plans in this repo (branch, merge to `main`, and authorize pushes to `origin`).
- Attribution/license: MIT, Yoshiko Studios LLC (this machine's default org).

## Runtime assumptions

- **OS/shell:** macOS (darwin), zsh. Note the zsh word-splitting gotcha for multi-word shell vars
  (use bash arrays for conditional CLI args).
- **Toolchain present:** a working Rust toolchain (`cargo`, `clippy`, `rustfmt`), `bd` ≥ 1.1.0,
  `uv`, `python` 3.14, `gh` (authenticated), `d2` (for any diagrams), Pelican (for the `web/` build).
- **Network/credentials:** `gh` is authenticated for the coarse upstream tracking issue; no other
  network access is required to execute (beads is local-only). Pushes to `origin` are
  **operator-authorized only** (conservative git authority).
- **Side-effects:** execution runs in a git worktree (`.worktrees/<plan-id>`); code changes land on
  the `<plan-id>-execute` branch and merge to `main` under the landing lock; the plan folder and
  beads stay primary-side. All new drift/budget behavior is **read-only / warn-only** — no
  destructive side effects. Safe to run as-is on this machine.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
