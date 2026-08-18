---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #143: Five plan.md **Epic:** fields are dangling refs to pre-rename beads-skills-mol-* beads

- **Number:** 143
- **Title:** Five plan.md **Epic:** fields are dangling refs to pre-rename beads-skills-mol-* beads
- **URL:** 
- **State:** OPEN
- **Labels:** priority::low

## Body

Discovered during plan-040 Issue 4.4's backfill.

MEASURED: plan-007, plan-009, plan-010, plan-012 and plan-017 each record an epic id with the
`beads-skills-mol-*` prefix. `bd list --all --json` returns ZERO beads with that prefix (of
1019) — plan-010's yf- rename did not carry the old ids into the current DB.

Consequence: those plan.md `**Epic:**` fields are dangling references. resume-scan would report
found=false for them, and stamp-tracker cannot stamp their (known) trackers. All five trackers are
already closed, so there is no practical urgency — this is a data-integrity record, not an outage.

Decide: repair the mapping, or mark the field explicitly historical. Do NOT silently rewrite.
Evidence: docs/plans/plan-040-james-dixson-1cabe4/references/tracker-backfill-map.md
