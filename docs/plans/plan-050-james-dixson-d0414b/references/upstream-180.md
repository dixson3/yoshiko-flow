---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #180: yf-plan: close-reconcile-step requires the reconcile gate resolved first — undocumented chain ordering

- **Number:** 180
- **Title:** yf-plan: close-reconcile-step requires the reconcile gate resolved first — undocumented chain ordering
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## `close-reconcile-step` requires the reconcile GATE resolved first — undocumented ordering

`SKILL.md` §6.4's close chain lists `close-reconcile-step` before `verify-reconcile`, cascade-close
and the completion gate. It does not state that the **reconcile gate** must be resolved before
`close-reconcile-step` can succeed.

plan-048's executor hit this: `close-reconcile-step` would not pass until the reconcile gate was
resolved, an ordering nowhere in the documented chain. It resolved it and continued, but the chain
as written is incomplete.

### Why it matters beyond one plan

§6.4 is an **ordered gate chain** whose whole contract (REQ-COMPLETE-001) is that ordering
constraints are declared rather than discovered. An undeclared constraint inside the chain that
declares its constraints is the same defect class as a step that passes without checking anything:
the document asserts completeness it does not have.

### Proposed fix

Add the constraint to §6.4's stated ordering, or make `close-reconcile-step` resolve the gate itself
when all execution beads are closed (it already has the information). Either way the chain's
documented order should be executable top to bottom without discovery.

### Related

- plan-048 execution, §6.4 chain

