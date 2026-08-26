---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #225: plan_extract: a COLUMN-0 PARAGRAPH under an open issue is dropped silently (#206's third family member)

- **Number:** 225
- **Title:** plan_extract: a COLUMN-0 PARAGRAPH under an open issue is dropped silently (#206's third family member)
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

Measured by plan-053 (EXP-001), and re-verified **on the merged tree after both #206 fixes
landed** — so this is a surviving shape, not one those fixes were expected to reach.

## The defect

A column-0 paragraph inside `## Epics`, under an open issue, is dropped **silently**:

```text
unparsed: []
any issue detail carrying the column-0 paragraph: False
```

`--strict` exits 0. That is the same silent-loss signature #206 is about — content vanishes
while the extractor reports it read the document completely.

## Why plan-053 deliberately did NOT widen its fix to cover it

This is a real reason, not a scoping convenience. **A column-0 line is not a continuation
under CommonMark**, so collecting it into `detail` would be *wrong* — it would attribute plan
body to an issue, which is the very corruption plan-053's column-0 *fence* guard exists to
prevent (`ctl-206-dropped-continuation` assertion 5).

The right answer is most likely `unparsed[]`: the construct is non-conformant and the
extractor should say so rather than either swallowing it or ignoring it. That makes this a
**different change with a different risk profile**, needing its own RED fixture and its own
corpus delta, rather than a bigger version of #206.

## Evidence

- `docs/plans/plan-053-james-dixson-4015d3/findings/exp-001-extractor-drop-fix.md`
- `docs/plans/plan-053-james-dixson-4015d3/assets/deferred-defects.md` § D1

Filed by plan-053 Issue 7.2 as a measured, deliberately out-of-scope defect.

