---
type: Reference
okf_spec: OKF-PLAN
id: post-work-measurements
description: Post-work corpus re-measurement against the targets fixed at approval, with a pass/fail column (Issue 6.2 / SC23)
---

# Post-work measurements, against the targets fixed at approval

**Issue:** plan-049 6.2 · **Criteria:** SC23, SC5, SC8, SC31 · **Measured:** 2026-08-20, on
the merged tree at `main`. Every corpus figure **excludes plan-049 itself** per D-3, so the plan
is not inside its own denominator.

## The scorecard

| # | Target, fixed at approval | Target | Measured | Verdict |
| --: | :-- | :-- | --: | :-- |
| 1 | inline declarations recovered as edges | ≥ 60 of 89 | **74** | ✅ |
| 2 | documents modified by the grammar widening | 0 | **0** | ✅ |
| 3 | documents modified by the write phase | exactly 2 | **2** | ✅ |
| 4 | `plan-006` / `plan-007` no longer report `0 edges` | > 0 | **9** / **17** | ✅ |
| 5 | corpus `unparsed[]` after the widening (SC31) | ≤ 81 | **83** | ❌ **+2** |
| 6 | corpus `unparsed[]` after the write phase (SC23/SC31) | ≤ 73 | **75** | ❌ **+2** |
| 7 | the DAG guard reports no L1–L4 loss, at either point | exit 0 | **exit 0** | ✅ |
| 8 | FULL tier over the merged tree, non-zero command count (SC22) | pass, > 0 | **pass, 44** | ✅ |

## The residue trajectory, and the single cause of both misses

| Point | Residue | Δ | What moved |
| :-- | --: | --: | :-- |
| before any change | 81 | — | the inherited baseline |
| after the grammar widening (Epic 2) | **83** | **+2** | two `plan-010` declarations became **visible and refused** |
| after the write phase (Epic 3) | **75** | **−8** | `plan-008` −5, `plan-015` −3 |

**Rows 5 and 6 are the same miss counted twice.** The write phase performed exactly as derived
(−5 and −3, both predicted in `assets/proposed-write-diff.md` before the gate was evaluated).
The entire shortfall is the `+2` from Epic 2, carried forward.

Those two are `plan-010` L280 (a referent list followed by a prose tail) and L311
(`depends-on: G1, 4.4`, where `G1` is a gate id). Both were **invisible** to the extractor
before this plan; the widened grammar now sees them, reads them, and **refuses** them. A refusal
is a residue row.

**The only way to have hit 73 was to silently drop them** — which REQ-DATA-052 forbids in its
own text (*"a refusal is a finding, never a silent drop"*) and which is precisely the
degrade-quietly behaviour that made 89 declarations invisible in the first place. Full
derivation in [widening-measurements.md](widening-measurements.md).

**The target was misderived at approval, in the way this plan's own Approach warns about**
(Principle 3: *a number is not a target unless it is derivable from what the plan permits*;
Principle 4: *unblocking is unmasking*). `≤ 73` was fixed before the refusal behaviour of the new
grammar was known, and Principle 4 predicts an increase.

## The figure that moved for the right reason

| Figure | Before | After | Reading |
| :-- | --: | --: | :-- |
| materialised edges (L2) | 928 | **1028** | **+100.** The dark matter is now read. |

`plan-006` went from **0 edges** to **9**, and `plan-007` from **0** to **17** — both had
previously reported `0 unparsed, 0 edges` while carrying declarations, the residue metric
recording the loss as perfection.

## Linter-side figures, reported as DELTAS not floors

SC23 requires `files_checked` be reported as a delta, because *"a floor of 731 was already true
at drafting"* — a floor that is already satisfied asserts nothing.

| Figure | At drafting | Now | Δ |
| :-- | --: | --: | --: |
| `files_checked` | 731 | **731** | **0** |
| report-only findings | 1340 | **928** | **−412** |
| `errors` | — | **0** | — |

The report-only drop is not an improvement in document quality; it is the direct effect of
Issue 4.7's re-scope (`disposition-alphabet-offered`, 30 findings retired) and Issue 0.2's
`promote = false` (relational findings no longer demoted into the report-only bucket at
`complete`). Stated so nobody reads `−412` as a corpus that got cleaner on its own.

## The drifting-literal instances this plan predicted about itself

plan-049's Issue 6.2 text anticipated two of its own drafting literals going stale
(`files_checked` 731→752, report-only 1340→1341). Re-measured here they read **731** and
**928** — different from both the drafting figures *and* the predicted drift, because the work
itself moved them. That is a third live instance of the #135 pattern, inside the plan that
scoped #135, and it is exactly what Issue 5.2's rule now reports on an in-flight plan.

## Reproduce

```bash
uv run _shared/plan_extract.py docs/plans/*/ --json \
  --exclude 'plan-049-james-dixson-725bc0' \
  | jq '{edges:([.[]|select(.counts)|.counts.edges]|add),
         unparsed:([.[]|select(.counts)|.counts.unparsed]|add)}'
uv run _shared/doc_lint.py --exclude 'docs/plans/plan-049-james-dixson-725bc0/**' --json \
  | jq '{files_checked,errors,report_only}'
```
