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

REQ-AGENT-064: Under the autonomous default the coordinator **continues to the next ready bead without operator input**. An epic boundary is a **report, not a stop**. The coordinator halts only on the declared stop set: (1) an outward-facing or irreversible write; (2) a capability gate whose `Test:` exits non-zero; (3) a declared destructive local operation; (4) a mechanical counter threshold (`yf_attempts >= N`, or `max_review_cycles >= N` in the plan phase); (5) a declared mechanical check that exits non-zero — validation FAIL, audit/`ready-check` fail, merge conflict, dirty worktree, or a corrupted bead DB (which routes to `yf-beads-init`). No halt is reachable by prose judgement alone: every stop class is an exit code or a counter.
Rationale: The coordinator's only explicit wait was "Wait for operator", and it was the loop's documented exit — so an ordinary unsatisfiable gate routed straight to a stop. Measured in the same file: "report blocked gates" appeared 5x and "continue to the next bead" 0x, leaving the continue case unwritten rather than merely under-emphasised. Enumerating the stop set mechanically closes the loophole in the other direction too: without an exit code, "scope ambiguity" re-admits arbitrary stopping.
Verification: coordinator.md Loop states the continue-to-next-ready-bead instruction and that an epic boundary is a report; each of the five stop classes maps to a command exit code or a counter comparison.

## Investigator

REQ-AGENT-020: Investigators run in disposable worktrees. No code from an investigation worktree lands in the project.
Rationale: Experiments may install dependencies, write throwaway code, or modify config — none of this should pollute the project.
Verification: SKILL.md Phase 2 dispatches with `isolation="worktree"`; investigator.md header states "disposable worktree".

REQ-AGENT-021: Investigator output follows a structured finding format: Finding title, Approach Tested, Result, Implications for Plan, Recommendations. Every load-bearing conclusion in Result and Implications is marked **measured** (a command ran; this was its output) or **inferred** (what the author concluded from that output). Any inference the plan will build on must be corroborated by a second independent signal, or recorded as uncorroborated.
Rationale: Structured output allows the planner agent to mechanically incorporate findings. The measured/inferred split exists because an inference recorded with the confidence of a measurement propagates undetectably: in d3-pxe plan-014 the inference "the CT rebooted" was written as if `uptime -s` had been read, and reached five plan artifacts — one of which would have restarted a production database to reproduce a bug that did not exist. Four independent signals were available and any one would have caught it, so corroboration is cheap where it matters.
Verification: investigator.md Execute section shows the template with the measured/inferred marking and the corroboration requirement.

## Reconciler

REQ-AGENT-030: The reconciler verifies each bead is closed before updating its linked upstream issue. If verification fails, it flags the issue for the operator rather than guessing.
Rationale: Updating an issue as "resolved" when work is incomplete misleads the team.
Verification: reconciler.md Rules: "Verify before acting. Never update upstream without confirming work was done."

REQ-AGENT-031: Disposition mapping is: `include` → close with comment, `partial` → comment only (do NOT close), `supersede` → close with "not planned" reason, `deferred` → **no upstream action** (the issue stays OPEN and untouched), `exclude` → no action and not verified. `deferred` is a non-action: the row records a scoping decision taken in *this* plan, not work done on that issue, so there is nothing to attribute upstream and no comment is written.
Rationale: Each disposition has a specific upstream action; conflating them produces wrong issue states.
Verification: reconciler.md Execute section step 3; SKILL.md Phase 6.3 disposition table.

## Red-Team

The EVALUATE `red-team` stance owns the adversarial verdict that drives the Phase 3 transition. (Phase 3 Review runs the conformance `reviewer` first as a mechanical gate, then the `red-team`.)

REQ-AGENT-040: The red-team produces a verdict of APPROVE, REVISE, or INVESTIGATE-MORE.
Rationale: Clear signal to the operator; ambiguous feedback stalls the workflow.
Verification: red-team.md Output section.

