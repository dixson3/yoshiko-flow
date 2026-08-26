---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #216: coordinator: beads are closed in batches, making 84% of observed interval overlap an artifact

- **Number:** 216
- **Title:** coordinator: beads are closed in batches, making 84% of observed interval overlap an artifact
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

**Measured:** plan-052 EXP-006 §1 / I-5.

The coordinator closes beads in **batches** rather than when each unit of work finishes. That
collapses distinct work intervals onto a single timestamp, so **84% of all observed interval
overlap is an artifact** of when the closes were flushed — not of when work actually ran
concurrently.

Any concurrency or parallelism measurement over this corpus is therefore measuring the flush
schedule, not the work.

**Expected:** close each bead when its work finishes.

Companion to D5 — filed separately because either fix alone leaves the measurement unusable.

*Filed by plan-052 as a deliberately deferred defect. Full enumeration:
`docs/plans/plan-052-james-dixson-fa8056/assets/deferred-defects.md`.*
