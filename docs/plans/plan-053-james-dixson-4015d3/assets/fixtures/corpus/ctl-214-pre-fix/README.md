# `ctl-214-id-collision` — PINNED NEGATIVE FIXTURE

A frozen copy of the eleven `REQ-PLAN-073`-bearing files as they stood at the commit recorded
in `PINNED-AT.txt` — the merge that landed plan-053's intake, i.e. **before Issue 0.2**.

## Why this exists

`ctl-214-id-collision` asserts a property of the **live tree**, and Issue 0.2 fixes that tree.
Once 0.2 lands the control is green there and can never be driven RED against it again — the
same ordering inversion Issue 1.6a hit, and plan-052 Issue 0.3 before it. The fix is the one
those two used: pin a negative fixture and drive the RED against it.

This is not a workaround for running the epics out of order. It is structural: the plan is
**SPEC-first**, so Epic 0 lands before Epic 1 by design, and a control that grades Epic 0's
work is therefore always authored after the thing it grades.

## Running it

```bash
YF_TREE="$PWD/fixtures/corpus/ctl-214-pre-fix" bash fixtures/ctl-214-id-collision.sh   # RED
bash fixtures/ctl-214-id-collision.sh                                                  # GREEN
```

The `YF_TREE=` prefix is recorded verbatim in `red-prework.md`, so the RED observation states
on its face which tree it was made against.
