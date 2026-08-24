---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (working dir `beads-skills`) is **both the source and a consumer of its own
skills**. It ships a family of beads-backed Claude Code skills (`yf-plan`, `yf-research`,
`yf-herdr`, `yf-change-validation`, `yf-drift-check`, `yf-beads-*`) plus `yf`, a Rust binary that
embeds the skill tree via `rust-embed` and deploys it to five harnesses.

**Stack:** Python 3.14 driven by `uv` (PEP-723 inline deps, no project venv) for every skill
script; Rust (cargo) for the `yf` kernel; markdown as the artifact format throughout. Task
tracking is `bd` (beads) 1.1.2 on embedded Dolt, `dolt.local-only = true`. Upstream issue
tracking is GitHub (`dixson3/yoshiko-flow`) via `gh`, at **coarse** granularity — one tracker per
plan.

**The three-artifact rule governs this plan.** Editing `skills/` does not change the skill the
session is running: the repo's `skills/` matches none of the `SKILL_DIR` resolver's six roots, so
a running session always resolves the **installed** copy. That makes it safe for this plan to
rework `yf-plan` while executing under it — the one hard constraint is **no `yf skills install` /
`yf self install` mid-execution**, because `plan_manager.py` is re-invoked per call and a
mid-run deploy would run new scripts against old prose.

**Validation** is `CHANGE-VALIDATION.md` (approved), executed by `change_validation.py` in a FAST
(affected) and FULL (CI ∪ repo-checks) tier. `DRIFT-CHECK.md` declares 51 nodes / 50 edges of
cross-artifact agreement.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-23 -->

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
- Plan directory: `docs/plans/plan-052-james-dixson-fa8056`

## Operator identity

- **Operator:** James Dixson (`james@yoshikostudios.com`), sole maintainer and the repository owner.
- **Role and authority scope:** full authority over this repository — merges to `main`, upstream
  issue creation/closure, and release/deploy of the `yf` binary. There is no second approver, so
  every consent gate in this plan resolves to this one person.
- **What still requires explicit authorization, and is never assumed:** any `git push`; any
  outward-facing `gh` write (issue create / comment / close); `yf self install` (deploy); and any
  destructive local operation. The plan's `upstream-write` gate exists for precisely this reason.
- **Not applicable:** `bd dolt push` — this repo sets `dolt.local-only = true`, so there is no
  replication target and the command must never be proposed.

## Runtime assumptions

Recorded because a cold reader in another repo cannot infer them, and several are load-bearing
for this plan's own controls.

- **`bd` is 1.1.2.** Measured limits this plan depends on (EXP-001, EXP-005): gate `--type` is
  **unvalidated free text**; `bd gate resolve` records **no resolver identity** (`--actor` and
  `BEADS_ACTOR` are both accepted and discarded); the `bead` gate type is non-functional
  (*"multi-rig routing removed"*); `bd dep add --no-cycle-check` still refuses on the single-edge
  path; formula **aspects exist** and weave at cook time over formula-declared steps only;
  `bd mol burn` exits 0 on cancellation (#202), so a scripted burn must pass `--force` and read
  the output.
- **`bd list --json` omits `started_at`;** `bd export --all` carries it. `metadata` is only ever
  `object` or `null`, so `.metadata.plan` in `jq` cannot type-error.
- **macOS with bash 3.2** — no `mapfile`, no `declare -A`. Any shipped shell must be 3.2-clean.
- **`_shared/` is canonical**; `skills/*/scripts/` holds byte-identical vendored copies enforced by
  `_shared/sync.py --check` in the FAST tier. Edit `_shared/`, never the copy alone.
- **Execution is serial.** A single coordinator runs beads one at a time — measured mean
  concurrency 1.10–1.53, with 84% of apparent interval overlap being batch-close bookkeeping
  (EXP-006). No step in this plan may assume parallel execution.
- **`uv run` inside a worktree** needs `env -u VIRTUAL_ENV`; never use uv's `--active` suggestion
  there, which targets the primary venv.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
