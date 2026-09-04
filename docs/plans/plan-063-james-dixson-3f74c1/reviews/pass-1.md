---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 1 on plan-063. REVISE with 16 concerns, 6 high. Measured: SC3b is IMPOSSIBLE because _recheck_unescape rewrites the escaped pipe and the clause lacks -E (the plan-062 pipe class one layer deeper); Capability Gate 2 is a reachability cycle the drafter WORDED AROUND rather than removed; Issue 3.1s literal git argv is invalid; path-scoping the commit without scoping the guard creates a new post-boundary halt; the dispatch wrapper as specified does not halt; and A1 requires seven REQ ids, not six.'
---
# Red-Team Pass 1 — plan-063-james-dixson-3f74c1

## Verdict: REVISE

## Strengths

**The DAG enforces the plan's headline ordering** — `5.1 <- 2.3, 3.3` is a real edge, not prose.
29 issues, no cycles, no dangling `depends-on`, every issue named by a criterion and every
criterion naming a real issue.

**Every factual claim checked against source is accurate**: `_worktree_teardown(plan_dir, force)`
at `:4354` with no default; the branch delete at `:4392`; the duplicate at `:9515`; dispatch at
`:9747`; `worktree_dirty` at `:8043`; L16's whole-index commit and substring filter verbatim;
`resolvable_by_agent` 5 writes / 0 reads across all of `skills/` and `scripts/`; L8–L15 bare
`subprocess.run` with `bd list` the only one lacking `cwd=`; all four stubs.

**The A2 simulation is confirmed** by re-running the script's own `parse_plan` + `reaches_req`:
21 implementation issues, `req_bearing = {0.1…0.6}`, `unreachable = []`.

SC13 verified live — exits 0 today, stops matching after the fix. Gate 1 is green, discriminating
and correctly placed.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **SC2b is VACUOUS.** `grep -c 'delete-execute-branch'` = **1** today, so `-le 1` holds before any work. The string occurs once at `:9516` — the action *label* — while the duplicate the criterion names is the `ctx.run` call at `:9515`, which the grep cannot see. Issue 2.2 has no discriminating verification. | Clause over the call expecting absence, plus a positive Tier-1 case asserting L18 emits no `delete-execute-branch` action and the delete still happens inside `_worktree_teardown`. |
| C2 | high | **SC3b is IMPOSSIBLE — the plan-062 pipe class one layer deeper.** `_recheck_unescape` (`:3209`) rewrites `\|` → `|` before execution, and the clause has no `-E`. In BRE `\|` *is* alternation; stripping the backslash makes it a literal pipe. Measured: the escaped form matches, the unescaped form does not. SC3b can never hold at L5/L11 even after 3.2 lands. | Add `-E`. |
| C3 | high | **Capability Gate 2 is a reachability cycle, and the plan WORDED AROUND THE DETECTOR.** It `Blocks: 5.1`; its Test runs a script authored by **5.2**, and `5.2 depends-on 5.1`. `gate_consistency` passed only because the Instructions avoid naming the id — and the plan *says so out loud*. That is evading the detector, not removing the cycle. | Swap the edges: `5.2 depends-on 2.3, 3.3`; `5.1 depends-on 5.2`. Then the evidence is a predecessor and the Instructions can name it honestly. |
| C4 | high | **Issue 3.1's literal argv is invalid git.** After `--` every token is a pathspec. Measured: `git commit -o -- <dir> -m "msg"` → `error: pathspec '-m' did not match any file(s)`, exit 1. Implemented as written, L16 fails **every** landing at a post-outward-write step. | Pin the order: `git commit -m <msg> -o -- <plan_dir>` (measured working). |
| C5 | high | **Path-scoping the commit without scoping the guard creates a NEW halt on a normal landing.** L16's guard is `git diff --cached --quiet` over the **whole index** (`:9358`). Measured: unrelated file staged + plan dir unchanged → guard says "staged", scoped commit exits 1 `no changes added to commit`, L16 returns halting `fail` at `L_PUSHED_2`. | Scope the guard too: `git diff --cached --quiet -- <plan_dir>`, and cover the case in 3.3. |
| C6 | high | **Nothing verifies the #342 fix does not break a normal landing.** The only existing L16 test drives a `FakeRunner` with `{"diff\|--cached": _R(1)}` — no real git runs, so an argv git rejects (C4) still passes. Issue 3.3's two new cases are both **negative**. SC11 is exit 0 today regardless. If the new test also uses `FakeRunner`, SC3 is vacuous too. | 3.3 must state the new cases run against a **real sandbox git repo with a bare origin**, and add a **positive** case: plan-folder writes (including a new untracked file) *are* in the commit. Add an SC. |
| C7 | medium-high | **The wrapper as specified does not halt.** `_land_execute`'s predicate is `if r["verdict"] == "fail" and r.get("halting")` (`:9779`). An `inconclusive` row with `halting=True` falls through and the loop **runs the next step**. For L18 that is invisible; for an early step the landing walks past a crash. | 1.1 must name the mechanism: return the halted envelope from the `except` block, or widen the predicate. SC1 must assert `halted is True` **and** that no subsequent step row was produced. |
| C8 | medium | **Issue 0.6 says "six ids"; A1 derives SEVEN.** `touched = {REQ-LAND-020, 030…035}` — `REQ-LAND-020` is named in 0.6's own body and is not in `CITED_NOT_TOUCHED`. A six-bullet log → A1 FAIL → SC9b false at completion. | Reword to seven, naming `REQ-LAND-020` explicitly. |
| C9 | medium-high | **Epics 3 and 4 both define "dirty outside the plan folder" with nothing forcing agreement.** 3.2 builds the enforcement predicate; 4.2 builds the prediction predicate for the same fact. Two implementations of one rule is exactly how the dry-run stops predicting L16 — this plan's objective. | `4.2 depends-on 3.2`; one shared helper; a criterion asserting a single definition site. |
| C10 | medium | **Issue 2.2 removes the suite's only proof that L18 deletes the execute branch.** After the fix the delete happens inside `_worktree_teardown` via `_run_git`, invisible to `ctx.run` — and still invisible after 5.1, since a corrected stub performs no deletion. | 2.2 must *replace* the assertion: capture the stub's args and assert `(ctx.plan_dir, force=False)`, and assert no `branch -d` reaches `ctx.run`. |
| C11 | medium | **SC11 and SC15 already hold.** SC11 is exit 0 whether or not 3.3 adds a test, so it cannot discharge 3.3. | Give SC11 a floor that moves, or discharge 3.3 by SC3/SC3c alone. |
| C12 | medium | **Issue 3.2's prefix test will not match raw porcelain lines** — they carry a two-char status + space, and quote paths with spaces. A naive `startswith` matches nothing; a naive `in` reinstates the substring bug. | Prescribe `--porcelain=v1 -uall -z`, split on NUL, prefix-test the path field; add a spaced-path case. |
| C13 | low-medium | **SC13 and SC4b are bare negative greps** — they also pass when nothing was searched (`git grep` exits 1 on an unmatched pathspec). | Pair each with a positive control in one clause. |
| C14 | low | **SC2 and SC13 pin inconsistent spellings** — SC2 requires an exact single-line literal that a wrapped call would fail while SC13 accepts it. | Loosen SC2 to a whitespace-tolerant `-E`. |
| C15 | low | **Factual nits.** The stub is at `:140` not `:139`; the `or "0"` laundering is at `:9396` not `:9401`; and **#341's title is inverted** — the field is constantly `True`, so it can never report *clean*. | Fix the numbers; note the inverted title in the row and in 6.2's draft. |
| C16 | low | **Gate 3 is a frontloading miss** — evidence exists when 3.3 closes but it blocks 6.3, eight issues later. | Move `Blocks:` to `5.1`. |

