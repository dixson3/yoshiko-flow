---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 2 on plan-063. REVISE with 13 concerns (C17-C29), 2 high and 3 medium-high. All 16 pass-1 resolutions re-measured and REAL. But FOUR pass-1 fixes introduced new defects: C3s edge swap made 5.1 a DAG sink, C7s mechanism made the claimed exit 2 impossible, C11s floor measures growth rather than passing, and C5s stated rationale is false. Also finds the suite is red for six issues in the direction the plan never considered, and that the stubs are unfaithful on the RETURN axis which check_mock_fidelity is structurally blind to.'
---
# Red-Team Pass 2 — plan-063-james-dixson-3f74c1

## Verdict: REVISE

## Strengths

**All sixteen pass-1 resolutions re-measured and REAL** — not read from the table. C2 verified
*through the actual `_recheck_unescape` path*: `recheck-criteria` executes the backslash-stripped
`grep -qE`, exit 1 today, and it matched **all three** plausible post-fix fixtures. C3's cycle is
genuinely gone: `5.2 <- 2.3, 3.3`, `5.1 <- 5.2`, evidence producer a real ancestor, Instructions
naming no id. C4 reproduced in a sandbox both ways.

**Every clause runs and every clause is correctly unmet**: 23 FALSE, 5 manual, 1 holds. None
impossible, inverted, or 126/127. All repo checkers clean; A2 confirmed with `touched` = **7**
ids. No issue lacks a criterion; no criterion names a nonexistent issue. SC11's floor arithmetic
is right *as a growth gate*.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C17 | high | **`5.1` and all of Epic 4 are DAG SINKS — Epic 6 is not ordered after them.** Sinks: `{4.4, 5.1, 6.6}`. `6.3`'s ancestor set contains **no Epic-4 issue and not `5.1`**, so the FULL tier, the primary-checkout confirmation, the handoff and the index refresh may all run before the dry-run fields exist and before the stubs are corrected. **The `5.1` half is a regression from C3's swap** — pre-swap `5.1` was an ancestor of `6.1`; post-swap it is a leaf. | `5.3 depends-on 5.1` and `6.1 depends-on 4.4`. |
| C18 | high | **Fixing L18 BREAKS the suite until `5.1` — the symmetric direction the plan never considered.** Measured with only Issue 2.1 applied: `test_prune_is_strategy_aware` and `test_each_step_invokes_the_RIGHT_EXECUTABLE` both fail with `TypeError` (1-arg stubs at `:1023`, `:1254` called with `force=False`). 2.2 repairs `:1023`; `:1254` waits for `5.1`. The FAST row runs the whole file on every `skills/yf-plan/scripts/**` edit, so the on-edit gate is **red from 2.1 through 5.1 — six issues.** | Move the `:1254` and `:1180` corrections into Issue 2.1's change-set, as 2.2 already does for `:1023`. |
| C19 | medium-high | **Issue 1.1's "exit 2" is IMPOSSIBLE given the mechanism C7 prescribed.** Returning `{"halted": True}` makes the CLI compute `verdict = "fail"` (`:8382`, halted wins) → exit **1**. EXP-002's measured exit 2 came from calling `_land_execute` directly, where the row *fell through* — an artifact of the very defect C7 removed. **C7's resolution silently invalidated the exit-code claim.** | State exit **1** and why, or amend the verdict derivation (needs a REQ-LAND-012 amendment, hence an Epic-0 issue). Either way SC1 must assert the code explicitly. |
| C20 | medium-high | **The stubs are unfaithful on the RETURN axis too, and Issue 2.3 makes that load-bearing in the same change-set.** The real `_worktree_teardown` returns `{"status", "path", "branch", "steps"}` and **never** `"action"`; all four stubs return `{"action": "removed"}`. 2.3 makes L18 branch on `wt["status"]`, which the stubs do not carry. `check_mock_fidelity` binds `inspect.signature` and is **structurally blind** to return shape. The plan's own headline diagnosis applies verbatim and the remedy does not reach it. | 5.1 must correct the stubs' **return dict**, not just the parameter list; 2.3 must state missing-key behaviour; 5.2 must record that the check covers the argument axis only. |
| C21 | medium-high | **Issue 3.1's C5 rationale is FALSE — measured.** With the scoped guard, in the exact cited case: guard exits 0 → commit skipped → push succeeds → the post-condition still sees `M other.txt` and returns a **halting fail**. Scoping the guard removes a misleading commit error; it does **not** remove the halt. Dangerous because if 3.3 case (a) is written expecting `pass`, the natural "fix" is to scope the post-condition — re-opening #342 on the exact axis Gate 3 guards. | Correct the sentence; 3.3 case (a) must pin the expected envelope (`verdict: fail`, `halting: true`, file absent from `HEAD`). |
| C22 | medium | **SC11 does not measure "passes".** Measured on a broken tree: `6 failed, 45 passed` still yields `45`. `56 passed, 3 failed` would satisfy it. **Pass-1's C11 fix introduced a new instance of the class it removed.** | Pair the count with the exit code in one clause. |
| C23 | medium | **Issue 5.3 can wire a RED check into `CHANGE-VALIDATION.md` before 5.1 fixes the stubs** — `5.3 <- 5.2` only. Between them the check reports ≥4 by design, so every subsequent on-edit validation fails. | `5.3 depends-on 5.1` — the same edge C17 needs. |
| C24 | medium | **The Approach still asserts the pre-swap order** ("the check must land after the stubs are corrected"). The DAG now orders `5.2` before `5.1`. | Rewrite, and say the consequence: the check *does* fail on arrival in that window, which is what Gate 2 measures. |
| C25 | medium | **Gate 1 is a frontloading miss, and pass 1 cleared it.** Its Test depends on nothing any issue produces, so its floor is the first issue after 0.0 — but it blocks `1.1`, so `0.1`–`0.7` run first, **including 0.7**, whose correctness depends entirely on in-place mode. Under worktree mode, seven SPEC commits and a hand-cut branch land in the wrong address space before the gate fires, and its remediation is a restart that throws that work away. | `Blocks: 0.7, 1.1, 3.1, 4.1`. Not `0.0` — gating that would recreate R4. |
| C26 | low-medium | **SC4c pins an identifier no issue prescribes.** A reasonable `_land_dirty_outside_plan_dir` yields 0 and SC4c goes false for a naming reason. | Name the helper in 3.2, or loosen the pattern. |
| C27 | low-medium | **Issue 4.1's new facts are digest-covered and one is mutated by the landing itself.** `execute_worktree_present` flips true→false when L18's teardown runs, and the digest is re-derived on resume — so a halt after a partial L18 MISMATCHES. (Today's field has the same shape, so 4.1 preserves a latent bug rather than creating it.) | 4.1 must state the field is landing-mutated; SC5b must cover a **post-teardown** resume, or exclude those fields from the digest with the reason recorded. |
| C28 | low | **C14 only partially resolved.** With `/usr/bin/grep` (what `bash -c` resolves), the `-E` pattern does not match a **wrapped** call — grep is line-oriented, so `\s*` cannot span a newline. SC13 still accepts what SC2 rejects. | Drop the claim, or state that 2.1 must not wrap the call. |
| C29 | low | **SC15 already holds** — not vacuous (the bundle grows and it is re-evaluated at completion) but it confirms rather than discharges 6.6. | Acceptable; record so a later pass does not re-raise it. |

## Missing

- **Nothing records that the Tier-1 suite is expected red between 2.1 and 5.1** (C18).
- **Nothing pins the exit code of a crashed landing** (C19) — SC1 runs a test whose assertions are
  unspecified on the one number EXP-002 measured wrong.
- **The mock-fidelity check's axis is not bounded in writing.** Return shapes (C20), keyword-only-ness
  and non-callable assignments are all outside it. 5.2 should say what it does **not** cover, so
  "the class is closed" is not over-claimed a third time.
- `check_amendment_log`'s success line under-counts (`n_impl` subtracts a hardcoded `{4.6, 4.7}`
  baseline absent from this plan). Cosmetic, in the instrument — worth a line in 6.1.

