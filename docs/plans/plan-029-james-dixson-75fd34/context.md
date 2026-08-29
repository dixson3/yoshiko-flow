---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**beads-skills** (`dixson3/yoshiko-flow`) — a collection of Beads-backed skills for Claude Code
(and cross-harness agents): `yf-plan`, `yf-research`, `yf-incubator`, plus the beads/markdown/
diagram/validation utility skills. Skills live under `skills/<name>/` with a `SKILL.md`, a
`scripts/` dir of PEP 723 `uv run` Python helpers, `spec/` (SPEC.md + REQ-* requirements), and
`protocols/` companion rules. Shared code lives at repo-root `_shared/` and is **vendored** (not
imported) into each skill via `_shared/sync.py`. Task tracking is **Beads (`bd`)** — never markdown
TODOs. The repo is **SPEC-first**: a `REQ-*` requirement lands before the code that implements it.
Skills are installed via `install.sh`; the *installed* copy is a stale rust-embed snapshot, so
testing drives the working-tree copy (see `TESTING.md`), never the installed skill. This working
directory is the same codebase as the published skill repo issues are filed against.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-17 -->

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
- Plan directory: `docs/plans/plan-029-james-dixson-75fd34`

## Operator identity

- Git user: `james-dixson` (James Dixson)
- Contact / attribution: `dixson3@gmail.com`, Yoshiko Studios LLC (repo owner + sole maintainer).
- Authority scope: full — may approve plans, authorize commits/pushes, and file upstream issues on
  `dixson3/yoshiko-flow`. New code is MIT-licensed, current year.

## Runtime assumptions

- **OS/shell:** macOS (darwin), zsh. Paths and `uv run` shebang lines assume a POSIX toolchain.
- **Toolchain present:** `bd` ≥ 1.1.0, `uv` (for PEP 723 script deps — the engine adds `pyyaml`),
  `git`, `gh` (authenticated; used for the upstream tracking issue), Python ≥ 3.11.
- **Network:** none required for the engine/tests; `gh` needs network only at land-the-plane to
  file/update issue #83. No external API keys needed (unlike yf-research).
- **Side-effects:** execution writes under `skills/`, `_shared/`, and the plan folder; runs in a
  git worktree (`.worktrees/plan-029-execute`) and lands per the `main` landing strategy. Migration
  (`yf-okf migrate`) only mutates a folder when explicitly invoked on it — never bulk-rewrites.
- **Safe-to-run caveat:** editing `plan_manager.py` / `_shared/` affects live tooling — changes take
  effect only through the working-tree checkout, and tests must drive that copy, not the installed
  skill (`TESTING.md`).

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
