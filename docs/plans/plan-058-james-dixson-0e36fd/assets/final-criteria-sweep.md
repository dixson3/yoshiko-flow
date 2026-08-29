---
type: Asset
okf_spec: OKF-PLAN
id: ASSET-final-criteria-sweep
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# Final criteria sweep — the same instruments, re-run against the finished tree

Every gate `Test:` and every non-manual Success Criterion `Verification`, re-run as written after
all 39 issues closed. Paired against the Issue 0.1 baseline so each instrument's movement is
visible.

## Result

| Instrument | Before | After | Verdict |
| :-- | --: | --: | :-- |
| Gate: Fan-out eliminated | 1 | **0** | flipped |
| Gate: Mechanical fan-out check green | 2 | **0** | flipped |
| SC1 | 5 | **0** | flipped |
| SC1b | 5 | **0** | flipped |
| SC2 | 5 | **0** | flipped |
| SC2b | 5 | **0** | flipped |
| SC3 | 5 | **0** | flipped |
| SC3b | 1 | **0** | flipped |
| SC4 | 5 | **0** | flipped |
| SC4b | 2 | **0** | flipped |
| SC4c | 5 | **0** | flipped |
| SC5 | 5 | **0** | flipped |
| SC5b | 5 | **0** | flipped |
| SC6 | 2 | **0** | flipped |
| SC6b | 1 | **0** | flipped |
| SC8 | 1 | **0** | flipped |
| SC8c | 1 | **0** | flipped |
| **SC7** | **0** | **0** | **invariant — green before AND after, as required** |
| SC3c | 5 | 5 | **N/A** — Follow-on activation declined |
| SC6c | 2 | 0 | **N/A — and VACUOUSLY GREEN. See below.** |
| SC8b | 1 | 1 | **N/A** — no destructive verb added |

**15 progress criteria and 2 gate tests flipped red → green. SC7, the sole invariant, was green
before and after and was never touched.** Three criteria are N/A as a direct consequence of the two
operator declines, exactly as the plan's gate Instructions specify.

## A vacuous criterion, found and reported rather than claimed

**SC6c is green, and its green means nothing.** Its `Verification` is:

```
uv run skills/yf-beads-upstream/scripts/test_check_no_universe_fanout.py
```

— which is **byte-identical to SC6's**. SC6c is supposed to assert that *the `deps_for` rule and its
control shipped once Issue 1.7 landed*. Issue 1.7 did **not** land (the operator declined), so that
rule did not ship — yet the criterion passes anyway, because it runs a command that SC6 already
makes green.

This is precisely the **vacuous-criterion class** the plan's own review cycles hunted and caught
four instances of. It is reported here rather than counted as a pass: **SC6c is N/A, not green.**

The related honest note is that this was *predictable at authoring time* — two criteria sharing a
verification command cannot discriminate between the two claims they make. The `-k` selector
discipline the plan applied so carefully to SC1/SC3/SC4c (naming tests explicitly so a selector
cannot be satisfied by unrelated work) was not applied to SC6c, which names no selector at all.

## Reading the residual exit codes

- **SC3c = 5** — pytest collected no test matching `-k followons_no_per_bead_dep_list`. Correct: the
  test was never written, because the behaviour it asserts was never implemented. A *red* N/A is
  more honest than SC6c's green one.
- **SC8b = 1** — `grep "dry-run by default"` finds nothing in `skills/yf-beads-hygiene/SPEC.md`.
  Correct: no destructive verb was added, so no requirement precedes one. Marking this green would
  be asserting a contract that protects nothing.
