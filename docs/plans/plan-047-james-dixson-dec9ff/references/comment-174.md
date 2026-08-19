---
type: Reference
okf_spec: OKF-PLAN
id: comment-174-draft
disposition: partial
target: https://github.com/dixson3/yoshiko-flow/issues/174
status: DRAFTED — NOT POSTED (operator gated)
---

# Draft comment for #174 — review-phase validation pass (falsify + cross-check matrix)

**Disposition: partial. #174 stays OPEN.**

plan-047 (Epics 0–5) delivers both things this pass was blocked on.

**1. The assertions are machine-readable.** `_shared/plan_extract.py` emits criteria, issues and
their edges as JSON, failing loudly on anything it cannot parse.

**2. The criterion↔issue join key now exists.** `REQ-DATA-018` makes success criteria carry
stable ids (`SC<n>[a-z]`, unique, insertable without renumbering) in a fixed
`| # | Criterion | Verification | Discharged-by |` table, with a bidirectional completeness
rule: every criterion names at least one issue, and every issue is named by at least one
criterion. This is enforced by the linter and seeded by `seed_plan_md`, so new plans get it by
construction.

**This is an addition, not a codification, and deliberately not backfilled.** Precedent was 31
of 367 criteria in **2 of 47** plans. The edge cannot be recovered from history: only 13.3% of
criteria mention an issue id, the strongest signal is ~73% precise, and combined yield is ≈10% —
*a mention is not a discharge*. Shipping inferred edges would be worse than an empty matrix,
because nothing downstream could distinguish an inferred edge from a declared one. So the matrix
starts empty and fills forward.

**Your own note is now answerable.** #174 says the two checks "likely want to be one pass with
two checks… worth deciding deliberately rather than building two extractors." There is now
**one** extractor, and both #113's walk and #174's matrix are consumers of it. That decision can
be made on the merits rather than forced by tooling.

**Still open:** the two checks themselves — falsify-every-criterion, and the cross-check matrix.
