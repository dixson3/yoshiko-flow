#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tier-1 tests for the `cell-vocabulary` check kind (plan-059 Issue 1.6, REQ-DATA-076).

Two claims, and they pull in opposite directions — which is why both are asserted here rather
than left to SC1 and SC1b separately:

  ctl-269-vocab-reports      the check FIRES on an off-vocabulary cell, attributably by name
  ctl-269-vocab-never-fails  the check NEVER FAILS a real historical bundle

The second is the one that is easy to ship broken. The check reads a column that the live
corpus writes with **45 distinct tokens**, so an implementation at `E` — or at `W`, which IS an
`E` at `review`/`ready-for-approval` — would hard-fail essentially every review report ever
written. Shipping at `R` is what makes the pin *visible* rather than a gate nothing can pass,
and an exit code is the only thing that proves it.

This test invokes the VENDORED `skills/yf-plan/scripts/doc_lint.py`, not `_shared/`, per
plan-059's tree rule: every verification of code this plan writes runs from the repo root
against the repo tree, never against `${SKILL_DIR}` (the installed skill, which by AGENTS.md
cannot be redeployed mid-execution and would therefore be a permanent false RED).

Run:  uv run skills/yf-plan/scripts/test_severity_vocabulary.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parent.parent.parent
LINT = SCRIPTS / "doc_lint.py"
FIXTURE = REPO / "skills/yf-plan/fixtures/severity-vocabulary/off-vocabulary-med.md"
HISTORICAL = REPO / "docs/plans/plan-027-james-dixson-a59656/reviews/pass-1.md"
SPEC = REPO / "skills/yf-plan/spec/data.md"

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def lint(path: Path) -> tuple[int, dict]:
    r = subprocess.run(
        ["uv", "run", str(LINT), "--type", "review", "--path", str(path), "--json"],
        capture_output=True, text=True, cwd=REPO,
    )
    try:
        return r.returncode, json.loads(r.stdout)
    except json.JSONDecodeError:
        return r.returncode, {"_stdout": r.stdout, "_stderr": r.stderr}


def vocab_findings(res: dict) -> list[dict]:
    return [f for f in res.get("findings", []) if f.get("check") == "cell-vocabulary"]


# ---- the ratified set is DECLARED, not hard-coded -------------------------------------
marker = "Ratified severity vocabulary: "
spec_line = next((l for l in SPEC.read_text().splitlines() if l.startswith(marker)), None)
check("ctl-269-vocab-marker: the ratified set is written at line start in spec/data.md",
      spec_line is not None,
      f"no line beginning {marker!r} in {SPEC} — the check has no declared set to read")
ratified = {t.strip() for t in (spec_line or "").removeprefix(marker).split("|") if t.strip()}
check("ctl-269-vocab-marker: the ratified set is exactly the operator's option (b)",
      ratified == {"high", "medium", "low", "medium-high", "low-medium"},
      f"got {sorted(ratified)} — option (c)'s qualifier suffix was DECLINED at the Start Gate")

# ---- ARM 1: the check REPORTS -----------------------------------------------------------
rc, res = lint(FIXTURE)
found = vocab_findings(res)
check("ctl-269-vocab-reports: the check fires on the off-vocabulary fixture",
      len(found) >= 1,
      f"expected >= 1 cell-vocabulary finding, got {len(found)}: {res}")
check("ctl-269-vocab-reports: it fires on `med` AND on the declined qualifier suffix",
      any("'med'" in f.get("detail", "") for f in found)
      and any("medium (blocking)" in f.get("detail", "") for f in found),
      f"details: {[f.get('detail') for f in found]}")
check("ctl-269-vocab-reports: it stays SILENT on the two conforming rows",
      len(found) == 2,
      f"expected exactly 2 findings (C3, C4); `high` and `medium-high` must not fire. got "
      f"{[f.get('detail') for f in found]}")
check("ctl-269-vocab-reports: the fixture carries NO OTHER finding",
      len(res.get("findings", [])) == 2,
      "an unrelated finding would turn SC1 red for a reason that is not the check under test")

# ---- ARM 2: the check NEVER FAILS a historical bundle ------------------------------------
hrc, hres = lint(HISTORICAL)
hfound = vocab_findings(hres)
check("ctl-269-vocab-never-fails: the historical bundle really does contain off-vocabulary cells",
      len(hfound) >= 1,
      "if it contained none, 'never fails' would be vacuously true and this arm proves nothing")
check("ctl-269-vocab-never-fails: every cell-vocabulary finding ships at `R`",
      all(f.get("severity") == "R" for f in hfound),
      f"severities: {[f.get('severity') for f in hfound]} — a `W` IS an `E` at `review`")
check("ctl-269-vocab-never-fails: the historical bundle reports ZERO errors",
      hres.get("errors") == 0,
      f"errors={hres.get('errors')} — an `E` here would fail every review report ever written")
check("ctl-269-vocab-never-fails: and the linter EXITS 0 on it",
      hrc == 0,
      f"exit {hrc} — the printed severities are not the contract; the exit code is")

# ---- the two arms must be DISTINGUISHABLE ----------------------------------------------
# A check that reported nothing anywhere would satisfy arm 2 trivially. A check at `E` would
# satisfy arm 1 and break arm 2. Only the shipped shape satisfies both.
check("the reporting arm and the never-fails arm are BOTH non-vacuous",
      len(found) >= 1 and len(hfound) >= 1 and hres.get("errors") == 0,
      "a silent check passes arm 2 for the wrong reason; an `E` check fails arm 2 outright")

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
