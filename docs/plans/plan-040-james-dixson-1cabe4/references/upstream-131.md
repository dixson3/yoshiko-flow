---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #131: yf-plan: stamp the coarse tracker URL onto the plan epic so closable can see it

- **Number:** 131
- **Title:** yf-plan: stamp the coarse tracker URL onto the plan epic so closable can see it
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement

## Body

Follow-up filed by plan-038 (Issue 4.5). **File-only** — implementing it is `yf-plan`'s scope, not `yf-beads-upstream`'s.

## Problem

`yf-beads-upstream closable` (shipped in plan-038, `REQ-BUP-052`) proposes which upstream issues can be closed, using a **per-bead signal**: an issue is closable when every bead carrying an `External:` mapping to it is closed.

`yf-plan` Phase 4.5 files its one coarse tracking issue per plan with a direct `gh issue create`. Nothing records that URL on any bead — so **no bead ever maps to a coarse plan tracker**, and `closable` structurally cannot see them.

That is exactly the population that goes stale: #103, #95, #96 and #98 were all coarse plan trackers left open on plans at `status: complete`, each found only by an ad-hoc human sweep. See #117 for the full in/out split.

## Proposed fix

In `yf-plan` Phase 4.5, after creating the tracking issue, stamp its URL onto the plan epic:

```bash
bd update <epic> --external-ref <tracker-url>
```

## Why this shape

It adds **no coupling in either direction**. `yf-beads-upstream` keeps its zero-coupling per-bead signal and needs no knowledge of `yf-plan`'s configurable `plans-root`; `yf-plan` just records a fact it already has in hand. Future coarse trackers then show up in `closable` automatically.

It is **forward-looking only** — existing unstamped trackers stay invisible and still need a one-off human sweep.

Refs #117.