REQ-AGENT-041: Every concern in a red-team review shall carry a severity and a recommendation,
emitted in **one shape**: a `## Concerns` table whose `Severity` column holds exactly one token
from the closed vocabulary REQ-DATA-076 ratifies — `high | medium | low | medium-high |
low-medium` — with **no qualifier suffix**.
Rationale: Concerns without actionable recommendations don't help the operator fix them. The
*shape* half is newer and is the plan-059 amendment: the earlier text named `high/medium/low`
while the template emitted a bulleted `— severity: …` line, so the vocabulary was neither closed
nor mechanically readable. `doc_lint`'s `cell-vocabulary` check locates its column by header name
in a table; a bulleted list has no column, so the pin bound only historical tables and never the
pass being written. The suffix exclusion is not stylistic — `medium (blocking)` is the exact token
that fired research 005's severity-decay detector on `plan-026`.
Verification: red-team.md Output template and Rules carry the table form and the ratified tokens;
`doc_lint --type review` reports a `cell-vocabulary` finding (at `R`) for any off-vocabulary cell,
asserted by `skills/yf-plan/scripts/test_severity_vocabulary.py`.

REQ-AGENT-042: High-severity concerns block approval.
Rationale: Proceeding with known high-severity issues produces plans that fail during execution.
Verification: red-team.md Rules: "High blocks approval."

