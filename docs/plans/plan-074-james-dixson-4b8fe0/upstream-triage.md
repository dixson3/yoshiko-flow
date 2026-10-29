---
type: Reference
okf_spec: OKF-PLAN
description: Disposition of each candidate upstream issue, with the reasoning behind
  it — the triage record behind plan.md's Upstream Issues table.
---
# Upstream Issue Triage: Native gate-wrapper compatibility

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #417 — yf-plan: resolve-start-gate can't find the Begin: wrapper under bd 1.3.0 (poured as issue_type gate, not task)

> ## Symptom

At execute start, `plan_manager.py resolve-start-gate <plan_dir>` returns:

```json
{"verdict": "inconclusive", "passed": false, "epic": "yf-mol-t42s", "wrapper": null, "gate": null,
 "rea...

**Disposition:**
**Notes:**
