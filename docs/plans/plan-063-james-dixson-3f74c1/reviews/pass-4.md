---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 4 on plan-063. REVISE with 4 concerns, one high. C30s arithmetic independently verified correct (exactly 2 stubs survive; -ge 2 is right) and C31 measured to cost zero parallelism. HEADLINE C37: the pass-3 C33 resolution excluded fields from the landing digest, which contradicts REQ-LAND-002 and REQ-LAND-011 ("every fact") — a normative deviation with no SPEC issue in a SPEC-first repo.'
---
# Red-Team Pass 4 — plan-063-james-dixson-3f74c1

## Verdict: REVISE

## Strengths

**C30's fix is arithmetically correct, verified independently.** 4 one-arg stubs exist; Issue 2.1
corrects `:1180`/`:1254`; 2.1 is an ancestor of 5.2, which precedes the blocked 5.1. Exactly **2**
survive at gate time, so `-ge 2` is right, and the Condition, Test, R2 and Approach ¶2 now agree.
Both survivors match the check's stated pattern, so it will see them.

**C31 introduced no cycle and cost nothing.** Full DFS over 33 edges: no cycle. Critical-path
depth is **21 with and without** the new edge — 4.2 already depended on both — so the Epic 3 /
Epic 4 parallelism loss is nil.

**C32's SC2e is correct in the main direction**: count 3 today (exit 1), 1 after 2.1, and a
partial fix leaves 2 and fails. All changed clauses re-measured correctly unmet; none vacuous.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C37 | high | **C33's resolution put an unSPEC'd normative deviation into a SPEC-first plan.** Issue 4.1 now decides to *exclude the execute-worktree fields from the digest*, and SC5b requires a post-teardown resume **not** to halt. But `REQ-LAND-002` says every fact shall be re-derived and checked against `manifest_digest`, and `REQ-LAND-011` says a resume shall **re-derive every fact** and **halt** on mismatch. `_land_digest` implements exactly that, with nothing filtered. Excluding two facts changes both requirements — and Epic 0 enumerates seven ids, **neither `-002` nor `-011` among them**. AGENTS.md: SPEC changes always happen first. | Add an Epic-0 issue for `REQ-LAND-036` (the digest's coverage set excludes **landing-mutated** facts, naming the fields and the rationale) and amend `-002`/`-011`'s "every fact" wording. Update Issue 0.6's id list and the amendment-log count accordingly. |
| C38 | low-medium | **R3 contradicts the gate it describes**, on the exact point pass-2 C25 established. R3 says the gate blocks "1.1, 3.1 and 4.1"; its actual `Blocks` is `0.7, 1.1, 3.1, 4.1`, and its Instructions say blocking the branch-creation issue is load-bearing. **A stale mitigation cell is how that blocking got lost once already.** | Add `0.7` to R3's mitigation text. |
| C39 | low | **SC2e keys on the RETURN shape, not the arity it claims to check.** A stub corrected on the return axis only — `lambda pd: {"status": …}` — drops the count to 1 and SC2e passes green while the stub is **still one-arg**. The gate and SC8 catch it, so this is defence-in-depth, not an escape. | Grep the arity directly, or state in the cell that it is a proxy and SC8 is the authority. |
| C40 | low | **SC5b is one-sided.** Under the exclusion branch it is a genuine regression test, but it would also pass if the digest covered nothing, and the positive control that exists lives in a different file than SC5b runs. | Have Issue 4.1's case assert both directions: flipping `execute_worktree_present` leaves the digest equal, **and** flipping `primary_checkout_dirty_outside_plan_dir` changes it. |

## Missing

Nothing new. Pass-3's Missing 1 (the untested `--apply` CLI preamble) is filed in Issue 6.1.

## Gate Assessment

Three capability gates, all reachable. Gate 1's condition is operator-set evidence outside its
`Blocks` set. Gate 2's evidence producer (5.2) precedes its blocked issue (5.1) — the C3/C30 fixes
hold and the `-ge 2` arithmetic verifies. Gate 3 sits at its floor. **No frontloading miss found.**

## Upstream Assessment

Unchanged and sound: five `include` rows each mapped to a resolving issue, #331 honestly `partial`
with the recurring residue filed in 6.1, #332 `exclude` with a stated reason.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C37 | high | Verified against source: `_land_digest` covers `facts` with **nothing filtered**, and `REQ-LAND-011` requires a resume to re-derive **every fact** and halt on mismatch. Excluding two fields is genuinely normative. New **Issue 0.5b** adds `REQ-LAND-036` (the coverage set excludes LANDING-MUTATED facts, naming both fields and the rationale) and amends `-002`/`-011`'s wording; `0.6 depends-on 0.5b`; the amendment-log count went SEVEN → **NINE**; SC9 widened to `REQ-LAND-03[0-6]` `-eq 7`, re-measured exit 1 (correctly unmet). **My pass-3 C33 resolution introduced an unSPEC'd deviation into a SPEC-first plan and I did not notice.** | `main-session` | `resolved` |
| C38 | low-medium | R3's mitigation now names **0.7** alongside 1.1/3.1/4.1, with the reason restated inline. The concern is exactly right that a stale mitigation cell is how that blocking got lost once already — pass-2 C25 had to re-establish it. | `main-session` | `resolved` |
| C39 | low | SC2e's cell now states it is a **PROXY** on the return shape and that SC8 is the authority on arity. Kept rather than replaced: the gate and SC8 both catch the escape, so it is defence-in-depth, and saying so is better than implying a guarantee it does not give. | `main-session` | `resolved` |
| C40 | low | Issue 4.1's test must now assert **both directions** — flipping `execute_worktree_present` leaves the digest equal AND flipping `primary_checkout_dirty_outside_plan_dir` changes it — so SC5b cannot be satisfied by a digest that covers nothing. | `main-session` | `resolved` |
