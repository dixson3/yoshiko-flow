# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`beads-skills` is the working-directory name for the git repo `dixson3/yoshiko-flow` — a
collection of 13 Claude Code / agent **skills** that orchestrate work through `bd` (beads, the
Dolt-backed issue tracker) plus utility skills (markdown lint/pdf, diagram authoring, instruction
optimization, drift-check). Each skill is a directory under `skills/<name>/` containing a
`SKILL.md` (YAML frontmatter + procedure), optional `scripts/*.py` helpers run via `uv` (PEP 723
inline deps), and optional `protocols/*.md` companion rules + a `manifest.json` (per-rule
sha256+semver). Skills install to `~/.claude/skills/` (or `.agents/`, or project scope) via
`install.py` (wrapped by `install.sh`, run through `uv`), which also copies companion rules to the
`rules/` surface. The repo tracks its own work with `bd` and plans with the `bdplan` skill
(`docs/plans/`). This plan (plan-010) renames every skill to a `yf-` prefix and replaces
`install.py` with a Rust binary `yf` distributed via Homebrew (`dixson3/homebrew-tap`).
Reference tools live at `~/workspace/dixson3/naba` (Go behavioral model) and
`~/workspace/dixson3/homebrew-tap`.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-06-14 -->

- `bd`: bd version 1.0.5 (Homebrew)
- `git`: git version 2.54.0
- `uv`: uv 0.11.21 (5aa65dd7a 2026-06-11 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.94.0 (2026-06-10)
- `glab`: glab 1.102.0 (b5a548b3)
- `claude`: 2.1.177 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/beads-skills`
- Working directory at plan creation: `/Users/james/workspace/dixson3/beads-skills`
- Plan directory: `docs/plans/plan-010-james-dixson-73eebd`

## Operator identity

- Git user: `james-dixson` (James Dixson, `dixson3@gmail.com` / `james@yoshikostudios.com`).
- Organization: Yoshiko Studios LLC; GitHub `dixson3`. Sole maintainer of this repo and the
  reference tools (`naba`, `homebrew-tap`).
- Authority scope: full owner — may create releases, push to `dixson3/homebrew-tap`, and set repo
  secrets (e.g. `HOMEBREW_TAP_TOKEN`). Git push authority for plan execution is conservative
  (report-and-authorize per the BEADS land-the-plane protocol), not auto-push.
- New code is attributed MIT © current year, James Dixson / Yoshiko Studios LLC.

## Runtime assumptions

- macOS (Darwin 25.x, arm64) with zsh; Homebrew at `/opt/homebrew`. Release matrix also targets
  linux amd64/arm64 via cargo-dist CI on GitHub Actions (ubuntu runners).
- Toolchain present: `bd` ≥ 1.0.5, `uv`, `git`, `gh` (authenticated to `dixson3/yoshiko-flow`),
  and a Rust toolchain (`cargo`, `rustc`) plus `cargo-dist` for the distribution epic.
- Network access to GitHub (releases, tap pushes, `gh issue`). `HOMEBREW_TAP_TOKEN` must be set as
  a repo secret before any real release tag (Gate G3).
- Execution side effects: plan-009 worktree model is in effect — code edits land on the plan
  branch in `.worktrees/<plan-id>`; bead tracking + plan folder stay primary-side. The driving
  `bdplan`/`yf-plan` orchestrator runs from the **installed** `~/.claude/skills/` copy, never the
  repo tree (INV-1). Upstream pushes and `dixson3/homebrew-tap` commits are operator-authorized,
  not automatic, except the cargo-dist release workflow which runs on an explicit `v*` tag.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
