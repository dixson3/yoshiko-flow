---
type: Asset
okf_spec: OKF-PLAN
id: ASSET-edge-equivalence
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# Edge-set equivalence, re-proven post-rewrite (Issue 1.1, risk R1)

EXP-002 proved equivalence *before* the rewrite, against a 1,801-bead universe. This is the
**post-rewrite** re-proof, run in the execution tree against the universe as it stands now, with
both edge sets built **in one process** so nothing about the comparison depends on serialization.

## Method

`collect_parent_edges` (the new, rows-reading implementation) versus a verbatim reconstruction of
the **pre-fix** loop — `deps_for_show(bid)` per bead, the same `edge_type()` filter, the same
`depends_on_id or id or target` chain — over the **same** `beads` dict.

## Result

| | Edges | Time | Subprocesses |
| :-- | --: | --: | --: |
| **FAST** (rows, `dependencies[]`) | 1,736 | **0.0017 s** | **0** |
| **SLOW** (pre-fix, `bd show` per bead) | 1,736 | **398.24 s** | **1,905** |

```
universe: 1905 beads
EQUIVALENT: True | fast_only: 0 | slow_only: 0
targets identical: True
SPEEDUP: 233,157x
```

**Zero divergence in either direction**, and the resolved `target` bead is identical edge for
edge — not merely the same edge count.

## What this adds beyond EXP-002

1. **It re-proves the property on a universe that has since GROWN** (1,905 beads, up from 1,801),
   so the result is not an artifact of the corpus EXP-002 happened to measure.
2. **It re-confirms EXP-001's timing independently.** 398 s here versus the 334 s recorded
   pre-execution — consistent, and larger because the universe is larger. That is the defect
   behaving exactly as diagnosed: **the cost scales with repository HISTORY, not activity.**
3. **It measures the real slow path rather than inferring it.** An earlier attempt at this
   comparison was killed by a 2-minute command budget — which is precisely the observation
   #268 was originally filed on, and precisely why a kill cannot distinguish *slow* from
   *wedged*. Run to completion, it terminates cleanly at 398 s.

## The two traps the plan recorded, both confirmed live

- **The target id is named differently by source.** `bd show` carries it as `id`; `bd list`'s
  `dependencies[]` uses `depends_on_id`. Both sets above resolve identically **because** the
  `depends_on_id or id or target` chain was preserved verbatim. A comparison written against
  `depends_on_id` alone would have read a false 100% divergence.
- **The `--include-gates` edge gap is PRESERVED, not fixed.** `load_universe_rows()` still omits
  the flag, so gate parent-child edges stay invisible to this walk — identically before and
  after. Filed separately (Issue 3.4) rather than smuggled in on a performance fix.
