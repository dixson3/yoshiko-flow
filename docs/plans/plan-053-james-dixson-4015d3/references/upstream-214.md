---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #214: yf-plan: `REQ-PLAN-073` id collision — two different requirements share one id

- **Number:** 214
- **Title:** yf-plan: `REQ-PLAN-073` id collision — two different requirements share one id
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/214
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

**Measured:** plan-052, D-18. Re-confirmed on the tree at execution time.

Two different requirements are both numbered `REQ-PLAN-073`:

- `skills/yf-plan/SPEC.md:345` — *"the plan and incubator roots shall be configurable"*
  (plan-037 / #107)
- `skills/yf-plan/spec/phases.md:150` — the **`stamp-tracker`** requirement (tracker URL
  stamped onto the plan epic as `external_ref`)

Reproduce:

```
grep -n 'REQ-PLAN-073' skills/yf-plan/SPEC.md skills/yf-plan/spec/phases.md
```

A cited id that resolves to two different requirements makes **every citation of it
ambiguous** — including the ones in `SKILL.md` §5.2a, which cite REQ-PLAN-073 meaning the
stamp.

**Expected:** renumber one of them and update its citations.

*Filed by plan-052 as a deliberately deferred defect. Full enumeration:
`docs/plans/plan-052-james-dixson-fa8056/assets/deferred-defects.md`.*
