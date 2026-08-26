---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #208: update-status accepts out-of-vocabulary statuses silently — strands the plan AND relaxes doc_lint (STATUS_SEVERITY fails open)

- **Number:** 208
- **Title:** update-status accepts out-of-vocabulary statuses silently — strands the plan AND relaxes doc_lint (STATUS_SEVERITY fails open)
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/208
- **State:** OPEN
- **Labels:** type::bug, priority::high

## Body

## Summary

`update-status` accepts **any** string as a plan status with no validation. Writing an out-of-vocabulary value strands the plan: it becomes invisible to `parked`, ineligible for `execute`, and — less obviously — it **silently changes what `doc_lint` enforces**.

The docstring says the writer is free-form by design:

> The writer is otherwise **free-form** — it accepts any status string and does not validate against an enum. The status vocabulary is the source of truth in SPEC.md (REQ-PLAN-001) and the SKILL.md Phase Model "Status values:" line

That is a defensible design choice for the *writer*. The problem is that three downstream consumers key on the vocabulary and each fails differently and silently when it is violated.

## Measured

Set `status: incomplete` (intending "parked, do not resume") on a plan that had been `approved`. `update-status` accepted it with exit 0. Consequences:

**1. Invisible to every nudge.** `_is_parked` requires status `approved` exactly:

```
$ plan_manager.py parked
No parked plans.
```

`list --json-output` → `"parked": false`. The `/yf-plan status` nudge and the land-the-plane parked check will never surface this plan again — the opposite of what "parked" was meant to achieve.

**2. Ineligible for `execute`.** SKILL.md §5.1 filters candidates for `approved` (or `executing`). `incomplete` is neither, and **no documented transition leads out of it**.

**3. `doc_lint` silently relaxes.** This is the subtle one. `STATUS_SEVERITY` has no `incomplete` key, so findings fall through to their declared severity instead of being promoted:

- under `review` / `ready-for-approval`: `WARN → ERROR`
- under `approved`: `{WARN: REPORT, ERROR: REPORT}`
- under `incomplete`: **no mapping** → declared `W`

So the `upstream-cells-filled` finding (#185) showed as `W` and the document returned `verdict: PASS`. That green is an artifact of an unrecognised status, not a clean document — and it is exactly the kind of green that gets read as "the linter agrees this is fine."

## Suggested fix

Not necessarily to make the writer strict — the free-form docstring gives a real reason for that. Options, roughly in order of cost:

1. **Warn on write.** If the status is not in the SPEC.md vocabulary, emit a warning naming the vocabulary and the known consequences. Cheap, preserves free-form, kills the silence.
2. **Make `STATUS_SEVERITY` fail closed.** An unrecognised status should map to the *strictest* profile, not the most permissive. A status the linter does not recognise is the last one whose findings should be downgraded.
3. **Add a real parked/incomplete status** to the vocabulary, `STATUS_SEVERITY` and `_is_parked`, if "approved but deliberately not executing" is a state worth having. It clearly is — that is what this plan needed and why an out-of-vocabulary value got invented.

## Context

Found in `dixson3/astrospike` `plan-001`, which was parked as `incomplete` after an aborted pour (#186/#187) and then could not be brought back without hand-editing. Related: #206 (extractor drop-through), #207 (`resume-scan` and burned epics) — all three surfaced on the same recovery path.

