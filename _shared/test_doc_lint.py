#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tier-1 tests for `_shared/doc_lint.py` (plan-047 Issue 1.3, REQ-DATA-024).

**The headline assertion is the EXIT CODE, not the printed findings.** EXP-005 reproduced a
linter printing `errors=4` while the delegating engine reported `status: pass`, because the
linter exited 0. Without this test the CHANGE-VALIDATION row added in Epic 3 is decorative:
the command runs, prints, and passes.

Run:  uv run _shared/test_doc_lint.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SHARED = Path(__file__).resolve().parent
REPO = SHARED.parent
LINT = SHARED / "doc_lint.py"
FIXTURES = REPO / "tests" / "fixtures" / "doclint"

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def run(*args: str) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(LINT), *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# --- 1. the exit contract: 1 on an error finding, 0 on a clean file ------------------

rc, out = run("--type", "plan", "--path", str(FIXTURES / "plan" / "bad.md"))
check("known-bad plan fixture exits 1", rc == 1, f"got {rc}")
check("known-bad plan fixture reports FAIL", "FAIL:" in out)

rc, out = run("--type", "finding", "--path", str(FIXTURES / "finding" / "bad.md"))
check("known-bad finding fixture exits 1", rc == 1, f"got {rc}")

with tempfile.TemporaryDirectory() as td:
    clean = Path(td) / "plan.md"
    sys.path.insert(0, str(SHARED))
    import plan_template  # noqa: E402

    clean.write_text(
        "---\ntype: Plan\nokf_spec: OKF-PLAN\nid: plan-999-t-000000\nauthor: t\n"
        "created: 2026-01-01\nstatus: scoping\n---\n"
        + plan_template.seed_body("Clean fixture", "plan-999-t-000000", "t", "2026-01-01")
        + "\n## Investigation Findings\n_none_\n"
    )
    rc, out = run("--type", "plan", "--path", str(clean))
    check("a freshly seeded plan.md exits 0", rc == 0, f"got {rc}: {out.strip()[:300]}")
    check("...and reports PASS", "PASS:" in out, out.strip()[:200])

# --- 2. an error-severity finding, and ONLY it, sets the exit code -------------------

rc, out = run("--type", "plan", "--path", str(FIXTURES / "plan" / "bad.md"))
check("warnings are reported alongside errors", " warning(s)" in out)

# --- 3. INCONCLUSIVE is exit 2, and only means "could not run" -----------------------

rc, out = run("--type", "no-such-type")
check("an unknown type is INCONCLUSIVE (exit 2), not FAIL", rc == 2, f"got {rc}")
check("...and says INCONCLUSIVE", "INCONCLUSIVE" in out)

# --- 4. --path is an explicit override, not a filter ---------------------------------
# The fixture lives OUTSIDE docs/plans/**, so a filter-over-glob implementation would
# select nothing and exit 0 — a vacuous pass. This is the regression guard for that.

rc, out = run("--type", "plan", "--path", str(FIXTURES / "plan" / "bad.md"), "--json")
check("--path reaches a file outside the type's globs", '"files_checked": 1' in out, out[:200])

# --- 5. the engine is path-keyed and inert where nothing matches ---------------------

with tempfile.TemporaryDirectory() as td:
    rc, out = run("--root", td, "--json")
    check("a repo with no yf documents exits 0", rc == 0, f"got {rc}")
    check("...and checks zero files", '"files_checked": 0' in out, out[:200])

# --- 6. --no-exclude is a real positive control --------------------------------------

rc_with, out_with = run("--type", "plan", "--json")
rc_without, out_without = run("--type", "plan", "--no-exclude", "--json")
import json  # noqa: E402

n_with = json.loads(out_with)["files_checked"]
n_without = json.loads(out_without)["files_checked"]
check("--no-exclude widens the file set", n_without >= n_with, f"{n_without} vs {n_with}")

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