## Missing

- **EXP-002's recommendation 6 is dropped** — assert no step returned `inconclusive` with an
  `exception` key. That is the wrapper's own green-on-an-unrunnable-path risk.
- **No check that the digest survives a resume** once 4.1 puts live booleans into `facts`.
  `primary_checkout_dirty_outside_plan_dir` can flip mid-landing, and REQ-LAND-011 re-checks the
  digest on resume — in a plan that exists because a landing had to resume.
- **EXP-002 rec 5(b)** (routing L8–L15 through `ctx.run`) is unscoped and unrecorded.
- **#331 is worked around for the third consecutive plan** with no issue recording the residue.
- **No criterion covers Issue 4.4's "drop the field" branch.**

## Gate Assessment

| Gate | Verdict |
| :-- | :-- |
| Gate 1 (in-place) | Green now, discriminating, correctly placed. **No concern.** |
| Gate 2 (mock-fidelity discriminating) | **Cycle — C3.** Also: with the script absent, `test "" -ge 4` exits 1, indistinguishable from "found fewer than 4". Wrap to fail loudly. |
| Gate 3 (L16 commits only its own paths) | Correctly red today (pytest exit 5), discriminating once 3.3 lands. Frontloading miss (C16). **Its value is entirely contingent on C6** — if the new test uses `FakeRunner`, this gate stands between the landing and nothing. |

## Upstream Assessment

