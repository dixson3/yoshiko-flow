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

REQ-INT-003: Surface detection. The skill recognizes both behavioral-rule subdir forms —
`AGENTS/*` (capitalized, repo-root) and `.agents/rules/*` — and normalizes K2 relocations to the
surface the project already uses. It does not impose one on a project that has the other.
Rationale: Forcing a surface switch would fight the project's existing convention.
Verification: SKILL.md "Surface detection" block; `agents/instruction-optimizer.md` uses the
passed `RULES SURFACE`.

REQ-INT-004: Runtime carve-out vs Surface Convention §1. skill-authoring's Surface Convention §1
forbids a skill's *installer* from writing to `AGENTS/` or editing `CLAUDE.md`. This skill edits
those files at **runtime via its apply agent** — a different mechanism, explicitly permitted.
Rationale: A consistency reviewer would otherwise read the runtime edits as a Surface Convention
violation. They are not: §1 governs install-time writes only.
Verification: SKILL.md Rules (runtime carve-out note); this REQ.

REQ-INT-005: No companion rule, no hook. The skill ships no `protocols/` rule and registers no
hook; install.sh auto-discovers it with zero changes. Triggering is via `description` only —
best-effort, not guaranteed on every write.
Rationale: Locked scope chose description-only triggering; install.sh installs companion rules
only when a `protocols/` dir exists.
Verification: `ls skills/optimal-instructions/` shows no `protocols/`; install.sh §auto-discovery
needs no edit; README documents the limitation.
