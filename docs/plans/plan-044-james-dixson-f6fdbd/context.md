---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**yoshiko-flow** ships a family of beads-backed agent skills (`yf-plan`, `yf-research`,
`yf-beads-*`, `yf-okf`, …) plus **`yf`**, a Rust CLI that installs and maintains them across five
agent harnesses (claude-code, codex, opencode, pi, and a bare `agents` surface).

Two non-obvious properties dominate this plan:

1. **The repo is both source and consumer of its own skills.** Editing `skills/` changes nothing
   about the `yf` you are running until you rebuild and redeploy — they are separate artifacts.
   Skills are `rust-embed`-baked into the binary at compile time in **release**; a **debug** build
   reads `skills/` from disk at runtime. So `./target/debug/yf` is always current and
   `yf` on `PATH` deploys whatever *its* binary embeds. A bare `yf skills install` from `PATH` can
   quietly overwrite newer skills with older ones.
2. **Beads runs in Dolt server mode.** `.beads/dolt` is the server data dir (itself a Dolt repo)
   and `.beads/dolt/yoshiko_flow` is the database — so **two `.dolt/` directories always exist**.
   That fact is the root cause of #159 (see exp-002). `.beads/` is git-excluded
   (`.git/info/exclude:9`), so a fresh clone has no bead database at all.

Stack: Rust (cargo workspace, crate `yf/`) + Python skill helpers run via `uv` with PEP-723 inline
deps. SPEC-first is mandatory: the `SPEC.md` requirement lands before the code.

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
- Plan directory: `docs/plans/plan-044-james-dixson-f6fdbd`

## Operator identity

- Git user: `james-dixson` (james@yoshikostudios.com)
- Role: sole maintainer and operator of this repo; also its primary end user.
- Authority scope: full — may approve plans, authorize pushes to `main`, and file/close upstream
  issues on `dixson3/yoshiko-flow`. No second approver exists, which is why this plan leans on
  automated gates (red-team passes, capability gates, the coverage gate) rather than human review
  for its correctness guarantees.

## Runtime assumptions

- **OS/shell:** macOS (Darwin 25.5.0), zsh. Paths like `~/.claude`, `~/.config/opencode`,
  `~/.codex`, `~/.pi/agent` are assumed to be the harness surfaces; a Linux operator should
  re-derive them from `harness_desc::DESCRIPTORS` before running Epic 2.
- **Network:** required. Epic 3 needs `gh` authenticated against `dixson3/yoshiko-flow` for the
  bulk `gh issue list --state all` query. Epics 0–2 are offline apart from `cargo` fetches.
- **Credentials:** `gh` owns its own credential store — no token is passed inline or written to
  config anywhere in this plan.
- **Beads:** `bd` >= 1.1.0 (measured 1.1.2), server mode, `dolt.local-only = true`. **No Dolt
  remote may be configured**; Epic 1 exists partly to enforce that.
- **Side-effect permissions.** This plan mutates real state in three places, all deliberate:
  - the live bead DB (Issue 3.1 rewrites one `external_ref`; Issue 3.6 closes one bead) —
    both reversible;
  - 14 historical plan bundles under `docs/plans/` (Issue 3.7b) — git-tracked, so recovery is
    `git checkout`, and gated behind a human capability gate;
  - the operator's real `~/.claude` skills dir (the Criterion 8 operator check only).
  **Everything else is sandboxed.** All harness tests set `HOME` to a tempdir and clear `CI`; a
  leak would apply `permissions.defaultMode: "bypassPermissions"` to the operator's real config,
  which is the exact harm the plan-042 consent gate exists to prevent.
- **Binary discipline:** use the **workspace-root** `target/debug/yf`, never `yf/target/debug/yf`,
  and never a `PATH` `yf` for deployment steps.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
