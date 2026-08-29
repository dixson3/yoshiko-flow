---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #173 - yf-plan: success criteria and upstream dispositions
  are never checked against the engine that enforces them'
---
# Upstream #173: yf-plan: success criteria and upstream dispositions are never checked against the engine that enforces them

- **Number:** 173
- **Title:** yf-plan: success criteria and upstream dispositions are never checked against the engine that enforces them
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium

## Body

Filed from plan-046 execution, at operator instruction: **record, do not fix**.

## Two concrete defects, one family

### 1. A plan instruction contradicted the engine that enforces it

plan-046 Issue 4.5 instructs: *"**Close #140** as `partial` so a future reader cannot conclude the nested tier was built."*

`plan_manager.py` `verify-reconcile` enforces the opposite:

> `#140 is CLOSED; a `partial` row must stay OPEN (its remaining half is still real work)`

Both are defensible in isolation. The **engine is right**: `CLOSED`/`completed` asserts the work is done, while #140's own close comment argues in detail — with measurements — that two of three OUT items are *not* done. The issue's **state** and its top comment contradicted each other, and the state is what every list view, search, and triage pass reads. That is the same failure mode as an index asserting a file that is not there, which is what plan-046 existed to remove.

The clincher: **promotion to error-level enforcement is recorded in `skills/yf-okf/SPEC.md` (`REQ-OKF-CHK-002`) and has no tracker issue at all.** #171 covers the nested-`index.md` half. So closing #140 would have left real, un-deferred, **untracked** work with nowhere to live. An open #140 *is* its tracker. Resolved at reconcile by reopening #140 with an explanatory comment.

### 2. A markdown-bolded disposition cell is invisible to the parser — and fails OPEN

plan-046's Upstream Issues table wrote the disposition as `**partial**`. `verify-reconcile` read the literal string, matched no known disposition, and returned **`inconclusive`** — which **exits 0 and halts nothing**.

It reads perfectly to a human. It silently verifies nothing.

De-bolding the cell turned the free `inconclusive` into a real `fail` and surfaced defect 1 underneath. **Implication beyond plan-046: any bolded disposition cell, in any plan, has been silently unverified.** Suggested fix: normalize the cell (strip inline emphasis) before matching, and/or make an unrecognized disposition a `fail` rather than an `inconclusive` — failing open is the wrong default for a check whose whole job is to catch unreconciled rows.

## Why this is a family, not two incidents

**Neither was caught by five red-team cycles**, because the reviews checked each artifact for **internal coherence** — the disposition against the plan's intent, the criterion against the plan's prose — and **never against the code that scores it**.

That is the same defect as plan-046's **SC3**, where a success criterion (`grep` must return zero `OKF v0.1` hits) forbade exactly what Issues 2.1/2.3/2.4 required, and survived all five cycles. Its predecessor **SC9** had the identical shape and was caught only at pass 4/5.

**The generalization:** *yf-plan has no review step that checks a plan's success criteria and upstream dispositions against the machinery that enforces them.* Every instance so far has been found at execution, by the engine, after approval.

**Cross-references:**
- plan-046 `findings/exec-003-sc3-unsatisfiable.md` — the SC3 conflict and the operator ruling on it.
- plan-046 `plan-retrospective.md` — seven entries, including this family recorded three times independently.
- #135 — a measured literal in `plan.md` goes stale when the plan is inside its own measured corpus. Same root: plan text asserting facts nothing re-checks.

Source: plan-046 (`docs/plans/plan-046-james-dixson-aabefa/`). Tracker: #167.

