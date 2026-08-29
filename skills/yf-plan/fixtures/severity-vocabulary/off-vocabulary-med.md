---
type: review
description: Fixture for REQ-DATA-076's cell-vocabulary check — one off-vocabulary severity cell and nothing else wrong.
---
# Review pass — cell-vocabulary fixture

**Verdict:** REVISE

This file is a **fixture**, not a real review pass. It exists so plan-059's SC1 can assert that
`doc_lint`'s `cell-vocabulary` check fires **attributably**.

It is deliberately **schema-clean apart from the single off-vocabulary cell** in `## Concerns`.
That is not tidiness: `doc_lint` exits `1` whenever any `E`-severity finding is present, so a
fixture carrying an unrelated `E` would turn SC1 red for a reason that has nothing to do with the
check under test — and the failure would look exactly like the check being broken.

## Strengths

- Carries every section `review.toml` requires, in the order it requires them.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | A legal token, present so the check is shown to stay silent on conforming rows rather than firing on the whole column. | None — this row must produce no finding. |
| C2 | medium-high | The hyphenated family the operator ratified at plan-059's Start Gate. Present so a naive `high\|medium\|low` implementation is caught. | None — this row must produce no finding. |
| C3 | med | **The defect under test.** `med` is the abbreviation the corpus actually contains and it is not a ratified token. | Write `medium`. |
| C4 | medium (blocking) | The qualifier suffix the operator **declined** (option (c)). It is precisely the token that fired research 005's severity-decay detector on `plan-026`, so legalising it would erase the signal the pin preserves. | Write `medium`; put the blocking-ness in the Concern cell. |

## Missing

- Nothing. Absence of a real finding is the point of a fixture.

## Gate Assessment

Not applicable — this document reviews no plan.

## Upstream Assessment

Not applicable — this document reviews no plan.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | Conforming row — nothing to resolve. | `main-session` | `resolved` |
| C2 | medium-high | Conforming row — nothing to resolve. | `main-session` | `resolved` |
| C3 | medium | Fixture row: left off-vocabulary on purpose. | `main-session` | `resolved` |
| C4 | medium | Fixture row: left off-vocabulary on purpose. | `main-session` | `resolved` |
