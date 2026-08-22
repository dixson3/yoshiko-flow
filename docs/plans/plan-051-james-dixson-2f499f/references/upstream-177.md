---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #177: yf-plan red-team: no check that a numeric target is derivable from the plan's own scope rules

- **Number:** 177
- **Title:** yf-plan red-team: no check that a numeric target is derivable from the plan's own scope rules
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/177
- **State:** OPEN
- **Labels:** 

## Body

## A numeric target can be fixed-at-approval, falsifiable, and still contradict the plan's own rules

Every red-team pass in plan-047 verified that its residue target was **fixed at approval** — the
property REQ-PLAN-033's discipline is about. **Not one verified that the target was DERIVABLE FROM
WHAT THE PLAN PERMITS.** Those are different properties, and the second was false the whole time.

### Instance 1 — plan-047's residue target (measured at execution)

The target of **54** came from EXP-001's *"~96 of 150 mechanically recoverable"* — a figure that
counted a construct as recoverable if a rule *could* produce an edge from it. In the same finding,
EXP-001 warned that several of those classes produce the **wrong** edge, having measured a prototype
silently emptying 20 `depends-on` declarations. The plan adopted that warning as Issues 1.4/1.4a's
refusals **and** kept the target derived from the optimistic half.

The two were never reconcilable. Execution measured a residue of **81**, the gate went red for the
right reason, and the operator re-based the target with the corrected derivation recorded.
Seven review cycles did not catch it.

### Instance 2 — plan-048's SC5 vs D-10

`SC5` required every instantiated type's fixture to drive exit 1. `D-10` forbade an `E`-severity
check on any path outside a plan bundle unless the corpus already passed it — measured, because
`bundle_status` is null off the plan axis so `STATUS_SEVERITY` cannot soften. **Five `W`-only types
could not reach exit 1 without an `E` that D-10 forbids.** Resolved in D-10's favour at execution,
recorded as a deviation.

Both criteria were individually well-formed. Neither was checked against the other.

### Proposed change

Add a check to `red-team.md`'s procedure:

> **Target derivation.** For every numeric target, threshold, or floor a criterion asserts, state
> its derivation and check it against the plan's own scope decisions, refusals, and out-of-scope
> declarations. *"Is this number fixed at approval?"* and *"is this number reachable given what
> this plan is allowed to do?"* are different questions, and only the second catches a target
> inherited from the optimistic half of a finding whose pessimistic half the plan also adopted.
>
> Likewise, for every pair of criteria and every criterion-vs-decision pair, ask whether satisfying
> one forecloses the other. A criterion can be perfectly falsifiable in isolation and unsatisfiable
> in context.

### Related

- plan-047 `assets/residue-analysis.md` (the re-derivation)
- plan-048 `plan-retrospective.md` RE-004 (the SC5/D-10 conflict)

