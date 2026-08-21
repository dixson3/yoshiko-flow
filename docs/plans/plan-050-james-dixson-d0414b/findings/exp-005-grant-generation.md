---
type: Finding
okf_spec: OKF-PLAN
id: exp-005
status: complete
---

# Finding: Can the upstream grant be generated from the Upstream Issues table? (#178)


> **SUPERSEDED at pass-3 C12 — read this before acting on anything below.** This finding's central
> recommendation, that the grant generator can call `_verify_row` itself, was **refuted by measurement**:
> `_verify_row` returns no `required_action` (only `{detail, disposition, issue, verdict}`), is
> **network-bound** (its first act is `gh issue view` per row, returning `inconclusive` before consulting
> any table), and returns `fail: "unrecognised literal"` when handed an `exclude` row directly. The plan
> ships a **shared requirement table** instead — Issues **3.2** (extract the table, make `_verify_row` read
> it) and **3.2a** (the `grant` verb on top of it). The finding is retained unedited below because the
> refutation is the useful part; do not build the design it recommends.

## Approach Tested

Looked for an existing disposition → end-state map in `plan_manager.py`, to determine whether a
generator would need a new one (and could therefore drift from the verifier).

## Result

**measured:** the map already exists — `_verify_row` at `skills/yf-plan/scripts/plan_manager.py:2012`,
with the disposition literals declared once at `:3908` and shared with `doc_lint`'s R2c rule:

```
:2025  include    -> state must be CLOSED, and a comment must mention the plan id
:2036  supersede  -> CLOSED with reason NOT_PLANNED
:1992  _mentions_plan_id  -> requires the FULL plan id
```

**inferred:** #178 is unusually cheap, and cheaper than the issue assumes. The generator does not
need its own map — it can call the **same function that verifies the result**. A grant generated
from `_verify_row`'s own requirements cannot disagree with the verifier that later checks it,
because there is one map, not two.

That property is the real prize. plan-048 halted its own reconcile because the hand-derived grant
and the verifier disagreed about one `include` row. Two independent transcriptions of one rule is
the M12 class; sharing the function removes the class rather than fixing an instance.

## Implications for Plan

- Ship a `grant` verb that reads the Upstream Issues table and emits the required action per row
  **by asking `_verify_row` what it will demand**, not by re-encoding the rules.
- The `deferred` disposition (added by plan-048) and `tracker`/inconclusive (REQ-CLI-018) must be
  covered — a generator silently omitting a disposition is the same silent-green class as #181.

## Recommendations

- **Driven-red fixture:** plan-048's actual grant, with the `#172` close omitted, must be rejected
  by the generator's own round-trip check. That is a real recorded failure, not a synthetic one.
- Do not let the generator write the authorization file. Generating the *proposal* is mechanical;
  authorizing it is a consent gate and stays with the operator.
