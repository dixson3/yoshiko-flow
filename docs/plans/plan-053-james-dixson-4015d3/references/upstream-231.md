---
type: Reference
okf_spec: OKF-PLAN
id: upstream-231
description: The coarse upstream tracking issue for plan-053
---

# Upstream #231: plan-053-james-dixson-4015d3 execution tracking

- **URL:** https://github.com/dixson3/yoshiko-flow/issues/231
- **Title:** plan-053-james-dixson-4015d3 execution tracking
- **State:** OPEN
- **Disposition:** `tracker` — the single coarse tracking issue for this plan-scale effort
  (AGENTS.md one-tracker-per-plan convention), filed at Issue 7.3 through the
  `/yf-beads-upstream` route.
- **Resolved by:** 7.3

## Why this row exists at all

The tracker is **stamped onto the plan epic `yf-mol-bh8` as its `external_ref`**
(`REQ-PLAN-073`):

```text
external_ref = https://github.com/dixson3/yoshiko-flow/issues/231
```

That stamp is what makes it an **ordinary mapped bead** rather than the structurally-invisible
kind. `upstream.py closable` groups by `external_ref`; a tracker filed with a bare
`gh issue create` and recorded on no bead is invisible to it, which is how **five** trackers
previously went stale and had to be closed by hand (#103, #95, #96, #98, #134).

## Why `verify-reconcile` reports it INCONCLUSIVE, by construction

`REQ-CLI-018`: a `tracker` row is **report-only**. The coarse tracker is closed by the
land-the-plane sweep, not by reconciliation, so it carries no end-state contract in *either*
direction — it must be neither required-closed nor required-open.

It is deliberately **not** collapsed into `deferred`. Those are different facts: a `deferred`
row is report-only because there is nothing to attribute; a `tracker` row is report-only
because reconcile is not the thing that closes it. Neither may absorb the other.

So `verify-reconcile` exits **0** with 8 of 9 rows `pass` and this one `inconclusive`, and that
is the correct and expected shape — not a gap.

## Body

The issue body records the objective, the eight upstream rows and their end states, the method
(SPEC-first, RED-before-GREEN, class-fixes-over-instance-fixes), the verification totals, and
the six defects filed rather than fixed. It is reproduced upstream rather than duplicated here;
read it with `gh issue view 231`.
