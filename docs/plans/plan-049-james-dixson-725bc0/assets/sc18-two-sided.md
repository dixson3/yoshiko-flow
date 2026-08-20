---
type: Reference
okf_spec: OKF-PLAN
id: sc18-two-sided
description: Two-sided evidence that the promoted CHANGE-VALIDATION rows actually select and redden (Issue 4.4 / SC18)
---

# SC18 evidence: the promoted rows select **and** redden, driven in both directions

**Issue:** plan-049 4.4 · **Criterion:** SC18 · **Run:** 2026-08-20

## Why this criterion is worded the way it is

SC18 asks for a **two-sided** demonstration, and its own text explains why the one-sided form
is unsatisfiable:

> Measured: the deletion yields `{"commands": [], "status": "pass"}` — a **vacuous green, never
> red** — and `change_validation.py` has no verb flagging a §1 id that no §3 glob references,
> so "deleting the row reddens it" is unsatisfiable as a one-sided assertion.

That is exactly what re-measurement here confirms. A missing §3 row does not fail; it selects
**nothing** and returns `pass`. So "the row is load-bearing" can only be shown by running the
*same* breakage twice — once with the row, once without — and observing that the verdict differs.

## The breakage

A one-line mutation of `_shared/dag_guard.py` neutering the **L3** comparison — the count-only
drift `REQ-DATA-051` forbids by name:

```python
# shipped
cp, cq = Counter(p["L3"]), Counter(q["L3"])
# mutant
cp, cq = Counter(), Counter()
```

This is the right mutant for the criterion: it does not break a syntax check or a type check.
Only a control that actually *executes the guard's mutant suite* can see it.

## The two arms

| Arm | §3 rows | Selected commands | Verdict |
| :-- | :-- | :-- | :-- |
| 1 — rows present | `_shared/dag_guard.py` → `dag-guard`, `gate-dagguard` | `uv` ✅, `uv-_shared` ✅, **`dag-guard` ❌** | **`fail`** |
| 2 — rows deleted | *(none match)* | *(empty)* | **`pass`** |

```console
$ uv run change_validation.py run --tier fast --changed _shared/dag_guard.py --json
{"status":"fail","commands":[{"id":"uv","ok":true},{"id":"uv-_shared","ok":true},{"id":"dag-guard","ok":false}]}

$ # …with the `_shared/dag_guard.py` and `_shared/**` rows deleted, same broken tree:
{"status":"pass","commands":[]}
```

Both the tree and the mutation are **identical** across the arms. The only variable is the §3
row, so the difference in verdict is attributable to the row and to nothing else.

## What arm 2 shows, stated plainly

`{"commands": [], "status": "pass"}` is a **vacuous green**. It is not a warning, not an
`INCONCLUSIVE`, and not distinguishable at the exit-code level from a tree where every control
ran and passed. An unreferenced §1 id is silently inert — and today **plan-047's and plan-048's
best positive controls are executed by nothing** for exactly this reason.

## The coupling, accepted knowingly

Issue 4.4 promotes **this plan's own** gate scripts —
`docs/plans/plan-049-james-dixson-725bc0/scripts/gate-dagguard.sh` and `gate-cellcheck.sh` —
into committed §1 rows, which means a completed bundle's scripts become part of the repo's
land-the-plane recipe. That coupling is deliberate and bounded:

- these scripts were **authored by this plan for this purpose** and land with it, whereas a
  historical bundle's gate scripts were authored for a different plan's gates and would drift
  out from under the row;
- the alternative is what the corpus already demonstrates — controls that exist and execute
  never.

**If a second plan needs them, move them to a non-bundle home** (`_shared/` or `tests/`) rather
than adding a second bundle coupling.
