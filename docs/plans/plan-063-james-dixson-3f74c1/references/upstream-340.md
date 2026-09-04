---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #340 - L18 crashes with a TypeError on every landing:
  _land_l18_prune calls _worktree_teardown with one arg, signature needs two'
---
# Upstream #340: L18 crashes with a TypeError on every landing: _land_l18_prune calls _worktree_teardown with one arg, signature needs two

- **Number:** 340
- **Title:** L18 crashes with a TypeError on every landing: _land_l18_prune calls _worktree_teardown with one arg, signature needs two
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

## The defect

`_land_l18_prune` calls `_worktree_teardown` with one argument; the function requires two.

```python
# skills/yf-plan/scripts/plan_manager.py:9512
wt = _worktree_teardown(ctx.plan_dir)

# skills/yf-plan/scripts/plan_manager.py:4354
def _worktree_teardown(plan_dir: Path, force: bool) -> dict:
```

Measured, on the first real landing ever performed through `land --apply`:

```
File "skills/yf-plan/scripts/plan_manager.py", line 9512, in _land_l18_prune
    wt = _worktree_teardown(ctx.plan_dir)
TypeError: _worktree_teardown() missing 1 required positional argument: 'force'
```

This is an **uncaught exception**, not a step returning `fail` — so it produces a Python
traceback rather than a landing envelope, writes no journal phase, and returns no verdict a
caller could act on.

## Why it survived until now

**L18 had never executed.** `land --apply` was an unconditional stub (#327) that exited 2 before
reaching the executor, so the whole L0–L19 chain was dead code. plan-060's Epic-6 rehearsal drove
`_land_execute` **directly**, which is how it caught a real journal bug — and it did not reach
this line under its sandbox conditions.

So the fix for #327 made the executor reachable, and **the first invocation immediately hit a
latent arity bug in the code that fix made live.** That is #327's own argument about dead code,
demonstrated by its remedy, on its own landing.

## Blast radius, measured

The crash lands **past the irreversible boundary**, at the second-to-last step. On plan-062's
landing everything before it completed correctly:

| | |
| :-- | :-- |
| `main` | pushed twice, in sync with `origin` |
| #327 | CLOSED with its attribution comment |
| #266, #304 | OPEN, each commented — refusals honored |
| beads | 31 of 31 closed |
| plan status | `complete` |
| journal | `L_MIRRORED` (L17 done) |

The only residue was the **undeleted execute branch** — L18's own job. So the damage here is
small, but it is small by luck of position: an identical arity bug at L7 or L12 would have
crashed mid-write with no envelope and no journal advance.

## The resume interaction is the sharper half

Because the exception escapes rather than returning a halting `_step`, the journal stays at
`L_MIRRORED`. A resume then re-enters at L18 and crashes identically — an unbreakable loop until
the code is fixed. It cannot skip past its own crash.

## Suggested direction (not prescriptive)

- Fix the call: `_worktree_teardown(ctx.plan_dir, force=False)` (or whatever the intended
  policy is — note L18 is documented as strategy-aware via `REQ-LAND-023`, so `force` may want
  to follow the landing strategy rather than be hardcoded).
- **Wrap step dispatch in `_land_execute` so an exception becomes a halting `_step`** with a
  journal phase and a verdict, rather than a traceback. A step that raises is currently
  indistinguishable from the harness itself breaking.
- **Add an arity/signature check to the test suite** for every `LAND_EXECUTOR` row — the whole
  chain was dead code for its entire existence, so any other row may carry the same class of
  defect. A cheap `inspect.signature` sweep over the fifteen step functions would have caught
  this before a landing did.

## Provenance

Found on the **first real `land --apply` invocation**, landing **plan-062**
(`plan-062-james-dixson-c3e98f`, tracker #330) — the plan that wired the seam. Adjacent to #327.

