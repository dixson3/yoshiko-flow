---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` is a repository of beads-backed skills for Claude Code and four other agent
harnesses, plus the `yf` Rust binary that embeds and deploys them. It is **both the source and
a consumer of its own skills**, so a change under `skills/` does not affect the running session
until the binary is rebuilt and redeployed — three artifacts that move independently (repo
source, binary-embedded tree, session-installed skill).

This plan edits `skills/yf-plan/scripts/plan_manager.py` (a ~10k-line Python CLI invoked via
`uv run` with PEP 723 inline deps) and `skills/yf-plan/spec/landing.md`. Task tracking is `bd`
(beads), local-only — `.beads/` is gitignored and never co-committed. The repo is SPEC-first:
the `REQ-*` requirement lands ahead of the code that implements it.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-09-03 -->

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
- Plan directory: `docs/plans/plan-062-james-dixson-c3e98f`

## Operator identity

- Git user: `james-dixson`
- Operator: James Dixson (`james@yoshikostudios.com`), sole maintainer of `dixson3/yoshiko-flow`
- Authority scope: full — merges to `main`, upstream issue writes, and the `yf self install`
  redeploy are all the operator's to authorize. An executing agent authorizes **none** of them:
  `land --apply` refuses without a controlling terminal, and that refusal is detection rather
  than prevention (see #293, #304).

## Runtime assumptions

- **OS/shell:** macOS (darwin 25.5.0), `zsh`. BSD `grep`/`sed`, not GNU — the criteria clauses
  avoid GNU-only flags.
- **Python:** invoked only as `uv run <script>`; scripts carry PEP 723 inline deps.
  **`uv run <script>` is the ONLY correct form for `test_land_apply.py`** — it reads the file's
  PEP 723 block, which pulls in `click`. The `uv run --with pytest python3 -m pytest <file>`
  form **exits 2 on collection** with `ModuleNotFoundError: click`, because `--with pytest`
  builds an environment containing only pytest and never reads PEP 723. Measured in red-team
  pass 1 (C1); an earlier draft of this file asserted the inverse, which is where the plan's
  broken invocations came from. `CHANGE-VALIDATION.md:137` already uses the correct form.
- **`jq` is required** by several criteria clauses and by the extract/audit reads.
- **Network:** `gh` must be authenticated for Issue 5.1's upstream filings. Every test in this
  plan runs offline — `LandingContext(runner=...)` injects a fake process spawner, so no test
  touches the network or a real remote.
- **Side effects:** the sandbox spikes in `findings/` were run in `$(mktemp -d)` and left no
  residue. No test in this plan may run `land --apply` against this repository.
- **Mid-execution deploy is FORBIDDEN.** `plan_manager.py` is re-invoked per call, so a
  `yf skills install` / `yf self install` during execution would run new scripts against prose
  loaded at invocation. The redeploy is the last step of landing, from a clean `main` in sync
  with `origin`.
- **This plan modifies the very script that executes it.** That is safe by design: the
  `SKILL_DIR` resolver reaches the *installed* copy, and the repo's `skills/` directory matches
  none of its search roots. Issue 5.5 nonetheless routes this plan's own landing through the newly-wired
  `--apply` (the OPERATOR runs it, per SKILL.md §6.0; Issue 5.4 confirms the checkout carries the fix), which is the first execution to depend on the change being correct.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
