# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`beads-skills` (published as `dixson3/beads-backed-skills`) is a collection of
beads-backed Claude Code skills authored by James Dixson / Yoshiko Studios. Skills live
under `skills/<name>/` (each with a `SKILL.md` + optional `scripts/*.py` run via `uv run`
with PEP 723 inline deps, and frontmatter declaring `skill-group` / `depends-on-tool` /
`depends-on-skill`). An `install.py` resolves the transitive `depends-on-skill` closure and
installs into `~/.claude/skills` (and/or `~/.agents/skills`). Task tracking is `bd` (beads,
Dolt-backed); the repo is itself a beads workspace. This plan modifies the **bdplan** skill
(`skills/bdplan/`: `SKILL.md`, `agents/*.md`, `scripts/plan_manager.py`,
`formulas/*.formula.toml`) — the planning skill that is being used to author this very plan
(a dogfooding situation, see plan.md Risks). Stack: Python 3.14 via `uv`, git, bd/Dolt, d2
for diagrams, pandoc/xelatex for PDFs.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-06-14 -->

- `bd`: bd version 1.0.5 (Homebrew)
- `git`: git version 2.54.0
- `uv`: uv 0.11.21 (5aa65dd7a 2026-06-11 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.94.0 (2026-06-10)
- `glab`: glab 1.102.0 (b5a548b3)
- `claude`: 2.1.173 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/beads-skills`
- Working directory at plan creation: `/Users/james/workspace/dixson3/beads-skills`
- Plan directory: `docs/plans/plan-009-james-dixson-996e44`

## Operator identity

- Git user: `james-dixson`
- Name / contact: James Dixson · james@yoshikostudios.com · GitHub `dixson3`
- Organization: Yoshiko Studios LLC
- Authority scope: repo owner / maintainer. Git authority is **conservative by default** —
  the agent does not commit, push, or `bd dolt push` without explicit operator
  authorization (bdplan REQ-ORCH-014). New code attribution: MIT, James Dixson /
  Yoshiko Studios LLC, current year.

## Runtime assumptions

- **OS/shell:** macOS (darwin 25.x), zsh. Commands must use non-interactive flags
  (`rm -f`, `cp -f`, `BatchMode=yes`) — interactive aliases can hang the agent.
- **Network:** local-first. `bd`/Dolt operate locally; upstream is GitHub
  (`dixson3/beads-backed-skills`) via `gh` (authenticated). d2's first PNG render may fetch
  a one-time Chromium (owned by the dotfiles bootstrap).
- **Credentials:** `gh` is authenticated for the upstream repo; no other secrets needed.
- **Side-effect permissions:** filesystem edits under the repo are fine; git
  commit/push/`bd dolt push` require explicit authorization (conservative).
- **Worktree-specific (this plan):** assumes git ≥ 2.x worktree support and `bd` ≥ 1.0.5
  with native worktree DB resolution via `git rev-parse --git-common-dir` (INV-2). The
  Capability Gate + a runtime viability fallback guard this assumption.
- **Bootstrapping:** this plan's first execution runs **in-place** (the worktree feature it
  builds does not yet exist); worktree mode + the D2 default-on flip apply only after the
  Issue 2.5 dogfood acceptance passes.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
