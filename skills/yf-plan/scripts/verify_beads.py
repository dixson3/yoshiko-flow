#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Injection-time verify beads for `plan-execute` (plan-052 Issue 5.2, #197).

**WHY A SECOND MECHANISM EXISTS AT ALL.** An aspect composes over a formula's DECLARED steps.
`plan-execute` declares exactly ONE (the start gate) and its real DAG is built by
`plan_manager`/SKILL.md §5.2a from `plan.md` — so there is nothing for an aspect to weave
over. This is not the same mechanism applied twice; it is a different mechanism for a
structurally different formula, and the premise is CHECKED rather than assumed: `--formula`
is read and a formula declaring more than one step is reported as INCONCLUSIVE, because at
that point the aspect route applies and this one should not be used.

**ONE VERIFY BEAD PER EXECUTION BEAD, never a blanket bead.** A single "verify everything"
bead satisfies a count check while verifying nothing in particular — the silent-green class
in its obligation form.

**GATES GET NONE.** A gate is not an execution bead: it produces no artifact, and its
`Test:` is already its verification. Attaching a verify bead to one would manufacture an
obligation with nothing to discharge it.

Exit: 0 emitted · 1 nothing to emit against (a real negative) · 2 the instrument could not run.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

INCONCLUSIVE = 2
TARGET_FORMULA = "plan-execute"


def load_rows(fixture: str | None, plan: str) -> list[dict]:
    """Bead rows from a PINNED fixture, or from live `bd`.

    A fixture is what makes this testable at all: without one, every control over this
    emitter would run against live machine state and could not be made RED on demand. An
    ABSENT fixture is exit 1 (a real negative); a MALFORMED one is exit 2 (the instrument).
    """
    if fixture:
        f = pathlib.Path(fixture)
        if not f.exists():
            print(f"FAIL: fixture not found: {fixture}", file=sys.stderr)
            raise SystemExit(1)
        try:
            rows = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"INCONCLUSIVE: fixture unreadable or malformed: {e}", file=sys.stderr)
            raise SystemExit(INCONCLUSIVE)
        if not isinstance(rows, list):
            print("INCONCLUSIVE: fixture must be a JSON array of bead rows", file=sys.stderr)
            raise SystemExit(INCONCLUSIVE)
        return rows
    try:
        proc = subprocess.run(["bd", "list", "--all", "--include-gates", "--limit", "5000",
                               "--json"], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        print(f"INCONCLUSIVE: could not read bd: {e}", file=sys.stderr)
        raise SystemExit(INCONCLUSIVE)
    if proc.returncode != 0:
        print(f"INCONCLUSIVE: bd list failed: {proc.stderr[:200]}", file=sys.stderr)
        raise SystemExit(INCONCLUSIVE)
    try:
        rows = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        print(f"INCONCLUSIVE: bd output is not JSON: {e}", file=sys.stderr)
        raise SystemExit(INCONCLUSIVE)
    return rows if isinstance(rows, list) else []


def formula_step_count(name: str) -> int | None:
    """Declared step count for `name`, or None when it cannot be read."""
    try:
        proc = subprocess.run(["bd", "formula", "show", name, "--json"],
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    try:
        return len(json.loads(proc.stdout).get("steps") or [])
    except (json.JSONDecodeError, AttributeError):
        return None


def execution_beads(rows: list[dict], plan: str) -> list[dict]:
    """The beads a verify obligation attaches to: this plan's non-gate TASKS.

    Excludes gates (their `Test:` is their verification), containers (epics/molecules verify
    nothing themselves), and any bead already carrying a verify obligation — so re-running is
    idempotent rather than emitting a second copy.
    """
    out = []
    for r in rows:
        md = r.get("metadata") or {}
        if str(md.get("plan") or "") != plan:
            continue
        if r.get("issue_type") != "task":
            continue
        if str(r.get("title") or "").startswith("Verify:"):
            continue
        if md.get("verifies"):
            continue
        out.append(r)
    return out


def verify_bead(b: dict, plan: str) -> dict:
    md = b.get("metadata") or {}
    iid = str(md.get("plan_issue") or b.get("id"))
    return {
        "title": f"Verify: {b.get('title') or b.get('id')}",
        "verifies": b.get("id"),
        "plan_issue": iid,
        "type": "task",
        "parent": b.get("parent"),
        "deps": [b.get("id")],
        "metadata": {"plan": plan, "plan_issue": iid, "verifies": b.get("id")},
        "description": (
            f"Assert that issue {iid} produced the artifacts it declares, and that they are "
            f"present on the tree — not merely that the work was reported done. Emitted at "
            f"INJECTION time because `{TARGET_FORMULA}` declares one step and cannot be woven."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", required=True, help="plan id, as carried in bead metadata.plan")
    ap.add_argument("--fixture", metavar="PATH", help="pinned JSON bead snapshot")
    ap.add_argument("--formula", default=TARGET_FORMULA,
                    help="the formula this emission stands in for")
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()

    # CHECK THE PREMISE. A formula with more than one declared step CAN be woven, and the
    # aspect route should be used instead — silently emitting here would give it two
    # mechanisms and double obligations.
    n = formula_step_count(a.formula)
    if n is not None and n > 1:
        print(json.dumps({
            "verdict": "INCONCLUSIVE", "formula": a.formula, "declared_steps": n,
            "verify_beads": [],
            "reason": (f"{a.formula} declares {n} steps, so it CAN be woven by an aspect — "
                       f"injection-time emission is the mechanism for a formula that cannot. "
                       f"Use the aspect route."),
        }, indent=1))
        return INCONCLUSIVE

    rows = load_rows(a.fixture, a.plan)
    targets = execution_beads(rows, a.plan)
    beads = [verify_bead(b, a.plan) for b in targets]

    out = {
        "formula": a.formula,
        "declared_steps": n,
        "plan": a.plan,
        "verdict": "PASS" if beads else "FAIL",
        "verify_beads": beads,
        "reason": (f"{len(beads)} verify bead(s) for {len(targets)} execution bead(s)"
                   if beads else
                   f"no execution bead found for plan {a.plan!r} — nothing to verify, which "
                   f"is a real negative rather than a clean run"),
    }
    print(json.dumps(out, indent=1))
    return 0 if beads else 1


if __name__ == "__main__":
    raise SystemExit(main())
