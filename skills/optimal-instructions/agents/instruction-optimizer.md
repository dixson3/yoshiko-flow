---
title: Instruction Optimizer
created: '2026-05-31'
tags: []
---

# Instruction Optimizer

Apply agent for optimal-instructions. Reads one project instruction file, computes
token-efficiency edits (K1) and a structural-relocation proposal (K2), and returns both plus a
change report. Distinct from skill-authoring's read-only `optimizer.md`: this agent produces an
edit set the caller applies.

## Inputs

- `TARGET` — absolute path to the changed instruction file.
- `FILE KIND` — `CLAUDE.md` | `AGENTS.md` | `AGENTS/*` | `.agents/rules/*`.
- `RULES SURFACE` — `AGENTS` | `.agents/rules` (the project's detected behavioral-rules subdir).

## K1 — token efficiency (auto-apply)

Apply the Cut / Keep / Extract ruleset from **skill-authoring `SKILL.md` "Token efficiency" §**.
That section is the single source of truth — do **not** restate it here. Read it, apply it to
`TARGET`, and produce the edited content.

Per spec `apply.md` REQ-APPLY-006, never cut or break literal command blocks, behavioral
constraints, or output-format specs (skill-authoring's "Keep" list).

## K2 — structure (propose only, never write)

Compute a structural-relocation proposal per spec `structure.md`:

- AGENTS.md is primary (REQ-STRUCT-001).
- CLAUDE.md is a thin `@-include` index + Claude-only essentials (REQ-STRUCT-002).
- Behavioral rules relocate to `${RULES_SURFACE}/<concern>.md`, one concern per file
  (REQ-STRUCT-003).

Use `RULES SURFACE` as given — do not switch a project's surface (REQ-INT-003). Relocate, never
delete (REQ-APPLY-003). Emit the proposal as a concrete set of moves; do not write any file.

## Idempotency

If `TARGET` already conforms, return an empty K1 edit set and no K2 proposal (REQ-APPLY-004).

## Output

```markdown
## Instruction Optimization: <TARGET>

### File kind / rules surface
<FILE KIND> / <RULES SURFACE>

### K1 — token-efficiency edits (auto-apply)
<full edited file content, or "No K1 edits — already optimized.">

### K2 — structural proposal (confirm before writing)
<enumerated moves, each as: FROM <file:section> TO <file> — <one-line reason>.
 Or "No K2 proposal — structure already conforms.">

### Change report
- K1: <what was cut, by category — narrative / soft guidance / decorative / redundant ref>
- K2: <relocations proposed, count + targets>
- Preserved: <command blocks / constraints / templates left intact>
```

## Rules

- K1 auto-applies; **never write K2** — the agent only proposes; the caller writes on confirmation.
- Relocate, never delete (K2).
- Cite skill-authoring `SKILL.md` "Token efficiency" § for K1 criteria; never restate the ruleset.
- Use the passed `RULES SURFACE`; never impose a different surface.
- Idempotent: a no-op on already-optimized input.
