# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (aka `beads-skills`) is the source repo for a suite of beads-backed Claude Code
skills (`yf-*`) plus the `yf` Rust CLI kernel. **This plan modifies the `yf-plan` skill's repo source** —
the structured-planning skill. Note the repo source (`skills/yf-plan/`) is **decoupled** from the
installed copy (`~/.claude/skills/yf-plan/`) that `/yf-plan` runs, so this is *not* a hot-swap
self-hosting change; validation uses a scratch-project harness (plan.md Epic 0 + the test-fidelity
risk).

`yf-plan` lives at `skills/yf-plan/` (installed to `~/.claude/skills/yf-plan/`): `SKILL.md`
(orchestration prose the main session follows), `scripts/plan_manager.py` (a Click CLI: worktree /
landing-lock / status / resume-scan / record-epic / audit verbs), `scripts/test_worktree.py`
(pytest), `formulas/plan-execute.formula.toml` (pours the start-gate molecule), `SPEC.md` (the
`REQ-PLAN-*` numbered contract) and topical `spec/*.md` (`phases.md`, `portability.md`, `agents.md`,
`cli.md`, `data.md`). The living-amendment log lives only in the repo-root macro `SPEC.md`.
SPEC-first is a project mandate (AGENTS.md): SPEC edits land before code.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-02 -->

- `bd`: bd version 1.0.5 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.26 (396ef7ce4 2026-06-30 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.95.0 (2026-06-17)
- `glab`: glab 1.106.0 (fc1869c7)
- `claude`: 2.1.198 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-021-james-dixson-bb3558`

## Operator identity

- Git user: `james-dixson` (James Dixson, GitHub `dixson3`).
- Contact / attribution: `james@yoshikostudios.com`; Yoshiko Studios LLC.
- Authority scope: repo owner — full authority over `dixson3/yoshiko-flow`, SPEC edits, the yf-plan
  skill, and the upstream GitHub issue tracker. Push stays operator-authorized (conservative git
  authority) at land-the-plane.

## Runtime assumptions

- **OS/shell:** macOS (Darwin, Apple Silicon), zsh; local execution, no network required for the
  code/tests (git worktree + Python/pytest run offline). `gh` auth only for upstream reconciliation.
- **Toolchain:** `uv` for the PEP-723 skill scripts + pytest (`scripts/test_worktree.py`); `bd`
  1.0.5 for the molecule pour; `git` ≥ 2.5 for worktrees.
- **Repo source ≠ installed skill (critical):** this plan edits `<git-root>/skills/yf-plan/`, but
  `/yf-plan` runs the installed `~/.claude/skills/yf-plan/` copy (skills are `rust-embed`-baked into the
  `yf` binary at build; deployed by `yf skills install`). Repo edits do **not** hot-swap the running
  skill, so plan-021 executes normally (worktree mode fine). Validate the change against a **scratch
  project** using the *modified* repo skill (Epic 0: Tier-1 `test_worktree.py` from the repo tree +
  Tier-2 rebuild/dev-link scratch smoke) — the installed copy tests the *old* skill.
- **Side effects / promotion boundary:** running `yf skills install` promotes the modified skill into
  `~/.claude/skills/` and changes how *all* future planning behaves — **do not promote until the Epic-0
  scratch smoke passes.**

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
