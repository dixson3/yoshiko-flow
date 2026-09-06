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
that installs them across five harnesses. It is **both the source and a consumer of its own
skills**: `skills/` in the working tree, the `rust-embed` tree baked into the binary, and the
session-installed copy are three separate artifacts that move independently.

This plan touches a fourth surface: **`web/`, a Pelican static site** published to
yoshikoflow.sh via S3 + CloudFront (`.github/workflows/web-deploy.yml`, chained off a successful
Release). Its non-obvious setup:

- `web/plugins/skill_pages.py` generates every per-skill page's title, "At a glance" block,
  `/skills/` index and `SKILL_NAV` from `skills/*/SKILL.md` frontmatter. **Only the prose body
  below the `<hr>` is authored.** The plugin is **fail-closed**: a skill with no authored page
  raises and halts the build.
- `pelicanconf.py` sets **no `PAGE_PATHS`**, so Pelican's default `["pages"]` silently excludes
  any new content directory — a page authored elsewhere builds green and emits nothing.
- `web/.venv` is **untracked** and exists only in the primary checkout, so it is absent from a
  `.worktrees/<plan-id>` execute worktree.
- `publishconf.py` requires `PUBLISH_URL`; `web/.envrc` is direnv-blocked on this host.
- Six `.d2` diagrams under `web/content/images/` have committed `.png` siblings. **No render
  target exists** in `web/Makefile`, CI, or `CHANGE-VALIDATION.md`; the only engine is
  `skills/yf-diagram-authoring/scripts/render.py`.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-09-05 -->

- `bd`: bd version 1.2.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.9 (9f9286029 2026-09-01 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.100.0 (2026-09-03)
- `glab`: glab 1.116.0 (e8436ca8a)
- `claude`: 2.1.259 (Claude Code)
- `d2`: v0.8.2 — **the D7 pin.** Every diagram in this plan is rendered with this exact
  version; the pin is load-bearing because renders are byte-identical *within* a version and
  differ across versions (measured).
- `pelican`: 4.11.0 (`web/requirements.txt`), with `pelican-sitemap` 1.2.2
- `zsh`: 5.9 (the shell agent tool calls run under)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-066-james-dixson-e7fadb`

## Operator identity

- Git user: `james-dixson` (james@yoshikostudios.com)
- Role: repository owner and sole maintainer of `dixson3/yoshiko-flow`.
- Authority scope: full — may authorize merges, pushes, and outward-facing writes
  (`gh issue create` / `comment` / `close`) against this repository.
- **The executing agent holds none of that authority.** Every outward-facing or irreversible
  write halts for explicit operator authorization, and a capability gate is never resolved on
  the operator's behalf however green its evidence.

## Runtime assumptions

- **OS / shell:** macOS (Darwin 25.5.0), **zsh 5.9**. zsh does **not** word-split unquoted
  parameter expansions, array indexing is 1-based, and `${PIPESTATUS[@]}` is a bash-ism that
  expands to **nothing** — the zsh spelling is `${pipestatus[@]}`. Any loop that writes must read
  its writes back; a green exit proves nothing.
- **Execution address space:** yf-plan may run in `.worktrees/<plan-id>`. **`web/.venv` does not
  exist there** — a check hardcoding it exits 127. Use `uv run --with-requirements
  web/requirements.txt`, or bootstrap the venv explicitly.
- **Network:** required — `gh` for upstream reads/writes, `uv` for dependency resolution. The
  build itself is offline once dependencies resolve.
- **Credentials:** `gh` holds its own credential store; no token is ever written to config or
  passed inline.
- **Side-effect permissions:** the plan writes freely under `web/`, `scripts/checks/`,
  `DRIFT-CHECK.md`, `CHANGE-VALIDATION.md`, `README.md`, `AGENTS.md`, `skills/yf-drift-check/spec/`
  and its own bundle. It performs **no deploy** (D4) and no `bd dolt push` (`dolt.local-only` is
  true — propose `git push` alone).
- **CI does not validate this work.** `grep change_validation .github/workflows/*` returns
  nothing and `ci.yml` has no web job, so whatever verification this plan writes is the only
  verification — until Issue 2.8 lands the CI job.
- **A `CHANGE-VALIDATION.md` row reading `docs/plans/<in-flight-plan>/` is structurally
  unsatisfiable from an execute worktree.** Issue 0.5's rows are therefore added at land only.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
