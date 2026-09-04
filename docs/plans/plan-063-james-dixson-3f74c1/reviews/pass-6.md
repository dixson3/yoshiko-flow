---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 6 on plan-063, run under an operator-authorized raise of max-review-cycles to 6. REVISE with ONE concern. Both pass-5 fixes verified (A1 derives 10 and Issue 0.6 says TEN; SC2es -eq 0 is right and conflicts with nothing). C43: the pass-5 C42 fix moved the third stub correction upstream of the mock-fidelity gate, so only ONE incompatible stub survives at gate time while the gate demands two — the third time this threshold has been wrong, each time for the same structural reason.'
---
# Red-Team Pass 6 — plan-063-james-dixson-3f74c1

## Verdict: REVISE

## Strengths

**Both pass-5 fixes verified.** A1 re-derived by loading the real `parse_plan`/`REQ_RE`/
`CITED_NOT_TOUCHED` over the current `plan.md`: **n = 10** (`REQ-LAND-002, -011, -020, -030…-036`),
matching Issue 0.6's "all TEN" exactly. SC9's `-eq 7` is unaffected — it counts `REQ-LAND-03[0-6]`
only, all seven still introduced in Epic 0. SC2e's `-eq 0` is the right target (3 stubs today,
correctly red), conflicts with neither Issue 2.2 nor SC8.

**Coherence sweep clean**: 30 issues, no dangling `depends-on`, no cycles, single sink `6.6`,
every `Discharged-by` id real, every issue covered by ≥1 criterion, every gate `Blocks` id real.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C43 | high | **The pass-5 C42 fix invalidated the mock-fidelity gate's arithmetic; the gate is permanently red and blocks the only path to Epic 6.** The gate asserts `-ge 2` and names its survivors as `land_rehearsal.py:140` **and** `test_land_apply.py:1023`. But C42 moved `:1023`'s correction into Issue 2.1, and 2.1 is an ancestor of the blocked issue (`5.1 ← 5.2 ← 2.3 ← 2.2 ← 2.1`) — so at gate-evaluation time all three `test_land_apply.py` stubs are fixed and **exactly one** survives. Measured: 4 one-arg stub sites exist repo-wide, 3 of them in `test_land_apply.py`. R2's cell restates the same stale "two". | Retarget the `Test` to `-ge 1` and rewrite the Instructions and R2 to name the single survivor `land_rehearsal.py:140`. Discrimination is preserved — a vacuous check returns 0. Do **not** restore `:1023` to 5.1: C42 established that omitting it from 2.1 raises the very `TypeError` 2.1 exists to remove. |

## Missing

Nothing further. A one-cell arithmetic correction in two places; no structural change, no new
issue, no dependency edge moves.

## Gate Assessment

Four gates. Start and Reconcile conventional. The `execute.worktree == false` gate is reachable,
blocks `0.7, 1.1, 3.1, 4.1`, correctly at its floor. The L16 gate is reachable and correctly
hoisted. **The mock-fidelity gate is unreachable as written (C43)** — its evidence-before-gate
edge direction remains correct; only the threshold is wrong.

## Upstream Assessment

Unchanged and sound. Five `include` rows mapped to resolving issues; #331 correctly `partial`
with the recurring residue in 6.1; #332 correctly `exclude`; SC15b's `-ge 6` matches.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C43 | high | Confirmed by measurement: 4 one-arg stub sites exist, 3 in `test_land_apply.py`, all corrected by Issue 2.1 — an ancestor of the blocked issue — leaving exactly **1**. Threshold retargeted `-ge 2` → **`-ge 1`**, with the Condition, Instructions, R2 and Approach all moved together. **Recorded as structural, not arithmetic**: this threshold has now been wrong THREE times (4, then 2, then 1), every time because a stub correction moved upstream of the gate. The Instructions now say the value is deliberately a FLOOR that survives further movement, and that discrimination is preserved because a vacuous check returns 0. Did not restore `:1023` to 5.1 — pass-5 C42 established that omitting it from 2.1 raises the very TypeError 2.1 exists to remove. | `main-session` | `resolved` |
