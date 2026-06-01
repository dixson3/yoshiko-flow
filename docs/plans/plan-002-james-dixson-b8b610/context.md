# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`beads-skills` (published as `dixson3/beads-backed-skills`) is a collection of
beads-backed skills for Claude Code. Each skill lives under `skills/<name>/` with a
`SKILL.md` entry point, optional `agents/`, `scripts/`, `spec/`, `reference/`, and a
`README.md`. Skills are installed into a target tree by the repo-level `install.sh`, which
auto-discovers every `skills/*/` directory and (when a skill ships a `protocols/` dir)
installs its companion rules to the scope+surface rules dir. Skill authoring is governed by
three project rules under `AGENTS/`: `OPTIMIZED_SKILLS.md` (token efficiency),
`CONSISTENCY.md` (internal consistency, enforced via a sub-agent check), and
`DOCUMENTATION.md` (README/index consistency). Task tracking is `bd` (beads); planning is
`/bdplan`. No build step — Python helpers run via `uv run` with PEP 723 inline deps.

This plan adds a new skill, `skills/optimal-instructions`, and makes a small reciprocal
edit to `skills/skill-authoring`.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-05-31 -->

- `bd`: present (beads CLI; data under `.beads/`)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.17 (2026-05-28, aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.93.0 (2026-05-27)
- `glab`: glab 1.100.0
- `claude`: 2.1.159 (Claude Code)

## Paths

- Repo root: the `beads-skills` working tree (resolve with `git rev-parse --show-toplevel`).
- Working directory at plan creation: repo root.
- Plan directory: `docs/plans/plan-002-james-dixson-b8b610` (relative to repo root).

## Operator identity

- Git user: `james-dixson`.
- Attribution: James Dixson (dixson3@gmail.com), Yoshiko Studios LLC, GitHub `dixson3`.
  Authority scope: owner/maintainer of this repo and its published counterpart
  `dixson3/beads-backed-skills`; authorizes skill creation, rule changes, and intake.

## Runtime assumptions

- POSIX shell (zsh/bash) on macOS (darwin); commands use non-interactive flags.
- Python helpers run exclusively via `uv run` (never bare `python`); PEP 723 inline deps.
- `bd` is initialized in this repo (`.beads/`); intake mutates the local beads DB.
- GitHub access via `gh` for the upstream remote `dixson3/beads-backed-skills`.
- Execution is local file authoring under `skills/` + docs; no network side effects beyond
  optional `gh`/`git push` during the session-completion (landing) workflow.
- No new third-party dependencies are introduced by this plan.

## Adjacent-concept glossary

- **K1** — the token-efficiency ruleset (cut narrative / keep templates / extract scripts),
  owned by `skill-authoring`.
- **K2** — the instruction-file structural convention (AGENTS.md primacy; CLAUDE.md as a
  thin `@-include` index; behavioral rules in the rules subdir), owned by the new skill.
- **Instruction files** — always-loaded context files: `CLAUDE.md`, `AGENTS.md`, `AGENTS/*`
  (or `.agents/rules/*`).
- **Split apply** — K1 edits auto-apply; K2 structural relocation is propose-and-confirm.

## Additional context

The skill is triggered by its `description` only (no companion rule, no hook), modeled on
`skill-authoring` (`user-invocable: false`). This is an accepted best-effort trigger.
