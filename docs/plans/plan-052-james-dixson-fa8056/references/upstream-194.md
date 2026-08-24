---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #194: yf-plan Phase 3 has no bead representation: fan out the red-team into parallel review lenses via a per-cycle plan-review wisp

- **Number:** 194
- **Title:** yf-plan Phase 3 has no bead representation: fan out the red-team into parallel review lenses via a per-cycle plan-review wisp
- **URL:** 
- **State:** OPEN
- **Labels:** type::feature, priority::high

## Body

DEFERRED FROM plan-051 (which scopes #184's serial-self-review half only).

FINDING. Phase 3 (PLAN/REVIEW) is the ONLY yf-plan phase with no bead representation.
Phase 2 = wisp (plan-investigate), Phase 5 = mol (plan-execute), Phase 3 = a prose loop
whose entire state is len(glob('reviews/pass-*.md')). The model can express a review
CYCLE but has no way to express a review LEVEL (parallel lenses over one draft).

COST, measured on plan-050: 13 review cycles, 11 red-team passes, all sequential, one
reviewer per pass.

PROPOSAL. A `plan-review` wisp, one per cycle: conformance step -> fan out N parallel
red-team arms with distinct lenses (conformance / adversarial / spike / payload-fidelity)
-> join -> resolve concerns -> `bd mol burn` at APPROVE. Vapor phase is correct: the
durable artifact is reviews/pass-N.md on disk, which is already the ledger, so the wisp
carries no audit value once the cycle ends.

EVIDENCE FOR FAN-OUT. plan-050's concerns-per-pass ran 5 -> 4 -> 11 -> 17 -> 14, with the
discontinuity exactly at pass 3 — the first Agent-dispatched pass. #184 fixes serial
self-review; parallel lenses are a separate, unmeasured axis on top of it.

HARD CONSTRAINT (must be an explicit non-goal in any plan that takes this up).
Do NOT move the review-cycle counter into beads. It is deliberately file-based and
monotonic (REQ-PLAN-030; REQ-PORT-006 count-equality between reviews/pass-*.md and
log.md `review-pass:` bullets). A wisp is ephemeral and burnable — putting the bound
inside it makes the bound RESETTABLE by `bd mol burn`, reintroducing precisely the
unbounded self-resolving loop D-8 forbids. The wisp orchestrates dispatch; the file
stays the ledger.

BLOCKER TO RESOLVE FIRST. The join primitive is NOT AVAILABLE in installed bd 1.1.2 —
see the companion issue on doc-vs-binary divergence. `waits-for` is documented at
beads.gascity.com/workflows/molecules but absent from `bd dep add --type`. Any work here
must first establish whether the join is expressible with the types that DO exist
(parent-child + blocks, or the existing gate pattern), or refute the mechanism.

BENEFIT IS UNMEASURED. This is a candidate for an experiment that can refute itself,
not a settled design.
