# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`beads-skills` is the development repo for a suite of beads-backed Claude Code skills
(the `yf-*` family: yf-plan, yf-research, yf-beads-*, yf-drift-check, yf-change-validation,
etc.) plus the `yf` Rust CLI kernel (`yf/`, a cargo workspace) that embeds the `skills/`
tree and provides preflight/doctor/install. Python skill helpers live under
`skills/<skill>/scripts/*.py` (PEP-723, run via `uv run`); shared helpers are vendored from
repo-root `_shared/` via `_shared/sync.py` (plan-014). Task tracking is beads (`bd`, local
Dolt DB under `.beads/`); upstream issue tracking is GitHub (`dixson3/yoshiko-flow`, coarse
one-issue-per-plan). The repo dogfoods its own approved `CHANGE-VALIDATION.md` (plan-015):
yf-plan's merged-tree validation runs `cargo fmt/clippy/test` + the per-skill pytest suites
+ `_shared/sync.py --check`. CI (`.github/workflows/ci.yml`) runs the cargo suite.

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
- Plan directory: `docs/plans/plan-016-james-dixson-041b2f`

## Operator identity

- Git user: `james-dixson` (James Dixson, GitHub `dixson3`).
- Role/authority: repo owner and sole maintainer; authorizes pushes, upstream issue
  writes, and manifest approvals for this repo. Org/email per `~/.claude/CLAUDE.md`
  (Yoshiko Studios LLC / `dixson3@gmail.com` on this host, or Beyond Identity on the
  `byid-mba-dixson3` machine).

## Runtime assumptions

- **OS/shell:** macOS (Darwin, Apple Silicon), zsh. Commands use non-interactive flags.
- **Toolchain:** `cargo`/rustc for the `yf` workspace; `uv` for all Python (PEP-723, no
  global installs); `bd` >= 1.0.5 with a local-only Dolt DB; `gh` authenticated to
  `dixson3/yoshiko-flow`.
- **Network:** needed only for `gh` upstream issue ops and `git push`/`bd dolt push` at
  land-the-plane; the build/test/sweep work is fully offline.
- **Side effects / authority:** EXECUTE runs in a git worktree (`.worktrees/<plan-id>`);
  merge-back + push are operator-authorized (conservative git authority). Epic B mutates
  `yf/src/` (Rust) and adds confirm-gated/auto git-hygiene ops to `yf doctor --repair`;
  the destructive ones (`git rm`, remote removal) are guarded (`--cached`, content-guard,
  `--remove-remote` opt-in). The plan touches yf-plan's *own* `plan_manager.py` (json-get
  consolidation) — the installed `~/.claude` copy lags the repo copy, so orchestration vs
  repo-source behavior can differ (observed: the installed audit copy still carries #36).

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
