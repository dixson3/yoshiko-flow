---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

Describe the project this plan belongs to: what it does, what stack it uses,
any non-obvious setup. A cold reader should not need to infer this from code.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-10-15 -->

- `bd`: bd version 1.3.1 (Homebrew)
- `git`: git version 2.54.0 (Apple Git-157)
- `uv`: uv 0.12.22 (70fe1196a 2026-10-01 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.102.0 (2026-09-30)
- `glab`: glab 1.120.0 (78790114c)
- `claude`: 2.1.288 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-073-james-dixson-cc76de`

## Operator identity

- Git user: `james-dixson`
- Attribution: fill in role, contact, and authority scope before intake.

## Runtime assumptions

List the assumptions this plan makes about the environment it will execute in
(OS, shell, network access, credentials, side-effect permissions). A cold
reader on a different machine should be able to decide whether the plan is
safe to run as-is.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