## Gate Assessment

| Gate | Verdict |
| :-- | :-- |
| Gate 1 | Green and discriminating. **Frontloading miss — C25**: it blocks `1.1` when its floor is `0.7`, and `0.7` is precisely the issue that breaks under worktree mode. |
| Gate 2 | **Cycle genuinely removed.** `5.2` is a real ancestor; Instructions name no id; `gate_consistency` PASS; correctly red today; 5.2 now requires the script to fail loudly on an absent target. Remaining risk is C23. |
| Gate 3 | Correctly red, hoisted to its floor, and C6's resolution makes it guard something real. **But its meaning is undefined until C21 is settled** — the test it names will observe a halting fail, and whether that counts as passing is written nowhere. |

## Upstream Assessment

Unchanged and sound. Six non-`exclude` rows each with a reference file; `Resolved By` accurate
against the DAG; `assets/upstream-drafts/` correctly absent. #341's inverted title and #331's
third-consecutive-workaround residue are both now recorded — C15 and C16 resolved. SC15b's floor
of 6 matches `_land_upstream_rows`' non-`exclude` count exactly.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C17 | high | Confirmed independently: sinks were `{4.4, 5.1, 6.6}` and `6.3`'s ancestry contained neither. Added `5.3 depends-on 5.1` and `6.1 depends-on 4.4`. **Re-verified: SINKS = `['6.6']` only, and 6.3's ancestry now includes 5.1 and all four Epic-4 issues, no cycles.** The 5.1 half was a regression my own C3 swap introduced. | `main-session` | `resolved` |
| C18 | high | Issue 2.1 now corrects the `:1180` and `:1254` stubs in the SAME change-set, as 2.2 already did for `:1023`. The plan reasoned about the stubs-first direction and never considered the symmetric one; the FAST row runs the whole file on every `skills/yf-plan/scripts/**` edit, so this would have left the on-edit gate red for six issues. | `main-session` | `resolved` |
| C19 | medium-high | Verified at `:8382`: `if out.get("halted"): verdict = "fail"` — halted wins over the inconclusive list, so `_land_exit_code` yields **1**. Issue 1.1 now states exit 1 and why, records that EXP-002's measured exit 2 was an artifact of the fall-through C7 removed, and requires SC1 to assert the code. **My C7 fix silently invalidated the exit-code claim and I did not re-derive it.** | `main-session` | `resolved` |
| C20 | medium-high | Issue 5.1 now corrects the stubs' RETURN SHAPE as well as their arity; 2.3 states the missing-key behaviour; 5.2 records that the check binds the argument axis ONLY, so 'the class is closed' is not over-claimed a third time. The plan's own headline diagnosis applied verbatim to its own remedy. | `main-session` | `resolved` |
| C21 | medium-high | **My rationale was false and is corrected.** Issue 3.1 now says scoping the guard removes a misleading commit error but does NOT remove the halt, and that the halt is intended and predicted by 4.2. Issue 3.3 case (a) must pin the expected envelope (`verdict: fail`, `halting: true`, file absent from `HEAD`) — writing it to expect `pass` would invite scoping the post-condition and re-open #342 on the axis Gate 3 guards. | `main-session` | `resolved` |
| C22 | medium | SC11 now pairs the exit code with the count in one clause. Re-measured: exit 1 today (suite passes, 51 < 56 — correctly unmet for the growth reason, not a masked failure). **Pass-1's C11 fix had introduced a new instance of the class it removed.** | `main-session` | `resolved` |
| C23 | medium | Closed by C17's `5.3 depends-on 5.1` edge — the check cannot be wired into the manifest while it is still deliberately red. | `main-session` | `resolved` |
| C24 | medium | The Approach sentence rewritten to the post-swap order, and it now says the consequence out loud: the check DOES fail on arrival in that window by design, which is what Gate 2 measures. | `main-session` | `resolved` |
| C25 | medium | Gate 1 now `Blocks: 0.7, 1.1, 3.1, 4.1`. The Instructions were then reworded a SECOND time because naming `0.7` tripped `gate_consistency` arm 1 — **the fourth time in this plan that a gate's prose named a blocked id.** Now worded without ids; `gate_consistency` PASS. | `main-session` | `resolved` |
| C26 | low-medium | Issue 3.2 now names the helper `_dirty_outside_plan_dir`, and SC4c loosened to `grep -cE 'def _[a-z_]*dirty_outside'`. Re-measured exit 1 (correctly unmet). | `main-session` | `resolved` |
| C27 | low-medium | Issue 4.1 now states `execute_worktree_present` is LANDING-MUTATED and offers the two resolutions (exclude from the digest, or cover a post-teardown resume). SC5b retargeted to `digest_survives_resume_after_teardown` so it covers the specific resume that mismatches. | `main-session` | `resolved` |
| C28 | low | Claim withdrawn rather than defended: grep is line-oriented, so `\s*` cannot span a newline and SC13 still accepts a wrapped call SC2 rejects. Recorded here rather than papered over; the practical risk is near zero because 2.1's fix is one short line. | `main-session` | `resolved` |
| C29 | low | Acknowledged and recorded: SC15 holds today, is not vacuous (the bundle grows and it is re-evaluated at completion), and confirms rather than discharges 6.6. Noted so a later pass does not re-raise it. | `main-session` | `resolved` |
