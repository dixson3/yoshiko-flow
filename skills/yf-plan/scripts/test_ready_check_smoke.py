# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
#     "click>=8",
#     "pyyaml>=6",
# ]
# ///
"""REQ-PLAN-085 (a), EXECUTED: `ready-check` smoke-runs what it approves (plan-071 Issue 2.4).

Run from anywhere:  uv run skills/yf-plan/scripts/test_ready_check_smoke.py

One passing fixture and the failing fixtures the requirement enumerates: a prose cell, a
`command not found`, an argparse usage error, a `No such file` on an UNDECLARED path (fails)
versus on a path the plan's `## Epics` text names (allowed, `not-yet-dischargeable`), and the
#356/#364 false-pass polarity (GREEN while a named input is missing). Each failing fixture
must fail WITH THE ROW ID in the reason, or the operator is told "not ready" and nothing else.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

_HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pm = _load("plan_manager", "plan_manager.py")
PLAN_ID = "plan-996-tester-smoke1"

_PLAN = """---
type: Plan
okf_spec: OKF-PLAN
id: {pid}
status: review
---
# Plan: smoke

**ID:** {pid}
**Status:** review

## Objective
t

## Epics
### Epic 1: e
- Issue 1.1: create `scripts/checks/declared-deliverable.py` and `findings/declared.md`

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
{rows}
"""


@pytest.fixture
def audit_passes(monkeypatch):
    monkeypatch.setattr(pm, "_audit_plan", lambda _pd: {"status": "pass", "findings": []})


def _bundle(tmp_path: Path, rows: str) -> Path:
    pd = tmp_path / "docs" / "plans" / PLAN_ID
    (pd / "reviews").mkdir(parents=True)
    (pd / "plan.md").write_text(_PLAN.format(pid=PLAN_ID, rows=rows), encoding="utf-8")
    (pd / "reviews" / "pass-1.md").write_text("# r\n\n## Verdict: APPROVE\n**Mode:** reading\n")
    return pd


def _ready(pd: Path) -> tuple[dict, int]:
    res = CliRunner().invoke(pm.cli, ["ready-check", str(pd), "--json"])
    assert res.output.strip(), f"no output; exception={res.exception!r}"
    return json.loads(res.output), res.exit_code


# --- the passing fixture -------------------------------------------------------------------

def test_clause_form_plan_is_ready_and_every_row_is_reported(tmp_path, audit_passes):
    pd = _bundle(tmp_path,
                 "| SC1 | a | `true` → exit 0 | 1.1 |\n"
                 "| SC2 | b | `false` → exit 1 | 1.1 |\n"
                 "| SC3 | c | manual: cannot be mechanized | 1.1 |")
    out, code = _ready(pd)
    assert code == 0, out
    assert out["ready"] is True
    by = {r["id"]: r for r in out["criteria"]["rows"]}
    assert by["SC1"]["status"] == "ran" and by["SC1"]["actual_exit"] == 0
    assert by["SC2"]["status"] == "ran" and by["SC2"]["holds_now"] is True
    assert by["SC3"]["status"] == "manual"
    assert out["criteria"]["checked"] == 3
    assert out["stale_approved"] is False
    assert out["gate_consistency"]["verdict"] in ("PASS", "INCONCLUSIVE")


# --- the failing fixtures, each naming its row ----------------------------------------------

def test_prose_cell_is_refused_by_row_id(tmp_path, audit_passes):
    pd = _bundle(tmp_path, "| SC1 | a | the operator eyeballs it | 1.1 |")
    out, code = _ready(pd)
    assert code == 3 and out["ready"] is False
    assert any(r.startswith("criterion SC1: prose") for r in out["reasons"]), out["reasons"]


def test_command_not_found_is_refused_by_row_id(tmp_path, audit_passes):
    pd = _bundle(tmp_path, "| SC1 | a | `definitely-not-a-command-xyz --flag` → exit 0 | 1.1 |")
    out, code = _ready(pd)
    assert code == 3
    reason = next((r for r in out["reasons"] if r.startswith("criterion SC1:")), "")
    assert "unrunnable" in reason and "127" in reason, out["reasons"]


def test_argparse_usage_error_is_refused_by_row_id(tmp_path, audit_passes):
    cmd = "python3 -c 'import argparse; argparse.ArgumentParser().parse_args([\"--bogus\"])'"
    # The usage error exits 2 — which `→ exit 2` would otherwise read as a legitimate
    # INCONCLUSIVE. The stderr signature is what catches it, not the exit code.
    pd = _bundle(tmp_path, f"| SC1 | a | `{cmd}` → exit 2 | 1.1 |")
    out, code = _ready(pd)
    assert code == 3
    reason = next((r for r in out["reasons"] if r.startswith("criterion SC1:")), "")
    assert "unrunnable" in reason and ("usage:" in reason or "unrecognized arguments" in reason), \
        out["reasons"]


def test_no_such_file_on_an_undeclared_path_is_refused(tmp_path, audit_passes):
    pd = _bundle(tmp_path, "| SC1 | a | `cat scripts/checks/never-declared.py` → exit 0 | 1.1 |")
    out, code = _ready(pd)
    assert code == 3
    reason = next((r for r in out["reasons"] if r.startswith("criterion SC1:")), "")
    assert "no-such-file" in reason, out["reasons"]


def test_no_such_file_on_a_declared_deliverable_is_allowed(tmp_path, audit_passes):
    """The allow-list is DERIVED from the plan's `## Epics` text via plan_extract — Issue 1.1
    above names `scripts/checks/declared-deliverable.py`, so a criterion that needs it before
    it exists is `not-yet-dischargeable`, not a readiness failure."""
    pd = _bundle(tmp_path,
                 "| SC1 | a | `cat scripts/checks/declared-deliverable.py` → exit 0 | 1.1 |")
    out, code = _ready(pd)
    assert code == 0, out["reasons"]
    row = next(r for r in out["criteria"]["rows"] if r["id"] == "SC1")
    assert row["status"] == "not-yet-dischargeable"


def test_green_while_missing_input_is_the_false_pass_polarity(tmp_path, audit_passes):
    """#356 / #364: a negated assertion over a missing collection passes on NOTHING."""
    pd = _bundle(tmp_path,
                 "| SC1 | a | `! grep -q needle scripts/checks/never-declared.py` → exit 0 | 1.1 |")
    out, code = _ready(pd)
    assert code == 3
    reason = next((r for r in out["reasons"] if r.startswith("criterion SC1:")), "")
    assert "empty-collection-suspect" in reason, out["reasons"]


