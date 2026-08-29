---
type: Finding
okf_spec: OKF-PLAN
description: "The shipped drift gate was tested against the ACTUAL regression that went unnoticed for nine days — it fires (exit 1) and clears (exit 0), with no residue."
---
# exec-002: does the gate catch the regression it was built for?

**Issue:** 3.2 (post-land verification) · **Measured:** 2026-08-28 · **Bears on:** D-1, R1, SC10

## Approach Tested

The plan's motivating fact is that root-index drift *"was fixed ~9 days ago and has already
regressed in 9 of the 30 index-bearing bundles — nothing noticed."* A gate built in response to that
should be tested **against that exact event**, not against a synthetic fixture. Anything else
answers a different question.

So: re-introduce the real regression into a real bundle and run the shipped gate.

```bash
# plan-055's index was missing its `assets/` entry — one of the 8 drifts Issue 3.4 repaired.
cp docs/plans/plan-055-.../index.md /tmp/idx.bak
grep -v '^- \[assets/\](assets/)' /tmp/idx.bak > docs/plans/plan-055-.../index.md
uv run scripts/checks/check_okf_index_drift.py --min-roots 30 ; echo $?

cp -f /tmp/idx.bak docs/plans/plan-055-.../index.md          # restore
uv run scripts/checks/check_okf_index_drift.py --min-roots 30 ; echo $?
```

## Result

**measured:**

| state | exit |
| :-- | --: |
| the real regression re-introduced | **1** (drift) |
| restored | **0** (clean) |

`git diff --stat` on the touched file afterwards is **empty** — the probe left no residue, on both
exit paths, which is what makes it a `probe` rather than a `consent` operation.

## Implications for Plan

**inferred:** this is the strongest evidence the plan produced, and it is a different claim from
SC10. SC10 asserts *the corpus is currently clean*; a corpus can be clean because it was repaired
and the gate is inert. This asserts the gate **distinguishes** the two states — the property that
would have made the nine-day regression visible on the day it happened.

It also exercises the `--min-roots 30` floor in the passing direction: both runs enumerated the
full corpus, so neither verdict is the vacuous "clean because nothing was read".

**inferred:** it does *not* establish that the gate catches every drift class. It catches
`missing`, which is the class all 8 observed drifts belonged to. `ghost` and `empty-dir` have unit
coverage in `_shared/test_okf.py` but no corpus-level RED observation, because the corpus contains
no instance of either.

## Recommendations

### Prefer a real regression to a synthetic one where the corpus supplies it

The synthetic fixture in `check-drift-driver-contract.sh` tests the driver's *contract* (a
nonexistent root is distinguishable from a clean corpus) and is deliberately independent of corpus
state. This probe tests whether the gate is *useful*. Both are needed and neither substitutes for
the other — which is why SC3 was rewritten mid-execution to stop depending on corpus cleanliness.

### Do not read this as coverage of `ghost` or `empty-dir`

Stated so a later reader does not inherit a broader conclusion than the measurement supports.
