---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #109: yf-plan: stale_approved is computed status-independently, so completed plans display "re-review before execute" forever

- **Number:** 109
- **Title:** yf-plan: stale_approved is computed status-independently, so completed plans display "re-review before execute" forever
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

`plan_manager.py list` (and `status`) tag a **completed** plan with:

```
⚠ STALE-APPROVED (re-review before execute)
```

For a plan in a terminal state this advice is not merely noisy, it is wrong: there is nothing to re-review and nothing to execute.

## Cause

In `_list_plans()` (`scripts/plan_manager.py:942-948`) the two advisory flags are computed asymmetrically:

```python
fp_status = _fingerprint_status(d)
stale = fp_status.get("stale_approved", False)     # status NOT consulted
# Parked = approved but never executed (#86, REQ-PLAN-068). Mutually
# exclusive with stale_approved (freshness gate) by construction.
parked = _is_parked(status, fp_status)             # status consulted
```

`_is_parked()` takes `status`; `stale_approved` does not. It is purely `bool(stored) and stored != current` (`:1458`).

The comment claims the two are "mutually exclusive … by construction", which holds for `approved`, but says nothing about terminal states — and that is where the asymmetry surfaces.

## Why it fires on ordinary, correct execution

Execution is *supposed* to amend the plan folder. In the case that prompted this, `/yf-plan execute` legitimately:

- amended `plan.md` where investigation contradicted the plan (an experiment proved one of the plan's own risk mitigations false), and
- added two new findings discovered during execution.

That is the process working. But it moves the content hash, so the moment the plan reaches `complete` it is permanently tagged as needing re-review before an execution that already happened.

So the flag fires on **well-executed** plans specifically. A plan executed without learning anything would stay "clean".

## Suggested direction

Suppress the flag for terminal statuses — i.e. give `stale_approved` the same status-awareness `parked` already has, or gate the *display* in `list`/`status` at `:991` and `:2574`.

Worth deciding what the field should mean at `complete`. Two defensible readings:

1. **Execution-eligibility only** (what `resume-scan` uses it for, REQ-PORT-041) — then it is simply meaningless once terminal and should not render.
2. **"Content differs from what was approved"** — a genuinely useful audit signal, but then the message is wrong: it should say something like *"amended during execution"*, not *"re-review before execute"*.

Reading 1 matches the requirement it is documented against; reading 2 would want a distinct tag.

## Workaround used

Re-ran `fingerprint write` on the completed plan so the stored hash records the content *as executed*, with the reason in the phase log; the approval-time hash remains in git history. That clears the tag but is per-plan, and it also silently re-baselines a field an operator might reasonably expect to be immutable after approval — which is another argument for fixing the meaning rather than the value.

Worth noting a secondary effect: the stale flag was masking two genuine portability-audit failures (findings added during execution were missing OKF frontmatter). They only surfaced once the fingerprint was current.

## Not fixed here

Reported rather than patched — the script lives in the user-global skill install and a change affects every consuming project. Same disposition as #108.
