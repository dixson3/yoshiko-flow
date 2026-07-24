---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #97 — Docs↔reality: what does yf-plan 'execution spanning multiple environments' actually mean today?

- **URL:** https://github.com/dixson3/yoshiko-flow/issues/97
- **State:** OPEN
- **Labels:** (none)
- **Disposition (this plan):** include — driver for workstream 1 (beads/upstream doc accuracy); resolved at reconcile by Epic 2 (Issue 2.1). Tombstoned from plan-034 (`yf-5p9x`).

## Body

Tracking a deferred investigation hoisted from local bead `yf-5p9x`.

The yf-plan web docs claim execution can span multiple environments. But default beads behavior keeps the bead DB **local** and never pushes beads themselves upstream via git; `yf-beads-upstream`'s "upstream" is about capturing follow-on work in an issue tracker, **not** multi-node execution coordination.

**Task:** Investigate + do a practical test of what "spanning multiple environments" actually means today, and reconcile the docs with implementation reality. "Spanning multiple environments" is the stated eventual goal but may not be practical with beads as-is.

**Deliverable:** corrected wording in `web/` + a note on the real capability/limitation.

_Deferred out of the post-plan-033 follow-ups plan; filed as the coarse upstream tracker for this thread._
