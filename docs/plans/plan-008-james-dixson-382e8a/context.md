# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`beads-skills` (published as `dixson3/beads-backed-skills`) is a repository of Claude Code
skills that orchestrate work through **beads** (`bd`, a Dolt-backed issue tracker). Skills
live under `skills/<name>/` (authoring source) and install to `.{claude,agents}/skills/`
via `install.py` (a `uv`-run PEP 723 script with a frontmatter-driven group/dependency
model — `skill-group`, `depends-on-tool`, `depends-on-skill`). Cross-skill content agreement
is enforced by a per-repo `DRIFT-CHECK.md` manifest (the `drift-check` skill). This plan adds
a new **`diagram-authoring`** utility skill (d2-based PNG generation) and wires soft,
instruction-level references to it from `bdplan` and `bdresearch`. Non-obvious setup: the
soft dependency is deliberately NOT a `depends-on-skill` edge (which `install.py` treats as a
hard force-install — see EXP-002); it is agent-instruction guidance only.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-06-06 -->

- `bd`: bd version 1.0.5 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.19 (7b2cff1c3 2026-06-03 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.93.0 (2026-05-27)
- `glab`: glab 1.101.0 (b3786045)
- `claude`: 2.1.167 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/beads-skills`
- Working directory at plan creation: `/Users/james/workspace/dixson3/beads-skills`
- Plan directory: `docs/plans/plan-008-james-dixson-382e8a`

## Operator identity

- Git user: `james-dixson`
- Operator: James Dixson (Yoshiko Studios LLC), GitHub `dixson3`, `dixson3@gmail.com` /
  `james@yoshikostudios.com`. Sole maintainer of this repo and the consuming dotfiles.
- Authority scope: full — owns the repo, the published skill repo, and `~/_dotfiles`.
  Git authority for execution is conservative-by-default (report handoff; push only on
  explicit instruction), per the project beads/landing protocol.
- Attribution convention: new modules/LICENSE → MIT, current year, Yoshiko Studios LLC.

## Runtime assumptions

- OS/shell: macOS (Darwin, arm64) + zsh on the dev machine; the skill itself targets both
  macOS and Linux (OS-independent preflight). Execution of this plan runs on the dev machine.
- Tools on PATH: `d2` v0.7.1 (Homebrew), `uv`, `bd` >= 1.0.5, `git`, `gh`. `rsvg-convert`
  present but unused (the d2-native PNG path was chosen over SVG→raster).
- Network: required once for d2's first PNG render (~140MB playwright Chromium). On the dev
  machine this is already warmed and is owned by the dotfiles bootstrap hook
  `65-d2-chromium.sh`, NOT by this skill. Offline execution works once warmed.
- Credentials: `gh` authenticated for the single coarse upstream tracking issue (#6 lineage)
  at land-the-plane. No other secrets needed.
- Side effects: writes new files under `skills/diagram-authoring/`, edits to
  `skills/bdplan/**` and `skills/bdresearch/agents/packager.md`, and project README/DRIFT-CHECK
  updates. No destructive operations. Git push is gated on explicit operator authorization.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
