---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**yoshiko-flow** (`dixson3/yoshiko-flow`) ships beads-backed agent skills plus the `yf` Rust CLI
that installs them across five harnesses. It is both the source and a consumer of its own skills.

This plan works on **`web/` (a Pelican static site)**, the **`DRIFT-CHECK.md` manifest**, and the
**`skills/*/SKILL.md` corpus**. Non-obvious setup a cold reader needs:

- **Diagrams are `.d2` sources with committed `.png` siblings.** The only render engine is
  `skills/yf-diagram-authoring/scripts/render.py` → `d2 --theme 0 --layout elk`. **This plan
  re-pins that layout to `dagre`** (D6), which invalidates every committed PNG's sha256 at once.
- **`archify` is installed** at `~/.claude/skills/archify` and was evaluated and **rejected** (D1).
  It is not part of this toolchain; see `findings/exp-001-archify-vs-d2.md` before reconsidering.
- `web/plugins/skill_pages.py` generates each skill page's title, "At a glance" block, `/skills/`
  index and `SKILL_NAV` from `SKILL.md` frontmatter. **Only the prose below the `<hr>` is authored.**
  It is fail-closed: a skill with no authored page halts the build.
- `pelicanconf.py` sets **no `PAGE_PATHS`**, so a page authored outside `content/pages/` builds
  green and emits nothing.
- `web/.venv` is **untracked** and absent from an execute worktree.
- **`## Invocation` is not a schema** — absent from 12 of 20 skills, ≥4 incompatible shapes in the
  8 that have it. Normalising it is Epic 0 and a prerequisite for the required-set check.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-09-07 -->

- `bd`: bd version 1.2.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.9 (9f9286029 2026-09-01 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.100.0 (2026-09-03)
- `glab`: glab 1.116.0 (e8436ca8a)
- `claude`: 2.1.259 (Claude Code)
- `d2`: v0.8.2 — currently pinned with `--theme 0 --layout elk`; **this plan proposes `dagre`** (D6)
- `pelican`: 4.11.0 (`web/requirements.txt`)
- `zsh`: 5.9
- `archify`: installed at `~/.claude/skills/archify`, version `2.17.0-dev.1`, channel `development`
  — **evaluated and rejected** (D1); recorded here so its presence is not mistaken for adoption

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-067-james-dixson-de852a`

## Operator identity

- Git user: `james-dixson` (james@yoshikostudios.com)
- Role: repository owner and sole maintainer of `dixson3/yoshiko-flow`.
- Authority scope: full — may authorize merges, pushes, and outward-facing writes.
- **The executing agent holds none of that authority.** This plan carries **three** human-typed
  gates — the dagre re-pin acceptance, the diagram human read, and upstream write authorization —
  and none may be resolved on the operator's behalf however green the evidence. The diagram gate in
  particular exists because plan-066 measured a corrected diagram whose count was right and whose
  membership was wrong.

## Runtime assumptions

- **OS / shell:** macOS (Darwin 25.5.0), **zsh 5.9**. zsh does **not** word-split unquoted
  parameter expansions, arrays are 1-based, and **`${PIPESTATUS[@]}` expands to NOTHING** — the zsh
  spelling is `${pipestatus[@]}`. Any loop that writes must read its writes back.
- **Never pipe pelican.** `| tail` masks its exit 1 and reports a broken build as green.
- **Execution address space:** may run in `.worktrees/<plan-id>`, where `web/.venv` does not exist.
  Use `uv run --with-requirements web/requirements.txt`.
- **Network:** required for `gh`; the build is offline once dependencies resolve.
- **Side-effect permissions:** writes freely under `web/`, `scripts/checks/`, `DRIFT-CHECK.md`,
  `CHANGE-VALIDATION.md`, `skills/*/SKILL.md`, `skills/yf-drift-check/spec/`, and its own bundle.
  No deploy. No `bd dolt push` — `dolt.local-only` is true, so propose `git push` alone.
- **A `CHANGE-VALIDATION.md` row reading `docs/plans/<in-flight-plan>/` is structurally
  unsatisfiable from an execute worktree.** Any such row is added at land only.
- **plan-066 is PARKED in `executing`** on branch `plan-066-james-dixson-e7fadb-execute`, with its
  diagram gate shut and #317 open. Issue 6.4 is the declared handoff that unblocks it. Do not
  abandon or complete plan-066 from this plan.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
