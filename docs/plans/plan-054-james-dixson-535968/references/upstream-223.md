---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #223: bd mol pour / yf-plan intake: one plan issue poured TWICE — 26 task beads for 25 declared issues, byte-identical duplicate

- **Number:** 223
- **Title:** bd mol pour / yf-plan intake: one plan issue poured TWICE — 26 task beads for 25 declared issues, byte-identical duplicate
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Filed by operator decision from the **plan-004** session in `dixson3/rc-files`.

## What happened

The §5.2a pour created **two beads for the same plan issue**. Measured immediately after Epic 1:

```
rc-files-mol-7ui.1.1  open     metadata: {"plan":"plan-004-...","plan_issue":"1.1"}
rc-files-mol-7ui.1.2  closed   metadata: {"plan":"plan-004-...","plan_issue":"1.1"}
```

Both carry **byte-identical title, description and dependency set** (dep order differs only). `bd show` on each:

```
.1.1  deps= ['rc-files-mol-6lo', 'rc-files-mol-7ui.1']
.1.2  deps= ['rc-files-mol-7ui.1', 'rc-files-mol-6lo']
```

Counted across the whole molecule:

```
beads in molecule: 34
duplicate plan_issue values: {'1.1': 2}
plan_issue values present: 1.1 … 6.5   (all 25 declared issues)
count with plan_issue: 26     <- one more than plan.md declares
```

So **exactly one** issue was duplicated; every other id from 1.2 through 6.5 is unique. `plan_extract.py --strict` on the same `plan.md` reports 25 issues, 0 unparsed — the plan document is not ambiguous.

## Why it matters

The executing agent closed one copy (with a real close reason) and left the other **open**. That is the natural outcome: from inside the run, the agent claims a bead, does the work, closes it, and has no reason to suspect a twin.

Left open, the duplicate keeps its epic **non-terminal**, so `close_cascade.py` at §6.4 fail-louds and **completion halts** — correctly, but at the far end of the run, with a diagnostic pointing at the epic rather than at the pour.

It is also invisible to the agent doing the work. It was caught only by an observing parent session counting the poured DAG against `plan.md` — i.e. by `pour_fidelity.py`'s job, which (per #210) is not shipped and could not run.

## Interaction with #210

This is precisely the defect `pour_fidelity.py` exists to catch, and #210 means that gate **cannot run in any repo but this one**. The two issues compound: the pour can duplicate, and the check that would notice is not installed. Fixing #210 would have surfaced this at §6.4 with an accurate message; it would not prevent it.

## What we did

Closed the duplicate with an explicit tombstone rather than as work:

```
POUR DUPLICATE — not work. Superseded by rc-files-mol-7ui.1.2, which carries the real Issue 1.1 close reason.
```

A manual pour-fidelity equivalent then reported: 0 dropped edges of 28, 26/26 issues mapped, only this known duplicate (both copies closed), cascade clean.

## Unknowns — I could not determine root cause from the consumer side

- Whether the duplicate originated in `bd mol pour` itself or in the skill's `bd create` loop over `plan_extract.py` output.
- Why issue **1.1** specifically — the first child of the first epic. That position is suggestive (an off-by-one or a retry on the first create), but I have one occurrence and cannot distinguish a systematic first-child bug from a transient.

Both would be answerable from the pour side with the molecule id `rc-files-mol-7ui` and the plan bundle, which is committed at `dixson3/rc-files@c49eea5` under `docs/plans/plan-004-james-dixson-f0bcc5/`.

## Suggested fix

1. Make the create loop **idempotent on `plan_issue`** — refuse to create a second bead carrying a `plan_issue` value already present in the molecule.
2. Failing that, have the pour **assert its own output**: bead count with `plan_issue` == issue count from `plan_extract.py`, at pour time rather than at §6.4. A duplicate detected at the pour is a one-line fix; the same duplicate detected at cascade-close is a halted completion.

## Related

- #210 — `pour_fidelity.py` not shipped; the check that would catch this cannot run.
- #209 — issue beads carry no `plan_dir`; same general area of pour metadata fidelity.
