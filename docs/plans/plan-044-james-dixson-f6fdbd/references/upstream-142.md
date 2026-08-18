---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #142: closable proposes closing issues that are already closed (or deleted) upstream

- **Number:** 142
- **Title:** closable proposes closing issues that are already closed (or deleted) upstream
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

Discovered during plan-040 Issue 4.4's backfill.

MEASURED: after stamping 18 coarse trackers, `upstream.py closable` proposed 25 closures:
  - 23 already CLOSED upstream
  - 2 no longer exist (#139 deleted, and a bare 'gh-91' ref)
  - 0 genuinely OPEN and actionable

The per-bead signal is CORRECT — all mapped beads really are closed. What is missing is a filter
to issues that are actually open upstream. Before the backfill closable proposed 7; after, 25 —
so making trackers visible made the report NOISIER rather than more useful.

Fix shape: before emitting a proposal, batch-query upstream state (one `gh issue list --state
all --json number,state` covers the whole set — do NOT add a per-issue call and reintroduce the
N+1 plan-040 Issue 4.1 just removed) and drop issues already closed / absent, or mark them
distinctly.

Out of scope for plan-040, which changed how closable READS BEADS, not what it PROPOSES.
Evidence: docs/plans/plan-040-james-dixson-1cabe4/references/tracker-backfill-map.md
