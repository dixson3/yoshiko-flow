---
type: Reference
okf_spec: OKF-PLAN
id: upstream-176
---
# Upstream #176: plan-048-james-dixson-ed68a5 execution tracking

- **Number:** 176
- **Title:** plan-048-james-dixson-ed68a5 execution tracking
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/176
- **State:** OPEN
- **Labels:**
- **Disposition (plan-048):** tracker

## Body

The coarse tracking issue for this plan, filed at Issue 4.5 under the operator's
upstream-write authorization and stamped onto the plan epic by `stamp-tracker`
(REQ-PLAN-073), so the tracker is visible to `upstream.py closable` rather than becoming a
sixth unmapped tracker closed by hand.

It **supersedes [#175](https://github.com/dixson3/yoshiko-flow/issues/175)** (plan-047's
tracker), which was closed as `NOT_PLANNED` only after this issue existed and linked it —
the ordering D-2 requires.

Its disposition is `tracker`, which `verify-reconcile` treats as **inconclusive by
construction** (`spec/cli.md` REQ-CLI-018): a coarse tracker is closed by the land-the-plane
sweep, not by reconciliation, so it carries no end-state contract in either direction. That
is deliberately *not* the same as `deferred`, which is report-only because a deferral is a
non-action. The two are report-only for different reasons and neither absorbs the other.

Full body as filed: see the URL above, drafted in `references/tracker-048-draft.md`.