REQ-AGENT-043: The red-team agent is **read-only with respect to the repository under review** — it never writes files in that repository. A **sandbox spike is authorized**: it may build and run throwaway code in a scratch directory outside the repository (e.g. `$(mktemp -d)`) whenever a claim is cheaper to *test* than to reason about, and shall leave no residue. `reviews/pass-N.md` and the `log.md` `review:` line are written by the main session **at red-team presentation** (create-on-present, #4) as a single atomic step, then the same file is updated in place as concerns are resolved (REQ-PORT-006/008). The resolver is **actor-agnostic**: under the autonomous default the main session resolves concerns and re-runs the red-team itself; under a checkpointed run the operator resolves them. The resolving actor is recorded in the Resolutions table's `actor` column (REQ-PORT-008).
Rationale: Agents that write files outside their dispatch scope violate agent isolation (REQ-AGENT-050 sibling) and make the review capture path non-auditable. Keeping the red-team read-only lets the main session atomically write the review artifact and the phase-log entry together; writing at presentation (not after resolution) makes the verdict portable while the plan is still parked in `review`. Naming no specific resolver keeps the requirement true under both autonomy levels; the read-only clause is independent of who resolves and is also GR-PLAN-002. **The read-only clause scopes the *repository under review*; it never forbade building something in a scratch directory and running it** (#182). The prohibition was a reasonable reading of silence, so the defect was under-specification rather than a wrong rule. Measured provenance: a review pass that *built* the thing it doubted caught a specification defect that four prose-only passes had read past. Prefer a spike whenever a claim is cheaper to test than to reason about.
Verification: `uv run skills/yf-plan/scripts/test_review_agent_contract.py && grep -qF "Read-only with respect to the repository under review" skills/yf-plan/agents/red-team.md && grep -qF "A sandbox spike is authorized" skills/yf-plan/agents/red-team.md`

REQ-AGENT-046: The red-team checks **gate reachability**, not only gate well-formedness: for each capability gate, its `Condition` must be satisfiable given what the gate `Blocks`. A condition that depends on evidence produced by an issue inside its own `Blocks` set is a cycle and is reported as a defect; the remedy is to gate the *mutating* step rather than the step that produces the evidence.
Rationale: A well-formed gate can still be unsatisfiable. In d3-pxe plan-013 a capability gate whose condition required a preview of the output of the very issue it blocked survived conformance and **two** red-team cycles, because every pass checked that the gate declared a type, approvers, a condition, and a test — none checked whether the condition could ever become true. The same cycle was independently reproduced in this skill's own plan-039 draft.
Verification: red-team.md Evaluate → Gates carries a "Gate reachability" item asking whether each `Condition` is satisfiable given its `Blocks` set.

REQ-AGENT-047: The red-team performs a **precondition cross-check**: for each issue, the artifacts, tools, and capabilities its text assumes are either produced by a declared `depends-on` predecessor or established by a gate. Each unmet precondition is reported together with the node that needed it.
Rationale: Across the five defects observed in d3-pxe plan-013, the precondition was written out in plain English in the issue body every time; only the machine-readable dependency edge was missing. A prose-vs-DAG cross-check therefore has enough information to catch them without a schema change. This is deliberately the prose check, not a topological DAG walk: the expensive branch (a `requires:` key plus a walk engine) was measured against the same corpus and found to buy nothing, and 2 of the 5 defects are not reachability failures a graph walk would find at all.
Verification: red-team.md Evaluate carries a "Precondition cross-check" item; it introduces no `requires:` schema key and no DAG-walk engine.

REQ-AGENT-048: The red-team performs a **premise check**: for each finding an epic, gate, or success criterion depends on, it asks whether the finding is a measurement or an inference; if inferred, whether an independent signal corroborates it; and **what would falsify it, and whether that was checked**.
Rationale: Both review passes reason about a plan's internal coherence, so a plan can be perfectly coherent and rest on a false premise — no pass re-tests the facts underneath it. The falsification prompt is the load-bearing part: it is answerable in seconds and askable with no domain expertise. Pairs with REQ-AGENT-021, which makes the measured/inferred distinction visible in the finding the red-team reads.
Verification: red-team.md Evaluate carries a "Premise check" item including the falsification question.

REQ-AGENT-049: The adversarial (red-team) pass **shall be dispatched as a sub-agent**, not performed by the main session. SKILL.md Phase 3 Review step 2 spawns a sub-agent whose prompt reads `agents/red-team.md`, mirroring the Phase 2 INVESTIGATE dispatch form. The main session remains the sole writer of `reviews/pass-N.md` and the `log.md` `review-pass:` line (REQ-AGENT-043).
Rationale: A red-team pass run by the main session is reviewing its own draft — it shares every assumption it is supposed to attack, so a concern the drafter cannot see is a concern the review cannot raise. The asymmetry was verbatim in the skill text: Phase 2 said **spawn** and Phase 3 said **perform**, so following Phase 3 literally produced a self-review. Measured on plan-050, concerns per review pass ran 5 → 4 → 11 → 17 → 14, with the discontinuity at the first dispatched pass; passes 1–2 were main-session self-review and had advanced the plan to `ready-for-approval`. **Honesty clause:** this requirement constrains the *text* that specifies dispatch, not reviewer conduct — that a reviewer actually obeyed a rule has no exit code, and no verification here claims otherwise (#184, R2/R3).
Verification: `uv run skills/yf-plan/scripts/test_review_agent_contract.py && grep -qF "Spawn a sub-agent to perform the adversarial pass" skills/yf-plan/SKILL.md`

## Reviewer (conformance)

The EVALUATE `reviewer` stance is a mechanical conformance/completeness pass. It runs **first** in Phase 3 Review, as a gate before the `red-team`. It is distinct from the `red-team`: yf-plan deliberately carries both stances (the asymmetry vs yf-research, which has only `red-team`, is justified by the factoring test — semantic plan conformance warrants a dedicated pass).

REQ-AGENT-044: The reviewer produces a conformance verdict of PASS or INCOMPLETE against a mechanical checklist: every epic has ≥1 issue and every issue a clear deliverable; every intra-plan `depends-on` references an existing issue and the graph is acyclic; every Success Criterion is verifiable (names a command/file/grep); every upstream `include`/`partial` is wired to a resolving issue; every gate declares type + approvers (+ condition/test for capability gates); plan.md carries all required portability sections. It runs before the red-team pass and produces no `pass-N.md`.
Rationale: A mechanical completeness gate catches structural gaps before the adversarial pass spends attention on a plan that is merely incomplete; its PASS|INCOMPLETE contract is distinct from the red-team's APPROVE|REVISE|INVESTIGATE-MORE verdict.
Verification: reviewer.md Checklist + Output sections; SKILL.md Phase 3 Review step 1 reads the conformance verdict and gates on PASS.

REQ-AGENT-045: The reviewer is **read-only with respect to the repository under review** and conformance-only. It does not assess feasibility, risk plausibility, or approach soundness — those belong to the red-team. It never writes files in that repository. The same **sandbox spike** carve-out as REQ-AGENT-043 applies: it may build and run throwaway code in a scratch directory outside the repository and shall leave no residue.
Rationale: Separating the conformance and adversarial stances into non-interfering agents (the factoring test, case b) keeps each prompt focused and prevents the mechanical checklist from drifting into judgment calls. The spike carve-out is applied to both review agents together (D-8): `reviewer.md` carried the identical read-only sentence, and rewording only the red-team would leave the two agents contradicting each other on one constraint.
Verification: `uv run skills/yf-plan/scripts/test_review_agent_contract.py && grep -qF "Read-only with respect to the repository under review" skills/yf-plan/agents/reviewer.md && grep -qF "A sandbox spike is authorized" skills/yf-plan/agents/reviewer.md`

## Captor

REQ-AGENT-060: The captor drafts missing portability-contract files (the reserved `index.md`, context.md, motivation, references/upstream-*.md, reviews/pass-*.md) from current plan state. Invoked by `/yf-plan capture` via SKILL.md Phase: CAPTURE.
Rationale: Operators should not have to hand-write portability scaffolding when the plan folder already contains enough state to derive it. The captor centralizes the drafting heuristics.
Verification: `agents/captor.md` Draft section enumerates the contract files; SKILL.md Phase: CAPTURE dispatches to `agents/captor.md`.

REQ-AGENT-061: The captor is read-only. It returns drafts for review and never writes files. The main session writes on approval. The **approving actor is actor-agnostic**: under the autonomous default the main session reviews and approves the drafts it then writes; under a checkpointed run the operator approves first.
Rationale: Mirrors the read-only review-agent pattern (REQ-AGENT-043/045). Keeps agent dispatch scope small and makes the write path auditable.
Verification: `agents/captor.md` Rules state the captor never writes files and that the main session writes after approval, without naming a fixed approving actor.

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

## Lander

REQ-AGENT-065: *(added plan-060 Issue 0.4)* The `lander` agent is **read-only with respect to the
repository under review** — it never writes files in that repository. A **sandbox spike is
authorized**: it may build and run throwaway code in a scratch directory outside the repository
(e.g. `$(mktemp -d)`) and shall leave no residue.

It **emits a decision document and never a command.** Its output is a data structure — groupings,
titles, rationales, body paths, and per-step `enable`/`skip` choices with reasons — carrying no
shell invocation an executor could lift and run. `plan_manager.py land --apply` is the sole writing
layer (REQ-LAND-001), and it trusts the decision for **judgements only**, re-deriving every fact
and halting on a `manifest_digest` mismatch (REQ-LAND-002).

**The main session writes the decision file**, exactly as it writes `reviews/pass-N.md` for the
red-team (REQ-AGENT-043). The agent returns content; the session persists it.
Rationale: an agent that both decided and acted would hold write authority over the default
branch, the upstream tracker, the worktree set and the installed toolchain — the
highest-privilege role in the system. `dixson3/yoshiko-flow#293` is an executing agent closing a
consent gate by writing its own authorization into the close reason; a lander with write authority
is that defect at larger scale. Because there is no field in the decision document in which a
condition, an exit code or a consent can be asserted, the agent **cannot** fabricate an
authorization — a structural property rather than a procedural rule.
Verification: **executed** —
`bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_lander_agent_contract.py test_lander_contract`,
which asserts both verbatim sentences, the front-matter shape, the fenced `## Output` template, and
that the file contains no liftable imperative shell command.

> **What that verification does NOT establish, stated rather than left to be discovered.** The
> textual half of this check — including the `grep -qF` form the sibling requirements REQ-AGENT-043
> and REQ-AGENT-045 use — verifies that **the instruction was written**. It can never verify that
> **the instruction was obeyed**. The two are different claims, and a green `grep` on the first has
> repeatedly been read as evidence for the second.
>
> The behavioural half is therefore a **separate, paired check** (plan-060 Issue 2.6): assert
> `git status --porcelain` is **empty across a lander dispatch**, so a lander that writes to the
> repository is caught by observation rather than by trusting its own prompt. Neither half
> substitutes for the other, and this requirement is satisfied only by both:
>
> `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_lander_agent_contract.py test_dispatch_leaves_tree_clean`
>
> This is the same honesty clause REQ-AGENT-049 carries for dispatch, applied to read-only-ness:
> conduct has no exit code unless something observes the conduct.
