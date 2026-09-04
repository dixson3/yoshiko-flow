---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 3 on plan-063. REVISE with 7 concerns, one high. C19, C20, C21 and C27 independently re-derived and CONFIRMED correct. HEADLINE C30: the mock-fidelity capability gate is arithmetically unsatisfiable — pass-2s C18 fix moved two stub corrections into Issue 2.1, which is an ancestor of the issue that authors the check, so only 2 of 4 incompatible stubs survive to be found and the gate demands 4. Three artifacts assert a number the DAG makes impossible.'
---
# Red-Team Pass 3 — plan-063-james-dixson-3f74c1

## Verdict: REVISE

## Strengths

**Four pass-2 resolutions independently re-derived and CONFIRMED**, not taken on assertion:

- **C19 correct.** `_land_exit_code:7737` maps `fail→1`, and `land_cmd:8380` checks `halted`
  **first**, before the inconclusive branch. Returning the halted envelope from the `except`
  block sets `halted`, so verdict is `fail` and exit is **1**.
- **C21 correct.** Traced L16: the whole-index guard is non-zero on an unrelated staged file so
  the commit runs; scoping it makes it exit 0 and skip the commit; `--only` leaves the file
  staged, so the post-condition still sees it and returns a halting fail. "Removes a misleading
  commit error, does NOT remove the halt" is exactly right, as is the pathspec-order warning.
- **C20's premise verified.** `_worktree_teardown:4354` returns `{"status","path","branch","steps"}`
  and **never** `action`; all four stubs return `{"action": …}`; `_land_l18_prune:9511` reads
  `wt.get("action") or wt`.
- **C27's premise verified and reachable.** L19 follows L18, and `land_cmd:8361` re-derives facts
  and re-checks the digest on **every** action including `resume` — so a post-L18 halt at L19,
  which Epic 1's own wrapper newly makes possible, really does hit a mutated
  `execute_worktree_present`.

The 3.2 → 4.2 shared-helper ordering is correctly expressed and `_dirty_outside_plan_dir` names a
real identifier SC4c can pin.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C30 | high | **The mock-fidelity gate is arithmetically UNSATISFIABLE, as a consequence of pass-2's C18 resolution.** The gate wants `-ge 4` incompatible stubs. Issue 5.2 authors the check and binds `inspect.signature` only. But Issue 2.1 now corrects `:1180` and `:1254`, and **2.1 is an ancestor of 5.2** (`5.2 ← 2.3 ← 2.2 ← 2.1`). Measured: exactly 4 one-arg stubs exist; after 2.1 only **2** remain. There is no moment at which the check exists AND 4 are findable. This contradicts Approach ¶2, the gate's own Instructions, and R2's mitigation — **three artifacts assert a number the DAG makes impossible.** | Lower the threshold to `-ge 2` and rewrite the Condition, Instructions and R2 to name the two stubs 2.1 does **not** touch (`land_rehearsal.py:140`, `test_land_apply.py:1023`), recording *why* the count is 2. All three artifacts must move together. |
| C31 | medium | **Issue 4.1 emits the dirty-outside facts but does not `depends-on: 3.2`.** Only 4.2 carries that edge, so 4.1 may legitimately run first and write its own predicate — producing the second definition site SC4c exists to forbid. SC4c is discharged-by 3.2 and 4.2, not 4.1, so nothing local catches it. | Add `depends-on: 3.2` to 4.1, state the fields are computed **via** the shared helper, and add 4.1 to SC4c's Discharged-by. |
| C32 | medium | **Issue 2.1 now carries three separable edits** and only SC2 covers it — a grep for the call site. A completion that fixes the call and forgets a stub passes SC2, and no criterion discharged-by 2.1 fails. The breakage would surface only via the FAST tier, outside the criterion set; SC11 is discharged four issues later. | Add a criterion discharged-by 2.1 asserting stub arity at both sites, or split 2.1 so partial completion is visible in the bead graph. |
| C33 | low-medium | **Issue 4.1 hands the C27 decision to the executor** ("*either* exclude … *or* cover a post-teardown resume") but SC5b — "the digest **survives**" — admits only the first branch. An executor choosing the second cannot satisfy a criterion whose name asserts survival. | Collapse 4.1 to the exclude branch, or rename SC5b branch-neutrally and say what evidence each branch produces. |
| C34 | low-medium | **The wrapper is narrower than the Objective claims.** Issue 1.1 wraps `:9747`; the journal write at `:9754` and the row access at `:9755` are **outside** it, so a `LandingJournal.write` failure or a row missing `verdict` still tracebacks — precisely #340's failure mode. REQ-LAND-030's letter is satisfied; the Objective reads broader than what ships. | Extend the `try` through the journal write, or narrow the Objective and REQ-LAND-030 and file the residue in 6.1. |
| C35 | low | **The plan's theory is half-closed by its own tool.** `check_mock_fidelity` is signature-only, but the divergence that is load-bearing *in this plan* is the **return shape** (2.3 branches on `wt["status"]` against stubs returning `action`), fixed by hand in 5.1 with nothing in 6.1 about it. And on the theory itself: the evidence is 4 stubs of **one** function — "mock fidelity is *the* systemic gap" is a generalisation from n=1 target, defensible because the check is cheap, not because the sample supports it. | Add a return-shape check (or a documented decision not to build one) to 6.1. Soften the Motivation to what was measured. |
| C36 | low | Motivation says `land_rehearsal.py:139`; Issue 5.1 says `:140`. Measured: `:140`. | Correct the Motivation. |

