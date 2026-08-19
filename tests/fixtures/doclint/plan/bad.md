# Plan: A deliberately malformed plan.md

**ID:** plan-999-fixture-000000
**Author:** fixture
**Created:** 2026-01-01
**Status:** drafting
**Phase log:**
- 2026-01-01 scoping: this retired block is check `no-retired-phase-log` (REQ-DATA-012)

## Objective
Seeded known-bad fixture for `_shared/doc_lint.py`. Every defect below is deliberate.

## Motivation
Without a committed malformed instance, "the schema rejects bad documents" is satisfiable by
assertion alone and an empty schema passes.

## Upstream Issues
| Issue | Title | Disposition |
|-------|-------|-------------|

## Approach
The `## Investigation Findings` section is missing entirely (check `required-sections`), the
Upstream Issues table is missing two columns, the Risks table has the wrong columns, and the
criterion ids do not match the grammar.

## Epics
### Epic 1: Nothing

## Gates
### Start Gate (mandatory)
- Type: human

## Risks & Mitigations
| # | Risk | Mitigation |
| :-- | :-- | :-- |
| 1 | wrong columns, and a non-conformant row id | none |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| first | ids must match ^SC[0-9]+[a-z]?$ | this row fails | 1.1 |
| SC1 | a duplicate id below | this row passes | 1.1 |
| SC1 | duplicate of SC1 | this row fails | 1.1 |
