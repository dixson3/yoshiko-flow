---
type: Plan
okf_spec: OKF-PLAN
id: plan-206-fixture-cccccc
author: fixture
created: 2026-08-25
status: drafting
---
# Plan: dropped-continuation fixture

**ID:** plan-206-fixture-cccccc
**Author:** fixture
**Created:** 2026-08-25
**Status:** drafting

## Objective
Drive REQ-DATA-063 as amended by plan-053 (#206).

## Motivation
Two continuation shapes are dropped silently by the extractor while `--strict` reports
`unparsed: []` and exit 0. Both must reach `detail`, and neither of two adversarial shapes
may produce an edge. A column-0 fence must NOT be collected.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|

## Investigation Findings
None.

## Approach
None.

## Epics
### Epic 1: The two drop shapes and the two adversarial shapes
- Issue 1.1: DROP SHAPE 1 — a continuation line that is ENTIRELY one inline code span
  `RECOVERED_CODE_ONLY_LINE --json --strict`
  ORDINARY PROSE ON THE NEXT LINE.
- Issue 1.2: DROP SHAPE 2 — an INDENTED fenced block is continuation, collected verbatim
  PROSE BEFORE THE FENCE.
  ```bash
  RECOVERED_FENCE_LINE_ONE
      RECOVERED_FENCE_INDENTED_LINE
  ```
  - depends-on: 1.1
- Issue 1.3: ADVERSARIAL 1 — a `depends-on:` written inside a code span is PROSE, not an edge
  `depends-on: 1.1` is written here inside a code span and must produce NO edge.
- Issue 1.4: ADVERSARIAL 2 — a fence containing issue-and-subkey-shaped lines yields nothing
  PROSE BEFORE THE ADVERSARIAL FENCE.
  ```markdown
  - Issue 9.9: A PHANTOM ISSUE THAT MUST NOT BE EXTRACTED
  - depends-on: 9.9
  - touches: `nope.py`
  ```
  - depends-on: 1.1

```bash
# A COLUMN-0 FENCE that belongs to the PLAN BODY, not to issue 1.4.
# CommonMark: an indented opening fence is list-item continuation; a column-0 fence is
# document content. It terminates nothing, so a naive "collect every fenced line" variant
# swallows it into the LAST issue's bead description -- a NEW silent-corruption shape
# introduced while fixing an old one. This line is the guard.
COLUMN_ZERO_FENCE_MUST_NOT_BE_COLLECTED
```

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | none | low | none |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | none | `true` → exit 0 | 1.1 |
