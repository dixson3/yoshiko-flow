---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (aka `beads-skills`) is the source repo for a suite of beads-backed Claude Code
skills (`yf-*`) plus the `yf` Rust CLI kernel. Two implementation surfaces matter for this plan:

- **Rust kernel** — `yf/` (Cargo crate). `yf preflight` / `yf doctor` and the beads-init
  verify/repair engine live in `yf/src/beads_init.rs`. Build/test with `cargo` in `yf/`.
- **Skills** — `skills/<name>/` each with `SKILL.md`, `SPEC.md`, `protocols/*.md` (always-loaded
  rules installed to `~/.<surface>/rules/` by `install.sh`), and `scripts/*.py` (PEP-723, run via
  `uv run`). `beads_init.py` is a retired stub — repair moved into the Rust kernel (plan-010).

The repo dog-foods its own skills: its `.beads/` uses the embedded-dolt layout that is the subject
of this fix, and it was itself the repo that hit issue #56 on 2026-06-30. SPEC-first is a project
mandate (see AGENTS.md): SPEC edits land before implementation.

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
- Plan directory: `docs/plans/plan-020-james-dixson-81785d`

## Operator identity

- Git user: `james-dixson` (James Dixson, GitHub `dixson3`).
- Contact / attribution: `james@yoshikostudios.com`; Yoshiko Studios LLC. MIT-license attribution
  convention applies to new modules.
- Authority scope: repo owner — full authority over `dixson3/yoshiko-flow`, including SPEC edits,
  engine changes, and the upstream GitHub issue tracker. Push remains operator-authorized
  (conservative git authority) at land-the-plane.

## Runtime assumptions

- **OS/shell:** macOS (Darwin, Apple Silicon), zsh. Execution is local; no network access required
  for the fix itself (build + unit/integration tests run offline).
- **Toolchain:** `cargo`/rustc for the Rust kernel; `bd` 1.0.5 and standalone `dolt` 2.1.10 on PATH
  for the idempotency integration test (the test self-guards / skips when either is absent — e.g.
  in CI without them). `uv` for the PEP-723 skill scripts.
- **Side effects:** the engine change touches beads-repo **repair** of live Dolt data — the
  data-preserving invariant (`add -A && commit`, never `reset --hard`) is safety-critical. Tests
  run against throwaway `bd init` repos under a tempdir, never a real project's `.beads/`.
- **Credentials:** `gh` auth for upstream #56 reconciliation at land-the-plane only.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
