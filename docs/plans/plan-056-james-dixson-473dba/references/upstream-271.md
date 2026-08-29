---
type: Reference
okf_spec: OKF-PLAN
description: "Upstream issue #271 - plan-056-james-dixson-473dba execution tracking (the coarse tracker for this plan-scale effort)."
---
# Upstream #271: plan-056-james-dixson-473dba execution tracking

- **Number:** 271
- **Title:** plan-056-james-dixson-473dba execution tracking
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/271
- **State:** OPEN
- **Labels:**

## Body

The **coarse tracking issue** for this plan-scale effort, per the repo's Upstream Tracking
convention (`AGENTS.md`): ONE issue per plan, linking the plan bundle and its epic — never one per
execution bead.

Its `Disposition` in `plan.md`'s Upstream Issues table is the literal `tracker`, which is what
`plan_manager.py stamp-tracker` keys on to stamp this URL onto the epic bead as `external_ref`.
That stamp is what makes the tracker an **ordinary mapped bead** and therefore visible to
`upstream.py closable`; without it a coarse tracker is structurally invisible to the close-time
sweep, which is how five previous trackers went stale and were closed by hand (#103, #95, #96, #98,
#134).

`verify-reconcile` reports a `tracker` row as **`inconclusive` by construction**: the coarse tracker
is closed by the land-the-plane sweep, not by reconciliation, so it carries no per-disposition end-state
contract.

**This row was added during execution**, not at intake — the plan was drafted without a `tracker`
row, so `stamp-tracker` initially returned `skipped: no coarse tracker found`. Adding the row is
fingerprint-safe: the whole `## Upstream Issues` section is excluded from the content fingerprint
(REQ-PORT-040), which is exactly why review and pour bookkeeping can be recorded there without
invalidating an approval.

- **Epic:** `yf-mol-xbp`
- **Plan bundle:** `docs/plans/plan-056-james-dixson-473dba/`
