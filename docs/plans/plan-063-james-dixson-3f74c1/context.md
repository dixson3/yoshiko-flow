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
harnesses, plus the `yf` Rust binary that embeds and deploys them. It is **both the source and a
consumer of its own skills**: three artifacts move independently (repo source, binary-embedded
tree, session-installed skill), so an edit under `skills/` changes nothing about the running
session until a rebuild and redeploy.

This plan edits `skills/yf-plan/scripts/plan_manager.py` — **the same script the landing runs
from** — plus `skills/yf-plan/spec/landing.md`, `test_land_apply.py`, `land_rehearsal.py` and a
new `scripts/checks/` entry. Task tracking is `bd` (beads), local-only; `.beads/` is gitignored
and never co-committed. The repo is SPEC-first: the `REQ-*` requirement lands ahead of the code.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-09-03 -->

- `bd`: bd version 1.2.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.9 (9f9286029 2026-09-01 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.100.0 (2026-09-03)
- `glab`: glab 1.116.0 (e8436ca8a)
- `claude`: 2.1.259 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-063-james-dixson-3f74c1`

## Operator identity

- Git user: `james-dixson`
- Operator: James Dixson (`james@yoshikostudios.com`), sole maintainer of `dixson3/yoshiko-flow`
- Authority scope: full — merges to `main`, upstream issue writes and the `yf self install`
  redeploy are the operator's to authorize. An executing agent authorizes none of them:
  `land --apply` refuses without a controlling terminal, and that refusal is **detection rather
  than prevention** (#293, #304).

## Runtime assumptions

- **OS/shell:** macOS, `zsh`. BSD `grep`/`sed`, not GNU.
- **Python:** invoked only as `uv run <script>` so PEP 723 inline deps resolve. **The
  `uv run --with pytest python3 -m pytest <file>` form exits 2 on collection**
  (`ModuleNotFoundError: click`) because `--with` never reads the PEP 723 block — measured in
  plan-062. `CHANGE-VALIDATION.md:137` uses the correct form.
- **`jq` is required** by several criteria clauses and by both gate tests.
- **Network:** `gh` must be authenticated for Issue 6.1's filings. Every test runs offline —
  `LandingContext(runner=...)` injects a fake spawner for L0–L7 and L16–L19. **L8–L15 use bare
  `subprocess.run` and are NOT injectable**, which is why the rehearsal replaces whole steps.
- **Side effects:** sandbox spikes ran in `$(mktemp -d)` and left no residue. **No test may run
  `land --apply` against this repository.**
- **Mid-execution deploy is FORBIDDEN.** `plan_manager.py` is re-invoked per call, so a
  `yf self install` during execution would run new scripts against prose loaded at invocation.
- **This plan modifies the script that lands it.** That is why `execute.worktree: false` is
  mandatory: under worktree mode the primary checkout stays on `main` carrying the **unfixed
  L18**, and `land --apply` would crash at the prune exactly as plan-062's did. In-place mode
  alone creates no execute branch (#331), so Issue 0.7 cuts it by hand.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
