---
type: Review
okf_spec: OKF-PLAN
id: pass-4
description: "Red-team pass 4 — REVISE. 2 blockers: SC17's direct-file form is vacuous without a __main__ runner, and pass-3's `bash <missing>` repair was measurably false (127, not 1) across four criteria."
---
# Red-team pass 4: plan-057-james-dixson-9ecf1c

## Verdict: REVISE

> **All 11 concerns resolved by the main session.** Re-dispatched as pass 5.

**Date:** 2026-08-29 · HEAD `41fb2c3` · Reviewer: delegated adversarial agent (read-only)

Trend: **17 → 18 → 12 → 8** concerns; **8 → 6 → 2 → 2** blockers. Both blockers are one-clause
edits, and both are the *same class the prior pass was auditing for*.

## Strengths

Pass 3's repairs verified sound by execution:

- **SC12's producer↔consumer path matches byte-identically**, and the reviewer ran the check pass 3
  listed as *Missing* — all **62 path literals** across 29 Verification rows: every `MISS` is a file
  this plan creates, each named by a creating issue.
- **`--require 16` re-derived from scratch**: array = 9, Issue 1.0 names 7, and gate `Test`, SC0b
  prose, SC0b command and SC0's `test -x` list **all four agree** and all include the 7th.
- **The `diagrams/` removal is DURABLE, not temporary** — traced `make_plan_dir()` to its single
  caller (`init`, which creates a *new* plan\_id); no execution verb recreates it.
- **SC3 reproduces to the digit** (`described 184 · distinct 58 · repeated 126 · ratio 0.6848`), and
  **SC5's five nested bundles reproduce exactly**.
- **R11's `cmp` claim is TRUE** — and `yf --version` went stale a **fourth** time (`ad6acc7` vs HEAD
  `41fb2c3`), exactly as R11 now predicts, which is why routing the durable test to `cmp` was right.
- **SC19b is reachable** — a `skill` document type does select `skills/*/SKILL.md` (`class: selected`).
- Structural: 29 edges, no cycles, 0 issues without a criterion, `context.md` clean.

## Concerns

## Resolutions

