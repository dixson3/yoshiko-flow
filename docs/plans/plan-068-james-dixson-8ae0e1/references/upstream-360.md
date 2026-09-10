---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #360 - plan_manager land --apply ignores a validated
  ''skip'' adjudication (l11_recheck_criteria) and halts on it AFTER the merge and
  push'
---
# Upstream #360: plan_manager land --apply ignores a validated 'skip' adjudication (l11_recheck_criteria) and halts on it AFTER the merge and push

- **Number:** 360
- **Title:** plan_manager land --apply ignores a validated 'skip' adjudication (l11_recheck_criteria) and halts on it AFTER the merge and push
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

`plan_manager.py land --apply` **executes a landing step that the decision document adjudicated
`skip`**, and halts on it — *after* the merge and push have already completed and been pushed to
the remote. `land --validate-decision` passes the same document as conformant and narrowing-only
immediately beforehand, so the operator has an explicit green light that the skip will be honored.

Observed live landing `plan-029`.

## Reproduction

Decision document (validated, `digest_ok: true`):

```json
"steps": {
  "l0_lock_acquire": "enable",
  ...
  "l5_advisory_recheck": "enable",
  "l6_push_one": "enable",
  "l7_reconcile_writes": "enable",
  ...
  "l11_recheck_criteria": "skip:SC13 legs 6-7 assert global state of the third-party repo ...
     Enabling L11 would halt the landing after the non-skippable merge and push, on a defect
     this plan did not cause.",
  ...
  "l19_redeploy": "skip:merge_preview.touches_skills is false ..."
}
```

Validation immediately before apply:

```
land --validate-decision <decision.json> <plan_dir>
  verdict: pass
  reason:  "decision is conformant and narrowing-only"
  digest_ok: true
  problems: []
  ignored_enables: []
```

Then `land --apply`:

```
l0..l4                     pass
l5_advisory_recheck        fail, "halting": false   (correct — advisory)
l6_push_one                pass   ← merge pushed to origin
l7_reconcile_writes        pass
HALT
  halted_at:  "recheck-criteria"
  halt_class: 5
  reason:     "recheck-criteria exited 1. HALTING: completion stops here and `complete` is NOT set."
```

`l19_redeploy`'s skip appears to have been honored (nothing was redeployed); `l11`'s was not.

## Why this is severe

1. **It halts at the worst possible point.** L11 runs *after* `l6_push_one`. The merge is committed
   and pushed to the remote before the skipped step aborts the run, so the plan is left in a
   **partially landed** state: the outward-facing, irreversible half done, the bookkeeping half
   (`l8`–`l18`: close cascade, complete gate, pour fidelity, status update, residual mirroring,
   prune) never executed, and `status` frozen at `reconciling`.
2. **The skip's stated rationale predicted exactly this**, which is why it was adjudicated `skip`
   in the first place. The operator reasoned about the failure mode, encoded the mitigation, the
   validator confirmed the encoding, and the tool did it anyway.
3. **`--validate-decision` is actively misleading.** It reports `ignored_enables: []` — it has a
   concept of adjudications being ignored, and reported none. An operator who checks before
   applying (the documented workflow, and the only pre-flight available for a writing mode) gets
   an affirmative signal that is wrong.
4. **Adjudication is the only lever the operator has.** The decision document is the mechanism by
   which a human narrows a landing. If `skip` is advisory in practice, the mechanism does not
   exist, and the safe response for an operator is to stop using `land --apply` on any plan with
   a known-failing criterion.

## Expected vs actual

- **Expected:** `l11_recheck_criteria: "skip:…"` ⇒ the step does not run; the landing proceeds to
  `l12`.
- **Actual:** the step runs, fails, and halts the landing after the irreversible steps.

## Suggested fixes

1. Honor `skip` for `l11` (and audit every `lN` for whether its adjudication is actually consulted
   — `l19` appears to work, so this is likely a per-step omission rather than a systemic one).
2. If some steps are deliberately **non-skippable**, `--validate-decision` must **reject** a
   decision that skips them, naming the step. Silently accepting an adjudication that will not be
   honored is worse than refusing it.
3. Consider ordering: a criteria recheck that can halt completion should run **before**
   `l6_push_one`, not after. `l5_advisory_recheck` already occupies the pre-push slot; a halting
   recheck positioned after the push can only ever produce a partially landed plan.

## Related

- #358 — SC13's world-state defect, the criterion that was failing and the reason L11 was skipped.
- Companion issue (filed separately) — `land --apply` invokes `recheck-criteria` without the
  plan's declared criteria preamble environment, which is why the halt reported **9** false
  criteria when only **1** was genuinely false.

