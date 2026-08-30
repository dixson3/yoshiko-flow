---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` is a Rust binary (`yf`) that embeds and deploys a tree of agent **skills** to
multiple AI coding harnesses (claude-code, codex, opencode, pi, agents). The skills themselves are
markdown + PEP 723 Python under `skills/<name>/`; `yf` carries them via `rust-embed` and installs
them per harness.

The repository is **both the source and a consumer of its own skills** — this plan is authored by
`yf-plan`, a skill living in the tree it edits. Three artifacts move independently: repo source,
the binary-embedded tree, and the session-installed copy. Editing `skills/` changes none of the
running session's behavior until a rebuild and redeploy.

Stack: Rust (`yf/`, cargo), Python 3.11+ run via `uv` (PEP 723 inline metadata, no project venv),
Pelican + a custom `skill_pages.py` plugin for the website under `web/`, and `bd` (beads, Dolt-backed)
for all task tracking.

Non-obvious setup:

- **`.beads/` is untracked** (`.git/info/exclude`), so it exists only in the primary checkout and
  is never materialised in a git worktree. `dolt.local-only = true` — never `bd dolt push`.
- Validation is recipe-driven via `CHANGE-VALIDATION.md` (FAST on edit, FULL once per land).
- Cross-artifact agreement is declared in `DRIFT-CHECK.md` — 52 edges, **enforced by nothing
  runnable**, which is the defect this plan exists to close.


## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-30 -->

- `bd`: bd version 1.2.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.6 (7938ca5d5 2026-08-25 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.98.0 (2026-08-20)
- `glab`: glab 1.115.0 (c3612c8de)
- `claude`: 2.1.247 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-061-james-dixson-6d8c97`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson (`james@yoshikostudios.com`), sole maintainer and operator.
- Authority scope: full — owns merges to `main`, upstream issue filing on `dixson3/yoshiko-flow`,
  and release/deploy decisions. Outward-facing writes (push, `gh issue create`/`close`) remain
  operator-authorized per GR-PLAN-003 even so.

## Runtime assumptions

| Assumption | Detail |
| :-- | :-- |
| OS / shell | macOS (Darwin 25.5.0), `zsh`. Commands must not assume GNU coreutils — `grep -E`/`sed` are BSD variants |
| Python | invoked **only** through `uv run` with PEP 723 inline metadata; there is no project venv to activate |
| `jq` | **required** by the Epic-1 capability gate's Test. Verify presence before execution; the gate is unevaluable without it |
| Network | needed for `gh` (upstream issues) and `uv`'s first dependency resolution. Neither is needed by the checker itself once cached |
| Credentials | `gh` owns its own credential store. **No token is ever passed inline or written to config** |
| Side effects | this plan writes only to `skills/*/README.md`, `SPEC.md`, `scripts/checks/`, `CHANGE-VALIDATION.md`, `DRIFT-CHECK.md` §5 and the project-root `README.md`. It writes **nothing** under `web/` or to the OKF bundle corpus — those are #317 and #316 |
| Execution model | a git worktree at `.worktrees/<plan-id>` on `<plan-id>-execute`; plan-folder bookkeeping and every `bd` call stay **primary-side** |
| Deploy | `yf self install` must **not** run mid-execution. It is the last step of landing, from `main`, after the FULL tier passes on the merged tree |

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
