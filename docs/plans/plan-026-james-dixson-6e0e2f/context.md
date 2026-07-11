# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (a.k.a. `beads-skills`) is a monorepo of beads-backed Claude Code skills
(`skills/yf-*`) plus a Rust `yf` kernel binary (preflight/doctor). Each skill is a directory with
`SKILL.md`, an optional `SPEC.md`, `protocols/` (always-loaded trigger rules), and `scripts/`
(Python helpers run via `uv run` with PEP 723 inline deps). This plan touches three markdown
skills:

- `skills/yf-markdown-lint/` — GFM linter (`scripts/markdown_lint.py`, ~417 lines, rules
  ML001–ML009; SPEC.md drives the rule table). SPEC-first repo convention: a new `REQ-*` lands
  before code + a tagged test.
- `skills/yf-markdown-pdf/` — pandoc + xelatex MD→PDF (`scripts/md2pdf.py`, existing Lua filters
  `blocks.lua`, `landscape_wide_tables.lua`; frontmatter `depends-on-tool: [uv, pandoc, xelatex]`).
- `skills/yf-markdown-html/` — **new** in this plan, mirroring markdown-pdf's structure.

Skill system-tool deps are declared in SKILL.md frontmatter `depends-on-tool: [...]`, consumed by
the `yf` kernel's preflight/doctor (Epic 4 makes that declaration actually gate + report).

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-11 -->

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
- Plan directory: `docs/plans/plan-026-james-dixson-6e0e2f`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson (GitHub `dixson3`), repo owner/maintainer, full authority over the
  `dixson3/yoshiko-flow` codebase and its published skills.

## Runtime assumptions

- **OS/shell:** macOS (darwin), zsh. Filters and scripts should stay POSIX-portable where
  practical (downstream Linux/Windows consumers exist), but development + validation is macOS.
- **Toolchain:** pandoc **3.10** (`+lua`, `+server`; Figure AST / pandoc ≥3.0 required for the
  caption filter), xelatex present (MacTeX `/Library/TeX/texbin`). Python 3.14 via `uv`.
- **pandoc reader extensions matter:** the CriticMarkup filter requires `-f gfm-strikeout`; the
  caption filter requires `-f gfm+implicit_figures` (see exp-001). A cold reader on a different
  pandoc version must re-verify these — pandoc <3.0 lacks the Figure AST.
- **No network / credentials** needed to execute; upstream reconcile uses `gh` against
  `dixson3/yoshiko-flow` (coarse: one tracking issue per plan).
- **Side effects:** edits skill files under `skills/`, adds a new skill dir, updates SPEC/tests.
  No destructive operations.

## Adjacent-concept glossary

- **CriticMarkup** — an inline change-tracking syntax: `{++add++}`, `{--del--}`, `{~~old~>new~~}`
  (substitution), `{==highlight==}`, `{>>comment<<}`.
- **Authoring subset** — the fast on-edit `yf-markdown-lint` rule set
  (`ML001,ML002,ML005,ML006,ML007,ML008`, gaining ML010) that fires per-edit; the full audit adds
  ML003/ML004/ML009.
- **Implicit figures** — pandoc's mode where a lone image in a paragraph becomes a `Figure` AST
  node with a caption; off by default under `gfm`.
- **`depends-on-tool`** — SKILL.md frontmatter listing required system binaries, read by the `yf`
  preflight/doctor kernel.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
