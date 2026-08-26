---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #227: yf-incubator: STATUS_VALUES is dead code — #208's defect one skill over

- **Number:** 227
- **Title:** yf-incubator: STATUS_VALUES is dead code — #208's defect one skill over
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

Measured by plan-053 (EXP-004), re-verified on the merged tree.

## The defect

`skills/yf-incubator/scripts/incubator-index.py:47` defines a status vocabulary and **never
reads it**:

```console
$ grep -c STATUS_VALUES skills/yf-incubator/scripts/incubator-index.py
1
```

One occurrence in the whole file — the definition itself.

```python
STATUS_VALUES = {"incubating", "scoping", "exploring", "converging",
                 "concluded", "parked", "abandoned"}
```

## Why it matters

This is **#208's shape exactly, one skill over**: a status vocabulary that *looks* enforced and
enforces nothing. An out-of-vocabulary incubator status is accepted in silence, which is the
condition that produced #208 in `yf-plan` — an operator with no legal state for their case
invents one, and nothing says a word.

plan-053 closed the `yf-plan` instance (`REQ-CLI-026` warns on an unrecognised write;
`REQ-DATA-072` makes `doc_lint`'s `STATUS_SEVERITY` fail closed) and deliberately did not reach
into another skill's runtime.

## Note on the fix

The set **already contains `abandoned`**, so the remedy is to **read** it, not to extend it.
The `yf-plan` precedent is worth copying rather than re-deriving: warn on stderr, still write,
still exit 0 — the defect is the silence, not the permissiveness.

## Evidence

- `docs/plans/plan-053-james-dixson-4015d3/findings/exp-004-status-vocabulary.md`
- `docs/plans/plan-053-james-dixson-4015d3/assets/deferred-defects.md` § D3

Filed by plan-053 Issue 7.2.

