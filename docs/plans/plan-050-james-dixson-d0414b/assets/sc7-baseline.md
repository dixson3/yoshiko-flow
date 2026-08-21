---
type: Reference
okf_spec: OKF-PLAN
id: sc7-baseline
description: SC7's corpus files_checked baseline, captured BEFORE any Epic-2 change (Issue 0.2a)
---

# SC7 baseline: corpus `files_checked`, captured before the classifier lands

SC7 asserts the Epic-2 change **perturbed no selection**. That claim is only checkable against
a baseline taken *before* the change, which is why this issue is an Epic-0 ancestor of Epic 2
rather than a companion to Issue 2.3.

## The measurement

Re-measured at execution per D-5, not inherited from drafting.

| Field | Value |
| :-- | :-- |
| Command | `uv run _shared/doc_lint.py --json --exclude 'docs/plans/plan-050-james-dixson-d0414b/**'` |
| `files_checked` | **757** |
| `errors` | 0 |
| Tree | `plan-050-james-dixson-d0414b-development` at the Issue 0.2a commit |
| Taken | 2026-08-21 (UTC) |

## Only the EXCLUDED figure is recorded, and that is the point

The `--exclude` glob self-excludes this plan's own bundle, per the #135 self-exclusion
mechanism plan-049 shipped (REQ-DATA-059). The two figures behave differently:

| Figure | Drafting | Execution | Stable? |
| :-- | --: | --: | :-- |
| **excluded** (`--exclude <this plan>/**`) | 757 | **757** | **yes — reproduced exactly** |
| unfiltered | 817 → 820 | 832 | no — drifted within the drafting session, and again since |

The unfiltered count moves every time this plan writes a file into its own bundle — a review
pass, a finding, this very document. A baseline taken on it would be stale before the change it
exists to measure ever lands. That is the whole reason the exclusion exists, and it is why only
the excluded figure is recorded here.

## How SC7 is discharged

Issue 2.3 re-runs the **identical** command against the post-classifier tree and asserts
**equality against 757** — the excluded figure, and nothing else. Any delta is a failure,
because REQ-DATA-061 forbids the classifier from touching selection; a delta would mean the
preflight leaked into the lint path.

**The unfiltered figure is DIAGNOSTIC ONLY and is never a criterion.** It has moved
817 → 820 → 828 → 829 → 830 → 832 across this plan's drafting and review, one step per file
written into this plan's own bundle. Comparing it across the change would report a failure
caused entirely by this document existing.
