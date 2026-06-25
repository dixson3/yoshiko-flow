# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`beads-skills` is the source repo for a family of beads-backed Claude Code skills
(the `yf-*` skills) plus the compiled `yf` kernel. Skills live under `skills/<name>/`
as `SKILL.md` + `scripts/*.py` (run via `uv run`, PEP-723 inline deps). Shared Python
helpers live in repo-root `_shared/` and are **vendored** into consuming skills at
authoring time by `uv run _shared/sync.py` (marker-fenced regions or whole-file copies;
`sync.py --check` is the byte-level guard) — skills never import each other. Cross-file
content agreement is enforced by an approved `DRIFT-CHECK.md` manifest. Installation is
the compiled `yf` binary (`yf skills install`), which embeds/deploys only the `skills/`
tree; `_shared/` sits deliberately outside it. There is no `install.sh`. This plan
touches four skills (`yf-diagram-authoring`, `yf-markdown-pdf`, `yf-markdown-lint`,
`yf-research`), the `_shared/` registry+sync engine, and `DRIFT-CHECK.md`.

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
- Plan directory: `docs/plans/plan-017-james-dixson-9ac898`

## Operator identity

- Git user: `james-dixson` (James Dixson, GitHub `dixson3`).
- Role/authority: repo owner and sole maintainer; holds full authority to approve
  spec edits (including the fixed-authority `yf-research` CLI spec touched by #37) and
  to authorize upstream pushes to `dixson3/yoshiko-flow`.
- Contact: james@yoshikostudios.com.

## Runtime assumptions

- **OS/shell:** macOS (Apple Silicon, `d3-mbp-m5.local`), zsh. The glyph-coverage work
  (#34) is validated on macOS with `Arial Unicode MS` as mainfont; off-macOS it degrades
  to xelatex warnings rather than failing (documented in the plan).
- **Required tools (all present at authoring time):** `d2` 0.7.1, `pandoc` 3.10,
  `xelatex` (MacTeX, with `newunicodechar.sty`), `uv`, `git`, `gh`. No new tool or font
  install is required for execution on this machine; `brew install --cask font-symbola`
  is the documented portable fallback only.
- **Network/credentials:** `gh` authenticated against `dixson3/yoshiko-flow` for upstream
  reconciliation. No network needed for the build/test work itself.
- **Side effects:** execution edits skill source under `skills/`, `_shared/`, and
  `DRIFT-CHECK.md`; writes throwaway temp artifacts under `$TMPDIR` (reaped per run).
  Upstream issue updates happen only at operator-authorized land-the-plane.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
