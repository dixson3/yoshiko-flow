---
type: Record
okf_spec: OKF-PLAN
title: '#326 — re-label `deferred` and point at the completed design'
upstream_action: gh issue edit + gh issue comment
plan: plan-062-james-dixson-c3e98f
discharges: 5.1
status: drafted-awaiting-authorization
description: 'Draft for the ONE upstream EDIT in Issue 5.1: re-label the already-open #326 as `deferred` and comment a pointer to findings/exp-003, which carries the complete verified fix design (strip + temp file + compare-the-stripped-text, reusing okf.read_frontmatter, 7/7 spike). Records that REQ-LAND-027 is reserved for it, so the id hole in spec/landing.md is documented rather than unexplained.'
---
# Upstream filing draft — #326 re-label

> **NOT YET FILED.** Issue 5.1 of plan-062. Filing is an outward-facing write and is the
> operator's to authorize; this file is the reviewable draft.

## Intended actions

This is the one row of Issue 5.1 that is an **edit, not a create** — #326 is already open
(`https://github.com/dixson3/yoshiko-flow/issues/326`, currently labelled `bug`).

```
gh issue edit 326 --add-label deferred
gh issue comment 326 --body-file <this body, from the marker below>
```

The `deferred` label already exists in the repository, so no label needs creating. The
existing `bug` label is **kept** — the issue is still a bug; `deferred` records its
disposition, not its kind.

## Comment body

<!-- BODY BELOW THIS MARKER -->

**Deferred by plan-062, with the fix design already complete.**

plan-062 was narrowed at its pass-4 review by operator decision. Its scope is now exactly two
defects — the dead `land --apply` executor (#327) and the resume no-op that wiring it would
make reachable — and this issue was cut from it along with the five issues and four success
criteria of its Epic 3.

**Nothing was lost.** The investigation that would have fixed it ran to completion and is
recorded in full:

- `docs/plans/plan-062-james-dixson-c3e98f/findings/exp-003-*.md`

That finding carries a **complete, verified design**, not a sketch: strip the OKF frontmatter,
write the stripped text to a temporary file, and compare *the stripped text* on read-back —
reusing `okf.read_frontmatter` rather than adding a second frontmatter parser — with a 7/7
sandbox spike behind it. A later plan starts from a solved design rather than a blank page.

**`REQ-LAND-027` is reserved for this issue.** plan-062 added `REQ-LAND-028` and
`REQ-LAND-029` and deliberately skipped `027`, with the reservation written into
`skills/yf-plan/spec/landing.md` naming this issue and the finding. The gap in the id sequence
is therefore documented rather than unexplained, and the id is waiting when the fix lands.

Nothing in plan-062 depends on this issue, and this issue does not block it.
