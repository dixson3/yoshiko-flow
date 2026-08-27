# Spec: Skill structure & layout

How a beads-backed skill is laid out and resolves itself. Source of truth for the
formula-vs-agent separation and runtime self-location.

## Requirements

- **REQ-STRUCT-001** *(amended plan-054):* A beads-backed skill resolves its own directory at
  runtime via **`yf skill-dir <name>`**, falling back to a **pure-bash existence loop** over a
  cwd-inclusive superset of yf's own anchors — covering **all five** harness destinations, not
  only `.claude` and `.agents`. The block is **generated** by `_shared/sync.py` and is env-var
  first. — *Rationale:* the `find` idiom this requirement used to mandate searched six fixed roots
  and included **neither** `~/.pi/agent/skills` nor `~/.config/opencode/skills`, while `yf`
  installs to exactly those — so on a pi-only machine every script-backed skill died, and on a
  mixed machine it silently resolved to the claude-code copy. `find` also **exits 1 on a missing
  root even when it found the target**, which `| head -1` hides and `set -o pipefail` would
  expose, so the idiom was replaced rather than widened. — *Verify:* `uv run _shared/sync.py
  --check` exits 0; no consumer under `skills/` matches `find ~/.claude/skills`.

- **REQ-STRUCT-002:** Formulas (`formulas/*.formula.toml`) define *what work exists and how it
  connects* (the DAG); agent files (`agents/*.md`) define *how to execute* a step. The two are
  not conflated. — *Rationale:* declarative shape and execution instructions have different
  lifecycles and owners. — *Verify:* SKILL.md "Skill layout" + "Naming conventions" §.

- **REQ-STRUCT-003** *(amended plan-027, recorded plan-054):* A skill's `.formula.toml` is
  bundled with its consumer skill (`<skill>/formulas/`), and **`yf preflight` stages it** into the
  project's gitignored `.beads/formulas/` on every preflight (`REQ-YF-PRE-011`). The SKILL body
  carries **no per-call `cp`/`rm` bracket**. — *Rationale:* the source of truth stays in the skill,
  but the staging obligation moves into the kernel, because a skill that forgets to stage its own
  formula fails at pour time with nothing having warned it. — *Verify:* no `cp … .beads/formulas/`
  in any SKILL.md; the `e-formula-name` drift edge FAILs a SKILL.md carrying a staging bracket.

- **REQ-STRUCT-004:** SKILL.md owns orchestration (prerequisites, scoping, planning, pour,
  handoff, coordinate); per-step execution lives in agent files. — *Rationale:* SKILL.md loads
  every invocation; agent files load only when their step runs. — *Verify:* SKILL.md "SKILL.md
  responsibilities" §; presence of `agents/`.

- **REQ-STRUCT-005:** Multi-session skills hand off to a `coordinate` subcommand run in a new
  session rather than continuing inline after pour. — *Rationale:* the start gate is released in
  a fresh session, preventing accidental auto-execution of unapproved work. — *Verify:* SKILL.md
  "Coordinate subcommand" §; cross-ref yf-plan/yf-research handoff.
