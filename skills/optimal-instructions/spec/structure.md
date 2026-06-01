# Structure Specification (K2)

The instruction-file structural convention this skill owns. K2 is defined **here only** —
skill-authoring does not restate it (see `integration.md` REQ-INT-001).

REQ-STRUCT-001: `AGENTS.md` is the primary project instruction file. Project context,
command reference, and orientation live there.
Rationale: AGENTS.md is the cross-harness surface; CLAUDE.md is Claude-specific. Primacy in
the portable file keeps instructions reachable by other harnesses.
Verification: `agents/instruction-optimizer.md` K2 proposal logic; the before/after example in `apply.md`.

REQ-STRUCT-002: `CLAUDE.md` is a thin index. It carries `@-include` directives pointing at
`AGENTS.md` and `AGENTS/*` (or `.agents/rules/*`), plus only Claude-specific essentials that
have no portable home (e.g. an Upstream-Tracking block).
Rationale: Every line of CLAUDE.md is always-loaded Claude context; content that belongs in
the portable surface should not be duplicated into it.
Verification: K2 proposal demotes non-`@-include`, non-essential CLAUDE.md content to a relocation proposal.

REQ-STRUCT-003: Behavioral rules live in the project's rules-subdir surface — `AGENTS/*` or
`.agents/rules/*` — one concern per file.
Rationale: Factoring shared behavioral rules into their own file (vs inlining in AGENTS.md or
CLAUDE.md) is the deduplication the convention exists to enforce.
Verification: K2 proposal relocates behavioral-rule blocks to `${RULES_SURFACE}/<concern>.md`.

REQ-STRUCT-004: K2 content placement is the only structural authority. What belongs in
AGENTS.md vs CLAUDE.md vs the rules subdir is decided by REQ-STRUCT-001..003; the apply agent
applies these and nothing beyond them.
Rationale: A single authoritative placement rule prevents drift between agent behavior and spec.
Verification: `agents/instruction-optimizer.md` cites these REQs for placement decisions.
