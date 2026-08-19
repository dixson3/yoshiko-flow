---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (working dir historically `beads-skills`) is the source repo for a family of
beads-backed skills for Claude Code and other harnesses, plus the `yf` Rust binary that embeds
and deploys them. Stack: Python skill scripts run via `uv` with PEP-723 inline deps; a Rust
workspace under `yf/` (`rust-embed` bakes the `skills/` tree into release builds); `bd` (beads
1.1.2, Dolt storage, `dolt.local-only = true`) for all task tracking; `gh` for upstream issues
against `dixson3/yoshiko-flow`.

**The non-obvious setup a cold reader must know:** this repo is **both the source and a consumer**
of its own skills, and they are three separate artifacts that move independently — the repo
`skills/` tree, the binary-embedded tree, and the session-installed copy under `~/.claude/skills/`.
The repo's `skills/` directory matches none of the `SKILL_DIR` resolver's six roots, so it is
unreachable at runtime, not merely stale. Editing `skills/` changes nothing about the running
session. See AGENTS.md "Three artifacts, not one".

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-18 -->

- `bd`: bd version 1.1.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.3 (507230998 2026-08-07 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.97.0 (2026-07-31)
- `glab`: glab 1.113.0 (d62881304)
- `claude`: 2.1.228 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-047-james-dixson-dec9ff`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson <james@yoshikostudios.com>, sole maintainer and operator of this
  repository.
- Authority scope: full — may approve plans, authorize outward-facing writes (`gh` issue
  comments against `dixson3/yoshiko-flow`), authorize corpus-wide rewrites of `docs/plans/`, and
  authorize deploys (`yf self install`). Gate approvals in this plan route to this operator.

## Runtime assumptions

- **OS / shell:** macOS (darwin 25.5.0), `zsh`. **BSD `sed`/`grep`, not GNU** — this has caused
  real defects in this repo. `sed -E 's|...(a|b)...|'` fails with "parentheses not balanced" when
  `|` is both the delimiter and an alternation operator; use `#` or `/`.
- **Network:** required for `gh` only (Epic 10). Every other epic is local. No package installs
  beyond `uv`'s PEP-723 resolution, which is cached.
- **Credentials:** `gh` auth is present and owns its own credential store — no token is ever
  passed inline or written to config. No other credential is needed.
- **Side-effect permissions this plan assumes:**
  - Writes under `docs/plans/`, `skills/`, `_shared/`, `CHANGE-VALIDATION.md`.
  - **A corpus-wide rewrite of completed plan bundles**, gated (Issue 8.8b) and constrained to
    hash-neutral transforms (D-2 amended).
  - **Outward-facing `gh` issue comments**, gated (Issue 10.4).
  - A deploy (`yf self install --from-build --build`) at land-the-plane only — **never
    mid-execution**, per AGENTS.md, because `plan_manager.py` is re-invoked per call while
    `SKILL.md` prose is loaded once at invocation, so a mid-run deploy yields new scripts against
    old prose.
- **Never `bd dolt push`** — this repo is `dolt.local-only = true`. Upstream tracking is the
  orthogonal `gh` issue mirror.
- **Safe to run as-is on a different machine?** No. The plan measures and rewrites *this* repo's
  47-plan corpus and cites absolute counts from it; a cold reader on another checkout must
  re-measure before acting.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
