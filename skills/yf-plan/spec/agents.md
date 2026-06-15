# Agent Specification

## General Rules

REQ-AGENT-001: All task tracking uses `bd`. Agents must never use `TodoWrite`, markdown checklists, or inline task lists.
Rationale: Dual tracking systems diverge; `bd` is the single source of truth for execution state.
Verification: `grep -r 'TodoWrite\|markdown checklist' skills/yf-plan/agents/` returns nothing (except the prohibition itself).

REQ-AGENT-002: Agent files are harness-specific to Claude Code. They may reference Claude Code tool names directly (`Agent`, `AskUserQuestion`, etc.).
Rationale: Harness-agnostic indirection was removed; agents now use concrete tool references.
Verification: No "per Tool Mapping" or generic dispatch language in agent files.

## Coordinator

REQ-AGENT-010: The coordinator drives the bead DAG via a `bd ready` → claim → execute → close loop.
Rationale: This is the core execution engine; deviating from the loop skips work or double-executes.
Verification: coordinator.md Loop section describes the 6-step cycle.

REQ-AGENT-011: The coordinator drains all unblocked work before reporting blocked gates.
Rationale: Reporting a blocked gate while parallel work remains wastes operator attention.
Verification: coordinator.md Rules and Blocked gates sections.

REQ-AGENT-012: The coordinator dispatches the reconciler agent when all execution beads close and the reconcile gate auto-resolves.
Rationale: Reconciliation depends on all work being complete; premature reconciliation produces incorrect upstream updates.
Verification: coordinator.md Reconcile trigger section references `agents/reconciler.md`.

REQ-AGENT-013: On a resume, the coordinator runs the orphan sweep before the ready loop: it resets stuck (`in_progress`/claimed) beads to `open` and reports — never auto-closes — any bead it cannot positively classify. The sweep runs strictly before any reconcile-trigger evaluation.
Rationale: A crashed prior session leaves stuck beads the ready loop would skip; resetting makes them re-workable without auto-closing real work. See REQ-RESUME-002/003 (phases.md) for the cross-cutting contract.
Verification: coordinator.md "Resume orphan sweep" section specifies reset-not-close, report-unclassifiable, and the before-ready-loop ordering.

## Investigator

REQ-AGENT-020: Investigators run in disposable worktrees. No code from an investigation worktree lands in the project.
Rationale: Experiments may install dependencies, write throwaway code, or modify config — none of this should pollute the project.
Verification: SKILL.md Phase 2 dispatches with `isolation="worktree"`; investigator.md header states "disposable worktree".

REQ-AGENT-021: Investigator output follows a structured finding format: Finding title, Approach Tested, Result, Implications for Plan, Recommendations.
Rationale: Structured output allows the planner agent to mechanically incorporate findings.
Verification: investigator.md Execute section shows the template.

## Reconciler

REQ-AGENT-030: The reconciler verifies each bead is closed before updating its linked upstream issue. If verification fails, it flags the issue for the operator rather than guessing.
Rationale: Updating an issue as "resolved" when work is incomplete misleads the team.
Verification: reconciler.md Rules: "Verify before acting. Never update upstream without confirming work was done."

REQ-AGENT-031: Disposition mapping is: `include` → close with comment, `partial` → comment only (do NOT close), `supersede` → close with "not planned" reason.
Rationale: Each disposition has a specific upstream action; conflating them produces wrong issue states.
Verification: reconciler.md Execute section step 3; SKILL.md Phase 6.3 disposition table.

## Red-Team

The EVALUATE `red-team` stance owns the adversarial verdict that drives the Phase 3 transition. (Phase 3 Review runs the conformance `reviewer` first as a mechanical gate, then the `red-team`.)

REQ-AGENT-040: The red-team produces a verdict of APPROVE, REVISE, or INVESTIGATE-MORE.
Rationale: Clear signal to the operator; ambiguous feedback stalls the workflow.
Verification: red-team.md Output section.

REQ-AGENT-041: Every concern in a red-team review includes a severity (high/medium/low) and a recommendation.
Rationale: Concerns without actionable recommendations don't help the operator fix them.
Verification: red-team.md Output template and Rules.

REQ-AGENT-042: High-severity concerns block approval.
Rationale: Proceeding with known high-severity issues produces plans that fail during execution.
Verification: red-team.md Rules: "High blocks approval."

