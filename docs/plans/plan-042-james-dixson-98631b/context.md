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
a Rust CLI (edition 2021, `clap`, `rust-embed`) that embeds the `skills/` tree and deploys it.

This plan touches the **install/deploy path** of that CLI. Layout that matters here:

- `yf/src/cmd/self_cmd/install.rs` — `yf self install --from-build` (developer path).
- `yf/src/cmd/self_cmd/update.rs` — `yf self update` (end-user vendor path), including
  `refresh_user_skills`, the routine this plan factors out and shares.
- `yf/src/cmd/install.rs` — `harness skills install` (+ the `--tune` bridge).
- `yf/src/cmd/status.rs` — `harness skills upgrade` (what the vendor path execs today).
- `yf/src/cmd/harness/` — `harness tune`: config alignment + rule deployment, per harness.
- `yf/profiles/*.json` — a **second** `rust-embed` root holding the per-harness config profiles.
- `SPEC.md` + `skills/yf-plan/spec/` — the requirement surface (`REQ-YF-SELF-*`,
  `REQ-YF-TUNE-*`, `REQ-YF-MARK-*`, `REQ-YF-INSTALL-*`, `REQ-YF-FLOW-*`).

**Non-obvious, and load-bearing:**

- **`yf self install` and `yf self update` share no code path.** `self install` is from-build
  only (a bare invocation refuses, exit 1); `self update` is the vendor path. Converging them
  on one routine is this plan's structural move.
- **`harness tune` reads content from the BINARY's embedded tree, never from deployed skills**
  — so skills-then-tune ordering is conventional, not required.
- **A promoted binary must be exec'd at its captured install path**, never via a post-swap
  `current_exe()`, or the sync deploys the *old* embedded tree.
- **`harness skills upgrade` is single-destination** and writes the rules aggregate to a
  skills-sibling dir — wrong for every harness but claude-code. This is why the plan uses
  `install --tune` instead.

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
- Plan directory: `docs/plans/plan-042-james-dixson-98631b`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson (james@yoshikostudios.com) — repository owner and sole
  maintainer; full authority to approve, merge, and publish in this repo.

## Runtime assumptions

- **OS/shell:** macOS (Darwin 25.5.0), `zsh`. Harness detection and config paths are
  platform-sensitive; the plan's measurements are macOS.
- **Toolchain:** Rust with `cargo` on `PATH`; `uv` for Python entry points.
- **`bd` >= 1.1.0**, initialized. `.beads/` is gitignored (local-only).
- **`gh` authenticated** — for Issue 4.3's upstream filing and the intake tracker only. The
  sync itself makes no network calls.
- **THIS PLAN WRITES OUTSIDE THE REPO.** Unlike plan-041, its entire deliverable is deploying
  to operator surfaces: `~/.claude/skills/`, `~/.claude/rules/YOSHIKO_FLOW.md`,
  `~/.claude/settings.json`, and the codex / opencode / pi equivalents. **Every test that
  exercises deployment MUST use a sandboxed `HOME` or an explicit `--target`.** No test may
  write to the operator's real config surfaces.
- **Security-relevant:** the claude-code profile carries
  `permissions.defaultMode: "bypassPermissions"` and `skipDangerousModePermissionPrompt: true`.
  The consent gate (D-C1's split + **D-R**'s profile-declared predicate + D-N's flag) exists precisely to keep those from landing unrequested.
- **Destructive operations: none in this plan.** (`--prune` was scoped in as D-P, then struck at
  pass-1 review and moved to https://github.com/dixson3/yoshiko-flow/issues/155.) The sync
  writes and overwrites operator surfaces but deletes nothing.

## Adjacent-concept glossary

- **the sync** — deploying skills + the rules aggregate + harness config so the operator's
  surfaces match the promoted binary. This plan's whole subject.
- **safe half / consent-bearing half** — skills + rules (idempotent, no security semantics) vs.
  harness config alignment (can write `permissions.*`). D-C1 splits them by default; Epics 2
  and 3 follow that seam.
- **halting authority** — whether a failure stops the operation. Here: a sync failure is
  **fail-soft** and never invalidates a successful binary promote.
- **the rules aggregate** — `YOSHIKO_FLOW.md`, generated from every embedded skill's
  `protocols/*.md`. Regenerated wholesale (see #154).
- **the confirmation trap** — `install --tune --json` with no `--harness` returns
  `confirmation_required`, writes nothing, and **exits 0**. D-M makes it a caller-side failure.
- **captured install path** — the destination path recorded *before* a binary swap; the only
  safe thing to exec afterwards.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
