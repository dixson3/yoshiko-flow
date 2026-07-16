# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (aka `beads-skills`) is the monorepo of Beads-backed Claude Code skills
(the `yf-*` family) plus the `yf` Rust CLI. Layout: `skills/<skill>/` holds each skill's
`SKILL.md`, `SPEC.md`, `agents/`, and Python helpers under `scripts/` (run via `uv run`,
PEP-723 inline deps); `yf/` is the Rust kernel; `_shared/` is vendored Python shared code;
`website/` is the docs site; `docs/plans/` holds yf-plan plan folders. This plan touches two
skills: `skills/yf-research` (the `credibility_scorer.py` scoring helper) and `skills/yf-plan`
(the `plan_manager.py` lifecycle script + SKILL.md). Repo-wide validation is driven by the
approved root `CHANGE-VALIDATION.md` (per-skill pytest recipes). SPEC-first is mandatory
(AGENTS.md): the `REQ-*` edit lands before the code + tagged test; the living amendment log is
a single per-plan entry in the **root `SPEC.md`**.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-15 -->

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
- Plan directory: `docs/plans/plan-028-james-dixson-a9738b`

## Operator identity

- Git user: `james-dixson` (James Dixson, GitHub `dixson3`)
- Contact: james@yoshikostudios.com
- Authority scope: repo owner/maintainer — full authority to approve, execute, merge, and
  authorize upstream pushes on `dixson3/yoshiko-flow`.

## Runtime assumptions

- macOS (darwin, Apple Silicon), zsh shell. `uv` available for all Python helper/test
  invocation (`uv run <file>`, PEP-723 inline deps — no ambient venv needed).
- No network access required to implement or validate: all changes are to local Python and
  markdown; tests are offline unit tests. `credibility_scorer.py` scoring is pure/local.
- `gh` (authenticated) is needed only at RECONCILE to update/close #87 and #86 and at INTAKE
  to file the coarse tracking issue — not during code implementation.
- Side effects are local by default: yf-plan auto-commits the plan folder locally on a plan
  branch (never `main`, never a push). The upstream `git push` / `bd dolt push` stays
  conservative and authorized-only.
- `bd` is local-only in this repo (`.beads/` gitignored; gh-issue interchange, no Dolt
  remote). Coarse upstream tracking: one tracking issue per plan.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
