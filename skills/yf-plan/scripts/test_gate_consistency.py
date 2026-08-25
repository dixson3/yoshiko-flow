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

print()
if FAILURES:
    print(f"{len(FAILURES)} failure(s)")
    sys.exit(1)
print("all passed")
