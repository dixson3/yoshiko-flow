---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #217: yf-change-validation: `change_validation.py` persists no run record

- **Number:** 217
- **Title:** yf-change-validation: `change_validation.py` persists no run record
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

**Measured:** plan-052 EXP-004 §4 (recorded as D-13).

`change_validation.py` **persists nothing** about a run. There is no record of what ran, when,
against which tree, or with what verdict.

It is the shared prerequisite for **two** predicates plan-052 scoped and then could not build:

- **P5**, the recipe-row predicate — "did this row actually run?"
- **P6**, the criterion-re-check predicate — "when was this criterion last re-run?"

Neither question is answerable without a run record, which is why plan-052 **filed this rather
than building it**: building it would have pulled both predicates into scope with it.

*Filed by plan-052 as a deliberately deferred defect. Full enumeration:
`docs/plans/plan-052-james-dixson-fa8056/assets/deferred-defects.md`.*