REQ-AGENT-043: The red-team agent is read-only. It never writes files. `reviews/pass-N.md` and the phase-log `review:` line are written by the main session **at red-team presentation** (create-on-present, #4) as a single atomic step, then the same file is updated in place as the operator resolves concerns (REQ-PORT-006/008).
Rationale: Agents that write files outside their dispatch scope violate agent isolation (REQ-AGENT-050 sibling) and make the review capture path non-auditable. Keeping the red-team read-only lets the main session atomically write the review artifact and the phase-log entry together; writing at presentation (not after resolution) makes the verdict portable while the plan is still parked in `review`.
Verification: red-team.md Rules: "Read-only — never writes files" + "writes ... at presentation"; SKILL.md Phase 3 Review section "Write the report at presentation" states the main session writes `reviews/pass-N.md` + phase-log line atomically at red-team presentation.

## Reviewer (conformance)

The EVALUATE `reviewer` stance is a mechanical conformance/completeness pass. It runs **first** in Phase 3 Review, as a gate before the `red-team`. It is distinct from the `red-team`: yf-plan deliberately carries both stances (the asymmetry vs yf-research, which has only `red-team`, is justified by the factoring test — semantic plan conformance warrants a dedicated pass).

REQ-AGENT-044: The reviewer produces a conformance verdict of PASS or INCOMPLETE against a mechanical checklist: every epic has ≥1 issue and every issue a clear deliverable; every intra-plan `depends-on` references an existing issue and the graph is acyclic; every Success Criterion is verifiable (names a command/file/grep); every upstream `include`/`partial` is wired to a resolving issue; every gate declares type + approvers (+ condition/test for capability gates); plan.md carries all required portability sections. It runs before the red-team pass and produces no `pass-N.md`.
Rationale: A mechanical completeness gate catches structural gaps before the adversarial pass spends attention on a plan that is merely incomplete; its PASS|INCOMPLETE contract is distinct from the red-team's APPROVE|REVISE|INVESTIGATE-MORE verdict.
Verification: reviewer.md Checklist + Output sections; SKILL.md Phase 3 Review step 1 reads the conformance verdict and gates on PASS.

REQ-AGENT-045: The reviewer is read-only and conformance-only. It does not assess feasibility, risk plausibility, or approach soundness — those belong to the red-team. It never writes files.
Rationale: Separating the conformance and adversarial stances into non-interfering agents (the factoring test, case b) keeps each prompt focused and prevents the mechanical checklist from drifting into judgment calls.
Verification: reviewer.md Rules: "Conformance only" + "Read-only — never writes files".

## Captor

REQ-AGENT-060: The captor drafts missing portability-contract files (README.md, context.md, motivation, references/upstream-*.md, reviews/pass-*.md) from current plan state. Invoked by `/yf-plan capture` via SKILL.md Phase: CAPTURE.
Rationale: Operators should not have to hand-write portability scaffolding when the plan folder already contains enough state to derive it. The captor centralizes the drafting heuristics.
Verification: `agents/captor.md` Draft section enumerates the contract files; SKILL.md Phase: CAPTURE dispatches to `agents/captor.md`.

REQ-AGENT-061: The captor is read-only. It returns drafts for operator review and never writes files. The main session writes on approval.
Rationale: Mirrors the read-only review-agent pattern (REQ-AGENT-043/045). Keeps agent dispatch scope small and makes the write path auditable.
Verification: `agents/captor.md` Rules: "Never write files. The main session writes after operator approval."

REQ-AGENT-062: The captor must not invent reviewer verdicts, fabricate tool versions, or paraphrase upstream issue bodies. Reviewer drafts that cannot be reconstructed from phase-log reasoning are flagged inconclusive for the operator.
Rationale: Portability scaffolding is worthless if its content is fictional. Drafts must be derivable from plan state, not hallucinated.
Verification: `agents/captor.md` Rules enumerate these constraints.

REQ-AGENT-063: Under `--retro`, the captor additionally mines the current session's conversation for the seven portability classes (motivation, project environment, adjacent-concept glossary, reviewer verdicts/resolutions, upstream issue bodies, scope-change history, runtime/environment assumptions). Retro extends — never replaces — folder-state capture (folder state takes precedence), stays read-only, and observes the hard live-session boundary: it mines only the live conversation and omits any class lacking conversational evidence rather than inventing it. See REQ-PORT-032/033.
Rationale: Conversation-only context is the most-likely-to-be-lost portability class. Mining it in the agent (not the script) keeps the audit mechanical (REQ-PORT-010).
Verification: `agents/captor.md` "Retro mode (`--retro`)" section enumerates the seven classes and the live-session boundary; Rules include "Retro is current-session only".

## Planner

REQ-AGENT-050: The planner writes only to its resolved plan root — `docs/plans/<plan-id>/` for vault-default plans, or `Incubator/<slug>/plans/<plan-id>/` for incubator-scoped plans. The root is resolved during scoping (SKILL.md Phase 1.2) and passed to the planner as `plan_dir`.
Rationale: Plan synthesis should not modify project code, config, or other plans. The planner is root-agnostic: it writes to whatever `plan_dir` it receives.
Verification: planner.md Rules: "Write only to `<plan_dir>` (the resolved root)".

REQ-AGENT-051: The planner writes plan.md per the structure defined in SKILL.md Phase 3.
Rationale: A single plan.md schema ensures all downstream consumers (coordinator, reconciler, operator) can parse it.
Verification: planner.md Execute step 6 references "the Phase 3: PLAN section of SKILL.md".
