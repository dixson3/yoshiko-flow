---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` is the source repo for beads-backed skills for Claude Code and other harnesses, plus
the `yf` Rust binary that embeds and deploys them. Python skill scripts run via `uv` with PEP-723
inline deps; a Rust workspace under `yf/` (`rust-embed` bakes `skills/` into release builds); `bd`
(beads 1.1.2, Dolt, `dolt.local-only = true`) for task tracking; `gh` for upstream issues.

**The non-obvious setup:** this repo is **both the source and a consumer** of its own skills, and
they are three artifacts that move independently. See AGENTS.md "Three artifacts, not one".

**Specific to this plan:** the document-conformance engine lives in `_shared/` (`doc_lint.py`,
`plan_extract.py`, `pour_fidelity.py`, 17 `document_types/*.toml`), shipped by plan-047 and
plan-048. **Measured (EXP-004): `_shared/` is NOT vendored into any skill and `yf` embeds only
`../skills`** — so the engine exists in no deployed vault, which is why Issue 4.1 exists.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-19 -->

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
- Plan directory: `docs/plans/plan-049-james-dixson-725bc0`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson <james@yoshikostudios.com>, sole maintainer and operator.
- Authority scope: full — approves plans, authorizes outward-facing writes and corpus writes,
  authorizes deploys. Every gate in this plan routes here.

## Runtime assumptions

- **OS / shell:** macOS (darwin 25.5.0), `zsh`. **BSD `sed`/`grep`, not GNU.** zsh arrays are
  1-indexed — this produced a real defect in plan-047.
- **Network:** required for `gh` only, in Epic 6. Epics 0–5 are local.
- **Side-effect permissions this plan assumes:**
  - Writes under `_shared/`, `skills/`, `tests/`, `CHANGE-VALIDATION.md`, `DRIFT-CHECK.md`.
  - **A corpus write of exactly TWO documents** (Issue 3.3: plan-008's gate-block relocation and
    plan-015's de-bold), gated by the corpus-write gate, run on a **clean git worktree** so a
    guard FAIL means `git checkout -- docs/plans`. The 65 adjudications are **descoped** (D-2).
  - **Outward-facing `gh` writes**, gated. The grant must be generated **from the Upstream Issues
    table**, not a draft list — plan-048's hand-typed grant omitted a required close.
- **Never `bd dolt push`** — `dolt.local-only = true`.
- **Safe to run as-is elsewhere?** **No.** Figures are measured against *this* corpus (49 plan
  dirs, 81 residue, 1340 report-only, 89 inline declarations). **`Incubator/` does not exist here**,
  so those globs are inert though correct for other vaults.

## Scope boundary

This plan is the successor to plan-048's D-13 split. It carries the migration (#140, **redirected**
per D-2 at the 89 inline declarations rather than the 65 adjudications) and the enforcement binding
(#149). **Descoped:** the 65 hand-adjudications, and **eight** of the nine "free recoveries" that are not
gate blocks — the ninth, plan-015's de-bold, is IN scope and is one of the two documents this plan
writes.
