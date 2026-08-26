---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #219: yf-plan: `gate_consistency.py` does not check TEST/CONDITION FIDELITY

- **Number:** 219
- **Title:** yf-plan: `gate_consistency.py` does not check TEST/CONDITION FIDELITY
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

**Measured:** plan-052, at execution, by a human — **not** by the checker plan-052 shipped for
exactly this class of gate defect.

`skills/yf-plan/scripts/gate_consistency.py` (plan-052 Issue 4.2, the #113 sub-case) ships two
arms, and both are real:

- **ARM 1, self-satisfaction** — no issue in a gate's `Blocks` may be named in its
  `Condition`/`Test`/`Instructions` as producing that gate's evidence.
- **ARM 2, discharger closure** — no control the `Condition` requires may have all its
  dischargers inside, or transitively behind, that `Blocks` set.

**Neither arm looks at whether the `Test` actually implements the `Condition`.** A gate whose
Test *contradicts its own Condition* passes the predicate clean.

## The worked instance is plan-052's own Reconcile Gate

**Condition** (correct, verbatim):

> every non-gate execution bead **UNDER THIS PLAN'S EPIC**, EXCLUDING the reconcile step
> itself, is closed

**Test** (as shipped, faulty):

```
bd list --all --include-gates --json | jq -e '[.[]|select(.metadata.plan=="plan-052-james-dixson-fa8056" and .issue_type!="gate" and ((.title|startswith("Reconcile:"))|not) and .status!="closed")]|length==0'
```

The Test keys on `metadata.plan` and **never looks at parentage**, so it counted seven beads the
Condition already excluded — the deferred-defect beads (`parent=-`) that track upstream issues
which are **open by design**. They never close, so **the gate could never open** and reconcile
was unreachable.

`gate_consistency.py` reports this gate **PASS, 0 findings**.

## Why this is a genuine hole and not a bug in 4.2

4.2 meets its spec: SC13 asserts the two arms it commissioned, and both work. **The plan never
commissioned a third arm.** So this is a gap in the #113 sub-case's *scope*, not a defect in its
implementation — which is precisely why it belongs upstream rather than as a fix-in-place.

The general shape is this repo's recurring headline: *a step whose exit code reads the wrong
thing is worse than none*. A gate Test is the most load-bearing instance of that, because a Test
that disagrees with its Condition is **invisible to review** (both read plausibly on their own)
and **invisible to the checker** (which compares neither to the other).

## Suggested direction, not a specification

Fidelity is a prose/semantics judgement in general, so a full check may not be mechanizable. But
narrow, checkable sub-cases exist — e.g. a Condition naming a *scope* ("under this plan's epic",
"in this Blocks set") whose Test contains no corresponding structural filter. Even a
report-only heuristic would have caught this one.

*Filed as an eighth deferred defect from plan-052; the other seven are #211-#217. Enumeration:
`docs/plans/plan-052-james-dixson-fa8056/assets/deferred-defects.md`.*
