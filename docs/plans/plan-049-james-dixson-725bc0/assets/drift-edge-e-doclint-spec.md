---
type: Reference
okf_spec: OKF-PLAN
id: drift-edge-e-doclint-spec
description: Two-arm drift-verifier run proving the e-doclint-spec edge fires (Issue 0.6 / SC34)
---

# SC34 evidence: the `e-doclint-spec` drift edge fires on an injected divergence

**Issue:** plan-049 Issue 0.6 · **Criterion:** SC34 · **Run:** 2026-08-20

`yf-drift-check` has no runnable command — an edge is judged by dispatching the report-only
`drift-verifier` sub-agent. So "the edge fires" is demonstrated the only way it can be: by
running the verifier **twice**, on a control and on an injected divergence, and showing the two
arms differ. A single green arm would not distinguish a working edge from an edge that cannot
fail.

## The edge

| Field | Value |
| :-- | :-- |
| Edge id | `e-doclint-spec` |
| Source node (**fixed** authority) | `spec` — `skills/yf-plan/spec/data.md` |
| Derived node | `doclint-canonical` — `_shared/doc_lint.py` + `_shared/document_types/*.toml` |
| Contract | `field-set-equal`, judged in **both** directions |
| Trigger globs (§6) | `_shared/doc_lint.py`, `_shared/document_types/*.toml` |

## The injected divergence

One hunk in `lint()`, applied to a scratch copy of the engine. The spec file is **unchanged** in
both arms, so the only variable is the code:

```python
# shipped
mapping = (STATUS_SEVERITY.get(status or "", {})
           if schema.get("promote", True) else {})

# injected — bypasses the map in ONE direction only
mapping = STATUS_SEVERITY.get(status or "", {})
if not schema.get("promote", True) and status in ("review", "ready-for-approval"):
    mapping = {}
```

This is deliberately a *subtle* mutant. It satisfies the headline sentence ("promotion is off for
`plan-relations`") and violates only the clause REQ-DATA-053 spends a sub-clause on — **"in both
directions"**. A verifier that skims would pass it.

## Results

| Arm | Engine | Verdict | Basis |
| :-- | :-- | :-- | :-- |
| 1 — control | in-tree `_shared/doc_lint.py` | **PASS** | REQ-DATA-024/043/044/045/053 each traced to implementing code |
| 2 — injected | scratch copy, one hunk | **FAIL** on `doclint-canonical` | quotes REQ-DATA-053's "**in both directions**" clause and the contradicting lines |

Measured on `docs/plans/plan-048-james-dixson-ed68a5/plan.md` (`bundle_status: complete`), same
fixture both arms:

| Arm | `R1b` severity | `warnings` | `report_only` |
| :-- | :-- | --: | --: |
| control | `W` (declared `W`) | 4 | 0 |
| injected | `R` (declared `W`) | 0 | 5 |

Fault assignment was correct: `spec` is fixed authority, so the verifier reported the **engine**
drifting — not a CONFLICT, since the spec statement is current.

## Adverse finding: the edge caught a real, pre-existing divergence on its first run

Arm 1 passed on the five clauses under test but reported a divergence outside them, which is
recorded here rather than discarded:

> `REQ-DATA-024` read "**Two severities**, and only one is an error: `E` … and `W`", while nine
> checks across five schemas (`upstream-triage`, `upstream-reference`, `finding`, `review`,
> `plan-retrospective`) declare `severity = "R"` directly, and `doc_lint.py` has accepted it
> since `ERROR, WARN, REPORT = "E", "W", "R"`.

This is exactly the class the edge exists to catch — an implemented behaviour with no
declaration — and it had been live since plan-047. **Resolved in the same change-set**:
REQ-DATA-024's severity bullet now declares three severities and states that `R` is both
declarable and a demotion outcome. The finding is left in this record rather than quietly fixed,
because "the edge found something real on run one" is the strongest available evidence that it
is not decorative.

## Reproduce

```bash
# 1. copy the engine, apply the one-hunk mutation shown above
# 2. dispatch the report-only drift-verifier over `e-doclint-spec` twice:
#      arm 1: spec = skills/yf-plan/spec/data.md, engine = _shared/doc_lint.py
#      arm 2: spec = same file, engine = the mutated copy
# 3. assert arm 1 PASS and arm 2 FAIL, and that arm 2 quotes REQ-DATA-053
```
