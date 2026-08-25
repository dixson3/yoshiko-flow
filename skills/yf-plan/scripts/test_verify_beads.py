#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tests for verify_beads (plan-052 Issue 5.2, #197). Pure over fixture rows: no bd, no network."""
from __future__ import annotations

import importlib.util
import pathlib
import sys

_spec = importlib.util.spec_from_file_location(
    "verify_beads", pathlib.Path(__file__).resolve().parent / "verify_beads.py")
vb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vb)

FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(("ok   " if ok else "FAIL ") + label + (f" — {detail}" if not ok and detail else ""))
    if not ok:
        FAILURES.append(label)


PLAN = "plan-996-fixture"


def task(i, **kw):
    r = {"id": f"e.{i}", "title": f"Issue {i}", "issue_type": "task",
         "metadata": {"plan": PLAN, "plan_issue": str(i)}}
    r.update(kw)
    return r


rows = [
    task("1.1"), task("1.2"),
    {"id": "e.9", "title": "Gate: something", "issue_type": "gate",
     "metadata": {"plan": PLAN}},
    {"id": "e.0", "title": "Epic 1", "issue_type": "epic", "metadata": {"plan": PLAN}},
    {"id": "x.1", "title": "other plan", "issue_type": "task",
     "metadata": {"plan": "plan-other", "plan_issue": "1.1"}},
]

t = vb.execution_beads(rows, PLAN)
check("only this plan's TASK beads are targets", sorted(b["id"] for b in t) == ["e.1.1", "e.1.2"],
      str([b["id"] for b in t]))
check("a GATE gets no verify bead — its Test IS its verification",
      not any(b["id"] == "e.9" for b in t))
check("a CONTAINER (epic) gets no verify bead", not any(b["id"] == "e.0" for b in t))
check("another plan's bead is not a target", not any(b["id"] == "x.1" for b in t))

beads = [vb.verify_bead(b, PLAN) for b in t]
check("ONE verify bead per execution bead, never a blanket bead", len(beads) == 2, str(len(beads)))
check("each verify bead names the DISTINCT bead it verifies",
      sorted(b["verifies"] for b in beads) == ["e.1.1", "e.1.2"])
check("each carries plan + plan_issue metadata, so the mapping is reconstructable",
      all(b["metadata"]["plan"] == PLAN and b["metadata"]["plan_issue"] for b in beads))
check("each DEPENDS on the bead it verifies, so it cannot run first",
      all(b["deps"] == [b["verifies"]] for b in beads))
check("each inherits the target's parent, so it lands in the same epic",
      all("parent" in b for b in beads))

# Idempotence: a bead already carrying a verify obligation is not re-targeted, and a verify
# bead is never a target of another verify bead.
rows2 = rows + [
    task("1.3", metadata={"plan": PLAN, "plan_issue": "1.3", "verifies": "e.1.1"}),
    {"id": "e.v", "title": "Verify: Issue 1.1", "issue_type": "task",
     "metadata": {"plan": PLAN}},
]
t2 = vb.execution_beads(rows2, PLAN)
check("a bead already carrying a verify obligation is not re-targeted (idempotent)",
      not any(b["id"] == "e.1.3" for b in t2), str([b["id"] for b in t2]))
check("a verify bead is never itself a target — no obligation recursion",
      not any(b["id"] == "e.v" for b in t2), str([b["id"] for b in t2]))

check("an empty universe yields NO targets, which the caller reports as a real negative",
      vb.execution_beads([], PLAN) == [])

print()
if FAILURES:
    print(f"{len(FAILURES)} failure(s)")
    sys.exit(1)
print("all passed")
