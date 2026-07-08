# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (repo `dixson3/yoshiko-flow`, also the `beads-skills` working tree) is a family of
portable, cross-harness agent **skills** plus a single compiled Rust CLI, `yf`, that installs,
upgrades, verifies, and preflights those skills. Skills are beads-backed (`bd` / Dolt) and install
into either the `.claude` or `.agents` surface at user or project scope. This plan modifies the
**yf-plan** skill specifically: its `SKILL.md` doctrine, `SPEC.md` + `spec/*.md` requirements, and
`scripts/plan_manager.py` (a PEP 723 `uv`-run Click script, unit-tested by
`scripts/test_worktree.py`). Stack: Rust (the `yf` kernel, `cargo`), Python 3.11+ via `uv` (skill
helper scripts), and `bd` ≥ 1.1.0 for task tracking. Repo conventions are SPEC-first (SPEC edits
land ahead of code) and enforced by change-validation + drift-check manifests at the repo root.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-07 -->

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
- Plan directory: `docs/plans/plan-024-james-dixson-76cee9`

## Operator identity

- Git user: `james-dixson` (James Dixson, `james@yoshikostudios.com`)
- Role/authority: repo owner and maintainer of the `yf-*` skills; sole approver for this plan's
  start gate and operator-consent transitions.
- Attribution: MIT, Yoshiko Studios LLC (per the repo's attribution convention).

## Runtime assumptions

- **OS/shell:** macOS (darwin, Apple Silicon), zsh. Paths and tool versions above are host-specific
  (`d3-mbp-m5.local`); a cold reader on Linux should re-verify but nothing here is macOS-only.
- **Toolchain on PATH:** `bd` ≥ 1.1.0 (with `mol stale` / `children --json`), `git`, `uv`, `cargo`
  (Rust toolchain), `gh` (authenticated for the `dixson3/yoshiko-flow` remote), Python 3.11+.
- **beads DB:** local-only Dolt-backed `bd` in this repo; `.beads/` is gitignored (gh-only upstream
  interchange). No Dolt remote; never `bd dolt push`.
- **Network/credentials:** `gh` auth for reading/closing issues #69/#73 and filing the coarse
  tracking issue. No other network access required; the plan edits skill source + runs local tests.
- **Side effects:** edits `skills/yf-plan/**` (SPEC, SKILL.md, scripts) and repo-root manifests;
  runs local `cargo`/`uv`/`pytest` and `bd`. Execution is guarded by yf-plan's own worktree +
  landing-lock + change-validation gates. Safe to run as-is on the author's machine; a different
  clone must have the toolchain above and `gh` auth.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
