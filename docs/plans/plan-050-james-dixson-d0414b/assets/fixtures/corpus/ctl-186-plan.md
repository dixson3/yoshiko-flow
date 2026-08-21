---
type: Plan
okf_spec: OKF-PLAN
id: plan-186-fixture-aaaaaa
author: fixture
created: 2026-08-21
status: drafting
---
# Plan: masked-title fixture

**ID:** plan-186-fixture-aaaaaa
**Author:** fixture
**Created:** 2026-08-21
**Status:** drafting

## Objective
Drive REQ-DATA-062 (#186).

## Motivation
A title carrying an inline code span must survive extraction verbatim.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|

## Investigation Findings
None.

## Approach
None.

## Epics
### Epic 1: Fix `plan_extract.py` and its `mask_inline_code` helper
- Issue 1.1: Ship the `classify` mode on `doc_lint.py`
- Issue 1.2: A title with no code span at all
  - depends-on: 1.1
- Issue 1.3: Two spans, `alpha` and `beta`, plus trailing prose
  - depends-on: 1.1

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | none | low | none |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | none | none | 1.1 |
