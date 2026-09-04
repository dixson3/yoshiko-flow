---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 5 on plan-063. REVISE with 2 concerns, both high, both instances of a fix introducing a same-class defect. C41: Issue 0.6 says the amendment log must name NINE ids but check_amendment_logs A1 derives TEN — pass-1 C8 re-created at the new number. C42: SC2es -eq 1 is unsatisfiable and Issue 2.1 is internally contradictory, naming two failing tests while instructing a fix set that omits the stub backing the first of them. Priorities 2 and 4 cleared with no defect: REQ-LAND-036 does not conflict with REQ-LAND-018.'
---
# Red-Team Pass 5 — plan-063-james-dixson-3f74c1

## Verdict: REVISE

## Strengths

**Structure is clean.** `0.5b` exists, `0.6 depends-on 0.5b`, the Epic-0 chain is linear
(`0.0→0.7→0.1→0.2→0.3→0.4→0.5→0.5b→0.6`), zero dangling deps, zero cycles, single sink `6.6`.

**REQ-LAND-036 does NOT conflict with REQ-LAND-018** — checked directly. `-018`'s staleness
detection rests on `predicted_tree` and the target tip; `-036`'s exclusion set is named and
**disjoint** (`execute_worktree_present`, `execute_worktree_dirty`).
`test_digest_covers_merge_preview` mutates the merge preview and is unaffected. **Nothing in the
tree asserts the literal "every fact" behaviour** — every call site goes through
`pm._land_digest(manifest["facts"])`, so an exclusion inside `_land_digest` is transparent to all
of them. Issue 0.5b's amendment of `-002`/`-011` is correctly scoped.

All changed clauses re-measured correctly unmet: SC9 → 1, SC5b → pytest 5, SC2e → 1.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C41 | high | **Issue 0.6's count is wrong, and it contradicts its own enumeration.** It says the log must name "all NINE ids", then lists `REQ-LAND-030…-036` (7) + `-020` (8) + `-002`/`-011` (10). Measured against `check_amendment_log`'s actual A1 derivation over Epic-0 bodies: **`EPIC 0 TOUCHED n = 10`**. An executor following the literal "NINE" writes nine bullets and SC9b exits 1. **This is pass-1 C8 exactly, re-created at the new number.** | `NINE` → `TEN`. |
| C42 | high | **SC2e's `-eq 1` is unsatisfiable, and Issue 2.1 is internally contradictory.** Three `lambda pd: {"action"` stubs exist, each backing an L18 test: `:1023` → `test_prune_is_strategy_aware`, `:1180` → `test_a_skipped_step_is_surfaced_never_silent`, `:1254` → `test_each_step_invokes_the_RIGHT_EXECUTABLE`. Issue 2.1 names the first and third as the failing tests but instructs fixing `:1180` and `:1254` — so `:1180` belongs to a third, unnamed test while `:1023`, backing the **first-named** failing test, is not in the fix set. Either branch breaks: leaving `:1023` raises `TypeError` the moment 2.1 lands (the exact C18 harm 2.1 exists to prevent), or Issue 2.2 rewrites it — a `lambda pd:` cannot "capture the stub's call args and assert `(ctx.plan_dir, force=False)`" — and the count goes to **0**, failing SC2e's `-eq 1`. | Have Issue 2.1 correct **all three** stubs and set SC2e to `-eq 0`. |

## Missing

Nothing further found within budget. The verdict rests on C41 and C42 only; no concerns were
manufactured to justify the pass.

## Gate Assessment

Unchanged from pass 4 and sound. Three capability gates, all reachable; Gate 2's `-ge 2`
arithmetic re-verified; Gate 3 at its floor.

## Upstream Assessment

Unchanged and sound.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C41 | high | Confirmed by re-deriving A1 over the Epic-0 bodies: **n = 10** (`REQ-LAND-002, -011, -020, -030…-036`). Corrected NINE → **TEN**, and re-derived after the edit to confirm the body and its count now agree. **This was pass-1 C8 re-created at the new number** — I changed the id set in the C37 fix and updated the prose count by hand instead of re-deriving it. | `main-session` | `resolved` |
| C42 | high | Confirmed by mapping each stub to its test: `:1023` → `test_prune_is_strategy_aware`, `:1180` → `test_a_skipped_step_is_surfaced_never_silent`, `:1254` → `test_each_step_invokes_the_RIGHT_EXECUTABLE`. Issue 2.1 named the first and third as failing but instructed fixing the second and third — omitting the stub behind the first. Issue 2.1 now corrects **all three**, and SC2e's target moved `-eq 1` → **`-eq 0`**, re-measured exit 1 today (3 stubs present, correctly unmet). | `main-session` | `resolved` |
