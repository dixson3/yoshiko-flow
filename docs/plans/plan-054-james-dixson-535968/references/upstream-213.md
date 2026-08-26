---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #213: bd: `distill` cannot reconstruct gate steps — non-idempotent against bd's own pour

- **Number:** 213
- **Title:** bd: `distill` cannot reconstruct gate steps — non-idempotent against bd's own pour
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

**Measured:** plan-052 EXP-005, finding I-4(iii).

`bd distill` cannot reconstruct gate steps, so **pour -> distill -> pour does not round-trip**:
the gate is lost on the way back. distill is therefore non-idempotent against bd's *own* pour
output, which is the one input it should handle perfectly.

Consequence: distill cannot be used to recover or migrate a molecule that contains a gate
without silently dropping the gate.

*Filed by plan-052 as a deliberately deferred defect. Full enumeration:
`docs/plans/plan-052-james-dixson-fa8056/assets/deferred-defects.md`.*
