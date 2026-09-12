---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #328 - red-team: apply the measurement-ordering argument
  exhaustively, not opportunistically (d3-pxe plan-020 RE-002)'
---
# Upstream #328: red-team: apply the measurement-ordering argument exhaustively, not opportunistically (d3-pxe plan-020 RE-002)

- **Number:** 328
- **Title:** red-team: apply the measurement-ordering argument exhaustively, not opportunistically (d3-pxe plan-020 RE-002)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Process finding from **d3-pxe plan-020** (`plan-retrospective.md` RE-002). Filed against yoshiko-flow because the defect is in the red-team agent's reasoning pattern, not in the plan that surfaced it.

## What happened

plan-020 had a measurement epic (**Epic B**, which measures write amplification before and after a `recordsize` change) and several epics that precede it.

**Red-team pass 2 caught the ordering hazard in one place.** It added `depends-on: B.4` to Epic E, with this reasoning:

> *"E landing first can fail a correct Epic B or pass a failed one"*

That is exactly right, and it is a general argument: any change that perturbs the measured quantity must not land between the baseline and the re-measure.

**It never applied that argument to Epic A** — which also precedes Epic B, and which also touches the write path (it raises `zfs_arc_max` from 6.74 GB to 16 GiB on the very pool being measured). Epic A's baseline (A.2) is taken *after* Epic A, while SC3's band was derived from exp-002's measurements taken *before* it. Comparing one against the other is incoherent.

**Five review passes did not catch it.** It surfaced only during execution, when the post-Epic-A baseline came back 3.3× off the plan's basis and the criterion had to be re-derived mid-flight under an operator exception.

*(For completeness: Epic A turned out not to move the measured quantity — ARC serves reads, `ndirty` is set by writes, and the measurement confirmed RMW moved the wrong way for that explanation. The reasoning defect stands regardless: nobody checked, and the plan would have been equally wrong if it had.)*

## The defect class

**A correct general argument applied at one site and not swept across its own scope.** The reviewer reasoned about *one* epic's interaction with the measurement instead of about *the class of epics that interact with measurements*. That is a systematic gap, not a miss — the same reviewer would make it again on the next plan with the same shape.

## Candidate fix

In `red-team.md`, make the check **exhaustive over the scope of its own argument** rather than opportunistic:

> When a plan contains an epic that **measures** something, enumerate **every** epic ordered before it and, for each, state explicitly whether it perturbs the measured quantity — and if it does, whether the baseline is taken before or after it. Absence of an obvious effect is **not** a reason to skip the check; it is the answer the check should record.

The distinguishing property: the current behaviour fires when an interaction is *obvious* (Epic E changes the load, visibly). It misses interactions that require a step of reasoning (Epic A changes a cache, which *might* change the load). Those are precisely the ones a review is for.

## Related

- d3-pxe plan-020 tracker: https://github.com/dixson3/d3-pxe/issues/100
- The operator recorded the SC3 exception this produced as RE-001 in the same retrospective.

