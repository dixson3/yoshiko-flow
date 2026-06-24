# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`beads-skills` is the working repo for a suite of portable, beads-backed Claude Code skills
(the `yf-*` family) plus the `yf` Rust kernel (`yf/`, install/upgrade/verify/preflight). Skills
live under `skills/<name>/` as `SKILL.md` + `SPEC.md` + `scripts/*.py` (PEP-723, run via `uv
run`) + `protocols/*.md` (always-loaded rules) + `protocols/manifest.json` (hash-versioned).
This plan modifies two existing skills — `skills/yf-beads-hygiene/` and
`skills/yf-beads-upstream/` — and touches no kernel code. Task tracking is beads (`bd`); the
same working dir is the published skill repo (`dixson3/yoshiko-flow`), and upstream issue
tracking is GitHub via `gh` (coarse granularity — one tracking issue per plan-scale effort).

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-06-24 -->

- `bd`: bd version 1.0.5 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.24 (Homebrew 2026-06-23 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.95.0 (2026-06-17)
- `glab`: glab 1.105.0 (45c9976d)
- `claude`: not present

## Paths

- Repo root: `/Users/james/workspace/dixson3/beads-skills`
- Working directory at plan creation: `/Users/james/workspace/dixson3/beads-skills`
- Plan directory: `docs/plans/plan-013-james-dixson-0af2f8`

## Operator identity

- Git user: `James Dixson` (`dixson3@gmail.com`, Yoshiko Studios LLC)
- Role: sole maintainer/author of the yf skill suite; full authority to merge, push, and file
  upstream issues against `dixson3/yoshiko-flow`.

## Runtime assumptions

- macOS (Darwin, arm64); zsh shell. Tools per the inventory above (bd 1.0.5, gh authenticated).
- Network access for `gh` (GitHub issue create/close/comment) is available; pushes are
  operator-authorized (conservative push authority — never auto-push without confirmation).
- The beads DB is local-only (`dolt.local-only true`); no Dolt remote. `custom.upstream.enabled
  = true`, backend `github`, owner/repo `dixson3/yoshiko-flow`.
- Execution edits only `skills/yf-beads-hygiene/` and `skills/yf-beads-upstream/` plus their
  `protocols/` rules and the project CHANGELOG; tests run via `uv run`. No kernel rebuild needed.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
