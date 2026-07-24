---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (repo `dixson3/yoshiko-flow`, working dir `beads-skills`) is a family of
portable, cross-harness AI-agent skills plus a single compiled Rust CLI, `yf`, that installs,
upgrades, verifies, and preflights those skills. The skills live under `skills/yf-*/` (18 of
them, each with `SKILL.md` + `README.md` + `SPEC.md`); the `yf` binary is under `yf/` (Rust);
shared Python helpers under `_shared/`. The public documentation **site** this plan touches is a
**Pelican** static site under `web/`: content in `web/content/pages/`, the theme in
`web/themes/yoshikoflow/`, and two build-time plugins in `web/plugins/`
(`home_content.py`, `skill_pages.py`). The site is built with
`uv run --with-requirements web/requirements.txt pelican web/content -s web/pelicanconf.py`.
Task tracking is `bd` (beads, local-only Dolt under `.beads/`). The repo is the reference
instance for the `yf-drift-check` and `yf-change-validation` engines and carries an approved
root `DRIFT-CHECK.md` + `CHANGE-VALIDATION.md`.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-24 -->

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
- Plan directory: `docs/plans/plan-036-james-dixson-461061`

## Operator identity

- Git user: `james-dixson` (James Dixson, GitHub `dixson3`).
- Contact / org: `james@yoshikostudios.com` · Yoshiko Studios LLC (repo owner + maintainer).
- Authority scope: repo owner — authorized to author docs, edit the web plugin, extend the
  drift manifest, merge to `main`, push, and file/close upstream issues on this repo.

## Runtime assumptions

- **OS/shell:** macOS (Darwin, Apple Silicon), `zsh`. Build and lint run locally.
- **Toolchain:** `uv`, `pelican` (4.11.0, via `web/requirements.txt`), `bd` ≥ 1.1.0, `git`,
  `gh` (authenticated), plus `d2`/`naba` — all verified present (Tool inventory above).
- **Network:** not required for this plan's work (no live web research); `gh`/`git push` to
  GitHub only at land-the-plane, operator-authorized.
- **Side effects:** docs/plugin/manifest edits under `web/` and root `DRIFT-CHECK.md`; a
  Pelican build to a temp dir for the exit gate; no changes to any skill's behavior or the `yf`
  binary. Local-only beads (`.beads/` gitignored, never pushed). Safe to run on this machine
  as-is; a cold reader on another machine needs the same toolchain + a clone with the skills
  tree intact (the plugin reads `skills/*/SKILL.md` at build time).

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
