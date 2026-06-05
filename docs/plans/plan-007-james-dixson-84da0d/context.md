# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`beads-skills` is the working directory for a collection of Claude Code / agent skills
backed by **bd (beads)**, a Dolt-powered issue tracker. Skills live under `skills/<name>/`,
each with a `SKILL.md` (frontmatter + behavior), `README.md`, and optional
`agents/`, `scripts/`, `formulas/`, `templates/`, `spec/`, `protocols/` subdirs. A
repo-level `install.py`/`install.sh` installs skills (grouped by frontmatter `skill-group`)
and their always-loaded companion rules (`protocols/*.md`) into the user or project rules
surface (`~/.<surface>/rules/` or `<git-root>/.<surface>/rules/`, where surface is `.claude`
or `.agents`). The published counterpart is the GitHub repo `dixson3/beads-backed-skills`;
this directory is the same codebase. Project rules in `AGENTS/` (CONSISTENCY.md,
DOCUMENTATION.md) and `CLAUDE.md` govern skill authoring; this plan generalizes those two
rule files into a new `drift-check` skill. No build step — skills are markdown + Python
helpers run via `uv run` (PEP 723 inline deps).

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-06-04 -->

- `bd`: bd version 1.0.5 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.18 (e32666915 2026-06-01 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.93.0 (2026-05-27)
- `glab`: glab 1.101.0 (b3786045)
- `claude`: 2.1.160 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/beads-skills`
- Working directory at plan creation: `/Users/james/workspace/dixson3/beads-skills`
- Plan directory: `docs/plans/plan-007-james-dixson-84da0d`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson <dixson3@gmail.com>, Yoshiko Studios LLC (GitHub: dixson3). New
  modules/LICENSE default to MIT, current year.
- Authority scope: repo owner; conservative git authority — changes are reported as a
  land-the-plane handoff and committed/pushed only on explicit authorization.

## Runtime assumptions

- OS/shell: macOS (darwin), zsh. Paths and `find`/`grep` invocations assume BSD userland.
- Tooling: `uv` available for `uv run` (PEP 723 scripts); `bd` >= 1.0.5; `git`; `gh`
  authenticated for the GitHub upstream (`dixson3/beads-backed-skills`).
- Network: not required for the build itself (markdown + local scripts); only `gh` for
  optional upstream issue filing at land-the-plane.
- Side effects: execution writes only under `skills/drift-check/`, `AGENTS/`, `CLAUDE.md`,
  `README.md`, and `install.py`, plus this plan dir and `.beads/`. No destructive ops on
  unrelated paths. Git commit/push only on explicit authorization (conservative authority).
- The work is markdown/skill authoring + a paper portability probe; no service deploy, no
  credentials beyond `gh` auth.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
