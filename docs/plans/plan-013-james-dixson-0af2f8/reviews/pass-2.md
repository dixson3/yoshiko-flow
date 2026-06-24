# Review pass-2 — plan-013 (re-review, cycle 2)

**Verdict:** APPROVE
**Date:** 2026-06-24
**Reviewer:** red-team (adversarial), re-review after v2 revisions

## Strengths

- **C1 (high) genuinely resolved.** No-prompt auto-hoist off by default (`auto_hoist_followons`
  default-deny, mirrors `custom.upstream.enabled`); C.3 default = propose-with-single-confirm.
  The day-one self-dogfooding risk (D.4 auto-closing the plan's own follow-ons) is neutralized.
- **C2 resolved with the right asymmetry** — narrow (`discovered-from` AND non-active, auto) vs
  broad (created-after, gated-only); no-prompt restricted to narrow.
- **C3 decided, not hedged** — classifier authored once, copied per-skill, D.1 provisions the
  DRIFT-CHECK edge; enumerate refactored to the single definition.
- **C4 mechanical** — delivered = linked plan `Status: complete` OR merged PR, injected lookups,
  flag-for-review fallback.
- **C5 broadened**, **C6 / rollback / false-positive test all landed.**

## Concerns

| # | Severity | Concern | Resolution in v2.1 |
| :-- | :-- | :-- | :-- |
| P1 | low | DRIFT edge (D.1) needs an explicit second-copy site; the enumerate-consumes-classifier refactor was prose-only, not an owned issue. | Added Issue C.7 (port classifier copy + refactor enumerate); D.1 now depends on B.1 + C.7. |
| P2 | low | Refactoring enumerate could silently change existing land-the-plane worklist behavior; no parity check. | C.7 includes an enumerate-parity regression test. |

## Missing

Nothing blocking (both soft gaps closed by C.7).

## Gate Assessment

Gates minimal and correctly placed; Capability Gate test now matches its Condition (C5). New
A.2→C.3, A.2→A.4, B.1→C.7 edges sound; graph acyclic.

## Upstream Assessment

#38 (include → B/C/D) and #17 (include → A) unchanged and sound; A.1 fills REQ-BUP-043. D.4
applies coarse one-issue-per-plan (precedent #13/#14/#16). Self-cross-check neutralized.

## Operator Resolutions

| # | Resolution | Status |
| :-- | :-- | :-- |
| P1 | Added Issue C.7 (explicit enumerate-refactor owner); rewired D.1 → B.1 + C.7. | resolved |
| P2 | enumerate-parity regression test added to C.7. | resolved |

**Status:** APPROVE — both low concerns folded in (C.7 / D.1). Plan ready for portability audit + INTAKE.
