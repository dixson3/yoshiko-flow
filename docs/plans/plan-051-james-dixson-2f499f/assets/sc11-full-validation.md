---
type: Reference
okf_spec: OKF-PLAN
id: sc11-full-validation
description: SC11 — the FULL tier over the merged tree, plus the end-state re-run of every control
---

# SC11 — FULL tier over the merged tree, and the end-state re-run

## The merged tree

`main` had **not advanced** since the execute branch was cut:

```bash
git merge-base main plan-051-james-dixson-2f499f-execute   # == main (3712aa7)
```

So the merge is a fast-forward and the execute branch's **tree is byte-identical to the
post-merge tree**. The FULL tier below therefore validates the merged state exactly, not an
approximation of it.

## The FULL tier

```bash
# from the tree root. NOTE: no --changed. Measured at source, change_validation.py:820 gates
# --changed on tier == "fast", and plan_manager.py:3529 hard-codes the FULL invocation without
# it — so the flag cannot reach this run. (The repeated-flag defect is real and is filed
# upstream by Issue 4.6; it affects no invocation this plan makes.)
uv run skills/yf-plan/scripts/plan_manager.py validate-merged \
  docs/plans/plan-051-james-dixson-2f499f --json
```

| Field | Value |
| :-- | :-- |
| `status` | **`pass`** |
| `engine` | **`change-validation`** |
| `first_failure` | `None` |
| commands run | **45**, **0** non-pass |

`engine: change-validation` is the load-bearing field: `CHANGE-VALIDATION.md` §0 is
`approved: yes`, so **tier 1 fired** and a vacuous tier-3 `pass` was not reachable here.
The assertion is on the **status string**, not a failure count — the verb emits
`status: pass|fail` and exits 3 on non-pass.

## The end-state re-run — what the transition records cannot be

The red→green records in `red-prework.md` are evidence of a **transition**, written once and
never re-evaluated: `verify-all` reads that file, the fixtures are not CV recipe rows, and the
FULL tier does not touch them. So a later epic can silently undo an earlier one's green with
nothing detecting it.

| Control | Exit against the merged tree |
| :-- | --: |
| `ctl-182-spike` | **0** |
| `ctl-184-dispatch` | **0** |
| `ctl-165-executable` | **0** |

## The criteria with NO fixture — checked here because of RE-003

**This section exists because the mandate above was not enough.** SC4b was measured green at
Issue 1.2a and was **false by Epic 3** — Issue 3.2's new test file matched SC4b's pattern,
taking the hit set from 7 to 8 and out of subset. The 4.1 mandate covers the three *fixtures*;
SC4b is a `plan.md` criterion with **no fixture**, so nothing re-checked it. It was caught by
an **operator re-measurement**, not by any mechanism this plan ships (RE-003).

The fixture-less criteria are therefore re-checked at end state too:

| Criterion | Check | Result |
| :-- | :-- | :-- |
| SC4 | `git grep -q 'Read-only — never writes files' -- ':!docs/plans' ':!docs/research'` | **pass** — no matches |
| SC4b | hit set **8**, unenumerated **0** (row 18 added at 4.1) | **pass** |
| SC5 | the `e-spec-agent` row in `DRIFT-CHECK.md` §2 | **pass** |
| SC6 | `awk` §-scoped `### Review` \| `grep -q 'Agent'` | **pass** |
| SC7 | `bd cook --dry-run` on `plan-review.formula.toml` | **pass** |

**The generalizable finding:** a plan that re-checks only the artifacts it built a fixture for
has re-checked the easy half. Criteria discharged mid-plan are the ones that rot, precisely
because nothing re-reads them.
