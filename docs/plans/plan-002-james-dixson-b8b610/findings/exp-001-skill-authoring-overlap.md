# Finding: overlap between optimal-instructions and skill-authoring

## Question
Should `optimal-instructions` reuse `skill-authoring`'s optimizer agent / token-efficiency
ruleset, or ship its own self-contained logic?

## Evidence

### skill-authoring/agents/optimizer.md
- Already a token-efficiency optimizer for "any always-loaded instruction file:
  `SKILL.md`, agent `.md`, `.agents/rules/*.md`, `AGENTS.md`, `CLAUDE.md`" (line 9).
- Principles (lines 20-24) are near-identical to OPTIMIZED_INSTRUCTIONS.md: action over
  narrative, one source of truth, implicit over explicit, templates are data, constraints
  beat character traits.
- **Read-only** (line 114): "Never edits files. Caller applies fixes." Returns ranked
  HIGH/MEDIUM/LOW findings with suggested edits.
- Dispatched by skill-authoring's "Review sequence" (SKILL.md lines 170-178).

### skill-authoring/SKILL.md "Token efficiency" section (lines 62-91)
- Canonical Cut / Keep / Extract ruleset for always-loaded context. Same intent as
  OPTIMIZED_INSTRUCTIONS.md.

### What OPTIMIZED_INSTRUCTIONS.md adds that the optimizer lacks
- **CLAUDE.md as a thin index**: "It carries only `@-include` directives. Project context
  and command reference live in AGENTS.md; behavioral rules in AGENTS/ files." This
  structural convention is NOT in optimizer.md.

### Cross-skill reference is repo-idiomatic
- bdplan SKILL.md "Reference skills" defers to `beads`/`beads-extra`/`beads-authoring`
  rather than restating bd usage ("When in doubt about a bd behavior, consult beads-extra").
- Precedent: a doing-skill referencing a conventions-skill's single source of truth.

## Conclusion (recommended)
The optimization *ruleset* should have ONE source — skill-authoring (Token efficiency
section + optimizer.md). `optimal-instructions` should NOT restate it (that would violate
the very "one source of truth" principle the skill enforces). optimal-instructions owns
only what is unique:
1. The **auto-fix** workflow (read → apply edits → report) vs optimizer's report-only.
2. The **CLAUDE.md-as-index** structural rule (the @-include / AGENTS split).
3. The **trigger** (fires on CLAUDE.md / AGENTS.md / AGENTS/* create/modify in a project).
4. The change-report output format.

Open architecture fork for operator: how tightly to couple to skill-authoring
(hard runtime dispatch vs soft reference with self-contained fallback). See plan.md.
