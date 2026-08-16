---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**yoshiko-flow** — a repository of beads-backed agent skills for Claude Code and other
harnesses, plus `yf`, the Rust CLI that installs and maintains them.

Two artifacts, deliberately separate:

- `skills/` — portable skill directories (`SKILL.md`, `agents/*.md`, `scripts/*.py` run via
  `uv` with PEP-723 inline deps, `protocols/*.md` always-loaded rules).
- `yf/` — a Rust crate (edition 2021, `clap`, `rust-embed`, `serde`) that **embeds the
  entire `skills/` tree at build time** and deploys it to `~/.claude/skills/`.

The repo is **both the source and a consumer of its own skills**: editing `skills/` changes
nothing about the `yf` you are running until you rebuild and redeploy. That gap is the
subject of this plan.

Non-obvious setup: `skills/` sits **outside** the `yf/` cargo package, reached via
`#[folder = "../skills"]`. `rust-embed` is declared **without** `debug-embed`, so release
builds bake the tree in at compile time while debug builds read it from disk at runtime.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-16 -->

- `bd`: bd version 1.1.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.3 (507230998 2026-08-07 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.97.0 (2026-07-31)
- `glab`: glab 1.113.0 (d62881304)
- `claude`: 2.1.228 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-042-james-dixson-98631b`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson (james@yoshikostudios.com) — repository owner and sole
  maintainer; full authority to approve, merge, and publish in this repo.

## Runtime assumptions

- **OS/shell:** macOS (Darwin 25.5.0), `zsh`. The plan's build measurements are
  macOS/aarch64; rebuild timings will differ elsewhere, though the cargo semantics under
  test are platform-independent.
- **Toolchain:** a working Rust toolchain with `cargo` on `PATH` (measured against cargo
  1.97.1). `cargo build --release` must succeed from a clean checkout.
- **Network:** not required for the fix itself. Required once if `rust-embed` is not already
  in the local registry cache — relevant to Issue 1.2a, which needs an offline-resolvable
  scratch crate.
- **Credentials:** `gh` authenticated, for Issue 4.4 (posting the correction to #137). No
  other network credentials needed.
- **Side effects:** this plan writes **only** inside the repo — `yf/build.rs`,
  `yf/Cargo.toml`, tests, CI config, and docs. It changes **no command behavior** and
  deliberately does **not** write to `~/.claude/`, `~/.local/bin/`, or any harness config.
  That is what distinguishes it from plan-042.
- **Destructive operations:** none. The riskiest action is a `cargo build`, and experiments
  that build should run in an isolated worktree with their own `CARGO_TARGET_DIR`.
- **Beads:** `bd` >= 1.1.0, initialized and healthy in this repo.

## Adjacent-concept glossary

- **embed / embedded tree** — the copy of `skills/` compiled into the `yf` binary by
  `rust-embed`, as opposed to the on-disk `skills/` or the deployed `~/.claude/skills/`.
- **dep-info** — rustc's record of files an compilation unit read (here, via
  `include_bytes!`). Tracks file *content*, never a *directory listing* — the root of #137.
- **`rerun-if-changed`** — a build-script directive telling cargo when to re-run it.
  Emitting *any* disables cargo's implicit whole-package watch.
- **defect 1a / 1b** — this plan's shorthand: 1a = embed staleness (additions only),
  1b = version-stamp staleness (every skills-only change). Two distinct defects that #137
  conflates.
- **land the plane** — the session-close ritual: push open work upstream, sync, verify.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
