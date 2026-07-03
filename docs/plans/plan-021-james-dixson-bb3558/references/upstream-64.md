# Upstream #64: yf-plan: re-review gate — modifying a reviewed/approved plan must re-trigger red-team + conformance + portability audit before re-approval

- **Number:** 64
- **Title:** yf-plan: re-review gate — modifying a reviewed/approved plan must re-trigger red-team + conformance + portability audit before re-approval
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Proposal

When a plan that has already reached `review` or `approved` status is **modified**, yf-plan should automatically **invalidate the approval** and require a fresh review cycle — conformance review, red-team (adversarial), and portability audit — before the plan may return to an `approved` (and committed/intaken) state. Approval should be a property of a *specific plan content hash*, not a sticky status that survives arbitrary later edits.

## Motivation

Observed this session (plan-019): an already-`approved`, already-intaken plan received a post-approval scope addition (the dirty-build bypass). Nothing in the protocol forced a re-review — it only happened because the operator explicitly said "run red-team again," which surfaced a real medium-severity defect (C7: `build.rs` `YF_GIT_DIRTY` goes stale because of the existing `rerun-if-changed` narrowing). Had the operator not manually re-triggered, an approved plan would have carried an un-reviewed, defective change into execution.

Approval is a statement about *reviewed content*. Once the content changes, the prior APPROVE verdict no longer applies to what's on disk. The protocol should enforce that automatically rather than relying on operator diligence.

## Proposed behavior

- **Approval binds to content.** On the red-team APPROVE + portability-audit pass, record a fingerprint of the approved plan (e.g. a hash over `plan.md` + the contract files, or the git tree of `<plan-id>/`). Store it in plan.md front-matter / phase log.
- **Detect drift from the approved fingerprint.** On any subsequent `/yf-plan` operation (continue, capture, execute, status) — and ideally on-edit — recompute the fingerprint. If it differs from the last approved one while status is `review`/`approved`, the plan is **stale-approved**.
- **A stale-approved plan cannot execute.** `/yf-plan execute` must refuse (or warn-and-require-confirm) on a stale-approved plan and route back through review: conformance → red-team (new `pass-N.md`) → portability audit → re-approval. Only a matching fingerprint is execution-eligible.
- **Re-review is a full cycle, not a rubber stamp.** It writes a new `reviews/pass-(N+1).md` (create-on-present), appends the phase-log `review:` line, and re-runs `plan_manager.py audit`. The REQ-PORT-006 invariant (`count(pass-*.md) == count(review: lines)`) already supports multiple cycles.
- **Scope the trigger.** Only `review`/`approved` (and later) statuses re-trigger; edits during `scoping`/`investigating`/`drafting` are normal drafting and do not. A trivial/whitespace-only diff may be exempt (fingerprint over normalized content), but any semantic change to objective/approach/epics/gates/success-criteria re-triggers.

## Open questions

- **Fingerprint granularity.** Whole `plan.md` vs. section-scoped (so editing only the phase log or an Operator Resolutions table — which review itself mutates — does not falsely trigger). Review-in-progress writes to `reviews/` and the phase log must not self-trigger a re-review loop.
- **Interaction with intake.** plan-019 was modified *after* the molecule was poured. A re-review that changes epics/issues implies the poured beads are now stale too — does re-approval need to reconcile/re-pour? (Ties into #63's model, where the pour moves to execution start; under that model an intake-phase edit has no beads to reconcile, which is cleaner.)
- **Automation vs. friction.** On-edit auto-trigger (like the yf-change-validation / yf-drift-check on-edit hooks) vs. a gate checked at `continue`/`execute` time. The latter is less noisy; the former catches it sooner.
- **Operator override.** A `--force` re-approval path (recording the bypass + reason in the phase log, mirroring the existing portability-audit `--force`) for trivial edits the operator vouches for.

## Precedent / context
- plan-019: `approved` → post-approval dirty-build scope-add → manual "run red-team again" → pass-2 REVISE (found C7) → resolved → re-`approved`. This issue would have made that re-review automatic.
- Related yf-plan protocol issues: #63 (two-phase completion / worktree-per-write model), #62 (yf-spec skill).
- Existing on-edit trigger precedents to model the automation on: `yf-change-validation` and `yf-drift-check` (approved-manifest, on-edit, report-only).
