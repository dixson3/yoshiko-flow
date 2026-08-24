---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #201: change_validation.py: repeated --changed silently drops all but the last path

- **Number:** 201
- **Title:** change_validation.py: repeated --changed silently drops all but the last path
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## The defect

`change_validation.py` declares `--changed` with `nargs="*"` and **no** `action="append"`, so a
caller passing the flag more than once silently keeps **only the last occurrence**. Every earlier
path is dropped without a warning.

**At source** — `skills/yf-change-validation/scripts/change_validation.py:946`:

```python
pr.add_argument("--changed", nargs="*", default=None,
                help="changed paths; FAST affected-scoping (§3)")
```

**Demonstrated**, with the same parser configuration:

```python
>>> ap = argparse.ArgumentParser(); ap.add_argument('--changed', nargs='*', default=[])
>>> ap.parse_args(['--changed', 'A', '--changed', 'B']).changed
['B']
```

`A` is gone. No error, no warning, exit 0.

## Why it matters

This is a **validation-coverage hole affecting every caller**. The FAST tier scopes to the ids
the changed paths select, so a caller that passes two paths and gets one validated **receives a
green that covers half its change-set** — and cannot tell from the output. The failure is silent
in the direction that hides work rather than the direction that fails loudly.

## Suggested fix

Either `action="append"` (with flattening, since `nargs="*"` yields lists), or an explicit error
when the flag is repeated. The second is arguably better: it cannot silently change the meaning of
an existing caller's command line.

## Scope note

Confirmed at source rather than taken on report. This affects **no invocation plan-051 makes** —
the FULL tier is invoked without `--changed` at all (`change_validation.py:820` gates `--changed`
on `tier == "fast"`, and `plan_manager.py:3529` hard-codes the FULL invocation without it), and
plan-051's own SC10 deliberately uses **two separate single-path invocations** rather than one
two-path run. Filed here so the fix is not private to that plan.

Found while executing plan-051-james-dixson-2f499f (Issue 4.6).