Dispositions defensible; five `include` rows map to concrete issues and `Resolved By` is accurate
against the DAG. #340's row correctly makes closure conditional on 2.2 and 2.3 rather than the
one-line fix. `#331 partial` is honest but is the third plan to work around it and deserves a
residue note. `#332 exclude` correctly reasoned. **#341's quoted title is inverted** (C15).
`references/` carries all seven; `assets/upstream-drafts/` correctly does not yet exist.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | Confirmed independently: `grep -c 'delete-execute-branch'` = **1**, so `-le 1` held before any work. SC2b now targets the CALL — `grep -q 'ctx.run("git", ["branch", "-d"' … -> exit 1` — re-measured exit **0** today (present, correctly unmet). New **SC2d** adds the positive half: L18 still deletes the branch via the teardown. | `main-session` | `resolved` |
| C2 | high | **Confirmed behaviourally, and it is the third pipe defect in this plan lineage, in a third direction.** Measured on a fixture file: the clause as typed exits 0, but what `recheck-criteria` actually executes after `_recheck_unescape` strips the backslash exits **1**; adding `-E` restores exit 0. SC3b now uses `grep -qE`, re-measured exit 1 today (correctly unmet). | `main-session` | `resolved` |
| C3 | high | **The sharpest concern in the pass, and correct — I worded around the detector instead of removing the cycle, and said so in the plan text.** Edges swapped: `5.2 depends-on 2.3, 3.3` (author the check) and `5.1 depends-on 5.2` (correct the stubs). The evidence producer is now a genuine PREDECESSOR of the blocked issue. Re-verified: no cycles, no dangling deps, `gate_consistency` PASS. The Instructions were then reworded a second time because they still NAMED the blocked issue — the same arm-1 trip, caught by re-running the checker. | `main-session` | `resolved` |
| C4 | high | Reproduced exactly: `git commit -o -- d -m "msg"` -> `error: pathspec '-m' did not match any file(s)`, exit 1; `git commit -m "msg" -o -- d` succeeds and commits only the scoped dir. Issue 3.1 now pins the argument order and states that after `--` every token is a pathspec. | `main-session` | `resolved` |
| C5 | high | Issue 3.1 now scopes the GUARD as well — `git diff --cached --quiet -- <plan_dir>` — with the measured failure recorded: an unrelated staged file otherwise makes the whole-index guard say 'staged' while the scoped commit exits 1, producing a halting fail at `L_PUSHED_2`. | `main-session` | `resolved` |
| C6 | high | Issue 3.3 now requires a **REAL sandbox git repo with a bare origin**, not `FakeRunner`, and adds the missing **positive** case: the plan-folder writes, including a new untracked file, ARE in the commit and a normal landing still passes. New **SC3d** discharges it. Without this, Gate 3 would have stood between the landing and nothing. | `main-session` | `resolved` |
| C7 | medium-high | Issue 1.1 now names the mechanism: **return the halted envelope directly from the `except` block**, because `_land_execute`'s predicate is `verdict == "fail" and halting`, so an `inconclusive` row falls through and the loop runs the next step. Recorded that for L18 this is invisible (L19 is next) but for an early step the landing would walk into destructive work. | `main-session` | `resolved` |
| C8 | medium | Issue 0.6 now says **seven** ids and names `REQ-LAND-020` explicitly, with the reason: A1 derives it from 0.6's own body, so a six-bullet log fails A1 and SC9b goes false at completion. | `main-session` | `resolved` |
| C9 | medium-high | `4.2 depends-on 3.2` added, and 4.2 must call the SAME helper 3.2 builds. New **SC4c** asserts a single definition site (`grep -c 'def _dirty_outside' -eq 1`), re-measured exit 1 today. | `main-session` | `resolved` |
| C10 | medium | Issue 2.2 now REPLACES rather than deletes the assertion: capture the stub's args and assert `(ctx.plan_dir, force=False)`, and assert no `branch -d` reaches `ctx.run`. Records why — the real delete moves inside `_worktree_teardown` via `_run_git` and becomes invisible to `ctx.run`. | `main-session` | `resolved` |
| C11 | medium | SC11 now carries a floor that moves: `>= 56 passed` against 51 collected today. Re-measured exit 1 (correctly unmet). | `main-session` | `resolved` |
| C12 | medium | Issue 3.2 now prescribes `--porcelain=v1 -uall -z`, splitting on NUL and prefix-testing the path field, with the reason (two-char status prefix, quoted paths) and a spaced-path case. | `main-session` | `resolved` |
| C13 | low-medium | SC4b and SC13 now pair a positive control with the negative in one clause, so a mistyped pathspec or renamed file cannot produce a green. | `main-session` | `resolved` |
| C14 | low | SC2 loosened to a whitespace-tolerant `-E` pattern, so a wrapped call satisfies SC2 and SC13 consistently. | `main-session` | `resolved` |
| C15 | low | Line numbers corrected (`:140`, `:9396`). The **#341 row now records that the issue title states the direction backwards** — the field is constantly `True`, not constantly `False` — and requires the closing comment to correct it. | `main-session` | `resolved` |
| C16 | low | Gate 3 hoisted from `Blocks: 6.3` to `Blocks: 5.1`, its floor. Issue 6.1 additionally now files the L8-L15 injectability gap and the accumulating #331 residue (third consecutive plan to hand-cut its execute branch). | `main-session` | `resolved` |
