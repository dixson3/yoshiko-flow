---
type: Review
okf_spec: OKF-PLAN
pass: 3
---
# Red-team pass 3 — plan-048-james-dixson-ed68a5

## Verdict: REVISE

## Part A — audit of pass-2's resolutions

**9 of 12 landed as claimed. 3 landed only in form (N2, N7, and — for its stated purpose — N3).**
N1 partial (the gate's new wording makes a **false ancestry claim**); N2 partial (0.6a exists but all
four gate `Test:` lines are still bare `bash`); N3 partial (3.6 exists but gates nothing in Epics 4–5);
N5 partial (R4 claims scope Issue 4.1 does not contain); N7 **not in substance** (1.4b runs after 1.3,
so the target is still set after the measurement); N10 partial (12 non-Epic-0 issues still unnamed).
N3b, N4, N6, N8, N9, N11, N12 landed.

## Part B — independent verification of the main session's claims

**All mechanical claims hold**: 46 issues / 30 criteria / 7 gates, `unparsed[]` empty, no dangling
edges, no cycles, every issue transitively covered, `doc_lint` PASS, `audit` pass, `okf.py check` OK,
`markdown_lint` clean. Premise spot-checks all reproduced — `STATUS_SEVERITY` null-status behavior,
`parse_upstream_rows` bold defect, `resolve_derived` `_shared/` constraint, the `_table_rows` /
`first_table` shared defect, and the absent `tests/fixtures/doclint/reference/`. **D-5 is working.**

## Concerns

| # | Sev | Concern |
| :-- | :-- | :-- |
| H1 | high | **Issue 0.6a's deliverable has no location.** Either a wrapper — and all four gate `Test:` lines are bare `bash`, contradicting Issue 0.6's own sentence — or a resolver change, which is a skill behavior change with **no SPEC id allocated**, violating SPEC-first |
| H2 | high | **The declared target is still declared after the measurement.** 1.4b `depends-on: 1.3`, and **no number appears anywhere in plan.md**. SC20 still cannot fail |
| H3 | high | **`grammar widening` gate's evidence is in no ancestor of what it blocks** — `anc(3.1)` lacks 1.3/1.4b/1.5, so the gate can go red for "not built yet", which its Instructions define as capability-absent |
| H4 | high | **1.1 (escaped pipes) never reaches Epic 3**, so the relational rules can ship against the unfixed parser — violating the Approach's own stated ordering constraint |
| M1 | med | The `relational checks can fail` gate claims 3.2 is an ancestor of 3.4. It is not — third cycle with a false ancestry claim on this gate |
| M2 | med | R4 asserts a pre-write batch VERIFY is "explicit scope in 4.1"; **4.1's text contains no such scope** — the same shape as the N5 defect it repaired |
| M3 | med | **D-12 gates nothing it claims to gate** — `4.1` and `5.1` have no Epic-3 ancestor, so Epics 4–5 are ready-able before 3.6 evaluates. Also: `wc -l` of pass files is constant from approval, so end-of-Epic-3 is a frontloading miss |
| M4 | med | The plan violates the R1b it ships at 26% — 12 issues named by no criterion, notably **6.2 (FULL validation)**, **5.5 (positive controls)** and **6.4** |
| M5 | med | SC10c is unsatisfiable for `gate-split.sh` (no capability to build) and its glob expands to one invocation with three arguments |
| M6 | med | Two of Issue 0.4's three postconditions ship with no criterion — idempotence and fingerprint-neutrality are ungraded |
| L1 | low | R7 calls 46 "the record"; plan-047 measures **77** |
| L2 | low | The Motivation asserts "300 unparsed constructs" as fact — the figure this plan's EXP-001 refuted |
| L3 | low | Title and Objective still promise "normalize the corpus hash-neutrally", the framing D-4 retracted; 0.4 amends the SPEC for "the normalizer" when no normalizer is built |
| L4 | low | #173's `Resolved By` is 3.4 while the obligation SC21 grades is discharged by 6.5a |

## Gate Assessment

| Gate | Blocks | Evidence in ancestry? | Verdict |
| :-- | :-- | :-- | :-- |
| grammar widening non-vacuous | 3.1 | **no** | **H3, blocking** |
| relational checks can fail | 3.4 | partial — 3.3 yes, **3.2 no** | **M1** |
| normalizer aggregate diff | 4.2 | yes | sound |
| intake binding does not wedge | 5.3 | yes | **sound — still the best gate in the plan** |
| Upstream write | 6.5, 6.5a | yes | sound |

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 | high | 0.6a fixed as a **wrapper script** `scripts/gate-run.sh`; all four gate `Test:` lines rewritten to invoke it. No resolver change, so no SPEC id needed | `main-session` | resolved |
| H2 | high | The residual target **54** written into plan.md (Issue 1.5, SC1) as a literal fixed at approval; 1.4b adjudicates against it rather than declaring it | `main-session` | resolved |
| H3 | high | `3.1 depends-on 1.5` added | `main-session` | resolved |
| H4 | high | `3.1 depends-on 1.1` added | `main-session` | resolved |
| M1 | med | `3.4 depends-on 3.2` added, making the gate's condition true as written | `main-session` | resolved |
| M2 | med | The batch-VERIFY clause **struck from R4** — the revertable commit and the human gate are the honest mitigation | `main-session` | resolved |
| M3 | med | `4.1 depends-on 3.6` and `5.1 depends-on 3.6` added; D-12 restated to note the count is constant from approval, so it is a tripwire for a 4th cycle | `main-session` | resolved |
| M4 | med | Criteria added for 6.2, 5.5 and 6.1 | `main-session` | resolved |
| M5 | med | SC10c scoped to the three real gate scripts with an explicit per-script loop | `main-session` | resolved |
| M6 | med | Criterion added for the idempotence postcondition | `main-session` | resolved |
| L1 | low | R7 restated: "tying plan-045's 46, below plan-047's 77" | `main-session` | resolved |
| L2 | low | The Motivation now attributes 300 to plan-047 and gives the measured 150 | `main-session` | resolved |
| L3 | low | Title and Objective retitled to grammar-widening + bundle migration; 0.4's subject renamed to `okf.py migrate` | `main-session` | resolved |
| L4 | low | #173's `Resolved By` now reads `3.4, 6.5a` | `main-session` | resolved |
