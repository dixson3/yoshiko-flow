---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #161: plan-044-james-dixson-f6fdbd execution tracking

- **Number:** 161
- **Title:** plan-044-james-dixson-f6fdbd execution tracking
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/161
- **State:** OPEN
- **Labels:** —

## Body

The single **coarse tracking issue** for this plan-scale effort, per the project's
Upstream Tracking convention in `AGENTS.md`: one issue per plan, linking the plan folder
and its epic — not one per execution bead.

It is stamped onto the plan's epic (`yf-mol-6yh`) as `external_ref` at pour time
(REQ-PLAN-073), which is what makes it visible to `upstream.py closable`. Without that
stamp a hand-filed coarse tracker carries no bead mapping and is structurally invisible
to the close-time sweep — the failure mode that left five previous trackers stale.

## Disposition

`tracker` — not an incorporated worklist item. It is closed by the land-the-plane sweep
once the plan completes, not by reconciliation, which is why `verify-reconcile` classifies
a `tracker` row as `inconclusive` by construction rather than asserting an end state.
