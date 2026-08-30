---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #235 - yf-beads-hygiene reconcile: linked_plan_complete
  cannot distinguish DELIVERED work from a deliberately-parked ONGOING obligation
  — proposes closing the very issues filed to outlive the plan'
---
# Upstream #235: yf-beads-hygiene reconcile: linked_plan_complete cannot distinguish DELIVERED work from a deliberately-parked ONGOING obligation — proposes closing the very issues filed to outlive the plan

- **Number:** 235
- **Title:** yf-beads-hygiene reconcile: linked_plan_complete cannot distinguish DELIVERED work from a deliberately-parked ONGOING obligation — proposes closing the very issues filed to outlive the plan
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium

## Body

Found in `dixson3/rc-files` running `/yf-beads-hygiene` immediately after plan-004 completed. Reported by operator decision. Sibling of #234 (same session, different layer).

## What reconcile proposed

```
Obsolete upstream issues (3) — delivered, proposal-only:
  #10 Accepted risk: Claude Code subscription credential routed into general-purpose harnesses (plan-004 R7)  (linked_plan_complete)
  #9  plan-004-james-dixson-f0bcc5 execution tracking                                                          (linked_plan_complete)
  #7  4.5 Rotate EVRInet reusable auth key (<=90-day cadence)                                                  (linked_plan_complete)
```

**One of the three is correct. Two are false positives.**

| Issue | Reality |
| :-- | :-- |
| **#9** plan-004 execution tracking | ✅ Correct. The plan is `complete`; the coarse tracker is genuinely discharged. |
| **#10** Accepted risk (R7) | ❌ Its **own body** says: *"an accepted, **technically unmitigable** risk that **outlives the plan** and therefore needs a tracker rather than only a Risks-table row."* |
| **#7** Rotate auth key (≤90-day cadence) | ❌ A **recurring** obligation, labelled `status::deferred`. plan-003 completing does not stop a Tailscale key expiring every 90 days. Body: *"Rotate the EVRInet key in op before expiry."* |

## The class

**`linked_plan_complete` conflates two different relationships between an issue and a plan:**

- *"This plan's completion delivers this issue"* → closing is right.
- *"This plan deliberately parked this obligation upstream **because** it outlives the plan"* → closing is exactly wrong.

Both look identical to the signal: an open issue linked to a plan whose `plan.md` shows `Status: complete`.

## Why this is worse than an ordinary false positive

**The two mechanisms are in direct opposition, and both are working as designed.**

plan-004's red-team pass explicitly prescribed filing R7 as a standalone issue *so the obligation would survive the plan's closure*:

> *"**R7 has no upstream home.** It is the plan's only unmitigable risk and its only ongoing operator obligation, yet it is tracked nowhere but a Risks row. **File it as a standalone `gh` issue at intake**, so the accepted risk survives the plan's closure."*

The plan did that. Then, minutes after the plan reached `complete`, `reconcile` proposed closing it **because** the plan reached `complete`. The cleanup mechanism proposes to undo the durability mechanism, and each is behaving exactly as specified.

## Blast radius

`reconcile` is proposal-only and `--apply` **never closes upstream issues** (it only hoists non-active beads), so nothing was harmed here — the carve is doing its job. The realistic harm is an operator skimming a 3-line "delivered" list and closing all three by hand, discarding their own accepted-risk tracker and a live key-rotation reminder. The list is short and confidently labelled *"delivered"*, which is precisely what makes it skimmable.

## Adjacent, and worth comparing

`UPSTREAM_TRACKING.md` documents the **inverse** error for the `closable` check:

> **A clean run does not mean nothing needs closing.** The signal is per-bead, so hand-filed coarse plan trackers — which carry no bead mapping — are invisible to it and still need a human sweep.

So the codebase already warns that `closable` under-reports. `reconcile`'s obsolete-issue list **over-reports**, and carries no equivalent caveat. Whatever the fix, the two checks' error directions should probably be documented symmetrically.

## Suggested fix

Any one of these would have suppressed both false positives:

1. **Honor a durability label.** Treat `accepted-risk`, `recurring`, `deferred`, or `status::deferred` as *"not discharged by plan completion."* #7 already carries `status::deferred` — the signal was present and ignored.
2. **Honor `external_ref` on a still-deferred bead.** #7's mirror bead `rc-files-wl9` is `[deferred]` with `external_ref → issues/7`. A **deferred** bead pointing at an issue is a parked obligation, not delivered work. (Note this bead was *also* offered as a hoist candidate, which I declined — it is already upstream, so hoisting would tombstone a live mirror for no gain. Possibly a second, smaller bug.)
3. **Require a positive delivered signal rather than an absence.** A merged PR or a closing keyword is evidence of delivery; *"the linked plan is complete"* is only evidence about the plan.
4. **At minimum, split the report.** `Discharged by plan completion` vs `Linked to a completed plan — verify before closing`, so the confident word "delivered" is reserved for the case that earned it.

## Reproduction

```bash
uv run <skill>/scripts/beads_hygiene.py reconcile
```
against `dixson3/rc-files` at `1eb4770`, with plan-003 and plan-004 both `complete` and issues #7 / #10 open.

## Related

- #234 — remote hygiene blind to the git layer (same session).
