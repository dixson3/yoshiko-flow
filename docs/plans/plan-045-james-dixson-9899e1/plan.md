---
type: Plan
okf_spec: OKF-PLAN
id: plan-045-james-dixson-9899e1
author: james-dixson
created: '2026-08-17'
status: investigating
---
# Plan: Make plan execution and review autonomous by default, with human gates frontloaded: self-resolving review cycles, a non-stopping coordinator loop, an execute-start gate sweep, and push-based herdr delegation

**ID:** plan-045-james-dixson-9899e1
**Author:** james-dixson
**Created:** 2026-08-17
**Status:** investigating

## Objective
Make plan execution and review autonomous by default, with human gates frontloaded: self-resolving review cycles, a non-stopping coordinator loop, an execute-start gate sweep, and push-based herdr delegation

## Motivation

Across the last several plan executions the operator observed that plans **do not run
unattended**: they stop between epics rather than only at pre-declared human gates, and the
planning phase is equally conservative — each red-team cycle needs a manual acknowledgement
before the next one runs. The operator's requirement, stated directly:

> "when a plan is executed i want to have it run completely autonomously and only stop at human
> gates, further, ideally those human gates should be as 'frontloaded' as possible so the operator
> can answer questions/perform actions before the bulk of the coding work runs whenever possible…
> i want things to run autonomously as much as possible by default and only seek manual, operator
> acknowledgement when explicitly asked or when explicitly necessary."

This is a **class**, not a one-off — it reproduced across plans and in both phases — so per the
deviation-mining rule the fix belongs upstream in the skills, not in any single plan.

Diagnosis (this session, verbatim-cited, see Investigation Findings) found **three independent
textual causes** plus a fourth in the delegation layer. None is a model quirk; all four are
skill-text defects. One empirical control: plan-044 was launched with a hand-written autonomy
clause in its prompt and ran 20+ minutes unattended across multiple epics — the same skill, the
same model, differing only in that one instruction.

Who is affected: every operator running `/yf-plan execute`, and every delegated herdr session.
The cost is not just interruption — a stop mid-DAG splits the work across context windows and
invites the operator to re-decide things the plan already settled.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|

## Investigation Findings

_Six experiments dispatched; findings land in [findings/](findings/) as they complete._

**Pre-investigation checkpoint — the four diagnosed causes (evidence gathered this session):**

1. **Review cycles.** `yf-plan` SKILL.md Phase 3 grants autonomy to the conformance step
   ("resolve the listed gaps and re-run before proceeding — this is a mechanical gate, not a
   phase transition") and the very next step ends "Present the red-team verdict and concerns to
   the operator." The REVISE branch's "address concerns" has **no subject**, and is
   disambiguated toward the operator four more times, plus normatively in
   `spec/agents.md` REQ-AGENT-043. The `pass-N.md` **"Operator Resolutions"** table reifies it
   as a data structure. The correct pattern already exists in `agents/reviewer.md`
   ("**the main session** resolves the gaps").
2. **Execution.** In `agents/coordinator.md`, "Wait for operator" is the **only** explicit wait
   and is the loop's documented exit; because loop step 2 treats a failing gate test as
   "mark blocked, skip", an ordinary unsatisfiable gate routes straight there. "Report blocked
   gates" appears **5×** across the skill; "continue to the next bead" appears **0×**.
   Completion is written as a control transfer ("hand back to RECONCILE") although SKILL.md
   states "The coordinator IS the main session" — it hands back to itself.
3. **Gate frontloading.** Exhaustive grep for `frontload|up front|as early|gate placement`
   returns **zero hits**; the only topological rule (`agents/red-team.md`) prescribes the
   opposite ("gate the mutating step"). But the mechanism exists unused: the Start Gate is
   `Type: human` yet resolved non-interactively at execute start, and a capability gate whose
   `Test:` passes is auto-resolved and never prompts. **Nothing evaluates capability-gate tests
   at execution start** — they are only checked deep in the DAG.
4. **herdr delegation.** Child→parent push works **today** (`herdr agent prompt <pane-id>` with
   `--wait` omitted; `--wait` is opt-in and the only blocking behavior). But the launch recipe
   carries no autonomy clause, the fix exists only as advisory prose under `## Observe`
   ("If autonomy is wanted, say so explicitly") read *after* the prompt is composed, grep for
   `autonom` in yf-herdr SPEC.md returns **no match**, and the child is never told the parent
   exists. Polling is normative in REQ-HERDR-021.

## Approach

_Hypothesis, pending investigation._ **Autonomy is the default; stopping is the exception that
must be justified** — and every stop must be *mechanical* (an exit code or a counter), never a
judgement call, per #149's thesis that a step with no exit code is not a step.

### Scoping decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D-1 | Autonomy is **configurable** (`.yf-plan.local.json`) with an **autonomous default**, plus a **per-invocation override** | Mirrors `landing-strategy` / `execute.worktree`; keeps a cautious escape hatch for a risky plan without making caution the default |
| D-2 | The **irreducible stop set** is exactly four classes: outward-facing/irreversible writes; a capability gate whose `Test:` fails; destructive local ops; and scope ambiguity **only after a mechanical threshold** | Everything else becomes report-and-continue. Naming the set is what makes "stopping is the exception" enforceable rather than aspirational |
| D-3 | The ambiguity threshold counts **consecutive failed resolution attempts on the same bead**, resets on success, `N` configurable | Mechanical and per-bead; it is exactly the loop where an agent thrashes. Without a counter, "scope ambiguity" is a loophole that re-admits arbitrary stopping |
| D-4 | **REVISED after exp-003.** Gates become **structured beads** at creation (`gate_type`, `test`, `test_class`, `cwd` in metadata) so the sweep reads fields instead of parsing prose. The execute-start sweep then runs **only the SAFE-PROBE class** (~3s measured) and batches everything else into **ONE prompt** before any coding. `Type: human` gates are **never** auto-resolved | The scoped design was refuted: only 33% of live gates yield a runnable command; 59% are human-typed where a green test is explicitly not consent (auto-resolving would have granted publish authorization on 3 historical gates); most `auto` gates are *designed* to fail at t=0 because they assert the plan's own deliverables |
| D-7 | Fix the standalone bug exp-003 found: **`bd ready` never returns gate beads**, so `coordinator.md` loop step 2 has never fired | In scope because the coordinator loop is already being rewritten, and a sweep sharing one evaluate-gate routine with the lazy path requires the lazy path to work |
| D-5 | herdr child pushes to parent on **epic completion**, **blocker/failed gate/halt**, and **plan completion/abort** — never per bead | Per-bead would emit ~39 messages for a plan-044-sized DAG and flood the parent's context |
| D-6 | `plan-retrospective.md` is **emit-only** here: this plan defines the schema and writes an entry at every stop/intervention event. Analysis and the frontloading consumer stay with #145 | A consumer built today would read an empty corpus. Emit first, accumulate, then build the reader |

## Epics
_To be determined._

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

## Risks & Mitigations
_To be determined._

## Success Criteria
_To be determined._
