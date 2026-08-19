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

import json
import re
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
n_with = json.loads(out_with)["files_checked"]
n_without = json.loads(out_without)["files_checked"]
check("--no-exclude widens the file set", n_without >= n_with, f"{n_without} vs {n_with}")


# --- 7. CARVE-OUTS: the positive control must actually fire (plan-047 Issue 2.2-2.4) ------
# `control_fired: false` was originally the RIGHT answer for the WRONG reason: finding.toml's
# `paths` glob was single-level, so the 45 nested okf-migration-samples files were never
# selected and the carve-out under test was never exercised. A control that cannot fire is
# the same defect class as a gate that cannot fail.

CARVED = re.compile(r"(findings/okf-migration-samples/|/fixtures/|/references/)")

rc, out = run("--json")
on = json.loads(out)
rc, out = run("--no-exclude", "--json")
off = json.loads(out)

carved_on = [f for f in on["findings"] if CARVED.search(f["path"])]
carved_off = [f for f in off["findings"] if CARVED.search(f["path"])]

check("zero findings inside the carved regions with excludes ON",
      len(carved_on) == 0, f"{len(carved_on)}: {[f['path'] for f in carved_on][:3]}")
check("the positive control FIRES with excludes off",
      len(carved_off) > 0, "control cannot fire — the carve-out is untested")
check("...and the control widens the file set",
      off["files_checked"] > on["files_checked"],
      f'{off["files_checked"]} vs {on["files_checked"]}')

# The specific region that the single-level glob could not reach.
nested_off = [f for f in off["findings"] if "okf-migration-samples/" in f["path"]]
check("the control reaches the NESTED okf-migration-samples corpus",
      len(nested_off) > 0,
      "a single-level `findings/*.md` glob reaches 0 of these — the vacuity regression")

# --- 8. glob DEPTH regression, by fixture -------------------------------------------------
# tests/fixtures/doclint/nested-reach/deeper/bad.md is one level deeper than a `*/findings/*.md`
# glob can reach. Reverting finding.toml to the single-level form must fail this.

sys.path.insert(0, str(SHARED))
import tomllib  # noqa: E402

ft = tomllib.load((SHARED / "document_types" / "finding.toml").open("rb"))
check("finding.toml globs are RECURSIVE",
      all("**" in g for g in ft["paths"]),
      f'non-recursive glob present: {ft["paths"]}')

nested = REPO / "tests" / "fixtures" / "doclint" / "nested-reach" / "deeper" / "bad.md"
rc, out = run("--type", "finding", "--path", str(nested))
check("a nested malformed finding is caught (exit 1)", rc == 1, f"got {rc}")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    deep = root / "docs" / "plans" / "plan-000-x" / "findings" / "sub" / "bad.md"
    deep.parent.mkdir(parents=True)
    deep.write_text(nested.read_text())
    rc, out = run("--type", "finding", "--root", str(root), "--json")
    n = json.loads(out)["files_checked"]
    check("a recursive glob SELECTS a nested findings/ file a single-level glob misses",
          n == 1, f"selected {n} — reverting finding.toml to `findings/*.md` makes this 0")

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
