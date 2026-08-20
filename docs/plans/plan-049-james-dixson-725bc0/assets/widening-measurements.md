---
type: Reference
okf_spec: OKF-PLAN
id: widening-measurements
description: What the grammar widening moved, including the SC31 miss and its derivation (Issue 2.4)
---

# Issue 2.4 falsification: what the grammar widening actually moved

**Measured at** `HEAD = 458092d`. Per **D-3** every corpus figure below **excludes
plan-049 itself**, so the plan is not inside its own denominator.

## The four assertions Issue 2.4 makes

| # | Assertion | Target | Measured | Verdict |
| --: | :-- | :-- | :-- | :-- |
| 1 | inline declarations recovered as edges | **≥ 60** of 89 | **74** | ✅ |
| 2 | corpus `unparsed[]` does not rise above its pre-widening value | **≤ 81** | **83** | ❌ **+2** |
| 3 | documents modified | **0** | **0** | ✅ |
| 4 | the DAG guard reports no L1–L4 loss | exit 0 | exit 0, `losses: 0`, `over_upper_bound: 0` | ✅ |

## The headline numbers

| Figure | Before | After | Δ |
| :-- | --: | --: | --: |
| materialised edges (L2) | 927 | 1027 | **+100** |
| corpus residue (`unparsed[]`) | 81 | 83 | **+2** |
| documents modified | — | — | **0** |

## Assertion 2 MISSED, and the reason is structural rather than a defect

**This is recorded as a miss, not explained away.** The target was `≤ 81` — stated in the
plan as *"the no-added-residue floor for a reading change"*. The measurement is **83**.

The +2 is entirely accounted for: `plan-010` L280 and L311, both documented row-by-row in
[edge-audit-049.md](edge-audit-049.md). Both were **trailing-inline declarations the
extractor could not see at all** before this change. The widened grammar now *sees* them,
reads them, and **refuses** them — one for a prose tail, one for naming a gate id — and a
refusal is a residue row.

So the +2 and the +98 are the same event. A declaration cannot become visible-and-refused
without also becoming countable, and the only way to hold the residue at 81 would have been
to **silently drop** the two constructs the grammar cannot attribute. That is precisely the
degrade-quietly behaviour REQ-DATA-052 forbids (*"a refusal is a finding, never a silent
drop"*), and precisely the failure mode that made 89 declarations invisible in the first
place.

### The target was misderived, in the way the plan itself warns about

plan-049's own Approach states two principles that bear directly on this:

> **Principle 3.** *A number is not a target unless it is derivable from what the plan
> permits.* plan-048's residue target was misderived because nobody checked it against the
> plan's own refusals.

> **Principle 4.** *Unblocking is unmasking.* Every plan the extractor stops refusing trades
> quiet inconclusive rows for loud real ones.

`≤ 81` was fixed at approval **before** the refusal behaviour of the new grammar was known,
and it is not derivable from what the plan permits: Principle 4 predicts an increase, and
Principle 3 says a target that contradicts the plan's own mechanics is the wrong number.
The plan reproduced its own named failure mode on its own criterion. Recording that is more
useful than quietly satisfying the literal.

### What the correct derivation would have been

```
post_residue  =  pre_residue  +  (declarations made VISIBLE but not attributable)
        83  =          81  +  2
```
The second term is knowable only **after** running the widened grammar over the corpus, so
no honest pre-approval derivation could have produced a single literal. A **derived**
criterion — *"residue rises by at most the number of newly-visible unattributable
declarations, and every such row is named"* — is satisfiable, checkable, and would have
been the right shape. Both of its clauses hold here.

### The reading that would have been genuinely bad

A residue rise caused by the widening **breaking constructs that previously parsed** would
be a real regression. It did not happen, and that is separately measured: no plan's residue
fell or rose other than `plan-010`'s, and the DAG guard reports **zero L1–L4 loss** across
all 49 bundles — so nothing that used to be read stopped being read.

## Per-plan detail, the five affected plans

| Plan | Edges before | Edges after | Residue before | Residue after |
| :-- | --: | --: | --: | --: |
| `plan-006-james-dixson-bf6e21` | 0 | 9 | 0 | 0 |
| `plan-007-james-dixson-84da0d` | 0 | 17 | 0 | 0 |
| `plan-009-james-dixson-996e44` | 0 | 19 | 2 | 2 |
| `plan-010-james-dixson-73eebd` | 0 | 37 | 7 | 9 |
| `plan-012-james-dixson-a99822` | 0 | 18 | 1 | 1 |

## Reproduce

```bash
uv run _shared/dag_guard.py snapshot docs/plans --out /tmp/now.json
uv run _shared/dag_guard.py verify --pre <pre-widening>.json --post /tmp/now.json \
  --upper-bound --json
uv run _shared/plan_extract.py docs/plans/*/       # per-plan edges + residue
git diff --stat -- docs/plans ':!docs/plans/plan-049-*'   # must be empty
```
