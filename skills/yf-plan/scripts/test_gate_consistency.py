#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tests for gate_consistency.check_plan (plan-052 Issue 4.2, #113).

Pure-function tests over extracted-document shapes: no plan.md on disk, no bd, no network.
The five-fixture end-to-end assertion lives in the plan's own `ctl-113-gate`; this covers the
predicate's edges.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

_spec = importlib.util.spec_from_file_location(
    "gate_consistency", pathlib.Path(__file__).resolve().parent / "gate_consistency.py")
gc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gc)

FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(("ok   " if ok else "FAIL ") + label + (f" — {detail}" if not ok and detail else ""))
    if not ok:
        FAILURES.append(label)


def doc(gates, issues, criteria):
    return {"gates": gates, "issues": issues, "criteria": criteria, "unparsed": []}


def gate(name, blocks, condition="", instructions="", test=""):
    return {"name": name, "condition": condition, "instructions": instructions, "test": test,
            "blocks": [{"kind": "issue", "ref": b} for b in blocks]}


# --- ARM 1 --------------------------------------------------------------------------------
f = gc.check_plan(doc(
    [gate("G", ["2.1"], instructions="the RED observation is recorded by 2.1")],
    [{"id": "1.1", "depends_on": []}, {"id": "2.1", "depends_on": ["1.1"]}],
    []))
check("ARM 1 fires when a BLOCKED issue is named as producing the evidence",
      any(x["arm"] == 1 for x in f), str(f))

f = gc.check_plan(doc(
    [gate("G", ["2.1"], instructions="the RED observation is recorded by 1.1, outside Blocks")],
    [{"id": "1.1", "depends_on": []}, {"id": "2.1", "depends_on": ["1.1"]}],
    []))
check("ARM 1 does NOT fire when the named issue is OUTSIDE the Blocks set",
      not any(x["arm"] == 1 for x in f), str(f))

# The boundary rule: `1.5` must not match inside `1.55` or `11.5` or `1.5.2`.
for prose, should_fire in (("built by 1.55", False), ("built by 11.5", False),
                           ("built by 1.5.2", False), ("built by 1.5", True),
                           ("built by 1.5, and more", True)):
    f = gc.check_plan(doc([gate("G", ["1.5"], instructions=prose)],
                          [{"id": "1.5", "depends_on": []}], []))
    check(f"ARM 1 id boundary: {prose!r} -> {'fires' if should_fire else 'silent'}",
          any(x["arm"] == 1 for x in f) is should_fire, str(f))

# --- ARM 2 --------------------------------------------------------------------------------
issues = [{"id": "1.1", "depends_on": []}, {"id": "2.1", "depends_on": []},
          {"id": "2.2", "depends_on": ["2.1"]}]

# all dischargers inside Blocks -> finding
f = gc.check_plan(doc(
    [gate("G", ["2.1"], condition="ctl-x has a recorded RED observation")],
    issues,
    [{"id": "SC1", "verification": "`run ctl-x` → exit 0", "discharged_by": ["2.1"]}]))
check("ARM 2 fires when every discharger sits INSIDE the Blocks set",
      any(x["arm"] == 2 for x in f), str(f))

# a discharger outside Blocks -> no finding
f = gc.check_plan(doc(
    [gate("G", ["2.1"], condition="ctl-x has a recorded RED observation")],
    issues,
    [{"id": "SC1", "verification": "`run ctl-x` → exit 0", "discharged_by": ["1.1", "2.1"]}]))
check("ARM 2 is SILENT when at least one discharger is outside the Blocks set",
      not any(x["arm"] == 2 for x in f), str(f))

# TRANSITIVELY BEHIND: 2.2 is not in Blocks, but depends on 2.1 which is.
f = gc.check_plan(doc(
    [gate("G", ["2.1"], condition="ctl-y has a recorded RED observation")],
    issues,
    [{"id": "SC1", "verification": "`run ctl-y` → exit 0", "discharged_by": ["2.2"]}]))
check("ARM 2 fires on a discharger TRANSITIVELY BEHIND the Blocks set",
      any(x["arm"] == 2 for x in f), str(f))

# A control nothing discharges is its own finding — not a silent pass.
f = gc.check_plan(doc(
    [gate("G", ["2.1"], condition="ctl-orphan has a recorded RED observation")],
    issues, []))
check("ARM 2 fires when the Condition requires a control NO criterion discharges",
      any(x["arm"] == 2 and x.get("control") == "ctl-orphan" for x in f), str(f))

# A prose glob is not a control id.
f = gc.check_plan(doc(
    [gate("G", ["2.1"], condition="every ctl-199b-* control has an observation")],
    issues, []))
check("ARM 2 ignores a prose GLOB rather than treating it as a control id",
      not any(x.get("control", "").endswith("*") for x in f), str(f))

# A gate with no Blocks cannot be self-satisfying.
f = gc.check_plan(doc([gate("G", [], condition="ctl-x", instructions="1.1")], issues, []))
check("a gate with an EMPTY Blocks set produces no finding", f == [], str(f))

# --- plan-071 Issue 4.4 (#325): two facts, two signals ------------------------------------
# no capability gate declared -> PASS, gates: 0, exit 0 (a legitimate plan, e.g. plan-069)
v = gc.verdict_for(doc([], issues, []), [])
check("no gates declared -> PASS, exit 0, gates 0", v == ("PASS", 0, 0, 0), str(v))
# gates declared but none has an issue-kind Blocks -> INCONCLUSIVE, exit 2, evaluated/total
d2 = doc([gate("G", [], condition="ctl-x", instructions="1.1"),
          {"name": "H", "condition": "ctl-y", "instructions": "1.1", "test": "",
           "blocks": [{"kind": "reconcile-step", "ref": "reconcile step"},
                      {"kind": "epic", "ref": "epic:2"}]}], issues, [])
v = gc.verdict_for(d2, gc.check_plan(d2))
check("gates declared, none evaluable -> INCONCLUSIVE, exit 2", v[0] == "INCONCLUSIVE" and v[1] == 2, str(v))
check("...and the verdict carries evaluated/total = 0/2", (v[2], v[3]) == (0, 2), str(v))
# an evaluable gate with no findings is PASS with evaluated >= 1; with findings it is FAIL
d3 = doc([gate("G", ["2.1"], condition="ctl-x", instructions="1.1")], issues, [])
v = gc.verdict_for(d3, [])
check("an evaluable clean gate -> PASS with evaluated 1/1", v == ("PASS", 0, 1, 1), str(v))
v = gc.verdict_for(d3, [{"arm": 1, "detail": "x"}])
check("an evaluable gate with a finding -> FAIL, exit 1", v[0] == "FAIL" and v[1] == 1, str(v))

print()
if FAILURES:
    print(f"{len(FAILURES)} failure(s)")
    sys.exit(1)
print("all passed")
