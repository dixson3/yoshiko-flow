---
type: Reference
okf_spec: OKF-PLAN
id: closable-sweep
description: The land-the-plane closable sweep — proposals only; nothing was closed
---

# The `closable` sweep — proposals only

`upstream.py closable` reports which upstream issues have **all their mapped beads closed**. It
**never closes anything**: closing an upstream issue is outward-facing and gets the same confirm
contract as a push.

## What it proposed

```
gh issue close 147   gh issue close 150   gh issue close 152   gh issue close 153
gh issue close 176   gh issue close 183   gh issue close 193
```

## What was done: NOTHING. Three of the seven would have been WRONG

This run is a live demonstration of the caveat in the skill's own documentation — the signal is
**per-bead** and knows nothing about a plan's dispositions:

| Proposed | Verdict | Why |
| :-- | :-- | :-- |
| `#150` | **DO NOT CLOSE** | a `partial` row in this plan. It must stay **OPEN** by design *and* by the operator's authorization, which says so explicitly. The research programme is not finished; six of its ranked classes were delivered |
| `#183` | **DO NOT CLOSE** | plan-049's coarse tracker. `exclude` in this plan's table, closed by **plan-049's own** land-the-plane sweep, not by this plan's reconciliation. Explicitly not authorized |
| `#193` | **not authorized here** | this plan's own tracker. It is *legitimately* closable — its only mapped bead, the epic, is now closed — but closing it is an outward-facing write and the grant's scope clause is *"any upstream write not listed above"* is not authorized. It is proposed to the operator, not executed |
| `#147`, `#152`, `#153`, `#176` | **out of scope** | not rows in this plan's Upstream Issues table at all. They belong to earlier plans and are the operator's call |

`#150` is the sharpest case: `verify-reconcile` requires it **OPEN** with a plan-id mention, and
`closable` proposes closing it, in the same session. Both are correct within their own signal —
which is exactly why the verb proposes rather than acts.

## The other caveat, restated because a clean run is not a clean bill of health

> Hand-filed coarse plan trackers carry **no** bead mapping and are invisible to this signal.

`#193` is visible only because Issue 6.3 filed it through `/yf-beads-upstream`, so the epic
carries it as `external_ref` (REQ-PLAN-073). A tracker filed with a bare `gh issue create` would
not appear here at all — the defect that let five earlier trackers go stale.
