---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (aka `beads-skills`) is the source repo for the Yoshiko Flow (`yf-*`) Claude Code
skills plus the `yf` kernel. Two stacks live side by side: (1) **`yf/`** — a Rust/clap binary
(v0.4.0, `serde_json` with `preserve_order`, `rust-embed` to bake the skills into the binary,
distributed via a cargo-dist `install.sh`); root-level `SPEC.md §3` specifies its requirements as
`REQ-YF-<AREA>-NNN` ids enforced by a `yf/src/coverage.rs` REQ→test gate. (2) **`skills/`** — the
`yf-*` skills (SKILL.md + Python helper scripts run via `uv run` with PEP-723 inline deps). This
plan targets the **Rust kernel** — it adds a `yf harness tune` command and a `yf doctor` check.
Task tracking is `bd` (beads), local-DB, coarse upstream tracking to GitHub `dixson3/yoshiko-flow`.

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
- Plan directory: `docs/plans/plan-032-james-dixson-6cb87b`

## Operator identity

- Git user: `james-dixson` (James Dixson)
- Contact: james@yoshikostudios.com
- Org: Yoshiko Studios LLC
- Authority scope: repo owner / maintainer of `dixson3/yoshiko-flow`; sole approver of plan gates
  and authorizer of upstream pushes.

## Runtime assumptions

- OS/shell: macOS (Darwin), `zsh`. Development on `d3-mbp-m5.local`.
- Toolchain: a Rust toolchain (`cargo`) is required to build/test `yf` (the tool inventory above
  does not list `cargo`/`rustc` — the executor must confirm `cargo` is on PATH before Epic 2+).
- Network/credentials: `gh` authenticated for GitHub issue filing (upstream tracking); no other
  network access required. `bd` runs against a local Dolt DB (local-only, no remote push).
- Side effects: execution edits Rust source under `yf/`, `docs/recommended-settings.md`, and root
  `SPEC.md`; runs `cargo test`. The shipped feature writes `~/.claude/settings.json` (user scope)
  or project `.claude/settings.{json,local.json}` — but only via the tune command it builds, never
  as a build side effect. Safe to run on the maintainer's machine as-is; a cold reader on another
  machine must supply `cargo` and a GitHub-authed `gh`.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
