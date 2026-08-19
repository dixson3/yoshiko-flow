---
type: Reference
okf_spec: OKF-PLAN
id: comment-174-draft
disposition: partial
target: https://github.com/dixson3/yoshiko-flow/issues/174
---

# Drafted comment for #174 (partial)

> **DRAFT — not posted.** Posting is gated on the "Upstream write" capability gate.

---

`plan-048-james-dixson-ed68a5` landed a **subset** of the validation pass this issue proposes. #174 stays
**OPEN** — the full falsify-every-criterion, cross-check-every-claim pass is not built.

**What landed: the mechanical half.** Six relational rules over `plan.md`, as a new
`plan-relations` check kind that reads *across* sections (no per-document schema check can):

| Rule | Asserts |
| :-- | :-- |
| R1 | every `Discharged-by` names a real issue |
| R1b | every issue is named by some criterion, unless its epic **declares** itself bookkeeping |
| R2a | every `Resolved By` names a real issue |
| R2b | `exclude` resolves nothing; `include` resolves something |
| R2c | the disposition is a recognised literal (after emphasis normalization) |
| R3 | `plan_extract` and `parse_upstream_rows` agree on every disposition cell |

**What is explicitly NOT landed — and it is the harder half.** Every rule above is a
*referential* check: does the referent exist, is it shape-consistent. **None of them asks
whether a criterion's claim is TRUE.** That is #174's actual subject and it needs a judge,
not a parser.

**Two findings from building the mechanical half that #174 should inherit:**

1. **R1b needs a declared escape hatch, and inferring one is worse than having none.** An
   epic exempts itself with an explicit `<!-- epic-kind: bookkeeping -->` marker. An
   *inferred* exemption is indistinguishable from an oversight. Verified against
   `plan-048-james-dixson-ed68a5` itself: the marker exempts its Epic 0, and the four remaining R1b
   findings are exactly the four issues that plan had already recorded, in prose, as its
   "honest residual". The rule independently reproduced the author's own self-assessment.

2. **Promotion must be declared, not inherited.** `STATUS_SEVERITY` promotes `W → E` at
   `review`. If that fired on this rule family, every future plan would hard-fail R1b
   unless every non-bookkeeping issue were named by a criterion — a bar `plan-048-james-dixson-ed68a5`
   itself does not clear. A rule no in-flight plan can satisfy trains authors to write
   **fake criteria**, which is the exact failure R1b exists to prevent. So REQ-DATA-044
   declares promotion OFF for this kind, explicitly.

**Precondition now satisfied for #174.** `REQ-DATA-043` requires every `plan_extract`
consumer to return **INCONCLUSIVE (exit 2)**, never FAIL, on a plan with a non-empty
`unparsed[]`. Any judge #174 builds inherits a defined answer for the 24 of 48 plans that
are not fully readable: *this instrument could not read the plan*, which is a different
claim from *the plan is wrong*.

Plan: `docs/plans/plan-048-james-dixson-ed68a5/`.
