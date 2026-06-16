# Integration Specification (surface detection, carve-out, boundary)

How this skill coexists with skill-authoring and adapts to a project's rules surface.

REQ-INT-001: No duplication with skill-authoring. K1 (token efficiency) lives only in
skill-authoring; K2 (structure) lives only in this skill's `spec/`. Each skill references the
other rather than restating.
Rationale: The skill enforces one-source-of-truth; duplicating either body across the two skills
is the anti-pattern it exists to prevent.
Verification: grep shows no Cut/Keep/Extract ruleset in optimal-instructions; grep shows no
AGENTS.md-primacy / CLAUDE.md-index ruleset in skill-authoring (skill-authoring references this
skill for it).

REQ-INT-002: The two skills' `description` fields are mutually exclusive on the skill-dir vs
project-root axis. optimal-instructions TRIGGERs on project-root instruction files and SKIPs
skill-dir ones; skill-authoring SKIPs project-root instruction files and routes them here.
Rationale: Both skills can match `CLAUDE.md`/`AGENTS.md`; the distinguishing axis must live in
both descriptions so routing is unambiguous.
Verification: both SKILL.md frontmatter `description` fields name the axis; Epic 4.1 cross-check.

REQ-INT-003: Surface detection. The skill recognizes all three behavioral-rule subdir forms —
`AGENTS/*` (capitalized, repo-root), `.agents/rules/*`, and `.claude/rules/*` — and normalizes K2
relocations to the surface the project already uses. Both the `.claude` and `.agents` surfaces are
in scope. When the changed file is itself under a rules surface, that surface wins; otherwise an
existing surface is detected. It does not impose one on a project that has another.
Rationale: Forcing a surface switch would fight the project's existing convention; a project may
carry both `.claude` and `.agents` surfaces (one often symlinked into the other).
Verification: SKILL.md "Surface detection" block; `agents/instruction-optimizer.md` uses the
passed `RULES SURFACE`.

REQ-INT-004: Runtime carve-out vs Surface Convention §1. skill-authoring's Surface Convention §1
forbids a skill's *installer* from writing to `AGENTS/` or editing `CLAUDE.md`. This skill edits
those files at **runtime via its apply agent** — a different mechanism, explicitly permitted.
Rationale: A consistency reviewer would otherwise read the runtime edits as a Surface Convention
violation. They are not: §1 governs install-time writes only.
Verification: SKILL.md Rules (runtime carve-out note); this REQ.

REQ-INT-005: Minimal companion footprint, no hook. Strive for the minimum always-loaded
footprint: ship a `protocols/` rule only when an always-loaded obligation cannot be met by the
`description` trigger alone, and keep any such rule as thin as possible (a pointer to a single
source of truth, not a restatement). The skill currently ships exactly one such rule
(`protocols/INSTRUCTIONS.md`, a thin token-efficiency backstop pointing to skill-authoring's
ruleset) and registers no hook. install.sh auto-discovers both the skill and its rule with zero
changes. The `description` trigger remains best-effort (not guaranteed on every write); the
companion rule is the always-loaded backstop, not a trigger mechanism.
Rationale: Always-loaded context is paid every turn, so default to none and add only the
minimal necessary rule. The token-efficiency obligation must hold even when the description
trigger misses; shipping it as a thin portable protocol (consistent with yf-plan/yf-research)
replaces the former repo-local `AGENTS/OPTIMIZED_SKILLS.md` and removes its duplication of
skill-authoring's ruleset.
Verification: `ls skills/optimal-instructions/protocols/` shows `INSTRUCTIONS.md` +
`manifest.json`, each thin and pointer-only; install.sh §install_rules copies it; README
documents it.
