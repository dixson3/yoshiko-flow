---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #69: yf-plan: enforce a 'ready-for-approval' gate — re-run red-team after major revisions + complete portability audit before offering for approval

- **Number:** 69
- **Title:** yf-plan: enforce a 'ready-for-approval' gate — re-run red-team after major revisions + complete portability audit before offering for approval
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

yf-plan should not offer a plan for operator approval until it is genuinely *ready*. Two gates
must be **complete and green** before the approval prompt, and \"ready-for-approval\" should be a
first-class state distinct from \"approved\".

Observed in the plan-022 session: the plan was offered for approval (a) after a red-team pass
returned **REVISE** (concerns were revised, but the red-team was **not** re-run to confirm the
revisions cleared), and (b) **before** the portability audit had passed (the audit later failed
on unedited `context.md` template prose). Both are process gaps — approval was solicited on an
unverified plan.

## Desired contract

Define/enforce a **`ready-for-approval`** state with these invariants, ALL required before the
approval prompt is shown:

1. **Red-team ran clear with no outstanding revisions.** After *any* major-concern revision, the
   adversarial red-team is **re-run** (a new review cycle → `pass-(N+1).md`) and must return a
   non-REVISE verdict (APPROVE). A plan that last received REVISE is **not** ready-for-approval,
   even if the concerns were addressed — the addressing must be re-reviewed.
2. **Portability audit is complete and passing** (`plan_manager.py audit` → `pass`). Today the
   audit runs as the *last step of PLAN after approval*; it should be a **precondition of the
   approval prompt**, not a post-approval step.

Only when both hold does yf-plan present the plan and solicit approval. **Approval then moves the
plan state `ready-for-approval` → `approved` / ready-for-intake** — approval is the operator's
single act of consent on an already-verified plan, not the trigger that starts verification.

## Why

Approval should mean \"I consent to this verified plan,\" not \"I consent, now go verify it.\"
Soliciting approval on a REVISE'd-but-unre-reviewed plan, or before the audit passes, invites
approving a plan that then changes or fails its own gates — defeating the point of the gates.

## Acceptance

- [ ] yf-plan SKILL.md Phase 3 (PLAN) / Phase 4 (INTAKE) codify a `ready-for-approval` state (or
      equivalent invariant) with the two preconditions above.
- [ ] Red-team is re-run after major-concern revisions; a REVISE verdict blocks the
      approval prompt until a subsequent cycle returns APPROVE.
- [ ] The portability audit runs and must pass **before** the approval prompt, not after.
- [ ] Approval transitions `ready-for-approval` → `approved`; the status vocabulary /
      `update-status` reflect the new state (or document why the existing `review`/`approved`
      values already suffice with the added preconditions).
- [ ] spec/portability.md and the review-lifecycle spec updated (SPEC-first).

## Provenance

Filed from the plan-022 session (bd 1.1.x certification). Process feedback captured as-is.
