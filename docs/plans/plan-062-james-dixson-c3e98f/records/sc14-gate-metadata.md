---
type: Record
id: sc14-gate-metadata
plan: plan-062-james-dixson-c3e98f
created: 2026-09-03
---
# SC14 — capability-gate metadata read-back (Issue 0.0)

SC14 is `manual:` by design (pass-5 C47: a repo-wide clause over 194 historical gate
beads is permanently TRUE and so measures nothing). This file is its evidence.

## Declared gate count

```
$ grep -c '^### Capability Gate:' docs/plans/plan-062-james-dixson-c3e98f/plan.md
3
```

Three — matching the three gate beads below. The count is load-bearing (pass-3 C28).

## The three gate beads, SET at pour and READ BACK here

`plan_extract.py` recognizes only `Type|Approvers|Condition|Test|Blocks|Instructions`,
so the plan's `test_class:` and `cwd:` lines are dropped silently and `unparsed` stays
`[]` (#266). The metadata was therefore SET directly on each `bd create`, not derived
from extraction — a setter, not a detector (#273).

```json
{
  "id": "yf-mol-tm2d.6",
  "title": "Gate: execution is in-place, not in a worktree",
  "metadata": {
    "cwd": "repo-root",
    "gate_type": "auto",
    "test": "uv run skills/yf-plan/scripts/plan_manager.py config-resolve --json | jq -e '.keys[\"execute.worktree\"].value == false' > /dev/null",
    "test_class": "probe"
  }
}
{
  "id": "yf-mol-tm2d.7",
  "title": "Gate: the seam test is DISCRIMINATING before the seam is wired",
  "metadata": {
    "cwd": "repo-root",
    "gate_type": "auto",
    "test": "uv run skills/yf-plan/scripts/test_land_apply.py -k seam_reaches_executor -q; test $? -eq 1",
    "test_class": "probe"
  }
}
{
  "id": "yf-mol-tm2d.8",
  "title": "Gate: a resume does not re-execute irreversible steps",
  "metadata": {
    "cwd": "repo-root",
    "gate_type": "auto",
    "test": "uv run skills/yf-plan/scripts/test_land_apply.py -k resume_skips_completed -q",
    "test_class": "probe"
  }
}
```

All three carry `gate_type`, `test`, `test_class` and `cwd`. No write failed to take;
Issue 0.0 does not halt.

## Execute-start sweep (§5.2c), probe class

| Gate | Bead | Result | Reading |
| :-- | :-- | :-- | :-- |
| execution is in-place | `yf-mol-tm2d.6` | exit 0 — PASS, **resolved** | `config-resolve` reports `execute.worktree` value=`false` source=`config.local` |
| seam test is discriminating | `yf-mol-tm2d.7` | exit 1 — FAIL | **benign, declared.** The test does not exist until Issue 2.0, so pytest deselects all and exits 5; `test $? -eq 1` is then false |
| resume does not re-execute | `yf-mol-tm2d.8` | exit 5 — FAIL | **benign, declared.** No test collected until Issue 4.1 |

Both reds are named in their own gates' `Instructions:` as expected at this sweep.
Neither is a blocker.
