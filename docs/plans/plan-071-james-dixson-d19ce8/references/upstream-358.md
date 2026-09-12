---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #358 - yf-plan criteria: a success criterion must assert
  what the PLAN DID, not what the WORLD IS — external-state legs are falsifiable by
  concurrent fleet sessions'
---
# Upstream #358: yf-plan criteria: a success criterion must assert what the PLAN DID, not what the WORLD IS — external-state legs are falsifiable by concurrent fleet sessions

- **Number:** 358
- **Title:** yf-plan criteria: a success criterion must assert what the PLAN DID, not what the WORLD IS — external-state legs are falsifiable by concurrent fleet sessions
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

A yf-plan success criterion can assert a property of the **world** rather than a property of **what
the plan did**. Such a criterion is falsifiable by a third party the plan does not control, so it
reports FAIL on a plan that behaved perfectly.

Observed live on `plan-029` at RECONCILE-time, falsified by **another agent in the same operator's
fleet** working an unrelated plan in a different repository.

Sibling of #356 (empty-collection false-fail). Same surface — the criteria table — different root
cause, and neither subsumes the other.

## The live case

`plan-029` had a legitimate non-goal: *do not modify `Incubator/ystack/` or the `yoshiko-flow`
repository.* It encoded that as SC13:

```sh
test -s $PB/assets/base-sha && test -s $PB/assets/yoshiko-flow-sha \
  && git diff --name-only "$(cat $PB/assets/base-sha)"..HEAD > $T/ch \
  && ! grep -q '^Incubator/ystack/' $T/ch \
  && test -z "$(git status --porcelain -- Incubator/ystack/)" \
  && test "$(git -C ~/workspace/dixson3/yoshiko-flow rev-parse HEAD)" \
        = "$(cat $PB/assets/yoshiko-flow-sha)" \
  && test -z "$(git -C ~/workspace/dixson3/yoshiko-flow status --porcelain)"
```

Legs 1–5 assert facts about **this plan's own working tree** — sound. Legs 6 and 7 assert that an
**external repository's HEAD has not moved** and that its working tree is clean.

At execution time SC13 failed:

```
recorded  3fbc0c0  →  actual  bcd1511
  bcd1511 plan-064: intake — engine-repair plan for yf-okf-hygiene (#316, #294)
  f0dcb6a plan-064-james-dixson-a0b7fa: INTAKE approved
```

Both commits belong to **plan-064**, a concurrent session on an unrelated plan. Independently
verified that `plan-029` did nothing there:

| Evidence | Result |
| :-- | --: |
| `grep -rl yreview ~/workspace/dixson3/yoshiko-flow` | empty |
| ystack paths in `base-sha..HEAD` | 0 |
| `git status --porcelain -- Incubator/ystack/` | empty |

**The criterion's intent was fully satisfied. Its implementation still said FAIL.**

## Why this is a distinct class

The distinguishing property: the criterion's truth value depends on an actor outside the plan's
control, so it is **not a function of the plan's behaviour**.

- Re-running does not stabilise it — every unrelated commit to that repo re-falsifies it.
- The plan cannot make it pass, because passing requires a third party to *not act*.
- It gets **worse with fleet parallelism**. yf actively encourages concurrent sessions
  (`yf-herdr` exists to spawn them); a criterion that pins an external HEAD is a race against
  the operator's own tooling. Here the falsifying session was another `yf-plan` execution.
- **Consequence at RECONCILE:** the honest report is "one criterion failed," which is
  indistinguishable at a glance from a real defect. That trains a reader to discount criteria
  failures — the same erosion #356 describes from the opposite direction.

## The distinction that fixes it

**Assert what the plan DID, not what the world IS.**

| Shape | Example | Sound? |
| :-- | :-- | :--: |
| World-state | external `HEAD` equals a recorded sha | ✗ |
| World-state | external working tree is clean | ✗ |
| Plan-action | this plan authored no path under `<dir>` | ✓ |
| Plan-action | no commit in `base..HEAD` touches `<dir>` | ✓ |
| Plan-action | no commit in the external repo is attributable to this plan (author/branch/message/trailer) | ✓ |
| Plan-action | `grep -rl <this-plan's-marker> <external-repo>` is empty | ✓ |

The last two preserve the real intent — "we didn't touch it" — while remaining true regardless of
what anyone else does. `plan-029`'s corrected replacement was validated in both directions and
recorded in that plan's `proposed-criteria-edits.md`.

Note legs 1–5 were **already** written in the sound shape. As with #356's SC3, the defect was a
minority of legs written inconsistently with the rest of the same criterion — which again argues
for a stated rule rather than a convention authors are expected to absorb.

## Proposed changes

1. **Criteria-authoring guidance:** state the rule — a success criterion must be a function of the
   plan's own actions. Name the anti-pattern (pinning an external repo's HEAD, asserting another
   working tree is clean, asserting a shared service's state) and give the plan-action rewrite.
2. **Non-goals need a first-class encoding.** "Do not modify X" is a common and legitimate
   non-goal, and the world-state form is the *obvious* way to write it. Guidance should supply the
   attribution-based form so authors are not left to invent it — this defect is a predictable
   consequence of leaving the encoding open.
3. **Cheap mechanical lint:** flag any `verification` cell containing `git -C <path outside the
   plan root>` or comparing against a recorded external sha. Would have caught this instance.

## Severity

Medium — same reasoning as #356. No deliverable is corrupted, but the criteria table is yf-plan's
mechanical proof of done, and a criterion that cannot be made to pass by doing the right thing
degrades trust in every other row. `plan-029` caught it only because the parent session re-derived
the failure and confirmed the intent was met; the default path is a plan that reports a failing
criterion at RECONCILE with no way to discharge it.

## Disposition on plan-029

Not edited — the criteria table is inside the fingerprint and an edit forces mid-execution
re-approval (same call as ESC-001 / #356). The failure is documented with its context, and the
corrected form is recorded in the bundle for a later plan to land. This issue is the class fix.

