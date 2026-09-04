---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #327 - `land --apply` is an unconditional stub — the
  fully-implemented `_land_execute` has no caller, so no plan can land'
---
# Upstream #327: `land --apply` is an unconditional stub — the fully-implemented `_land_execute` has no caller, so no plan can land

- **Number:** 327
- **Title:** `land --apply` is an unconditional stub — the fully-implemented `_land_execute` has no caller, so no plan can land
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

## The defect

`land --apply` can never execute a landing. The CLI performs its two safety checks and then
falls into an **unconditional stub**, at `plan_manager.py:8305-8310`:

```python
where = _land_assert_primary_checkout()   # runs
gate  = _land_tty_gate()                  # runs
click.echo(json.dumps(_land_envelope(
    "inconclusive",
    "the --apply executor is not implemented in this change-set",
    remediation="Epics 3 and 4 implement the journal, the conflict contract and the "
                "L0-L19 steps."), indent=2))
sys.exit(2)
```

Observed against a validated decision (`pass` / `digest_ok: true` / `problems: []`), from the
primary checkout, in a real terminal (so the tty gate passed):

```json
{
  "verdict": "inconclusive",
  "passed": false,
  "reason": "the --apply executor is not implemented in this change-set",
  "remediation": "Epics 3 and 4 implement the journal, the conflict contract and the L0-L19 steps."
}
```

## This is DEAD CODE, not a missing feature

`_land_execute` is **fully implemented** — it drives L0-L19, advances the journal between
steps, supports journal-keyed resume, and is fail-closed at every edge. `LAND_EXECUTOR` wires
all 15 step functions in `REQ-LAND-004` order, and every one of those functions exists.

But `_land_execute` has **exactly one occurrence in the file — its own `def`**. Nothing calls
it:

```
$ grep -n '_land_execute' skills/yf-plan/scripts/plan_manager.py
9538:def _land_execute(ctx: LandingContext, resume_from: str | None = None) -> dict:
```

The engine was built and the ignition was never connected.

## The remediation text is stale and actively misleading

The stub says *"Epics 3 and 4 implement the journal, the conflict contract and the L0-L19
steps."* Epic 4 **did** implement them — commit `26bb490`, "plan-060 Epic 4: the ordered
landing steps L0-L19". A reader who trusts the message concludes the steps are missing and
goes looking for unwritten code, when what is missing is the single call that reaches it.

## Why the tests did not catch it

`plan-060` Epic 6's rehearsal exercised `_land_execute` **directly**. That is why it caught a
real bug in the journal (skipping L19 stalled the terminal state at `L_PRUNED` rather than
reaching `L_DONE`, refused by SC36b) — while being structurally unable to notice that no
caller reaches the function it was driving.

This is the **vacuous-check class** (#263) at the harness level: a test suite that passes
comprehensively over an engine no entry point invokes. The gap is not in the steps; it is in
the seam between the CLI and the steps, which nothing tests.

## Impact

`land --apply` is the sole writing mode of the landing capability, so **no plan can land
through the intended path**. plan-061 is blocked on it today with a validated decision, 12
unpushed commits, and 8 authored upstream drafts; every future plan hits the same wall.

## Suggested direction (not prescriptive)

- Replace the stub with the call into `_land_execute`, passing the `LandingContext` built from
  the validated decision, and honour its returned verdict + exit code.
- Add a test at the **seam**, not the engine: assert that `land --apply` against a valid
  decision reaches at least L0 (a lock acquisition is observable), so a disconnected entry
  point fails loudly. An engine-level test cannot express this.
- Re-check whether any other `plan-060` verb has the same shape — an implemented helper with
  no caller.

## Provenance

Found during **plan-061** (`plan-061-james-dixson-6d8c97`, tracker #315) at its landing step,
by the operator running the command in a real terminal. Blocks that plan's landing.

