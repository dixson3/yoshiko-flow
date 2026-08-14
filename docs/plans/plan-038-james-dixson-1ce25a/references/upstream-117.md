---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #117: yf-beads-upstream: push is write-only — no verb proposes CLOSING upstream issues whose work is done

- **Number:** 117
- **Title:** yf-beads-upstream: push is write-only — no verb proposes CLOSING upstream issues whose work is done
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

`yf-beads-upstream` can **create and update** upstream issues but has no path that ever proposes **closing** one. Every verb runs in the push direction; nothing reconciles the reverse edge — "this upstream issue's work is complete locally, it should be closed."

The result is that upstream-issue closure depends entirely on someone remembering. It is not remembered, and stale open issues accumulate.

## Evidence: this is a pattern, not a one-off

Four coarse tracking issues were found still **open** for plans that had reached `status: complete`, all discovered by ad-hoc human sweeps rather than by any tooling:

| Issue | Plan | Plan status when found |
| :-- | :-- | :-- |
| #103 | plan-036 | `complete` |
| #95 | plan-032 | `complete` |
| #96 | plan-033 | `complete` |
| #98 | plan-034 | `complete` |

All four were closed manually. Nothing in the workflow would have surfaced them — the coarse-granularity convention (AGENTS.md: one tracking issue per plan) makes each plan's completion *exactly* the signal that its tracker can close, and that signal is currently unused.

## Current verb surface (all push-direction)

```
enumerate     list open/blocked/deferred push candidates
mappings      report External: mappings for given bead IDs
granularity   report custom.upstream.granularity
config        report upstream config knobs
followons     detect follow-on beads under a plan subtree
hoist         ensure upstream issue per granularity, then close locally
land          land-the-plane: detect + hoist follow-on beads
unhoist       reopen wrongly-hoisted bead(s) from tombstone
```

`hoist` closes the **local bead** after pushing, never the upstream issue. `mappings` resolves bead → issue but only for explicitly-supplied bead IDs; it is not a sweep and has no completion semantics.

## Requested change

Add a **closable-candidate** verb — the mirror of `enumerate` — that reports upstream issues whose local work is demonstrably done:

- **`upstream.py closable [--json]`** — for each upstream issue mapped from this repo, report those where the mapped local work is terminal. Two signals, both mechanical:
  - *coarse / per-plan*: the issue is a plan tracker and that plan's `plan.md` reads `status: complete`;
  - *granular / per-bead*: every bead carrying an `External:` mapping to that issue is closed.
- Report `closable` / `not-closable` with the reason, and **never auto-close** — same propose-with-confirm contract as the follow-on hoist. Closing an upstream issue is operator-visible and outward-facing; it needs the same gate a push does.

## Where it should fire

At **land-the-plane**, alongside the existing push step. The companion rule (`protocols/UPSTREAM_TRACKING.md`) already makes close-time the moment upstream state is reconciled — today it only pushes *up*. Adding the closable sweep there makes the reconciliation bidirectional at the one point where the operator is already reviewing upstream state.

`yf-plan`'s Phase 6 reconcile step is the natural second consumer: it already parses plan dispositions and updates upstream issues per `resolves-upstream`, but a plan reaching `complete` does not currently imply its own coarse tracker gets closed. That gap is precisely what produced all four rows above.

## Notes

- Must respect the default-deny disabled short-circuit (`custom.upstream.enabled` ≠ `true` → silent no-op), like every other verb.
- Interacts with #105: if candidate enumeration is silently dropping beads, a closable sweep keyed on "all mapped beads closed" could reach a wrong verdict from the same owner-claim filter. Whatever classification fix #105 lands should be shared, not reimplemented.
