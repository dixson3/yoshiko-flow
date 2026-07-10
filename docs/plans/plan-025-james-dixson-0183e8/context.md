# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (`yf`) — a family of portable, cross-harness agent **skills** plus a single
compiled Rust CLI (`yf`) that installs, upgrades, verifies, and preflights those skills. Skills
are beads-backed (`bd`) and install into either the `.claude` or `.agents` surface at user or
project scope. This plan is **documentation-only**: it edits the repo `README.md` and
`docs/recommended-settings.md` — no Rust code, no `SPEC.md`, no skill-contract changes. Markdown
is plain GFM (linted by `yf-markdown-lint`). The relevant existing artifacts are `README.md`
(§Operating & health links the settings doc) and `docs/recommended-settings.md` (the recommended
`settings.json` baseline being expanded).

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-09 -->

- `bd`: bd version 1.1.0 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.26 (396ef7ce4 2026-06-30 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.96.0 (2026-07-02)
- `glab`: glab 1.106.0 (fc1869c7)
- `claude`: 2.1.201 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-025-james-dixson-0183e8`

## Operator identity

- Git user: `james-dixson` (James Dixson)
- Attribution: repo owner / maintainer (`dixson3`), full authority over this repo's docs.
- The operator's own `~/.claude/settings.json` is the reference baseline the plan documents.

## Runtime assumptions

- OS/shell: macOS (darwin), `zsh`. Execution is local to the repo checkout.
- No network access, credentials, or external side effects required to author the docs. The only
  network-touching step is the optional upstream tracking issue (`gh issue`) filed at INTAKE
  against `dixson3/yoshiko-flow`, which needs an authenticated `gh`.
- Documentation-only: the edits touch `README.md` and `docs/recommended-settings.md`. No build,
  no test suite, no `yf` CLI invocation beyond the `plan_manager.py` lifecycle helpers and
  `yf-markdown-lint`. Safe to run as-is on any clone of this repo.
- The documented `settings.json` recommendations are advisory prose about the operator's Claude
  Code config; applying them is the reader's choice, not an action this plan performs.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
