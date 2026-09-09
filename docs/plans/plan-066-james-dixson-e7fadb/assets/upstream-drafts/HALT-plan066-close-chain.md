---
type: Note
okf_spec: OKF-PLAN
description: "plan-066's §6.4 close chain HALTS at verify-reconcile on five rows. Four are an attribution gap nobody had authorized writes for; the fifth is an ordering conflict. Nothing posted."
id: halt-plan066-close-chain
plan: plan-066-james-dixson-e7fadb
created: 2026-09-09
---
# HALT — plan-066's close chain, at `verify-reconcile`

**This is a stop, reported rather than worked around.** `verify-reconcile` fails **5 of 7**
upstream rows. Nothing has been posted and plan-066 has not been advanced.

## The five failing rows

| Issue | State | Why it fails |
| :-- | :-- | :-- |
| `#317` | **OPEN** | an `include` row must end CLOSED |
| `#104` | CLOSED | closed, but **no comment carries the full plan id** |
| `#127` | CLOSED | same |
| `#363` | CLOSED | same |
| `#322` | CLOSED | same |

## Row 1 — `#317` is an ORDERING CONFLICT, and it is mine to flag

The authorized step order is *"drive plan-066 to `complete`, **then** close `#317`."* But
`#317` is an `include` row in plan-066's own Upstream Issues table, so
**`verify-reconcile` requires it CLOSED before the close chain can pass.** plan-066 cannot reach
`complete` with `#317` open.

**Closing `#317` first does NOT violate the stated constraint.** That constraint is *"do not close
a **tracker** for a plan still in `executing`"* — and `#317` is a **scope issue**, not a tracker.
The trackers are `#372` and `#379`, and both stay shut until their plans read `complete`.

So the resolution is a one-step reorder: **`#317` closes as the last act of plan-066's reconcile
(Issue 8.5), not after its completion.** The already-drafted `317-comment.txt` is unchanged.

## Rows 2-5 — an ATTRIBUTION gap, and four writes nobody authorized

These four are **already closed, and the fix in each is real and unchanged.** The failure is
narrower than it looks and worth stating exactly, because "closed with no explanation" would be
wrong:

> Each carries a close comment beginning **"Fixed in plan-066"**. What none carries is the **full
> plan id** `plan-066-james-dixson-e7fadb`, which is what `verify-reconcile` matches on.

The checker is right to require the full id. A short form is **ambiguous across plans** and cannot
be resolved mechanically — the full id is the key that maps a closed issue back to the bundle that
closed it, which is the whole point of `REQ-PLAN-074` / `#136`. A close a machine cannot trace is
an unproven reconciliation even when a human can read the intent.

**But this needs four upstream comments that are in neither the authorized set nor the earlier
draft set.** They are drafted here and **unposted**:

- [104-attribution.txt](104-attribution.txt)
- [127-attribution.txt](127-attribution.txt)
- [322-attribution.txt](322-attribution.txt)
- [363-attribution.txt](363-attribution.txt)

Each says the same thing: names the full plan id, states that no new work is claimed and the fix
is unchanged, and explains that the comment exists so the close is **traceable** rather than
merely explained.

## What unblocks the chain

Six writes, in this order. **None has been performed.**

```bash
P=docs/plans/plan-066-james-dixson-e7fadb/assets/upstream-drafts
Q=docs/plans/plan-067-james-dixson-de852a/assets/upstream-drafts

# 1-4  attribution only. These issues are ALREADY CLOSED and stay closed.
for n in 104 127 363 322; do
  gh issue comment "$n" --body-file "$P/$n-attribution.txt"
done

# 5    #317 — the scope issue, closing as the last act of plan-066's reconcile.
gh issue comment 317 --body-file "$Q/317-comment.txt"
gh issue close   317

# then: plan-066's §6.4 chain re-runs and should pass, plan-066 -> complete,
#       and only THEN #372, then plan-067 -> complete, then #379 last.
```

Verify each by reading it back, never by exit 0:

```bash
for n in 104 127 363 322 317; do gh issue view "$n" --comments | tail -12; done
gh issue view 317 --json state --jq .state    # CLOSED
for n in 104 127 363 322; do gh issue view "$n" --json state --jq .state; done   # all CLOSED
gh issue view 247 --json state --jq .state    # must still print OPEN
gh issue view 263 --json state --jq .state    # must still print OPEN
```

## What was completed before the halt

Issue 8.5's **local** half is done: the `Resolved By` column is filled for all seven rows (it was
`_TBD_` throughout, which `pass-1 C14` promotes to `E` severity at `reconciling`). Only the
upstream half remains, and it is gated.
