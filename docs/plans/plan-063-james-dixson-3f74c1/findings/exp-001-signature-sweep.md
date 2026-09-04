---
type: Finding
okf_spec: OKF-PLAN
description: 'Whole-module arity sweep of plan_manager.py: 252 module-level functions, 46 reachable from the 15 LAND_EXECUTOR steps, exactly ONE defect — #340. The dead-code-cluster hypothesis is refuted. HEADLINE: the real systemic gap is MOCK FIDELITY — 4 of 78 monkeypatched stubs are signature-incompatible, all four the same one-arg _worktree_teardown fake, including land_rehearsal.py:140, which is mechanically why plan-060 Epic 6 missed L18. Also finds two further latent L18 defects that are not arity mismatches.'
---
# EXP-001 — How many more #340-class defects are in the chain?

**Question.** The whole L0–L19 chain was dead code until plan-062 wired it, and its first real
run crashed on an arity mismatch. How many more are there?

## Approach Tested

Three static/dynamic passes plus a real-git sandbox spike, read-only against
`plan_manager.py` (9781 lines). An `ast` + `inspect.signature` binder over every module-level
call site at three scopes; a second pass for attribute calls (`ctx.*`) and return-shape
contracts; a **mock-fidelity** pass comparing every `monkeypatch.setattr` stub against the real
function; and a sandbox running the **real** `_land_l18_prune` against a real worktree under
four variants.

## Result

### HEADLINE 1: the cluster hypothesis is REFUTED — one defect, not many

| Scope | Functions | Defects |
| :-- | --: | --: |
| The 15 `LAND_EXECUTOR` steps | 15 | **0** (all exist, all bind as `fn(ctx)`) |
| Transitive closure from the steps | 46 | **1** |
| **Whole module** | **252** | **1** |

The one defect is #340, at all three scopes:

```
DEFECT _land_l18_prune line 9512: _worktree_teardown(...) -- def at line 4354
       (plan_dir: pathlib.Path, force: bool) -> dict
       call passes 1 positional, kwargs=[]; missing a required argument: 'force'
```

Two steps return `list[dict]`; `_land_execute:9748` handles that explicitly
(`batch = out if isinstance(out, list) else [out]`). All 15 build rows via `_step(...)`, so the
keys the driver reads are structurally guaranteed. **Scope a fix, not a sweep.**

Dispatch surfaces: exactly **one** `globals()[...]` in the file (`:9747`) and **zero**
getattr-style dispatches. Its target table is fully covered above. All 21 `ctx.run` sites are
clean — an initial "NO SUCH ATTRIBUTE" flag was a **false positive** of a class-level `hasattr`
(`self.run = self._dispatch` is assigned in `__init__` at `:8863`), corrected on re-run.

### HEADLINE 2: the real gap is MOCK FIDELITY, and it explains the miss

```
stubs checked: 78   INCOMPATIBLE: 4

  test_land_apply.py:1023  _worktree_teardown  real: (plan_dir, force)  stub: (pd)
  test_land_apply.py:1180  _worktree_teardown  real: (plan_dir, force)  stub: (pd)
  test_land_apply.py:1254  _worktree_teardown  real: (plan_dir, force)  stub: (pd)
  land_rehearsal.py:140    _worktree_teardown  real: (plan_dir, force)  stub: (pd)
```

**The mocks encoded the bug.** `land_rehearsal.py:140` is
`pm._worktree_teardown = lambda pd: {"action": "not-registered"}` — a one-arg fake of a two-arg
function. That is the concrete, mechanical reason plan-060's Epic-6 rehearsal drove
`_land_execute` directly and still passed, and `test_prune_is_strategy_aware`
(`test_land_apply.py:1020`) installs the identical stub, so Tier-1 was blind for the same reason.

Corroborating precedent, from the codebase's own record: `_dispatch`'s docstring (`:8856-8861`)
documents a **prior instance of this exact class** — a wrapped `ctx.run([...])` that made L7 run
`git issue comment` — caught by the Epic-6 rehearsal rather than by Tier-1.

### `force=False` is correct — measured, four sandbox runs

| Variant | Outcome |
| :-- | :-- |
| A — current tree | `TypeError: … missing 1 required positional argument: 'force'` — **#340 reproduced** |
| B — `force=False`, clean | `status: ok`; worktree removed, execute branch deleted, **feature branch preserved** (REQ-BRANCH-004) |
| C — `force=False`, dirty | `status: blocked`; worktree and branch survive — **yet L18 still returns `verdict: pass`** |
| D — `force=True`, dirty | `status: ok`; dirty tree clobbered |

The CLI path agrees: `worktree_teardown_cmd` (`:4458-4460`) takes `--force` defaulting to
`False`. **Absence finding:** `grep force spec/landing.md` returns no L18-related hit — the SPEC
is **silent** on L18's force value. `REQ-LAND-023` makes L18 strategy-aware about *which branch*,
not about force.

### Two further latent L18 defects — neither is an arity mismatch

**1. Duplicate branch deletion.** `_worktree_teardown` already deletes the execute branch
(`:4392`). L18 deletes it *again* at `:9515`. Variant B measured the consequence:

```json
{"action": "delete-execute-branch", "ok": false, "detail": "error: branch '…-execute' not found"}
```

Once #340 is fixed, **L18 will permanently report its own headline action as failed.** Invisible
today only because the teardown is always mocked.

**2. L18 never inspects the teardown status.** `:9512-9513` appends `wt.get("action")` and never
branches on `wt["status"]`. Variant C measured a `blocked` teardown — worktree and branch both
left behind — reported as `verdict: "pass"`. **A dirty worktree at landing is silently not
pruned.**

## Implications for Plan

**measured:** every count above came from a runnable pass or a sandbox run, not from reading.
**inferred:** the claim that the four stubs are *why* the bug survived is reasoning from a
mechanical fact (the stubs are incompatible) to a causal one; it is corroborated by the
`_dispatch` docstring recording the same pattern previously.

- The arity axis is clean. **The plan should not be a sweep** — one targeted fix plus a check
  that prevents recurrence.
- **Fixing #340 alone leaves L18 wrong in two more ways.** A one-line patch ships a permanent
  false `ok: false` and a prune that reports success without pruning.
- The mock-fidelity gap **generalizes past the landing chain** — 78 stubs are in scope, and no
  type checker validates a `monkeypatch.setattr` stub against its target.
- `test_prune_is_strategy_aware:1030-1033` asserts on the **duplicate** `ctx.run` call, so the
  fix and that test move together.

## Recommendations

1. `_worktree_teardown(ctx.plan_dir, force=False)` at `:9512` — **keyword form**, so the next
   signature change fails loudly rather than silently rebinding a positional.
2. Delete the duplicate `ctx.run("git", ["branch","-d", …])` at `:9515` and update
   `test_prune_is_strategy_aware` to assert on the teardown result.
3. Make L18 **branch on `wt["status"]`** — a `blocked` teardown must not report `pass`.
4. **Adopt the mock-fidelity check as a repo check** (~60 lines, no network, sub-second). It is
   the only one of the four passes that would have caught #340 *before* the first real `--apply`.
   Wire it into `CHANGE-VALIDATION.md`. The whole-module arity pass is cheap insurance alongside
   it, but is redundant with `pyright`/`mypy`; **the mock check is not.**
5. Fix the four stubs in the same change-set, or the new check fails immediately on landing.
6. **SPEC-first:** amend `REQ-LAND-023` or add a sibling stating L18's teardown is non-forcing per
   INV-1 and that a blocked teardown is surfaced. The spec's silence is how the call site drifted.
