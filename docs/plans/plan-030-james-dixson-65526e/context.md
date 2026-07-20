# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (aka `beads-skills`) is the source repo for the `yf-*` family of Claude Code
skills — beads-backed planning/research/hygiene skills installed into `~/.claude/skills/` (and
`.agents/skills/`) by `install.sh`. This plan modifies the **`yf-plan`** skill itself:
`skills/yf-plan/` holds `SKILL.md`, `SPEC.md`, `spec/*.md` (requirements: phases, cli, data,
portability), `agents/*.md`, and `scripts/*.py` (`plan_manager.py`, `close_cascade.py`, `okf.py`).
Stack: Python 3 helper scripts run via `uv` (PEP-723 inline deps), `bd` (beads / Dolt) for task
tracking, `gh` for GitHub upstream tracking. Convention is **SPEC-first** (AGENTS.md): the `REQ-*`
requirement lands before the implementing code + a tagged test. Non-obvious: the **installed** copy
of the skill under `~/.claude/skills/yf-plan` is the old rust-embed-baked copy — edits/tests target
the working tree under `skills/yf-plan/` (see TESTING.md Tier-2).

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-19 -->

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
- Plan directory: `docs/plans/plan-030-james-dixson-65526e`

## Operator identity

- Git user: `james-dixson` (James Dixson, GitHub `dixson3`)
- Contact: james@yoshikostudios.com
- Role / authority scope: repo owner and maintainer of `yoshiko-flow` / the `yf-*` skills — full
  authority to change skill SPECs, scripts, and behavior, and to land/push per the project's
  conservative git-authority convention (push only on explicit authorization).

## Runtime assumptions

- **OS/shell:** macOS (Darwin) + zsh; `bd` ≥ 1.1.0, `uv`, `git`, `gh`, Python 3 on PATH.
- **Deliverable is skill source, not runtime infra.** This plan's own changes are to `yf-plan`
  Python scripts + SPEC/markdown — validated by Tier-1 unit tests + the change-validation FULL tier,
  entirely locally. It is a `standard`-class plan (not `ci-release`), so it does not itself require
  a green real-runner execution.
- **Beads:** local-only beads repo (`.beads/` gitignored, gh-only upstream interchange). Task
  tracking via `bd`; no Dolt remote.
- **Upstream:** GitHub `dixson3/yoshiko-flow`, coarse granularity (one tracking issue per plan; #89
  is this plan's issue). `gh` authenticated.
- **Side effects / permissions:** git authority is conservative — local commits at the plan→execute
  boundary are permitted (never on the default branch); remote push only on explicit authorization.
- **Feature being built** targets GitHub Actions / release pipelines as the *classified* deliverable
  type, but building it requires no live CI run.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
