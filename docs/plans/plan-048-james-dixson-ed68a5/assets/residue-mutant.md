---
type: Reference
okf_spec: OKF-PLAN
id: residue-mutant
description: The residue bar is falsifiable (SC1)
---

# The residue bar is falsifiable (SC1, after the re-base to 81)

A target that only ever gets compared against the number that produced it is a tautology.
Re-basing 54 → 81 makes that risk sharper, not weaker: 81 is exactly what the current
implementation measures, so the bar must be shown to move in the failing direction.

## The mutant

Disable **one** recovery class — class A, the `Issue`/`Issues` noise-word prefix inside a
`Blocks:` value — and change nothing else:

```python
# _shared/plan_extract.py, inside the Blocks referent loop
- pm = _ISSUE_PREFIX.match(t)
+ pm = None  # MUTANT: class A (Issue-prefix) recovery disabled
```

## The result

| | Residue | Plans carrying unparsed | `gate-grammar.sh` |
| :-- | --: | --: | :-- |
| Unmutated | **81** | 24 | **exit 0** — capability present |
| Class A disabled | **98** | 30 | **exit 1** — capability absent |

```
$ bash scripts/gate-run.sh scripts/gate-grammar.sh     # with the mutant applied
residue: 98 (baseline 150, target <= 81); plans still carrying unparsed: 30
GATE: capability ABSENT — unparsed residue 98 exceeds the approval-fixed target of 81
exit=1
```

The mutation was reverted immediately; `_shared/plan_extract.py` is unchanged on disk.

## What this establishes, and what it does not

**Establishes:** the gate's residue assertion is *live*. A regression that loses a recovery
class raises the residue and turns the gate red. The bar is not satisfied by construction.

**Does not establish:** that 81 is the *right* number. That is a derivation, not a
measurement, and it is argued in
[residue-analysis.md](residue-analysis.md) — 150 baseline, 69 recovered by the four declared
classes, 81 refused by rules the plan itself declares. The mutant defends the bar's
*direction*; the derivation defends its *value*.

**No refusal class was relaxed to reach 81.** Issue 1.4a's negative mutant (a partly-readable
`Blocks:` list is refused whole) and EXP-001's measured harm (a mechanical repair silently
emptying 20 `depends-on` declarations) both stand unchanged.
