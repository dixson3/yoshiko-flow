---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (a.k.a. `beads-skills`) is a suite of beads-backed Claude Code skills plus a
Rust CLI, `yf`, that installs, upgrades, verifies, and preflights those skills. The skills
(`yf-plan`, `yf-research`, `yf-beads-*`, etc.) live under `skills/`; the `yf` binary lives in
`yf/` (a Cargo workspace) and **embeds** the skill/rule files at build time (`embed` module,
`protocols/manifest.json` per skill). This plan touches the `yf` crate only —
`yf/src/preflight.rs` (the shared preflight kernel every beads skill routes through) and
`yf/src/cmd/self_cmd/` (the `yf self` install/update surface added in plan-018).

Non-obvious setup:
- Rust toolchain builds `yf`; `cargo test --workspace` + a `uv` pytest row are the approved
  `CHANGE-VALIDATION.md` full tier (dogfooded validation gate).
- Skills/rules are installed to scope+surface dirs (`~/.claude/rules`, `~/.agents/rules`, or
  project-scoped equivalents) by `install.sh` / `yf skills install`; preflight hash-checks the
  installed companion rule against the embedded manifest.
- SPEC-first is a repo rule (AGENTS.md): the `SPEC.md` `REQ-*` requirement lands ahead of code.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-02 -->

- `bd`: bd version 1.0.5 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.26 (396ef7ce4 2026-06-30 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.95.0 (2026-06-17)
- `glab`: glab 1.106.0 (fc1869c7)
- `claude`: 2.1.198 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-019-james-dixson-eea8e7`

## Operator identity

- Git user: `james-dixson`
- Contact: james@yoshikostudios.com
- Role / authority: repo owner and maintainer (`dixson3/yoshiko-flow`); full authority over
  design, intake, merge, and the operator-authorized upstream push (yf-plan Phase 6.2).

## Runtime assumptions

- **OS/shell:** macOS (darwin, aarch64) + zsh at authoring time; the `yf` code is
  cross-platform (Linux + macOS targets per REQ-YF-SELF-002/003) and must not regress on
  Linux. No OS-specific behavior is added by this plan.
- **Build/test:** a Rust toolchain and `uv` are present; validation is `cargo test --workspace`
  and the `uv` pytest row (the approved CHANGE-VALIDATION full tier). Tests must be
  **hermetic** — the new offer path is explicitly designed to require **no network** (cache-only)
  and no `current_exe`/`CI` dependency (red-team C2), so it runs green in CI.
- **Network:** none required by the plan's code paths at runtime; the existing `nag.rs` network
  fetch (`yf version`/`doctor`) is untouched.
- **Side effects:** preflight's only sanctioned mutation remains the gitignore scaffold plus the
  new `preflight.json` version-stamp write — no new external side effects; the offer is
  report-only (an `instructions` string).
- **Execution model:** yf-plan Phase 5 runs in an isolated git worktree by default; bead
  tracking and the plan folder stay primary-side. The upstream push (Phase 6.2) is
  operator-authorized, not automatic.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
