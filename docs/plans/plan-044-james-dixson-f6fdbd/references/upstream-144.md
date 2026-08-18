---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #144: yf-beads-upstream: a bead stays open when its upstream issue closes — the reverse of #117, with no reconciler

- **Number:** 144
- **Title:** yf-beads-upstream: a bead stays open when its upstream issue closes — the reverse of #117, with no reconciler
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

When an upstream issue is closed, **nothing closes the local bead that mirrors it.** The bead stays `open`, keeps its `external_ref`, and keeps appearing in `bd ready` as available work that no longer exists.

This is the **exact mirror of #117**, one direction over. #117 was *"push is write-only — no verb proposes closing upstream issues whose work is done"*, and plan-040 fixed it via `closable` + the coarse-tracker stamp. The reverse edge — *upstream closed, local bead still open* — has no reconciler at all.

## Measured

Across all 13 open beads carrying an `external_ref`, checked against live upstream state:

```
bead      issue  upstream
yf-1656   #132   CLOSED    <-- STALE
yf-m78m   #118   OPEN
yf-252c   #119   OPEN
yf-297v   #120   OPEN
yf-csf5   #121   OPEN
yf-7ntv   #122   OPEN
yf-pxet   #123   OPEN
yf-rd33   #124   OPEN
yf-ybri   #125   OPEN
yf-mrv9   #126   OPEN
yf-3d13   #127   OPEN
yf-ik3q   #128   OPEN
yf-uz5k    #92   OPEN

STALE (open bead, closed/gone upstream): 1 of 13
```

**n=1 today** — stated plainly rather than inflated. But the mechanism is systematic, not accidental.

## Why it recurs

`yf-1656` was created by **plan-040 itself**. Its Issue 5.2b closed #132 as `supersede` (the `--backend` surface was removed, so the broken jira entry ceased to exist). Reconciliation updated upstream correctly and **never touched the mirror bead**. Nothing in the reconciler, in `hoist`, or in the close step looks at that edge.

So every `supersede`/`include` disposition that closes an issue whose bead stays open produces another instance. A second one is already predictable: **#141 supersedes #128**, and #128's mirror `yf-ik3q` is open — when #128 closes, `yf-ik3q` becomes stale the same way.

## Why it matters

The failure is quiet and points the wrong way:

- `bd ready` offers the bead as available work. An agent or operator picking it up does work that is already done, or discovers only after opening the issue that it is closed.
- It is **invisible to `closable`**, which reasons from local bead state to propose upstream closures. This is the opposite direction — upstream state to local bead — and no verb reads it.
- It compounds with #142 (`closable` proposes closing already-closed issues): both come from the same root, that **local and upstream state are only ever reconciled in one direction**.

## Suggested directions

Not prescriptive.

- **A `stale-beads` / reverse-`closable` verb**: for each open bead with an `external_ref`, report those whose upstream issue is `CLOSED` or gone. Propose `bd close <id> --reason "upstream #N closed"`, **never auto-close** — same propose-with-confirm contract as `closable` and the follow-on hoist. The measurement above is essentially the whole implementation.
- **Close the mirror at reconcile time.** When the reconciler closes an upstream issue per an `include`/`supersede` disposition, close the mapped bead in the same step. Narrower, and it prevents the plan-040 case at source rather than sweeping afterwards.
- Consider whether both belong in one **bidirectional reconcile** verb rather than two one-way ones — `closable` (local → upstream) and this (upstream → local) are the same operation read from opposite ends, and a single verb would not have missed one direction.

## Immediate instance

`yf-1656` should be closed against #132 whenever this is picked up, or by hand in the meantime.

## Related

- **#117** — the same gap, opposite direction. Closed by plan-040.
- **#142** — `closable` ignores current upstream state. Same root cause.
- **#138** — plan-040's tracker; the plan that both fixed #117 and created this instance.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

