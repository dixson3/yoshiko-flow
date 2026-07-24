---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` is a family of portable, cross-harness agent skills plus a single compiled
Rust CLI (`yf`). This plan is **docs-only + upstream-issue filing**, working in the `web/`
Pelican site (`web/content/pages/*.md`, theme `web/themes/yoshikoflow/`) and a repo-root
`VOICE.md`. Diagram authoring uses d2 (source-of-truth) + naba (flair) per the
`yf-diagram-authoring` convention. The site builds with Pelican from `web/` (deps via
`uv run --with-requirements web/requirements.txt`).

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-23 -->

- `bd`: bd version 1.1.0 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.26 (396ef7ce4 2026-06-30 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.96.0 (2026-07-02)
- `glab`: glab 1.106.0 (fc1869c7)
- `claude`: 2.1.201 (Claude Code)
- `d2`: 0.7.1 (`/opt/homebrew/bin/d2`) — diagram source→render engine (`yf-diagram-authoring`)
- `naba`: present (`/Users/james/.local/bin/naba`, + `~/.claude/skills/naba`) — diagram flair pass
- `pelican`: 4.11.0 (via `uv run --with-requirements web/requirements.txt pelican`) — static-site build (the Epic 7.2 exit gate)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-035-james-dixson-74d7ae`

## Operator identity

- Git user: `james-dixson` (James Dixson, GitHub `dixson3`).
- Role/authority: repo owner and maintainer of `dixson3/yoshiko-flow`; authorized to edit docs,
  file/close upstream issues, and land plans on `main`.
- Contact: `james.dixson@beyondidentity.com` (byid-mba-dixson3) / `dixson3@gmail.com`.

## Runtime assumptions

- **OS/shell:** macOS (Darwin, `d3-mbp-m5.local`), zsh.
- **Network/credentials:** `gh` authenticated to `dixson3/yoshiko-flow` (issue read/write); live web
  research was completed during INVESTIGATE (not required at execute).
- **Side effects:** docs-only + upstream-issue filing. Edits land under `web/`, repo-root `VOICE.md`,
  and the affected skills' doc surfaces; the only non-doc writes are new GitHub issues (Epic 3, the
  coarse tracker, and the two follow-on beads). **No `yf`/Rust code changes, no SPEC behavior
  change.** Diagram authoring runs d2 + naba locally; the exit gate runs a local Pelican build.
- **Beads:** local-only Dolt DB under `.beads/` (gitignored, never pushed) — consistent with the very
  workflow this plan documents.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
