---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #377 - 69 payload .md files across 9 landed plan bundles
  lack YAML frontmatter — those bundles fail the portability audit'
---
# Upstream #377: 69 payload .md files across 9 landed plan bundles lack YAML frontmatter — those bundles fail the portability audit

- **Number:** 377
- **Title:** 69 payload .md files across 9 landed plan bundles lack YAML frontmatter — those bundles fail the portability audit
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Found while parking plan-066 (#317). Its own bundle audit went red on 11 frontmatter-less payload bodies; repairing those surfaced the same defect across the wider corpus.

## Measurement

```
payload .md files scanned: 1406
lacking YAML frontmatter :   69   across 9 bundle(s)

  21  plan-063-james-dixson-3f74c1
  15  plan-029-james-dixson-75fd34
  11  plan-053-james-dixson-4015d3
   8  plan-061-james-dixson-6d8c97
   5  plan-052-james-dixson-fa8056
   3  plan-062-james-dixson-c3e98f
   3  plan-065-james-dixson-7c8cd4
   2  plan-033-james-dixson-46aca2
   1  plan-041-james-dixson-a9d837
```

Reserved OKF members (`index.md`, `log.md`) are excluded from the scan — they are correctly frontmatter-less.

Confirmed against the real instrument, not just the scan: `plan_manager.py audit docs/plans/plan-063-…` returns `status: fail` with **21 findings, all `REQ-OKF-003: no YAML frontmatter block`**. Four of the six most recent bundles fail (061, 062, 063, 065).

## Why it went unnoticed

The close-time bundle-conformance audit (`audit-close`, `REQ-PLAN-075`) is **advisory by design** — it exits 0 unconditionally and never gates `set complete`. So a plan can land, report complete, and leave its bundle failing the portability audit, with nothing contradicting the green close. That is the intended behaviour, and it is also why 5% of the corpus drifted without a signal.

This is a **detection-timing** gap rather than a missing check: the check exists, runs, and reports — but at a binding where its finding cannot change the outcome, and it is never re-run afterwards.

## The remedy is known and already exercised

plan-066 repaired its own 11 using **plan-057's `type: Asset` precedent** — giving each payload body real frontmatter.

**Do not fix this by exclusion.** `OKF-EXTENSION.md` §3b forbids excluding these paths, and an exclusion would convert a visible failure into a silent one — the same shape as the defect it would be papering over.

## Scope note

Each of the nine is a **landed historical artifact**, so a batch pass rewrites bundles belonging to completed plans. That is mechanical and low-risk (frontmatter addition only, no body edits), but it should be one reviewed diff rather than nine silent ones.

## Suggested follow-up

- A single batch pass adding `type: Asset` (or the correct OKF type per file) across the 9 bundles.
- Consider whether `audit-close` should stay purely advisory, or gain a non-blocking **but recorded** failure signal that a later sweep can find — the current design makes a finding that nothing can act on.

## Related

- #317 / plan-066 — where this was found
- #363 — OKF-EXTENSION documentation remediation

