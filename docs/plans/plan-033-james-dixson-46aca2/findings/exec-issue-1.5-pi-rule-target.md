# Issue 1.5 (execution) — Pi always-loaded rule target: RESOLVED

**Verdict:** OUTCOME 1 — first-party evidence found.
**Resolved target:** `~/.pi/agent/AGENTS.md` (Pi's always-loaded global instructions/context file).
**Rejected:** `~/.pi/agent/APPEND_SYSTEM.md`.

## First-party evidence (earendil-works/pi — official repo; tool = pi.dev)
1. **`packages/coding-agent/docs/usage.md`** ("## Context Files"): Pi loads `AGENTS.md` or
   `CLAUDE.md` at startup from `~/.pi/agent/AGENTS.md` (global), parent dirs, and cwd. The
   `--no-context-files`/`-nc` flag governs `AGENTS.md`/`CLAUDE.md` discovery — NOT
   `APPEND_SYSTEM.md`. `APPEND_SYSTEM.md` is documented as a *system-prompt extender*,
   semantically distinct from context/rule files.
2. **Issue #748** (closed) — "`APPEND_SYSTEM.md` auto-discovery not implemented": Pi has
   `discoverSystemPromptFile()` for `SYSTEM.md` but **no** auto-discovery for
   `APPEND_SYSTEM.md`; it requires a manual per-run CLI path. Therefore it is NOT an
   always-loaded surface and is disqualified as yf's rule target.

## SPEC action taken
`REQ-YF-TUNE-020` pinned to `~/.pi/agent/AGENTS.md` (OUTCOME 1). The `--pi-rule-target`
opt-in fallback is now moot (kept documented, not the operative path). This aligns Pi with
the codex/opencode `AGENTS.md` convention already in the target map.

## Gate
Resolves the "Pi rule target verified" capability gate (bd `yf-mol-y7f.11`). Epic 6.3 may
proceed against the verified target; no `--pi-rule-target` follow-on is needed (Epic 10.2
condition (d) does NOT fire).
