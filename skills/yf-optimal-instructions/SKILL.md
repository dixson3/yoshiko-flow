---
name: yf-optimal-instructions
description: 'Auto-fix skill for project instruction files. On create/modify of a project
  CLAUDE.md, AGENTS.md, AGENTS/*, or repo-root .{claude,agents}/rules/* file, reads it,
  auto-applies token-efficiency cuts, and proposes structural fixes — AGENTS.md primary,
  CLAUDE.md a thin @-include index, behavioral rules in the project rules surface — then
  reports what changed. TRIGGER when: a project-root instruction file (CLAUDE.md, AGENTS.md,
  AGENTS/*, or repo-root .{claude,agents}/rules/*) is created or modified. SKIP for: instruction
  files INSIDE a skill directory under .{claude,agents}/skills/<skill>/ (a skill''s SKILL.md,
  agents/*.md, its own rules) — those route to yf-skill-authoring; also application code, end-user
  docs, notes. Distinguishing axis: this skill owns project-root instruction files (in both the
  .claude and .agents surfaces); yf-skill-authoring owns skill-dir instruction files.'
user-invocable: false
skill-group: utility
depends-on-tool: [uv]
depends-on-skill: [yf-skill-authoring]
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
  - Agent
title: yf-optimal-instructions
created: '2026-05-31'
tags: []
---

# yf-optimal-instructions

Active, on-write optimizer for project instruction files (`CLAUDE.md`, `AGENTS.md`,
`AGENTS/*`, repo-root `.{claude,agents}/rules/*`). Reads the changed file, auto-applies
token-efficiency cuts, proposes structural relocation, and reports what changed.
Background: see [[README]].

## SKILL_DIR

```bash
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo .)
SKILL_DIR=$(find ~/.claude/skills ~/.agents/skills "$GIT_ROOT/.claude/skills" "$GIT_ROOT/.agents/skills" .claude/skills .agents/skills -maxdepth 1 -name yf-optimal-instructions -type d 2>/dev/null | head -1)
[ -z "$SKILL_DIR" ] && { echo "ERROR: yf-optimal-instructions skill directory not found"; exit 1; }
```

## Two bodies of knowledge

- **K1 — token efficiency** (cut narrative, keep templates/constraints/command blocks,
  extract scripts). Single source of truth: **yf-skill-authoring `SKILL.md` "Token efficiency"
  §**. This skill cites that anchor and never restates the ruleset.
- **K2 — instruction-file structure** (AGENTS.md primary; CLAUDE.md a thin `@-include`
  index; behavioral rules in the project's rules surface). Owned here, in [[spec|spec/]].

## Scope vs yf-skill-authoring

This skill handles **project-root** instruction files. Instruction files **inside a skill
directory** under `.{claude,agents}/skills/<skill>/` (`SKILL.md`, `agents/*.md`, a skill's own
rules) are yf-skill-authoring's domain — route them there. The two skills' `description` fields are
mutually exclusive on this skill-dir vs project-root axis.

## Surface detection

The behavioral-rules subdir exists in three forms — `AGENTS/*` (capitalized, repo-root),
`.agents/rules/*`, and `.claude/rules/*`. Detect which the project uses; normalize to **that**
surface, never impose one. If the changed file is itself under a rules surface, that surface
wins; otherwise detect an existing one:

```bash
CHANGED_FILE="<absolute path to the changed instruction file (the TARGET from step 1)>"
case "$CHANGED_FILE" in
  */.claude/rules/*) RULES_SURFACE=".claude/rules" ;;
  */.agents/rules/*) RULES_SURFACE=".agents/rules" ;;
  *)
    for s in "AGENTS" ".agents/rules" ".claude/rules"; do
      [ -d "$GIT_ROOT/$s" ] && RULES_SURFACE="$s" && break
    done
    RULES_SURFACE="${RULES_SURFACE:-AGENTS}"   # default for a greenfield project
    ;;
esac
```

A project may carry both `.claude/` and `.agents/` surfaces (one often symlinked into the
other); pick the changed file's own surface so relocations stay on the surface the operator
is editing.

## Workflow

1. Identify the changed instruction file and its kind: `CLAUDE.md` | `AGENTS.md` | `AGENTS/*`
   | `.{claude,agents}/rules/*`. If the path is inside a skill dir, stop — defer to yf-skill-authoring.
2. Detect `RULES_SURFACE` (above).
3. Dispatch the apply agent. Read `${SKILL_DIR}/agents/instruction-optimizer.md` and follow
   it. Prompt:

   ```
   Read ${SKILL_DIR}/agents/instruction-optimizer.md and follow its instructions.

   TARGET: <absolute path to changed file>
   FILE KIND: <CLAUDE.md | AGENTS.md | AGENTS/* | .claude/rules/* | .agents/rules/*>
   RULES SURFACE: <AGENTS | .agents/rules | .claude/rules>
   ```

4. The agent returns: **K1 edited content** (auto), a **K2 proposal**, and a **change
   report**.
5. **Write K1 edits** (auto-apply — low-risk, reversible).
6. **K2 is propose-and-confirm.** Present the K2 proposal to the operator. Write K2 edits
   only after explicit confirmation. Never delete content — only relocate.
7. Surface the change report (K1 applied, K2 proposed/applied/declined).

## Idempotency

Running on an already-optimized file is a no-op. The agent returns an empty K1 edit set and
no K2 proposal when input already conforms — required because an on-write skill re-processes
its own output on the next write.

## Rules

- K1 auto-applies; K2 never writes without operator confirmation.
- Relocate, never delete (K2).
- K1 criteria are cited from yf-skill-authoring `SKILL.md` "Token efficiency" §, never restated
  here or in the agent.
- Detect and normalize to the project's existing rules surface; do not impose one.
- This skill edits `CLAUDE.md` / `AGENTS/*` at **runtime via its apply agent** — distinct
  from the Surface Convention §1 *installer* prohibition, which governs install-time writes.
  See [[spec|spec/]].

## Companion rule

This skill ships `protocols/INSTRUCTIONS.md` — an always-loaded rule that `install.sh` surfaces
to the rules dir. It states the on-write token-efficiency obligation for all instruction
surfaces (project-root and skill-dir) and points to yf-skill-authoring `SKILL.md` "Token
efficiency" § as the single source of truth. It is the always-loaded backstop for this skill's
best-effort `description` trigger. `scripts/manifest_update.py` maintains `protocols/manifest.json`.

## Reference

- [[README]] — what this skill is, when it fires, accepted limitations.
- [[spec|spec/]] — K2 structure, split-apply contract, idempotency, surface detection, the
  runtime carve-out, and the no-duplication boundary with yf-skill-authoring.
