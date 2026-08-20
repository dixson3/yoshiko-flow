---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #178: yf-plan: generate the upstream-write authorization grant FROM the Upstream Issues table, not the draft list

- **Number:** 178
- **Title:** yf-plan: generate the upstream-write authorization grant FROM the Upstream Issues table, not the draft list
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## An upstream-write authorization grant should be GENERATED from the Upstream Issues table

plan-048 halted its own reconcile because the operator's authorization grant was **hand-listed from
the drafted comments** rather than derived from the plan's `## Upstream Issues` table.

`#172` carried disposition `include`. `REQ-PLAN-074` requires an `include` row to reach **CLOSED**
with a plan-id mention. The grant listed the tracker, the `#175` supersede and the three comments —
and did not list closing `#172`, because no *draft* existed for it. The subordinate correctly
refused to close it ("any upstream write not listed above is not authorized"), and
`verify-reconcile` — a **halting** §6.4 step — failed on that one row.

The omission was in the grant, not the plan: the required end state was mechanically derivable from
the table the whole time.

### Proposed change

Add a verb, or a documented step in `SKILL.md` §6.2 / the Upstream-write gate's Instructions:

> **Generate the grant from the table, never from the draft list.** For each non-`exclude` row of
> `## Upstream Issues`, emit the end state `REQ-PLAN-074` requires — `include` → CLOSED with a
> plan-id mention; `supersede` → CLOSED / NOT_PLANNED; `partial` → OPEN with a mention; `deferred`
> → OPEN, no action. A draft-derived grant systematically omits every row whose required action is
> a **close** rather than a **comment**, which is precisely the row that halts reconcile.

A `plan_manager.py grant --json` verb emitting the authorized action set would make this mechanical
and auditable; the gate's `test -f` sentinel could then be checked against it.

### Related

- plan-048 `assets/upstream-authorization.txt` and its amendment
- plan-049 already carries the lesson in its gate Instructions; this issue is the upstream fix

