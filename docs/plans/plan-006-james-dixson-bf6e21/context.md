# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`beads-skills` is a repository of beads-backed skills for Claude Code (and other agent
harnesses). Each skill lives under `skills/<name>/` with a `SKILL.md` (YAML frontmatter +
markdown body), optional `scripts/` (Python helpers run via `uv run`, PEP 723 inline deps),
`agents/` (sub-agent prompts), `protocols/` (companion rules surfaced to the rules dir at
install + a `manifest.json` hash), `formulas/`, and a `README.md`. A repo-level `install.sh`
copies selected skills into a target tree (`<root>/.{claude,agents}/{skills,rules}/`) via
`rsync`, and surfaces each skill's `protocols/*.md` as rules.

The eight skills split into two natural groups this plan formalizes: **beads** (bdplan,
bdresearch, beads-authoring, beads-extra, beads-upstream, incubator) which need the `bd` binary,
and **utility** (optimal-instructions, skill-authoring) which run with no `bd` dependency.

Non-obvious setup: project rules (`AGENTS/CONSISTENCY.md`, `AGENTS/DOCUMENTATION.md`) mandate a
consistency sub-agent run after every change to a skill file, and README-sync between
implementation, skill READMEs, and the project README. This plan's edits (8 SKILL.md +
installer + README) are subject to both. The repo uses `bd` (beads) for all task tracking — no
TodoWrite/markdown TODOs.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-06-03 -->

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
- Plan directory: `docs/plans/plan-006-james-dixson-bf6e21`

## Operator identity

- Git user: `james-dixson` (James Dixson, dixson3@gmail.com / james@yoshikostudios.com)
- Organization: Yoshiko Studios LLC; GitHub: dixson3
- Authority scope: repo owner. Default git authority is **conservative** — the executor
  reports the land-the-plane sequence and does not commit/push without explicit operator
  authorization. New code attribution: MIT, Yoshiko Studios LLC, current year.

## Runtime assumptions

- OS/shell: macOS (darwin), zsh. Paths and `rsync`/`shutil.which` behavior assume a POSIX
  environment.
- `uv` is present (every skill already requires it at runtime; this plan makes it an
  install-time prereq too). `rsync` is present (today's `install.sh` already depends on it).
- `bd` (beads ≥ 1.0.5) present for beads-group runtime, but **not** required to *install* any
  skill (warn-anyway policy).
- Network/credentials: only Issue 3.3 (file upstream tracking issue) needs `gh` auth against
  `github.com/dixson3/beads-backed-skills`. No other step needs network.
- Side effects: install writes under `<root>/.{claude,agents}/`; the plan's verification uses a
  throwaway `--target` temp dir. No destructive ops outside the chosen target (rsync `--delete`
  mirrors only within the per-skill destination subdir).

## Adjacent-concept glossary

- **Companion rule** — a `protocols/*.md` file a skill ships that the installer copies into the
  rules dir (always-loaded instruction surface); hash-tracked by `protocols/manifest.json`.
- **Group (install group)** — the `skill-group` frontmatter value; the unit `--group` selects.
- **PEP 723** — inline script metadata (`# /// script`) letting `uv run` resolve a script's deps
  (here, PyYAML for `install.py`).
- **Soft dep** — a skill grouped with a tool's group for intended-use reasons despite no hard
  `depends-on-tool` entry (e.g. `incubator` → beads).

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
