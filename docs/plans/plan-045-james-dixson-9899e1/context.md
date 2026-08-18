---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**yoshiko-flow** ships beads-backed agent skills (`yf-plan`, `yf-research`, `yf-herdr`,
`yf-beads-*`, …) plus **`yf`**, a Rust CLI that installs and maintains them across five agent
harnesses. This plan modifies **`yf-plan` and `yf-herdr` themselves** — the skills that produce and
delegate plans, including this one.

Three properties dominate:

1. **Reflexivity.** The repo is both source and consumer of its own skills. A running session loads
   the **installed** copy (`~/.claude/skills/`), which changes only on an explicit `yf self
   install`; editing `skills/` changes nothing until then. See the plan's Reflexivity note.
2. **SPEC-first is mechanically enforced.** `DRIFT-CHECK.md` §7 marks `spec` / `per-skill-spec` as
   **fixed authority**, so a SKILL.md-first change FAILs rather than updating the spec.
3. **The validation surface is uneven.** `skills/*/SPEC.md` and `skills/*/spec/*.md` match **no**
   CHANGE-VALIDATION §3 glob, and `yf-herdr` ships no scripts and no tests at all — Epic 1 exists
   to close that before the implementation epics land.

Stack: Rust (cargo workspace, crate `yf/`) + Python skill helpers via `uv` with PEP-723 inline deps.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-17 -->

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
- Plan directory: `docs/plans/plan-045-james-dixson-9899e1`

## Operator identity

- Git user: `james-dixson` (james@yoshikostudios.com)
- Role: sole maintainer and operator; also the primary end user of the skills this plan changes.
- Authority scope: full — may approve plans, authorize pushes to `main`, and file/close issues on
  `dixson3/yoshiko-flow`. **No second approver exists**, which is precisely why this plan leans on
  mechanical gates (the five-class stop set, `max_review_cycles`, `yf_attempts`, D-8's postcondition
  pairing) rather than human review for its correctness guarantees — and why removing stops without
  adding verification would be net-negative.

## Runtime assumptions

- **OS/shell:** macOS (Darwin 25.5.0), zsh. `direnv` is active and **resets cwd between tool
  calls** — the cause of the exp-007 wrong-address-space incident. Any issue that commits must
  verify its cwd first.
- **`herdr` is required for Epic 5 only.** herdr 0.8.0, and the session must be herdr-managed
  (`HERDR_ENV=1`). The "herdr probe surface" gate tests this; on failure Epic 5 is tombstoned and
  the rest of the plan proceeds.
- **`bd` >= 1.1.0** (measured 1.1.2), Dolt **server mode** — so `.beads/dolt` and
  `.beads/dolt/<db>` both contain `.dolt/`. `.beads/` is **git-excluded**, so a fresh clone has no
  bead database: any trial must run in place, never in a clone.
- **`dolt.local-only = true`.** Never `bd dolt push`.
- **Network:** required only for `gh` (upstream reconcile) and `cargo` fetches. Epics 2–4 are
  otherwise offline.
- **Side-effect permissions.** This plan mutates `skills/yf-plan/**`, `skills/yf-herdr/**`,
  `CHANGE-VALIDATION.md`, `DRIFT-CHECK.md`, and — in Issue 4.5 — writes real retrospective entries
  into this bundle. **It does not mutate any other plan bundle.**
- **Sandbox discipline:** every harness test sets `HOME` to a tempdir and clears `CI`. A leak would
  apply `permissions.defaultMode: "bypassPermissions"` to the operator's real config.
- **Binary discipline:** the workspace-root `target/debug/yf`, never a `PATH` `yf`, and **no
  `yf self install` mid-execution** (see Reflexivity).

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
