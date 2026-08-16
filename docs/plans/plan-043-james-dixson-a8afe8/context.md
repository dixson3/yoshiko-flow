---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**yoshiko-flow** — beads-backed agent skills for Claude Code and other harnesses, plus `yf`,
a Rust CLI (edition 2021, `clap`, `rust-embed`) that embeds and deploys them.

This plan touches only the **`yf-plan` skill**, specifically its Phase 6.4 close step. Layout:

- `skills/yf-plan/SKILL.md` — the phase model as **prose an LLM executes**. Phase 6.4 is
  `SKILL.md:1064-1140`.
- `skills/yf-plan/scripts/plan_manager.py` — 22 flat CLI verbs (`audit`, `complete-gate`,
  `update-status`, …). There is **no** orchestrator and no `close`/`reconcile` verb.
- `skills/yf-plan/scripts/close_cascade.py` — the one self-contained close-step script.
- `skills/yf-plan/spec/` — `phases.md` (REQ-COMPLETE-*), `cli.md` (REQ-CLI-*), `data.md`;
  plus `skills/yf-plan/SPEC.md` and the root `SPEC.md` amendment log.

**Non-obvious, and load-bearing for this plan:** Phase 6.4 has **no extension seam**. Steps
are prose calling flat verbs, and the repo explicitly forbids the harness-hook shape
(`SKILL.md:1220`, `SPEC.md:197`: *"a portable, documented script-verb step — never a harness
hook or scheduler"*). The "contract" is therefore SPEC + convention + tests.

Phase 6.3 (reconcile) is a **pure sub-agent dispatch** with no verdict, no exit code, and no
captured output — which is why its failures are invisible.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-16 -->

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
- Plan directory: `docs/plans/plan-043-james-dixson-a8afe8`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson (james@yoshikostudios.com) — repository owner and sole
  maintainer; full authority to approve, merge, and publish in this repo.

## Runtime assumptions

- **OS/shell:** macOS (Darwin 25.5.0), `zsh`.
- **`bd` >= 1.1.0**, initialized and healthy. `.beads/` is gitignored (local-only).
- **`gh` authenticated** — required at runtime by `verify-reconcile` (Epic 1) and by the
  Epic 4 upstream posts. **Tests must mock `gh`; no test may hit the network.**
- **`uv`** for all Python entry points (PEP 723 inline deps).
- **Network:** required only for the `gh` paths above. R1 treats `gh` unavailability as
  INCONCLUSIVE, never a completion halt.
- **Side effects:** this plan writes inside the repo (`skills/yf-plan/**`, `SPEC.md`,
  `CHANGE-VALIDATION.md`) and posts comments to GitHub issues #136/#140/#145 in Epic 4.
  It does **not** write to `~/.claude/` or any harness config.
- **Destructive operations:** none. `verify-reconcile` and the close-time audit are both
  read-only with respect to upstream; neither closes nor comments on an issue.

## Adjacent-concept glossary

- **Phase 6.4 / close step** — `cascade-close → complete-gate → set complete`, the fixed
  sequence this plan makes extensible.
- **fail-loud** — a step that exits non-zero and halts `set complete`. Reserved for
  **actionable state failures** (close a bead, run a `gh` command).
- **propose-only** — a step that reports and never halts. For failures resolved by
  **authoring prose** (`/yf-plan capture`'s job, which does not advance status).
- **class A / class B** (from E3) — audit failures that are execution-authored and invisible
  to the Phase-3 gate (A) vs. those predating the check or the OKF migration (B).
- **delta reporting** — comparing the close-time audit against the stored Phase-3 verdict, so
  only *new* findings surface.
- **verdict envelope** — the shared `{passed, reason, remediation}` JSON every close step
  emits to stdout on every path.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
