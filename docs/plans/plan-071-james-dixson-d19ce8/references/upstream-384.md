---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #384 - yf-plan: a success criterion can be reported green
  before its Discharged-by issues have run, and criteria commands are never smoke-run'
---
# Upstream #384: yf-plan: a success criterion can be reported green before its Discharged-by issues have run, and criteria commands are never smoke-run

- **Number:** 384
- **Title:** yf-plan: a success criterion can be reported green before its Discharged-by issues have run, and criteria commands are never smoke-run
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Evidence from a live `yf-plan` run (d3-pxe plan-021, 7 epics / 24 issues, 4 red-team cycles). Two related defects in the same class: **a criterion that is green while asserting nothing.**

## Defect 1 — nothing prevents a premature green mid-run

At Epic 2 of 7, the executing session reported *"SC1 and SC5 already passing"*.

- **SC1** was *"the `session` variable returns a non-empty option list"*, `Discharged-by: 2.3, 4.1, 7.4`. **Issue 4.1 had not run** — no variable existed in the committed artifact at all. The check probed the underlying API endpoint with hardcoded constants, so it was green independent of the thing the criterion names. It would also have stayed green had 4.1 bound the variable to the wrong field.
- **SC5** was *"exactly one dashboard with this title"* — trivially true before any converge, asserting nothing about a converge that had not happened.

Both were caught by the delegating parent session, not by any mechanism. `recheck-criteria` exists but runs **only at §6.4 completion** — far too late to catch a false *progress* report, which is what actually misleads an operator watching a run.

**Suggested fix.** The `Discharged-by` column is already machine-readable (`plan_extract.py` parses it). A criterion whose discharging issues are not all closed should be reportable only as `not-yet-dischargeable`. This could be a `plan_manager.py` verb the coordinator calls before reporting, or a check folded into the existing status path.

## Defect 2 — criteria commands are never executed at approval

The same plan's SC14 shipped through **four adversarial review passes** with this verification:

```
uv run scripts/plan020_dataset_growth_check.py -> exit 0
```

That script takes a required positional `dataset`. As written the command exits **2** on an argparse usage error. It is not runnable, and never was. Reviewers read it four times; nobody ran it.

Note the review history: passes 1-3 each independently caught *other* instances of this class — a command naming a nonexistent script, two pre-existing scripts blind to the claims attached to them, and a `gh` search that exited 0 on empty and matched an unrelated issue. The class was the dominant finding of the whole review, and an instance still shipped.

**Suggested fix.** At `ready-check` (or `audit`), **smoke-run each criterion's command** and require it to exit 0, 1 or 2 rather than an interpreter/usage error — a "does this command exist and parse its own arguments" gate, not a semantic one. Cheap, static, and it catches every instance above except the semantically-blind ones.

## Why the two belong together

Both are the same failure: a criterion is treated as evidence when it is not capable of being evidence. `yf-plan` already reasons carefully about fail-closed checks elsewhere (the `doc_lint` INCONCLUSIVE handling, `close-reconcile-step`'s halting exit code, `pour_fidelity`'s three-valued read). This is the same principle applied to Success Criteria themselves.

Observed via `yf-herdr` delegation — the parent session verifying the subordinate's self-reports is what surfaced Defect 1, which is an argument for that skill's "mine deviations" step having real yield.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
