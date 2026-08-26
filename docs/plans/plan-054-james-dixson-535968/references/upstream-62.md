---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #62: Propose yf-spec skill: build & manage specifications; yf-plan SPEC-first integration

- **Number:** 62
- **Title:** Propose yf-spec skill: build & manage specifications; yf-plan SPEC-first integration
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Proposal

Introduce a new **`yf-spec`** skill dedicated to building and managing specifications (the `SPEC.md` requirements surface: `REQ-*` ids, testable/non-testable classification, the living-amendment log, and the SPEC coverage gate), and wire **`yf-plan`** to route SPEC work through it.

## Motivation

- SPEC management is currently ad-hoc inside `yf-plan` execution: requirements get added/edited by hand during plan intake and remediation, with per-skill `SPEC.md` audits done reactively (see #55).
- The repo convention is now **SPEC-first** (added to `AGENTS.md` this session): the `SPEC.md` requirement must land ahead of the code that implements it. A dedicated skill makes that enforceable and repeatable rather than a prose rule.

## Scope (proposed)

- **`yf-spec`** — a skill for authoring and maintaining specifications:
  - allocate the next `REQ-<AREA>-NNN` id in an area, enforce testable-vs-non-testable classification
  - append living-amendment-log entries with date + rationale
  - verify SPEC coverage (every *testable* REQ has a tagged test) — the gate that exists today, promoted into the skill
  - detect drift between a REQ and its implementing code/test (may overlap/route to `yf-drift-check`)
- **`yf-plan` integration** — planning routes SPEC edits through `yf-spec`, sequenced **before** the implementation epics (SPEC-first). Plans emit the SPEC requirement as the first execution bead, not a trailing docs epic.

## Open questions

- Boundary with `yf-drift-check` (already verifies impl ↔ docs ↔ spec agreement) and `yf-skill-authoring` (owns skill-dir instruction files). `yf-spec` would own the *authoring/lifecycle* of requirements, not just agreement-checking.
- Whether SPEC lives one-per-repo (`SPEC.md`) or per-skill (`skills/*/SPEC.md`) — the repo currently has both.

## Precedent / context

- SPEC coverage gate + per-skill audit remediation: #55
- SPEC-first rule now in `AGENTS.md`
- First plan to adopt SPEC-first ordering: plan-019 (preflight self-update offer)
