# Review pass-1 — plan-013

**Verdict:** REVISE
**Date:** 2026-06-24
**Reviewer:** red-team (adversarial), after conformance PASS

## Strengths

- Investigation is real and load-bearing (exp-001/exp-002 verified live on bd 1.0.5:
  `discovered-from` edge, `dependency_type` vs `type` divergence, `(not set)` exit-0).
- Reuses the established hygiene live-layer/pure-core split honestly; reversible-tombstone
  (`bd close -r`, never `bd delete`) grounded in the `mol-yvv` precedent.
- The "hygiene proposes / upstream executes" carve is articulated and non-overlapping.
- Concrete regression anchor: reproduce the 2026-06-24 manual reconcile as one `reconcile --apply`.
- Risks section already names the divergent-classifier and false-obsolete risks.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | No-prompt auto-hoist **closes** local beads at land-the-plane — departs from the current operator-confirmed push contract (today nothing is closed; step 2 requires confirm). At session wind-down the operator is least likely to catch a wrong close; a false follow-on detection auto-removes a relied-on bead. | Don't ship no-prompt auto-close in iteration 1. Either propose-a-batch-with-single-confirm, or gate behind opt-in `custom.upstream.auto_hoist_followons=true` (default-deny). Reserve unattended path until the detection heuristic has live-validation evidence. |
| C2 | medium | Follow-on detection (C.2) unions two signals; "created-after-intake under subtree" is broad and could catch an actively in-progress bead. No precision/recall validation. | Restrict **auto**-hoist to the narrow signal (`discovered-from` AND status non-active); treat created-after as proposal-only in the gated path. Add fixture: in-progress created-after bead → NOT auto-hoisted. |
| C3 | medium | Shared-classifier decision is a 3-way runtime hedge — duplication is the exact divergence risk the plan names, and the drift-check mitigation is conditional ("if a manifest covers these paths") with no issue creating that manifest edge. | Decide classifier location at intake. If duplicated for install-independence, add an explicit issue to author/extend the DRIFT-CHECK.md edge asserting the two definitions agree. |
| C4 | medium | Obsolete-upstream detection has no concrete "delivered" signal — `gh issue list` gives issue state, not plan-completion; issue→plan→merged link unspecified. | Specify the mechanical signal in B.1 (linked plan.md `Status: complete`, or tracking issue's linked PR merged). If not mechanical, scope to flag-for-human-review only and say so. |
| C5 | low | Capability Gate test under-covers the Condition (no `--created-after`/`--parent`, no `bd close -r` probe). | Extend the test or downgrade the Condition wording to match what is asserted. |
| C6 | low | `granular` hoist path is thin; no coarse↔granular transition/coexistence story. | Add a note/sub-issue on transition semantics, or scope `granular` as implemented-but-not-the-tested-happy-path. |

## Missing

- No issue creates/extends the DRIFT-CHECK.md manifest edge the divergent-classifier mitigation depends on.
- No rollback / "un-hoist" operator story (no documented restore command for an over-hoisted bead, unlike hygiene's `restore` for edges).
- No explicit test for the false-positive auto-hoist case (active bead caught by created-after signal) — the single most important missing test given C1.
- Interaction with the existing `upstream.py enumerate` flow (`CANDIDATE_STATUSES = open,blocked,deferred`, status-only) vs the new active set (adds owner + ancestor walk) is unstated — two definitions could diverge.

## Gate Assessment

Gates used only where needed; wiring coherent (A.1 foundational; B.3→C.1; C.3→C.1+C.2;
Reconcile→D.3). Tighten the Capability Gate test (C5).

## Upstream Assessment

#38 (include → B/C/D) and #17 (include → A) dispositions sound; A.1 genuinely fills the
unimplemented REQ-BUP-043. D.3 applies the coarse one-issue-per-plan convention (precedent
#13/#14/#16). Self-cross-check: the plan dogfoods its own auto-hoist at D.3 — if C.3 ships
no-prompt, the plan's own follow-ons auto-close on day one. Strong reason to land C.3 as
propose-with-confirm first.

## Operator Resolutions

| # | Resolution | Status |
| :-- | :-- | :-- |
| C1 | Operator chose opt-in default-gated. New key `custom.upstream.auto_hoist_followons` (A.2, default-deny); land-the-plane default = propose-with-single-confirm (C.3); no-prompt only when opted in. | resolved |
| C2 | C.2 split into narrow signal (`discovered-from` AND non-active, auto-eligible) vs broad (created-after, gated-proposal-only). False-positive guard test added (C.6). | resolved |
| C3 | Classifier location decided at intake: authored once, copied per-skill for install independence; explicit DRIFT-CHECK.md edge (D.1) asserts agreement; `enumerate` refactored to consume the single definition. | resolved |
| C4 | B.1 obsolete signal made mechanical: linked plan `Status: complete` OR merged PR; else flag-for-human-review. Lookups injected for testing. | resolved |
| C5 | Capability Gate test broadened to probe `--created-after` and `bd close --reason`. | resolved |
| C6 | A.3 documents coarse↔granular transition/coexistence; coarse is the tested happy path, granular implemented-but-not-happy-path. | resolved |
| Missing: rollback | C.4 adds an un-hoist/restore path (reopen from tombstone + `--record` round trip). | resolved |
| Missing: false-positive test | C.6 adds the in-progress-created-after → NOT auto-hoisted test. | resolved |
| Missing: enumerate interaction | Approach: `enumerate` refactored to consume the single active-set definition. | resolved |

**Status:** resolved — all concerns and missing items addressed in plan v2; re-review (pass-2) follows.
