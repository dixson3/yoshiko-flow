---
type: Reference
okf_spec: OKF-PLAN
description: 'Dated wall-clock measurement of the CHANGE-VALIDATION FULL tier — a figure D-8 recorded as unmeasured anywhere in the repository.'
---
# FULL-tier wall-clock record

**Issue 6.2.** D-8 found the FULL tier's duration **recorded nowhere in the repository**, while
the plan's own criteria run under a 300 s `recheck-criteria` bound. This file is the citation
those criteria use **instead of re-running the tier inside that bound** — a criterion that
re-ran a multi-minute suite would either time out or make every completion pay for it.

## Measurement

- **date:** 2026-08-30
- **host:** d3-mbp-m5
- **tier:** `full`
- **command:** `change_validation.py run --tier full --json`
- **cwd:** the execute worktree (`.worktrees/plan-060-james-dixson-6a6ac9`)
- **duration_s:** 96
- **rows evaluated:** 14 of 62 — **the run STOPPED AT THE FIRST FAILURE**

## Read the duration with its truncation, not without it

`change_validation.py:840` **breaks on the first failure**, so this 96 s figure is a
**LOWER BOUND**, not the tier's full cost: it covers 14 rows before an `okf-index-drift`
failure ended the run. A green run evaluates all **62** rows and takes correspondingly longer.

Recording the number without that caveat would be the same defect this plan keeps finding — a
figure that is true about something other than what a reader will assume it measures. A clean
62-row run measured earlier in this execution exceeded the 120 s foreground budget and had to be
backgrounded, which is the honest headline: **the FULL tier does not fit in a 300 s criterion
bound with any margin, and it is not run inside one.**

## Why this file exists at all

`SC37` greps this file for a machine-readable `duration_s` line. The point is not the
number — it is that the number is **written down with its method**, so a later reader can tell
what was measured and re-measure it the same way.
