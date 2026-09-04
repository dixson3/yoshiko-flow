---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #343 - L16''s journal filter is a substring match: it
  misses land-beads.json and a collapsed ''?? .yf/'', so it does not even exempt the
  journal'
---
# Upstream #343: L16's journal filter is a substring match: it misses land-beads.json and a collapsed '?? .yf/', so it does not even exempt the journal

- **Number:** 343
- **Title:** L16's journal filter is a substring match: it misses land-beads.json and a collapsed '?? .yf/', so it does not even exempt the journal
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

## The defect

L16's post-condition filters the landing journal out of `git status --porcelain` with a
**substring match on one constant**:

```python
# skills/yf-plan/scripts/plan_manager.py:8544
LAND_JOURNAL_DIR = ".yf/plan/landing-journal"
# :9394-9403 — porcelain lines are kept unless LAND_JOURNAL_DIR is a substring
```

Two ways that fails:

**1. It does not cover its sibling.** L13 writes `ctx.root/".yf"/"plan"/"land-beads.json"`
(`:9296`) — a different path under `.yf/plan/`, not under `landing-journal/`. The filter does not
exempt it.

**2. Git collapses untracked directories.** Without `-uall`, an untracked `.yf/` reports as a
single line `?? .yf/`, which contains **neither** `land-beads.json` **nor**
`.yf/plan/landing-journal`. Measured, in a repo without the `/.yf/` gitignore anchor:

```
porcelain: '?? .yf/'
REAL L16 verdict: fail … porcelain='?? .yf/'
```

So the filter fails to exempt **even the journal it was written for**.

## Why it looks fine here

This repository carries a `/.yf/` gitignore anchor, so those paths never appear in porcelain at
all. **The anchor is the only thing making L16 pass** — the filter itself is decorative here and
inoperative in any repo lacking the anchor. The in-code comment credits the anchor, but the
filter is still the mechanism the post-condition claims to rely on.

## Consequence

A landing in a repo without the anchor fails L16 on the landing's **own** journal writes — at the
step past the irreversible boundary, after the L6 push and L7's public comments.

## Suggested direction (not prescriptive)

- Use `git status --porcelain -uall` so untracked directories are enumerated rather than
  collapsed. **Without this, no prefix filter can work.**
- Replace the substring test with a **path-prefix test over a `.yf/plan/` allowlist**, evaluated
  per entry, so siblings like `land-beads.json` are covered by construction rather than by adding
  each new constant.
- Add a Tier-1 case that runs L16 in a sandbox **without** the gitignore anchor, which is the
  only configuration where the filter is load-bearing.

## Provenance

Found while investigating **plan-063** (`plan-063-james-dixson-3f74c1`), in the same sandbox
spike that found #342. Adjacent to #342 (the same step's commit), #333 and #341 (the same
post-condition reached by other routes).