| Concern | Severity | Detail | Resolution |
| :-- | :-- | :-- | :-- |
| B1 | high | **SC17's direct-file form is VACUOUS without a `__main__` runner.** Spiked: two identical PEP 723 files each containing `assert False` — without the runner `uv run` imports the module, runs nothing, exits **0**; with it, exit 1. Independently re-measured: **36 of 74** repo test files have no `__main__` block. Issue 2.8 required only a `dependencies` header, so a conforming implementation yields SC17 exit 0 having executed zero tests — the mirror image of the cannot-PASS defect pass 3 removed from the same criterion. Compounding: `check-pytest-ran.sh`'s ASSERTION 0 needs `import pytest` or returns INCONCLUSIVE, which would leave **seven** more criteria unjudged. | **resolved** — Issue 2.8 now requires all three: PEP 723 header, `import pytest`, and the runner block, each with its measured justification. |
| B2 | high | **`bash <missing-script>` exits 127, not 1 — pass-3 C6's resolution was measurably FALSE**, and it now affected FOUR criteria (SC0c, SC19b, SC21, SC23), since SC23 was added in the same broken form. 126/127 map to `inconclusive`, counted in neither bucket — a direct violation of R11's own third rule, reproduced inside the pass auditing for it. | **resolved** — all four wrapped in `test -x … && bash …`; re-measured, each now exits **1**. |
| C3 | med | **No issue implements `assess`.** Epic 2 implements `audit`/`backfill`/`reindex`/`restore`; Issue 2.1 writes prose only. So D-3's "absorb" would leave the new SKILL.md advertising a verb `okf_hygiene.py` cannot dispatch — the exact defect SC23 exists to delete, **relocated one directory over**, and SC23 inspects `yf-okf` only, so it is blind to it. | **resolved** — Issue 2.1 must choose (a) real verb, (b) alias of `audit`, (c) retired; and `check-assess-verb-gone.sh` now asserts the GENERAL property (every advertised verb is dispatchable), so it catches relocation as well as removal. |
| C4 | med | **`sync.py`'s `okf.py` consumer list is hand-written** and names four skills. If Epic 2 vendors a fifth copy unregistered, `--check` never sees it and **SC5b stays exit 0 while the copy drifts forever** — the failure mode `sync.py`'s own comment describes. | **resolved** — Issue 1.6 either registers the fifth consumer or Issue 2.2 declares the script self-contained. |
| C5 | med | **Two Epic-3 deliverables had no criterion.** Issue 3.1 re-pins `OKF-BASELINE.md` *and* `yf-okf/SPEC.md:13` (still `knowledge-catalog`); SC20 covered only the first. Issue 3.1a's row-exists deliverable had no assertion, though Issue 2.10 has the identical deliverable and SC18 checks it. | **resolved** — SC20 extended with a POSITIVE grep (not a negative one: ~147 provenance citations of the old name must survive — the same substring trap SC23 hit); SC21 gained a `check-recipe-row.sh` clause. |
| C6 | med | **"The five crash states" are asserted three times and enumerated nowhere.** A five-state test and a five-state journal could be five *different* fives with every instrument green — on the plan's highest-severity data-loss risk. | **resolved** — enumerated S0–S4 in Issue 2.4; SC11's test must name each. |
| C7 | med | **`assets/backfill.json` is created in Epic 2, AFTER Epic 1 widens the rule to per-file enumeration** — so it arrives as a selected-but-unlisted nested file and turns the live gate red. Third appearance of this class (pass-2 C18, pass-3 C5). | **resolved** — Issue 2.4 adds the index entry in the same issue. |
| C8 | med | **R1's mitigation was blind to Issue 2.9**, which regenerates ~31 indexes with no ordering edge to Epic 1 — the "same issue" guarantee did not reach them. | **resolved** — `2.9 depends-on 2.8, 1.4`; R1 amended to say so. |
| C9 | low | Issue 1.0 carried "five"/"four" leftovers from the 4→5→6→7 growth — in the issue that owns the anti-off-by-one arithmetic. | **resolved** — seven. |
| C10 | low | The `assess` census said 9 hits; measured **11** over 10 lines. And the verb lives in four FILES (`SKILL.md`, `SPEC.md:454`, `README.md`, the trigger `description`), which Issue 3.4 did not say. | **resolved**. |
| C11 | low | `log.md` double-logged pass 1 under two different phase labels with two different arithmetics of the same 17 concerns. | **resolved** — duplicate removed. |

## Missing

- **The producer↔consumer path check** — run manually and clean, still not an instrument.
- **A `plan.md` ↔ instrument-output diff** — named Missing in passes 2, 3 *and* 4; it cost C9 and C10
  this pass, C8 last pass, C3/C12/C14 before that. This is now the longest-running open item.
- **A "verbs advertised vs verbs dispatched" check** — partially closed by C3's generalisation of
  `check-assess-verb-gone.sh`.

## Gate Assessment

| Gate | Verdict |
| :-- | :-- |
| Start | OK |
| Predecessor complete | **Sound** — directive parses in full, `unparsed: []` |
| Backfill authorization | **Sound.** Still the best gate in the plan |
| Upstream network reachable | **Sound** — `curl -sfI` re-verified live at exit 0 |
| Verification harness ready | **Sound** — `--require 16` re-derived independently; exits 1 today |
| Reconcile | OK |

PASS on 6 gates, no cycles over 29 edges, no frontloading miss, no gate's evidence inside its own `Blocks`.

## Upstream Assessment

Unchanged and defensible. `verify-reconcile` → exit 1, `"4 of 6 upstream row(s) did not reach the end
state"` — expected pre-execution, discharged by 3.5. Dispositions remain honest; #170's two-ground
`partial` still carries EXP-006's "~100 of 1383 concepts inspected" caveat.
