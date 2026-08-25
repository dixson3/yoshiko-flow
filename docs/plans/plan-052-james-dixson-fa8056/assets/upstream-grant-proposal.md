# plan-052 — upstream authorization PROPOSAL

**This file is a PROPOSAL, not an authorization.** Issue 7.2 generates it; the operator — and
no issue — writes `assets/upstream-authorization.txt`. That asymmetry is the whole point of
the `upstream-write` gate: a file some issue could write cannot express consent, which is why
the authorization file appears in **no** `touches:` list in this plan.

Every action below is **outward-facing and NOT hoistable**. Nothing here has been executed.

## A. Comments on issues this plan CLOSES (disposition `include`)

Each gets a comment recording what plan-052 did, then a close.

| Issue | Title | Discharged by | Action |
| :-- | :-- | :-- | :-- |
| #198 | yf-plan Phase 3: give the review loop a bead representation | 6.1 | comment + **close** |
| #199 | nothing re-checks plan.md Success Criteria at completion | 1.2, 2.2 | comment + **close** |
| #205 | close-out is manual and the closable signal is wrong in BOTH directions | 3.2, 3.3 | comment + **close** |
| #197 | formula aspects: make classify -> lint -> verify a bead that must be closed | 5.1, 5.2 | comment + **close** |
| #196 | retrospective prevention: fields are prose that nothing executes | 5.3 | comment + **close** |

## B. Comments on issues this plan ADVANCES but does NOT close (`partial`)

A partial disposition closes nothing. Each gets a comment naming the sub-case worked and what
explicitly stays open, so a later reader is not left to infer the boundary.

| Issue | Sub-case worked | Stays open | Action |
| :-- | :-- | :-- | :-- |
| #113 | gate-`Blocks`-set consistency (4.2) | the rest of the execution-rehearsal pass | comment only |
| #203 | the 0/1/2 contract applied to every step this plan ships (2.3) | the repo-wide sweep | comment only |
| #173 | #199's named sub-case (2.2) | the general criteria-vs-engine cross-check | comment only |
| #174 | #199/#198/gate-check sub-cases (2.2, 4.2) | the general falsification pass | comment only |
| #149 | M5 worked instances (5.1, 5.3) | M9 | comment only |
| #150 | two more ranked classes (5.1, 5.3) | the remainder | comment only |
| #202 | used as EVIDENCE for the counter decision (D-2) | the bd defect itself | comment only |
| #192 | commented, not scoped (D-29) | the structure-first DSL | comment only |

## C. Issues to CLOSE without a code change

| Issue | Why | Action |
| :-- | :-- | :-- |
| #194 | **Declined.** EXP-002 supplied the second independent measurement D-3 required: concerns are not lens-clustered and 75% serial dependence makes fan-out unsound. Three reopen conditions recorded, all required | comment + **close as declined** |
| #177 | **wontfix.** Refuted by plan-050 EXP-001 (`81` is textually identical whether measured or guessed) and declined by three successive plans. plan-052 did not investigate it — the close is housekeeping, not a deliverable | comment + **close as wontfix** |

## D. NEW issues to FILE — the seven deferred defects

Full text and measurements in [deferred-defects.md](deferred-defects.md). Filing these is what
turns `ctl-deferred-count` (SC21a) green; it is RED until then, correctly.

| # | Defect | Action |
| :-- | :-- | :-- |
| D1 | `bd distill --var` silently substitutes nothing and exits 0 | **file new** |
| D2 | a `type = "gate"` step with no `[steps.gate]` pours as a plain task, no diagnostic | **file new** |
| D3 | `bd distill` cannot reconstruct gate steps — non-idempotent against bd's own pour | **file new** |
| D4 | `REQ-PLAN-073` id collision (`SPEC.md:345` vs `spec/phases.md:150`) | **file new** |
| D5 | `started_at` written for 86/225 plan beads and not exposed by `bd list --json` | **file new** |
| D6 | the coordinator closes beads in batches — 84% of interval overlap is an artifact | **file new** |
| D7 | `change_validation.py` persists no run record (D-13) | **file new** |

## E. The coarse tracker

| Action | Detail |
| :-- | :-- |
| **file new** | `plan-052-james-dixson-fa8056 execution tracking`, per the AGENTS.md coarse convention — ONE issue per plan-scale effort, linking the plan folder and the epic `yf-mol-f2q`. It must be filed **through `/yf-beads-upstream`** so the epic carries it as `external_ref`; SC23 asserts that END STATE, not the route |

## Totals

| Class | Count |
| :-- | --: |
| comment + close (`include`) | 5 |
| comment only (`partial`) | 8 |
| comment + close (declined/wontfix) | 2 |
| new issues (deferred defects) | 7 |
| new issue (coarse tracker) | 1 |
| **total outward-facing actions** | **23** |

## What the operator must authorize

Write `assets/upstream-authorization.txt` covering **every** action above. Verified at pass 2
by execution: an absent or empty file exits 1 with verdict `fail`, so a file that some issue
could have touched cannot satisfy the gate.

```bash
uv run skills/yf-plan/scripts/plan_manager.py grant docs/plans/plan-052-james-dixson-fa8056 \
  --check docs/plans/plan-052-james-dixson-fa8056/assets/upstream-authorization.txt --json
```