## Missing — what a landing could still do wrong

1. **The `--apply` CLI preamble remains untested by anything.** EXP-002 measured zero coverage of
   `land_cmd:8210–8372` — decision load, `_land_repreview_or_halt`, digest binding, manifest
   derivation. A defect there aborts before L0 or binds a stale decision. It is in the plan's own
   finding and in **no** issue and **not** in 6.1's residual list.
2. **Exceptions outside step bodies** — C34.
3. **L16 still fails on untracked residue created DURING L7–L15**, post-outward-write. 4.2
   predicts dry-run-time dirt, which is the right mitigation, but a file created by the close
   chain is invisible then and reproduces the wedge this plan exists to prevent.
4. **The non-halting `inconclusive` fall-through survives by design** for L8/L12. Only the newly
   wrapped crash path returns early.

## Gate Assessment

| Gate | Verdict |
| :-- | :-- |
| in-place execution | Reachable, condition independent of what it blocks, correctly hoisted to block the branch-creation issue. **Sound.** |
| mock-fidelity discriminating | **NOT satisfiable — C30.** Not a reachability cycle (pass-1 C3 genuinely fixed that); an **arithmetic contradiction** introduced by pass-2's C18. It will run, evaluate `2 -ge 4`, and fail with no legitimate remediation. |
| L16 commits only its own paths | Reachable, evidence exists once 3.3 closes, correctly at its floor. **Sound.** |
| Reconcile | Standard. |

## Upstream Assessment

Dispositions reasonable. #341's note correcting the issue title's direction is verified against
`:8043`. #331 as `partial` with residue accumulating into 6.1 is honest. #332 `exclude`
defensible. SC15b's `-ge 6` matches the six non-`exclude` rows.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C30 | high | Confirmed by measurement: exactly **4** one-arg `_worktree_teardown` stubs exist, and Issue 2.1 corrects 2 of them upstream of the issue that authors the check — so only 2 survive. Threshold lowered to `-ge 2`, and the Condition, Instructions, R2 and Approach ¶2 were ALL rewritten together to name the two that remain (`land_rehearsal.py:140`, `test_land_apply.py:1023`) and record why the count is 2. **This was my pass-2 C18 fix breaking the gate my pass-1 C3 fix had just made reachable** — the fifth instance of this pattern in the plan lineage. | `main-session` | `resolved` |
| C31 | medium | `4.1 depends-on 0.6, 3.2` added, and 4.1's body now states the two `primary_checkout_*` fields are computed VIA `_dirty_outside_plan_dir` rather than by an inline predicate. SC4c's Discharged-by widened to `3.2, 4.1, 4.2`. | `main-session` | `resolved` |
| C32 | medium | New **SC2e** discharged-by 2.1 asserts both stubs were corrected, not just the call: `grep -c 'lambda pd: {"action"' -eq 1` (only `:1023` should remain). Re-measured exit 1 today — 3 such stubs — so a partial completion of 2.1 is now visible in the criterion set rather than only via the FAST tier. | `main-session` | `resolved` |
| C33 | low-medium | Issue 4.1 collapsed to the **exclude** branch, with the reason recorded there. The decision is taken in the plan rather than deferred to the executor, so 4.1 and SC5b now agree — SC5b asserts the digest survives, and only that branch can satisfy it. | `main-session` | `resolved` |
| C34 | low-medium | The Objective now states the scope honestly: the wrapper covers a step raising, and the executor's own bookkeeping (the journal write and the row-shape access) stays OUTSIDE it. That residue is filed by Issue 6.1 rather than silently implied to be covered. | `main-session` | `resolved` |
| C35 | low | Motivation softened from 'the common thread is not dead code' to 'the common thread, stated no more strongly than the evidence supports' — the sample is 4 stubs of ONE function. Issue 6.1 now also files the absence of a RETURN-shape fidelity check, the untested `--apply` CLI preamble, and the bookkeeping residue from C34. | `main-session` | `resolved` |
| C36 | low | Motivation corrected to `land_rehearsal.py:140`. | `main-session` | `resolved` |
