# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`beads-skills` is the working repo for the portable `yf-*` Claude Code skill suite plus the `yf`
Rust kernel (`yf/`). Skills live under `skills/<name>/` (SKILL.md + SPEC.md + PEP-723
`scripts/*.py` run via `uv run` + `protocols/*.md` + hash-versioned `protocols/manifest.json`).
Installation is the `yf` Rust binary (`yf skills install/upgrade`) — there is no install.py. This
plan adds a top-level `_shared/` dir (canonical Python helper + a repo-time sync tool) and edits
`skills/yf-beads-hygiene/` + `skills/yf-beads-upstream/` (regenerate the classifier fenced region)
and the repo-root `DRIFT-CHECK.md`. Task tracking is beads (`bd`); upstream is GitHub via `gh`
(coarse one-issue-per-plan).

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-06-24 -->

- `bd`: bd version 1.0.5 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.24 (Homebrew 2026-06-23 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.95.0 (2026-06-17)
- `glab`: glab 1.105.0 (45c9976d)
- `claude`: 2.1.190 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/beads-skills`
- Working directory at plan creation: `/Users/james/workspace/dixson3/beads-skills`
- Plan directory: `docs/plans/plan-014-james-dixson-916de2`

## Operator identity

- Git user: `James Dixson` (`dixson3@gmail.com`, Yoshiko Studios LLC)
- Role: sole maintainer/author of the yf skill suite; full authority to merge, push, and file
  upstream issues against `dixson3/yoshiko-flow`.

## Runtime assumptions

- macOS (Darwin, arm64); zsh. Tools per the inventory above (bd 1.0.5, uv, gh authenticated).
- Pure repo-time work: Python sync tool + skill-script edits + DRIFT-CHECK manifest; tests via
  `uv run`. No `yf` Rust rebuild required (option B vendoring touches no Rust).
- Network for `gh` (issue annotate/close) available; pushes operator-authorized (conservative).
- beads DB local-only (`dolt.local-only true`); upstream GitHub `dixson3/yoshiko-flow`.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
