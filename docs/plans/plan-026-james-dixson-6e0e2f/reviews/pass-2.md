# Red-Team Review — Pass 2

**Plan:** plan-026-james-dixson-6e0e2f
**Date:** 2026-07-11

## Verdict: APPROVE

Second-cycle review after pass-1 REVISE. All 10 pass-1 resolutions verified as actually landed in
plan.md (not merely claimed); the C1 factual correction confirmed against real code; the Epic 4
renumbering (4.1→4.4) introduced no dependency-graph breakage.

## Strengths
- All 10 pass-1 resolutions genuinely applied (verified line-by-line, not just the resolution table).
- C1 factual correction confirmed: `md2pdf.py:76-82` `check_deps()` + `REQ-MDPDF-003` exist; the
  Epic 4 reframe is accurate.
- Cited line refs correct: `markdown_lint.py:47` `MDLINK_RE` `[^)]*` (the #81 bug), `:49`
  `ALL_RULES` ending at ML009, REQ-MDLINT-011 current enumeration (SPEC.md:38).
- Epic 4 renumbering clean: 4.1(SPEC)→4.2(investigate)→4.3(dep 4.1,4.2,3.2)→4.4(dep 4.1,3.2); no
  dangling edges; risk table references `exp-002` by name not stale number.

## Concerns
| # | Severity | Concern | Disposition |
|:--|:---------|:--------|:------------|
| L1 | low | Epic 4: 4.1 (SPEC) has no dep on 4.2 (exp-002); if the declaration already enforces, 4.1's REQ could be partly redundant. Defensible — 4.1 states target observable behavior; 4.3 adapts. | Accepted — self-resolves at execution via exp-002. |
| L2 | low | 4.1's yf-kernel REQ has no named target SPEC surface yet. | Accepted — exp-002 identifies the surface; no plan change required. |

## Missing
Nothing blocking. Pass-1 M1/M2 both closed.

## Gate Assessment
Start gate (human/operator) appropriate. Reconcile Gate now requires **both** Issue 1.4 (lint) and
2.2 (pdf) closed before #46 counts reconciled — pass-1 gap closed.

## Upstream Assessment
Dispositions all `include`, specific, consistent; #46 partial boundary explicit. Coarse-tracking
convention gap closed — reconcile files one coarse plan-026 tracking issue (precedent #13/#14/#16)
referencing all five, not five granular pushes.

## Operator Resolutions
| Concern | Resolution | Status |
|:--------|:-----------|:-------|
| L1 (SPEC-before-investigate sequencing) | Accepted as execution-time refinement; exp-002 narrows enforcement wording. | resolved |
| L2 (unnamed target SPEC surface) | Accepted; exp-002 identifies the surface during Epic 4. | resolved |