def test_stale_approved_is_surfaced(tmp_path, audit_passes):
    pd = _bundle(tmp_path, "| SC1 | a | `true` → exit 0 | 1.1 |")
    text = (pd / "plan.md").read_text(encoding="utf-8")
    (pd / "plan.md").write_text(text.replace("status: review\n", "status: review\nfingerprint: deadbeef\n"),
                                encoding="utf-8")
    out, _ = _ready(pd)
    assert out["stale_approved"] is True


def test_gate_consistency_fail_blocks_readiness(tmp_path, audit_passes, monkeypatch):
    pd = _bundle(tmp_path, "| SC1 | a | `true` → exit 0 | 1.1 |")
    monkeypatch.setattr(pm, "_ready_gate_consistency",
                        lambda _p: {"verdict": "FAIL", "exit": 1, "findings": ["x"]})
    out, code = _ready(pd)
    assert code == 3 and any("gate_consistency FAIL" in r for r in out["reasons"])


def test_gate_consistency_inconclusive_is_reported_not_blocking(tmp_path, audit_passes,
                                                                 monkeypatch):
    pd = _bundle(tmp_path, "| SC1 | a | `true` → exit 0 | 1.1 |")
    monkeypatch.setattr(pm, "_ready_gate_consistency",
                        lambda _p: {"verdict": "INCONCLUSIVE", "exit": 2, "findings": []})
    out, code = _ready(pd)
    assert code == 0 and out["gate_consistency"]["verdict"] == "INCONCLUSIVE"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
