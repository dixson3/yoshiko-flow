---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #211: bd: `distill --var` silently substitutes nothing and exits 0

- **Number:** 211
- **Title:** bd: `distill --var` silently substitutes nothing and exits 0
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

**Measured:** plan-052 EXP-005, finding I-4(i).

A `bd distill --var` pass produced output with the **placeholders still intact** and returned
**exit 0**. A caller therefore cannot distinguish a successful substitution from a complete
no-op — the success signal is identical in both cases.

This is the "a step with no exit code is not a step" class in its silent-success form: the
command reports success while having done nothing, so any pipeline that depends on
substitution having happened proceeds on unsubstituted text.

**Expected:** either substitute, or fail non-zero naming the unsubstituted variables.

*Filed by plan-052 as a deliberately deferred defect (out of scope for that plan). Full
enumeration: `docs/plans/plan-052-james-dixson-fa8056/assets/deferred-defects.md`.*
