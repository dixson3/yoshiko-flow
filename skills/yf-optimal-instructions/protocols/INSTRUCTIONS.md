# Instruction-File Optimization Protocol

Always-loaded instruction surfaces — project-root files (`CLAUDE.md`, `AGENTS.md`, `AGENTS/*`, repo-root `.{claude,agents}/rules/*`) and skill-dir files (`SKILL.md`, `agents/*.md`, a skill's own rules) — must stay token-efficient. They load on every turn, so waste is paid repeatedly.

**Ruleset (single source of truth):** the Cut / Keep / Extract rules in the `yf-skill-authoring` skill's `SKILL.md` "Token efficiency" §. Reference that anchor; never restate the ruleset elsewhere.

**Apply on every create or modify** of an instruction file, routed by where the file lives:

- **Project-root** instruction files → the `yf-optimal-instructions` skill. Auto-applies token-efficiency cuts (K1) and proposes structural relocation (K2: AGENTS.md primary, CLAUDE.md a thin `@-include` index, behavioral rules in the project's rules surface).
- **Skill-dir** instruction files (under `.{claude,agents}/skills/<skill>/`) → the `yf-skill-authoring` skill. Same Cut/Keep/Extract ruleset plus its review sequence.

The two skills' triggers are mutually exclusive on the skill-dir vs project-root axis. K2 structural moves relocate, never delete, and require operator confirmation.
