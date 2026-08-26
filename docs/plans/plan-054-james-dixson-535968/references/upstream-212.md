---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #212: bd: a `type = "gate"` step with no `[steps.gate]` pours as a plain task, with no diagnostic

- **Number:** 212
- **Title:** bd: a `type = "gate"` step with no `[steps.gate]` pours as a plain task, with no diagnostic
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

**Measured:** plan-052 EXP-005, finding I-4(ii).

A formula step declaring `type = "gate"` but omitting the `[steps.gate]` table **pours as a
plain task**, silently. No warning, no error.

The result is a DAG that looks correctly poured and **gates nothing** — the author believes
work is held pending a condition, and it is not. A formula-authoring mistake becomes an
invisible correctness hole in the execution graph.

**Expected:** reject the formula, or pour the gate with a default, but never degrade silently.

*Filed by plan-052 as a deliberately deferred defect. Full enumeration:
`docs/plans/plan-052-james-dixson-fa8056/assets/deferred-defects.md`.*
