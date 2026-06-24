# Upstream #31: yf-beads-init: suppress bd-init instruction/hook cruft (AGENTS.md/CLAUDE.md beads boilerplate, .agents/.codex, git hooks)

- **Number:** 31
- **Title:** yf-beads-init: suppress bd-init instruction/hook cruft (AGENTS.md/CLAUDE.md beads boilerplate, .agents/.codex, git hooks)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Problem

When standing up a fresh repo, `bd init` (beads) injects a pile of artifacts that conflict with our conventions, requiring manual cleanup every time. Observed on a fresh `dixson3/gws-skills` init (bd 1.0.5, embedded dolt):

1. **Instruction-file boilerplate** — `bd init` writes/overwrites:
   - `AGENTS.md` with a full beads "Quick Reference / Non-Interactive Shell / Session Completion" block.
   - `CLAUDE.md` with a managed `<!-- BEGIN BEADS INTEGRATION -->` block (agent context profiles, session-close protocol, etc.).

   This duplicates guidance we already provide **once, user-scoped**, in `~/.claude/rules/BEADS.md`. It also fights our project convention (AGENTS.md = hand-authored primary source; CLAUDE.md = thin `@AGENTS.md` include shim).

2. **Harness cruft directories** — `bd init` creates:
   - `.agents/skills/beads/` (a per-project copy of the beads skill — redundant with the user-scoped install).
   - `.codex/config.toml` + `.codex/hooks.json` (Codex PreCompact/PostCompact/SessionStart hooks).
   - `.claude/settings.json` (a `SessionStart: bd prime --hook-json` hook).

3. **Git hooks activated** — `bd init` sets `core.hooksPath` to `.beads/hooks/` and commits the hook scripts (pre-commit, pre-push, post-merge, post-checkout, prepare-commit-msg). We deliberately run **without** beads git hooks (our existing repos have `core.hooksPath` pointing at the default `.git/hooks`, no beads wiring) — sync is manual via `bd dolt push`.

## Request

Have `yf-beads-init` (verify/repair) make a fresh/repaired repo match our conventions automatically, i.e. either suppress at init time or clean as a repair step:

- **Do not** inject beads boilerplate into `AGENTS.md` / `CLAUDE.md`. Leave instruction files to the operator; rely on the user-scoped `~/.claude/rules/BEADS.md`. If a managed block already exists, strip it.
- **Do not** create `.agents/skills/beads/`, `.codex/`, or a beads `.claude/settings.json` hook (or remove them on repair).
- **Do not** activate beads git hooks: leave `core.hooksPath` at the git default (`.git/hooks`) and do not commit `.beads/hooks/`. (Equivalently: a config knob like `hooks.install: false`.)

Net: a fresh beads repo should carry only the functional `.beads/` DB config (`config.yaml`, `metadata.json`, gitignore) and nothing that touches instruction files, harness hook dirs, or git hooks.

## Context

Encountered while relocating the multi-account `gws` skill work into `dixson3/gws-skills`. All four cruft classes were removed by hand post-init; this issue is to make that automatic.
