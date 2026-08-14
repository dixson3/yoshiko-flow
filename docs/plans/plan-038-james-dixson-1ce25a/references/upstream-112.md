---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #112: yf-plan: red-team should check gate REACHABILITY, not just gate well-formedness

- **Number:** 112
- **Title:** yf-plan: red-team should check gate REACHABILITY, not just gate well-formedness
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## The defect this would have caught

In `d3-pxe` plan-013, a capability gate was authored like this:

- **Condition:** operator has previewed `ansible-playbook host.yml --check --diff --tags otel_agent` for Issue 5.1, and authorises the apply
- **Blocks:** 5.1

That gate is **unsatisfiable**. It blocks Issue 5.1 in its entirety — including *authoring the change* — but its condition requires a preview of that change. The block prevents the artifact whose existence the condition depends on. A cycle.

It survived **all three** existing review passes:

- **Conformance** (`agents/reviewer.md`) checks "every gate declares a type + approvers (capability gates also declare a condition + test)". All four fields were present. Pass.
- **Red-team** (`agents/red-team.md`) checks "Gates: Only used where genuinely needed? Test commands valid? Instructions sufficient?" The gate was needed (a real host mutation under a SPEC requirement), the test command was valid shell, the instructions were sufficient. Pass — twice, across two REVISE cycles that found other real defects.

Nothing asks whether the condition is **reachable from the state the gate creates**.

## Root cause in the authored plan

The plan conflated two different actions: authoring the change and running `--check` are **read-only**; only the apply mutates. The governing requirement (`PVE-OBS-001`) gates the *apply*. Writing `Blocks: 5.1` gated the whole issue instead of the mutating step.

The fix was to split the issue into `5.1a` (author + produce preview evidence, ungated) and `5.1b` (apply, gated), and rewire the gate to block only `5.1b`.

## Proposed change

Add a gate-reachability item to the red-team `Evaluate` section — or better, to the conformance checklist, since it is pass/fail rather than judgment:

> **Gate reachability:** for each capability gate, can its `Condition` be satisfied *given what it blocks*? A gate whose condition depends on evidence produced by an issue in its own `Blocks` set is a cycle and is unsatisfiable. Gate the mutating step, not the step that produces the evidence.

Conformance is arguably the better home (mechanical, pass/fail), but note it currently runs before the DAG is fully drafted — so either it runs later, or this lands in red-team.

## Caveat

Single-plan evidence: one escape out of four real defects found. Suggestive, not conclusive. See the companion issue on an execution-rehearsal pass for the more general framing — this issue is the cheap targeted patch; that one is the structural fix.
