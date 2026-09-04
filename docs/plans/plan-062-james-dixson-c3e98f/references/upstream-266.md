---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #266 - CRITICAL: the plan.md Gates grammar cannot express
  test_class or cwd, so every capability gate defaults to a class that is never run'
---
# Upstream #266: CRITICAL: the plan.md Gates grammar cannot express test_class or cwd, so every capability gate defaults to a class that is never run

- **Number:** 266
- **Title:** CRITICAL: the plan.md Gates grammar cannot express test_class or cwd, so every capability gate defaults to a class that is never run
- **URL:** 
- **State:** OPEN
- **Labels:** type::bug, priority::critical

## Body

Plan: plan-056-james-dixson-473dba | Bundle: docs/plans/plan-056-james-dixson-473dba (repo-relative)

A capability gate declared in `plan.md` cannot say which class it belongs to, and the default is the
one class the execute-start sweep never runs. Every capability gate in every plan is affected.

MEASURED, against the installed skill:

1. `plan_extract.py:110` — the gate-field grammar is exactly:

       GATE_FIELD = re.compile(
           r"^- +\*{0,2}(Type|Approvers|Condition|Test|Blocks|Instructions)\*{0,2}\s*:\s*(?P<val>.*)$", re.I)

   There is no `test_class` and no `cwd`. Confirmed by extracting a real plan: the gate object carries
   `name/line/type/condition/test/test_kind/blocks/blocks_raw/instructions` and nothing else.

2. `test_gates.py:243` — `test_class = gate.get("test_class") or "manual"`, and line 244 routes
   `manual` (or an absent `test`) to INCONCLUSIVE.

3. `SKILL.md` §5.2c — "Run the `probe` class — and ONLY the `probe` class — unattended." §5.2d adds
   `build` only under `--sweep-gates=all`. `consent` and `manual` are never run by either setting.

4. `coordinator.md` and `SKILL.md` both state INCONCLUSIVE is never FAIL.

5. `grep -rn test_class` over `formulas/`, `plan_manager.py`, `gate_consistency.py` returns ZERO hits.
   The only writer is the hand-run `bd create --metadata` snippet in SKILL.md §5.2a, whose
   `${test_class}` shell variable has no source in the document.

CONSEQUENCE. SKILL.md §5.2a says the structured metadata is what "makes the sweep mechanical", and
warns: "Without this structure, do not build the sweep — a sweep over prose is a sweep that silently
sees a third of its input." But the authoring surface cannot supply the structure. So the value is
invented at pour time by whoever pours, and an omission yields `manual` — a gate that resolves
INCONCLUSIVE, is never auto-run, and never fails. A plan can declare `Type: auto` with a real
executable `Test:` and still get a gate that nothing ever executes.

`cwd` has the same shape and a worse failure mode: execution-worktree scripts under a gate poured
`cwd: repo-root` can never pass, so the gate permanently FAILs and stalls into stop class 2.

WHY THIS MATTERS BEYOND ONE PLAN. plan-056's red-team found its criteria layer vacuous in five
consecutive passes. The fix for the fifth was to move the load-bearing check from a Success Criterion
to a capability gate, on the reasoning that a gate's Test is executed by the coordinator and halts on
exit code, outside `recheck-criteria`'s verdict arithmetic. That reasoning is sound and the gate is
reachable — but the compensating control is inert by default, which is the same collapsed-signal
family tracked by #263 and #265: a declared control that cannot fire, and nothing distinguishes it
from one that fired and passed.

SUGGESTED REMEDY. Add `Test-class:` and `Cwd:` to the `## Gates` grammar and to `GATE_FIELD`, carry
them through `plan_extract.py` into the pour, and make `gate_consistency.py` report a capability gate
that declares `Type: auto` with an executable `Test:` but no `Test-class:` — since that combination is
today silently unrunnable. Consider whether an absent `test_class` on an `auto` gate should be an
error rather than defaulting to `manual`.

Found by plan-056 red-team pass 5.
