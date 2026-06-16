# Spec: Skill structure & layout

How a beads-backed skill is laid out and resolves itself. Source of truth for the
formula-vs-agent separation and runtime self-location.

## Requirements

- **REQ-STRUCT-001:** A beads-backed skill resolves its own directory at runtime via the
  `SKILL_DIR` find idiom that includes the real `.agents/skills` path (not only the symlinked
  `.claude/skills`), since BSD `find` does not follow a symlinked start path. — *Rationale:*
  formulas/agents must load regardless of which surface the harness exposes. — *Verify:* SKILL.md
  "Portability: SKILL_DIR resolution" §.

- **REQ-STRUCT-002:** Formulas (`formulas/*.formula.toml`) define *what work exists and how it
  connects* (the DAG); agent files (`agents/*.md`) define *how to execute* a step. The two are
  not conflated. — *Rationale:* declarative shape and execution instructions have different
  lifecycles and owners. — *Verify:* SKILL.md "Skill layout" + "Naming conventions" §.

- **REQ-STRUCT-003:** A skill's `.formula.toml` is bundled with its consumer skill
  (`<skill>/formulas/`), staged transiently into `.beads/formulas/` only during pour, then
  removed. — *Rationale:* keeps the source of truth in the skill (upgradeable with it) while
  satisfying `bd`'s fixed formula search path. — *Verify:* SKILL.md "Beads formulas" § stage/pour/rm.

- **REQ-STRUCT-004:** SKILL.md owns orchestration (prerequisites, scoping, planning, pour,
  handoff, coordinate); per-step execution lives in agent files. — *Rationale:* SKILL.md loads
  every invocation; agent files load only when their step runs. — *Verify:* SKILL.md "SKILL.md
  responsibilities" §; presence of `agents/`.

- **REQ-STRUCT-005:** Multi-session skills hand off to a `coordinate` subcommand run in a new
  session rather than continuing inline after pour. — *Rationale:* the start gate is released in
  a fresh session, preventing accidental auto-execution of unapproved work. — *Verify:* SKILL.md
  "Coordinate subcommand" §; cross-ref yf-plan/yf-research handoff.
