---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #73: yf-plan: cascade-close epic/child beads on plan completion

- **Number:** 73
- **Title:** yf-plan: cascade-close epic/child beads on plan completion
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::medium

## Body

## Problem

When a plan reaches `Status: complete`, closing the plan (or the plan molecule) does **not** cascade closure to open epic/child beads. Leaf tasks get closed during execution, and the top-level molecule may get closed, but the intermediate **epic** containers are left `open`.

### Observed (thesoftwarefactory, plan-003 + plan-002)

- `plan-003` shipped to production (v1.3.0), `plan.md` marked `Status: complete`, upstream reconciled.
- The plan molecule `thesoftwarefactory-mol-3f5` was `closed`, **but its 4 child epics** (`mol-3f5.1`–`.4`) remained `open`.
- The plan-002 molecule `thesoftwarefactory-mol-bw0` was itself `open` with two child epics (`.5`, `.6`) `open`, despite **every leaf under both** being `closed`.
- Net effect: `bd ready` reported **8 false-positive "ready" epics** long after the work shipped. Operator asking "what's on deck" gets stale containers, not real work.

The 8 stale beads had to be closed manually.

## Expected

On plan completion (plan status flips to `complete`, or the plan molecule is closed), a container bead whose children are **all closed** should be closed automatically as part of the same operation — cascading up through the epic → molecule hierarchy. A container with any still-open child must **not** be auto-closed (that's a real "incomplete plan" signal to surface, not to hide).

## Suggested direction

- On plan-complete / molecule-close, walk the plan's bead tree bottom-up; close any container whose children are all closed, with a close reason referencing the plan (e.g. "plan-NNN complete; all children closed").
- If a container has open children while the plan is marked complete, **fail loudly** (surface the inconsistency) rather than silently closing or silently leaving it — the plan claims done but has open work.
- Consider a `bd` idiom or helper for "close if all children closed" so both `yf-plan` completion and a land-the-plane sweep can reuse it.
- Likely homes: the `yf-plan` completion path and/or the coordinator completion handoff in `yf-beads-authoring`.

## Acceptance

- Completing a plan whose leaves are all done leaves **0 stale open epics/molecules** for that plan.
- `bd ready` after plan completion shows no container beads from the completed plan.
- A plan marked complete with genuinely-open children produces a visible warning/error, not a silent close.

