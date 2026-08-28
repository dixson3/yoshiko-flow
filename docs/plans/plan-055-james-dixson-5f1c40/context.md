---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**yoshiko-flow** ships `yf` — a Rust binary that deploys a tree of agent *skills* (markdown
instruction bundles plus Python/bash scripts) into multiple AI coding harnesses, along with a
rules aggregate and per-harness configuration. The repo is **both the source and a consumer of
its own skills**: `skills/<name>/` in the working tree is the source, `rust-embed` bakes that
tree into release builds, and a running session resolves an *installed* copy — three artifacts
that move independently.

Stack: Rust (the `yf` crate under `yf/`, with `SPEC.md` as the source of truth and parity tests
that assert SPEC↔code agreement), plus `uv`-run Python for skill scripts and `bash` for check
scripts. Task tracking is `bd` (beads), never markdown checklists.

Non-obvious setup a cold reader needs:

- **Debug reads `skills/` from disk; release bakes it at compile time.** `./target/debug/yf` is
  always current; a `yf` on `PATH` deploys whatever *its* binary embeds.
- **`SPEC.md` changes land BEFORE implementation**, and this is mechanically enforced here —
  `spec_table_matches_shipped_descriptor` parses the SPEC's descriptor table and asserts equality
  with the shipped Rust table.
- **Never run `yf skills install` / `yf self install` mid-execution.** `plan_manager.py` is
  re-invoked per call, so a mid-run deploy takes effect for scripts in the same session while
  `SKILL.md` prose stays loaded from invocation — a half-deployed session runs new scripts against
  old prose.
- The four harnesses this plan touches are **pi, opencode, codex and claude-code**, all installed
  on the authoring machine.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-27 -->

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
- Plan directory: `docs/plans/plan-055-james-dixson-5f1c40`

## Operator identity

- Git user: `james-dixson`
- Contact: `james@yoshikostudios.com`
- Role: sole maintainer and operator of `dixson3/yoshiko-flow`; authors the SPEC and authorizes
  every outward-facing write.
- **Authority scope:** full authority over this repository, including SPEC amendments, upstream
  issue creation and closure, releases and tags. Outward-facing writes (`git push`,
  `gh issue create`/`close`) remain operator-authorized per turn — the plan proposes, the operator
  authorizes. No other party has commit authority.

## Runtime assumptions

**This plan is NOT safe to run as-is on an arbitrary machine.** It measures and then *modifies*
harness skill directories under `$HOME`. A cold reader on a different machine should read this
section as a gate, not a description.

- **OS / shell:** macOS (darwin 25.5.0), `zsh`. The check scripts are `bash`. Paths assume a
  POSIX layout and `$HOME`-relative harness roots.
- **Four harnesses installed and on `PATH`:** pi 0.84.3, opencode 1.18.23, codex-cli 0.150.1,
  claude-code 2.1.247. **Every root-resolution finding in this plan is scoped to those versions**
  (R4); a materially later harness invalidates the measurement, not merely the wording.
- **Authenticated harnesses.** Epic 4/5 drive real headless sessions, which cost real model calls.
  Presence is testable; authentication and interactive consent are **not** — the live-harness gate
  is `human` for that reason.
- **Network access** for `gh` (upstream reconcile) and for the harnesses' model calls. `gh` owns
  its own credential store; **no token is ever written to config**.
- **Side-effect permissions — the material one:** Epic 5 **deletes directories under `$HOME`**
  (the migrated-away private skills trees). That is a declared destructive local operation, gated
  behind human review of per-directory dry-run verdicts, and the remover keeps anything it cannot
  prove yf authored and left unmodified.
- **`bd` is local-only here** (`dolt.local-only = true`): propose `git push` alone, never
  `bd dolt push`.
- Sandbox spikes run under a fake `HOME`; the operator's real harness trees are never used as
  test fixtures.

## Recovery runbook (mid-execution abandonment)

**If execution stops after 5.2 and before the branch lands**, this machine is migrated while `main`'s
binary still targets the private roots — so the next `yf self install` from `main` re-creates them and
re-establishes the divergent-duplicate hazard (R3). Recovery, in order:

1. Restore from the timestamped quarantine (the one-line restore shipped by Issue 5.2a).
2. Reinstall from `main`: `yf self install --from-build --build`.
3. Confirm with `yf harness skills status --harness <h> --scope user --json` that each root is
   `ok` / `unmodified: true` again.

**Do not run a bare `yf self install` between Epic 2 landing and 5.2's quarantine** (Issue 5.1a). In
that window the new binary writes only `.agents/skills` and `.claude/skills`, leaving the two private
trees stale and divergent — manufacturing the exact hazard this plan exists to remove, via the repo's
own default land-the-plane step.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
