---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #334 - `_land_tty_gate(allow_list=[None])` opens the
  consent gate unconditionally, and its test is vacuous'
---
# Upstream #334: `_land_tty_gate(allow_list=[None])` opens the consent gate unconditionally, and its test is vacuous

- **Number:** 334
- **Title:** `_land_tty_gate(allow_list=[None])` opens the consent gate unconditionally, and its test is vacuous
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

## Two defects, one site

### 1. `allow_list=[None]` is a total bypass

`_land_tty_gate` decides the escape with:

```python
if not allowed and allow_list and record.get("tty") in allow_list:
    allowed = True
```

In a no-tty environment `record["tty"]` is `None`. So `allow_list=[None]` satisfies
`None in [None]` and the gate opens. Measured:

```
no allow_list     -> False | tty = None
allow_list=[None] -> True  | allowed_by = operator-configured allow-list
```

The record even attributes it to an "operator-configured allow-list", which is the most
misleading possible label for a value that matches *because both sides are absent*.

**Scope, stated honestly:** `land_cmd` calls `_land_tty_gate()` with no `allow_list`, so this
is **latent, not reachable through the shipped CLI today**. It is filed because the escape is
one caller away and because `#293` is already an instance of an executing agent closing this
exact gate by asserting its own authorization.

### 2. The test that should catch it cannot

`test_land_apply.py:384`:

```python
allowed = pm._land_tty_gate(allow_list=[g["route_record"]["tty"] or "/dev/ttys999"])
assert allowed["allowed"] is False or allowed["route_record"].get("allowed_by")
```

Under CI/agent conditions `tty` is `None`, so `None or "/dev/ttys999"` yields
`["/dev/ttys999"]` — which never matches the actual `tty` of `None`. The gate refuses, the
**first disjunct is `True`**, and the assertion passes **without ever exercising the
allow-list**. The `or "/dev/ttys999"` fallback, added to make the test runnable, is precisely
what makes it measure nothing.

This is the `#263` vacuous-check class.

## Suggested fix

- Guard the membership test: `record.get("tty") is not None and record["tty"] in allow_list`.
- Replace the vacuous assertion with two directed cases — a matching allow-list entry that
  **does** open the gate, and `allow_list=[None]` that **must not**.

Found while executing plan-062 (`docs/plans/plan-062-james-dixson-c3e98f`); recorded in
`findings/exp-001`.

