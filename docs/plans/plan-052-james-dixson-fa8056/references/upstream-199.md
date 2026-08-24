---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #199: yf-plan: nothing re-checks plan.md Success Criteria at completion — a criterion discharged mid-plan rots silently

- **Number:** 199
- **Title:** yf-plan: nothing re-checks plan.md Success Criteria at completion — a criterion discharged mid-plan rots silently
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Split out of the **plan-051** session by operator decision, alongside #198. Related to #198 (both are "a stage a script could own"), but a **different trigger**: #198 fires inside the review loop, this fires at plan completion.

## The defect

**Nothing re-checks `plan.md`'s Success Criteria at end state.** A criterion is discharged by an issue mid-plan, measured green at that point, and then never re-read. A later epic can silently invalidate it.

This is not hypothetical — it happened in plan-051 and is logged there as **RE-003**.

## The measured instance

`SC4b` asserts that the hand-enumerated `#182` edit set is **closed**: every surviving `never writes files` restatement under `skills/yf-plan/**` and `web/content/**` must be an enumerated row in `assets/edit-set-182.md`.

| Point in the plan | Hit set | Subset holds? |
| :-- | --: | :-- |
| at `main` (pre-plan) | 7 | yes |
| after Issue 1.2a — SC4b's discharge point | 7 | **yes — measured green** |
| after Issue 3.2 (`1eb9bae`) | **8** | **NO** |

Issue 3.2 created `skills/yf-plan/scripts/test_review_agent_contract.py`, whose line 145 carries the phrase inside an **assertion message**:

```
"`Verification:` line greps for — an unscoped 'never writes files' is the "
```

That took the hit set from 7 to 8 and out of subset. SC4b was **false at plan completion** while every one of the plan's own mechanisms reported green.

## What did NOT catch it

Worth enumerating, because the plan was unusually well instrumented — 3 driven-red controls, a 45-command FULL tier, a 13-cycle predecessor:

- **The FULL `CHANGE-VALIDATION.md` tier** — `plan.md` criteria are not recipe rows.
- **The three `ctl-*` controls** — they cover the epics' behaviour changes, not the criteria table.
- **`redcheck.sh verify-all`** — it reads a red→green **transition record** written once and never re-evaluated.
- **The plan's own end-of-epic mandate** — it covers the three **fixtures** only. SC4b has no fixture.

It was caught by **operator re-measurement**, i.e. a human happening to re-run the command. Nothing the plan ships would have caught it, and nothing would catch the next one.

## The sub-class worth naming separately

The invalidating file was the plan's **own test script**, and it matched because a failure message **quotes the retired wording in order to explain it**. So the instrument became a member of the set it measures.

This recurs. plan-050's C119 is the same shape: a derivation's `grep` pattern, written into the issue text, **matched itself** and returned 7 instead of 6, making a capability gate unsatisfiable.

The resolution precedent is already ratified in this repo and should be cited rather than re-argued — **`REQ-BUP-053` / `GR-BUP-005`** (`skills/yf-beads-upstream/SPEC.md`) hold that statements quoting a forbidden construct *in order to forbid it* are **explanation, not the construct**, and go further:

> A check asserting *zero* occurrences of `bd github push` anywhere in the skill is therefore **wrong by construction** and shall not be written — it would fail on the invariant statements themselves, **pressuring a future editor into deleting the very rule this requirement enforces.**

That is the argument against "just reword it to dodge the grep", stated repo-wide, two years of context ahead of the plan that needed it. plan-051 took the enumerate-with-a-disposition route on that basis.

## Proposed shape

An **end-state criteria sweep** owned by a script, not by an author remembering:

1. At RECONCILE, parse `plan.md`'s Success Criteria table.
2. For each row whose `Verification` column is a runnable command, **re-run it against the merged tree** and report per-criterion pass/fail.
3. For rows that are not runnable, report them explicitly as **unmechanized** rather than silently skipping — the same honesty move `assets/edit-set-182.md` makes with its "NOTHING MECHANICAL" rows.
4. Fail the reconcile step on any regression.

Step 3 is the load-bearing one. A sweep that silently skips prose criteria reports green over the exact rows most likely to rot.

**This composes with #198.** If stages become scripts that own their own exit tests, "end-state sweep" is simply one more stage with a mechanical exit condition — it does not need bespoke machinery.

**Prerequisite, and it is not free:** this only works to the extent `Verification` columns are *executable*. plan-051's #165 work (`REQ-AGENT-049` and the `043`/`045` retarget) landed the corpus's **first three** whole-line-executable `Verification:` clauses out of a 221-clause census. So the sweep's coverage starts near zero and grows with that conversion. Say so rather than shipping a sweep that reports a vacuous green over 218 prose rows — **a non-empty vacuity guard is mandatory**, per the same rule SC4b, 3.2 and 3.3 all carry.

## Evidence

In the plan-051 bundle:
- `assets/sc11-full-validation.md` — the one-off end-state sweep, including all five fixture-less criteria. **A record, not a mechanism.**
- `assets/edit-set-182.md` row 18 — the quote-to-forbid disposition.
- `plan-retrospective.md` RE-003.

The generalizable finding, as stated there:

> a plan that re-checks only the artifacts it built a fixture for has re-checked the easy half. Criteria discharged mid-plan are the ones that rot, precisely because nothing re-reads them.

