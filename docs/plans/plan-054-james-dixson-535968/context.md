---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**yoshiko-flow** is both the source and a consumer of its own agent skills. It ships two
artifacts from one repository:

- **`yf`** — a Rust binary (workspace at `yf/`, crate version in `yf/Cargo.toml`) that installs,
  tunes and doctors agent-harness configuration. Skills are embedded at compile time via
  `rust-embed` in release builds and read from disk in debug builds.
- **19 skills** under `skills/` — markdown (`SKILL.md`) plus Python helpers, deployed into a
  harness-specific directory per harness.

Five harnesses are supported: `claude-code`, `codex`, `opencode`, `pi`, `agents`. Three carry a
config profile (`yf/profiles/*.json`); **pi deliberately does not** — its config surface is
unverified, so a pi tune deploys rules and skills only.

Task tracking is **beads** (`bd`), Dolt-backed and `dolt.local-only = true` — never
`bd dolt push`. Upstream issue tracking is GitHub (`dixson3/yoshiko-flow`) via `gh`, at **coarse**
granularity: one tracking issue per plan, never one per bead.

Validation is `CHANGE-VALIDATION.md` (approved; 51-row FULL tier). Cross-artifact agreement is
`DRIFT-CHECK.md` (100 edges over 50 nodes) — a prose/LLM judgement with no runnable command.

**Three artifacts move independently** and this plan touches all three: the repo source, the
binary-embedded tree, and the session-installed skill. Editing `skills/` changes nothing about
the running session until a rebuild and redeploy.

The public website (`web/`, Pelican → S3/CloudFront) **auto-publishes on a successful tag-push
Release**, so site content must be correct before the tag.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-26 -->

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
- Plan directory: `docs/plans/plan-054-james-dixson-535968`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson (`james@yoshikostudios.com`), repository owner and sole maintainer.
- Authority scope: full — may authorize outward-facing writes (upstream issue create/close,
  `git push`, tag push) and destructive local operations. Release cutting is the operator's
  decision alone.

## Runtime assumptions

**A cold reader on a different machine cannot run this plan as-is.** Epics 2 and 6 depend on
machine-specific state that is recorded here rather than assumed.

- **OS / shell** — macOS (Darwin 25.5.0), `zsh`. Note `grep` in the authoring session is a
  **ugrep shell-function wrapper**, not `/usr/bin/grep`; criteria must not depend on
  `grep -qv` semantics (upstream #224).
- **Toolchain** — the Tool inventory above, plus `cargo`/`rustc` for the `yf` workspace.
- **Third-party harness binaries, not pinned by this repo** — `pi` 0.84.1
  (`~/.nvm/.../bin/pi`) and `opencode` 1.18.23 (`~/.opencode/bin/opencode`). Epic 2's live
  regression requires both on `PATH`.
- **A local model gateway** — the live harness walk used CLIProxyAPI at `127.0.0.1:8317`. A
  machine without it must substitute its own model configuration.
- **Symlinked harness surfaces** — `~/.pi/agent/AGENTS.md` and `~/.config/opencode` are symlinks
  into `~/_dotfiles/rc-files`, which **is a git repository**. Any `yf harness tune --revert`
  during execution will leave that repository dirty **by design**. Do not commit it as part of
  this plan.
- **Network + credentials** — `gh` authenticated against `dixson3/yoshiko-flow` (it owns its own
  credential store; never write a token to config). Epic 6 additionally needs push rights and
  the release workflow's AWS OIDC role.
- **Side-effect permissions** — Epics 0–5 are local-only. Epic 6 performs **irreversible,
  outward-facing** writes: upstream issue closes, `git push`, and a `v0.5.0` tag push that
  **auto-publishes the website**. All are behind the human release-authorization gate.

## Adjacent-concept glossary

| Term | Meaning in this plan |
| :-- | :-- |
| **`SKILL_DIR`** | The bash block in each `SKILL.md` that locates the skill's own directory at runtime, so `${SKILL_DIR}/scripts/*.py` resolves. The subject of Epic 1. |
| **harness** | An agent CLI that loads skills — `claude-code`, `codex`, `opencode`, `pi`, `agents`. Each has its own skills directory and rule-file target. |
| **managed block** | The `BEGIN yf-managed-rules` region yf writes into a harness's `AGENTS.md`. Distinct from the claude-code **rules aggregate** (`YOSHIKO_FLOW.md`), a whole file. |
| **tune** | `yf harness tune` — writing harness *config* (and rules), as opposed to installing *skills*. |
| **consent gate** | The refusal-plus-delta that blocks a config write absent `--allow-permissions-write`. |
| **silent success** | An operation reporting success while its postcondition is false. The through-line of upstream #203 and of three defects this plan fixes. |
| **land the plane** | Session-close: push deferred beads upstream, run the FULL tier, sync user scope. |
| **coarse tracker** | The single upstream issue filed per plan, never one per bead. |
| **OKF bundle** | The portable plan-folder structure — reserved `index.md` and `log.md` beside `plan.md`. |

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
