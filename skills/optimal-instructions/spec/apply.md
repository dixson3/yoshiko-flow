# Apply Specification (split-apply contract + idempotency)

The contract for how edits are applied: K1 auto, K2 propose-and-confirm.

REQ-APPLY-001: K1 (token-efficiency cuts) is auto-applied. The main session writes K1 edits
without operator confirmation.
Rationale: K1 cuts are low-risk, reversible, and reported; gating them on confirmation adds
friction without safety.
Verification: SKILL.md Workflow step 5; `agents/instruction-optimizer.md` output (K1 edited content).

REQ-APPLY-002: K2 (structural relocation) is propose-and-confirm. The agent emits a *proposal*;
the main session writes K2 edits only after explicit operator confirmation.
Rationale: Demoting CLAUDE.md and relocating operator-authored governance is destructive and
could break projects relying on current placement.
Verification: SKILL.md Workflow step 6; `agents/instruction-optimizer.md` Rules (never write K2).

REQ-APPLY-003: Relocate, never delete. K2 moves content between files; it never removes content
outright. Every relocation appears in the operator-visible change report.
Rationale: Content the agent misreads as narrative may encode a behavioral constraint; relocation
is recoverable, deletion is not.
Verification: `agents/instruction-optimizer.md` Rules; change-report format (relocations enumerated).

REQ-APPLY-004: Idempotency. Running the skill on an already-optimized file is a no-op — empty K1
edit set, no K2 proposal.
Rationale: An on-write skill re-processes its own output on the next write; non-idempotent
behavior would oscillate or accrete edits.
Verification: `agents/instruction-optimizer.md` idempotency rule; the before/after example below
(running again on the "after" state yields no findings).

REQ-APPLY-005: K1 criteria are cited, never restated. The agent names **skill-authoring `SKILL.md`
"Token efficiency" §** as the criteria source and does not reproduce the Cut/Keep/Extract ruleset.
Rationale: Restating K1 would violate the one-source-of-truth principle the skill enforces.
Verification: `agents/instruction-optimizer.md` K1 section cites the anchor; grep shows no Cut/Keep
ruleset copied into this skill.

REQ-APPLY-006: Preserve literal command blocks, behavioral constraints, and output-format specs.
These are never cut by K1 nor relocated in a way that breaks them.
Rationale: They are output contracts and behavior gates, not narrative.
Verification: `agents/instruction-optimizer.md` "What to keep" defers to skill-authoring's Keep list.

## Acceptance example (before / after)

Falsifiable behavior, no separate fixture harness needed.

**Before** — a project `CLAUDE.md`:

```markdown
# MyProject

This file provides guidance to Claude when working in this repository. Please be thorough
and consider all the implications of your changes carefully.

## Build

To build the project, run the build command. You might want to run it like this:

    make build

## Testing Rules

Always run tests before committing. Never push if tests fail. Use `make test`.
```

**After K1 (auto-applied)** — narrative intro and soft guidance cut, command block kept:

```markdown
# MyProject

## Build

    make build

## Testing Rules

Always run tests before committing. Never push if tests fail. Use `make test`.
```

**After K2 (proposed, written on confirmation)** — CLAUDE.md demoted to an index; the
behavioral "Testing Rules" relocated to the detected rules surface; build context moved to
AGENTS.md:

`CLAUDE.md`:
```markdown
# MyProject

@AGENTS.md
@AGENTS/TESTING.md
```

`AGENTS.md` (gains the build section), `AGENTS/TESTING.md` (gains the testing rules, verbatim —
relocated, not rewritten).

Running the skill again on this "after" state produces no K1 edits and no K2 proposal
(REQ-APPLY-004).
