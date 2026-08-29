---
type: Review
okf_spec: OKF-PLAN
conformance: 'PASS (two non-blocking nits: broken `upstream-56` relative link; stale
  "Resolved'
red-team_verdict: REVISE → all concerns resolved in-place; plan ready to re-present
  for approval.
---
# Review Pass 1 — plan-020-james-dixson-81785d

**Conformance:** PASS (two non-blocking nits: broken `upstream-56` relative link; stale "Resolved
By" cell — both fixed during resolution).

**Red-team verdict:** REVISE → all concerns resolved in-place; plan ready to re-present for approval.

## Strengths
- Data-loss invariant (`add -A && commit`, never `reset --hard`/`--allow-empty`) is correct and load-bearing.
- Mode detection via `metadata.json` `dolt_mode`, not exit-code inference — respects the false-negative invariant; no existing consumer conflict.
- SPEC-first ordering correct (Epic 1 → 2.1 `depends-on: 1.1` → tests `depends-on: 2.3`; REQ-BINIT-016 authored before 3.1 tags it).
- Path derivation defensive (`.dolt/`-parent search, zero/>1 hard guard).
- Absence findings honestly disclosed (unreproduced wedge; server path untested-by-change).
- Native-verb necessity correctly argued (no cwd field in shelled model; must bypass bd).

## Concerns & Operator Resolutions
| ID | Severity | Concern | Resolution | Status |
|:---|:---------|:--------|:-----------|:-------|
| RT-1 | medium | `verify()` remediation string `beads_init.rs:252` hardcodes `bd dolt stop` — advises embedded operators the exact failing command | Added `:252` to Epic 2.3 scope: make the remediation mode-aware | resolved |
| RT-2 | medium(→high) | Chosen raw-`dolt` depends on a binary embedded installs may lack; `bd dolt commit` fallback was rejected on an *unverified* absence finding | Approach step 4 now a fallback chain: raw `dolt` → `bd dolt commit` → clear rc. Costs nothing; worst case == today | resolved |
| RT-3 | medium-low | Missing/empty `dolt_mode` routes an embedded repo to the failing server path (plausible on the triggering upgrade) | Approach step 1: keyless `dolt_mode` falls back to the `dolt-server.*` filesystem probe, not the server path | resolved |
| RT-4 | low | Commit-succeeds-but-migration-fails outcome unspecified (most likely real non-happy path) | Added explicit partial-failure note to Approach + a Success Criterion: reports FAIL, working set committed/recoverable, manual remediation | resolved |
| RT-5 | low | `skills/yf-beads-init/README.md:36` hardcodes server-only sequence, omitted from Epic 4 | Added README.md to Issue 4.1 | resolved |
| RT-M1 | note | `beads_init.py` retired stub not mentioned; stale `beads_init.rs:331` doc-comment refs it | Epic 2.3 now notes the stub + fixes the :331 comment drift | resolved |
| RT-M2 | note | No golden fixture from the real 2026-06-30 wedge | Added Risks note: coverage closed-by-decision (live state gone; sequence is the verified real-world fix) | resolved |

## Missing sections
None — all required portability sections present (verified by conformance).

## Gate Assessment
Appropriate and minimal. Start Gate (human/operator) justified for an engine change repairing live
data; Reconcile Gate (auto, all execution beads closed) standard. No over-gating. Test gates (3.1
plan-shape unit, 3.2 self-guarding idempotency integration) valid; the no-genuine-wedge coverage
limit is disclosed, not hidden.

## Upstream Assessment
Correct. Single coarse tracking issue #56 (`include`), matches AGENTS.md coarse-granularity mandate
(precedent #13/#14/#16). No granular sub-beads pushed. "Resolved By" cell updated to Epic 1/Issue
1.1; concrete bead ids fill in at intake.

**Final status:** all concerns resolved; frozen.
