#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["click>=8.1", "pyyaml>=6", "pytest>=8"]
# ///
"""Tier-1 tests for the REQ-DATA-028 / REQ-CLI-024 `approved` gate (plan-047 Issue 2.5).

**The hole this closes (#125), measured before the fix:** `ready-check` exited **3** and
`update-status <dir> approved` exited **0** on the *same plan*, in two consecutive commands.
`update_status` was a free-form writer by its own docstring, so the intake gate was prose
obedience, not code — nothing downstream of a failing audit could stop a plan reaching
`approved`, no matter what a linter returned.

Run:  uv run skills/yf-plan/scripts/test_update_status_gate.py
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan_manager as pm  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "docs" / "plans" / "plan-047-james-dixson-dec9ff"


def _bundle(tmp_path: Path, *, ready: bool) -> Path:
    d = tmp_path / "plan-047-james-dixson-dec9ff"
    shutil.copytree(SRC, d)
    # Set the status DETERMINISTICALLY, whatever the live bundle currently carries. An
    # earlier version substituted the literal "approved" and so silently did nothing once
    # the real plan moved to `executing` — the fixture was passing for an incidental
    # reason, which is the same defect class this plan exists to close. Caught by the FULL
    # tier, which runs from the repo root rather than from `scripts/`.
    t = re.sub(r"^\*\*Status:\*\* .*$", "**Status:** review", (d / "plan.md").read_text(),
               count=1, flags=re.M)
    t = re.sub(r"^status: .*$", "status: review", t, count=1, flags=re.M)
    (d / "plan.md").write_text(t)
    assert "**Status:** review" in t and "status: review" in t, "fixture did not set status"
    if not ready:
        # Delete the last pass file: the last recorded verdict becomes REVISE AND the
        # count-equality audit fails. Two independent reasons, so the test does not
        # depend on which one `ready-check` reports first.
        for p in sorted(d.glob("reviews/pass-*.md"))[-1:]:
            p.unlink()
    return d


def _status(d: Path) -> str:
    for line in (d / "plan.md").read_text().splitlines():
        if line.startswith("**Status:**"):
            return line.split("**Status:**", 1)[1].strip()
    return ""


@pytest.mark.skipif(not SRC.exists(), reason="plan-047 bundle not present")
def test_approved_is_refused_when_ready_check_is_red(tmp_path):
    d = _bundle(tmp_path, ready=False)
    assert pm._ready_check_result(d)["ready"] is False

    # The postcondition is that the refused call changes NOTHING, so snapshot first.
    # NB: asserting "no `- approved:` bullet exists" would be wrong — this bundle carries
    # a historical one from its real intake, and a test that mistakes pre-existing history
    # for a write is a test that fails on correct code.
    before_plan = (d / "plan.md").read_text()
    before_log = (d / "log.md").read_text()

    r = CliRunner().invoke(pm.cli, ["update-status", str(d), "approved", "-m", "nope"])
    assert r.exit_code == 3, f"expected refusal (3), got {r.exit_code}"
    assert "REQ-DATA-028" in r.output or "REQ-DATA-028" in (r.stderr or "")
    # A refusal that still writes is not a gate.
    assert _status(d) == "review", "status was written despite the refusal"
    assert (d / "plan.md").read_text() == before_plan, "plan.md mutated by a refused call"
    assert (d / "log.md").read_text() == before_log, "log.md mutated by a refused call"


@pytest.mark.skipif(not SRC.exists(), reason="plan-047 bundle not present")
def test_override_flag_writes_and_records_a_deviation(tmp_path):
    d = _bundle(tmp_path, ready=False)
    r = CliRunner().invoke(
        pm.cli,
        ["update-status", str(d), "approved", "-m", "operator approved",
         "--override-ready-check"],
    )
    assert r.exit_code == 0, r.output
    assert _status(d) == "approved"
    log = (d / "log.md").read_text()
    assert "OVERRIDDEN via --override-ready-check" in log, "override not stated in log.md"
    retro = (d / "plan-retrospective.md").read_text()
    assert "--override-ready-check" in retro, "no deviation recorded under the flag name"
    assert "deviation" in retro


@pytest.mark.skipif(not SRC.exists(), reason="plan-047 bundle not present")
def test_a_green_plan_is_unaffected(tmp_path):
    d = _bundle(tmp_path, ready=True)
    assert pm._ready_check_result(d)["ready"] is True
    r = CliRunner().invoke(pm.cli, ["update-status", str(d), "approved", "-m", "ok"])
    assert r.exit_code == 0, r.output
    assert _status(d) == "approved"


@pytest.mark.skipif(not SRC.exists(), reason="plan-047 bundle not present")
def test_the_gate_is_scoped_to_approved_only(tmp_path):
    """Every other status stays free-form.

    Gating all nine would break drafting by construction: a plan in `scoping` has no
    red-team verdict, so a blanket gate would make the first transition unreachable.
    """
    d = _bundle(tmp_path, ready=False)
    for status in ("drafting", "review", "executing", "reconciling", "complete"):
        r = CliRunner().invoke(pm.cli, ["update-status", str(d), status, "-m", "t"])
        assert r.exit_code == 0, f"{status} was gated: {r.output}"
        assert _status(d) == status


def test_the_flag_is_not_named_force():
    """REQ-CLI-024: the name was decided before the implementation (Issue 2.6).

    `--force` already means four different things on four other verbs, and `update-status`
    writes nine statuses — a bare `--force` there would not say what it forces.
    """
    params = {
        o.name
        for cmd in [pm.cli.commands["update-status"]]
        for o in cmd.params
    }
    assert "override_ready_check" in params
    assert "force" not in params, "the override must not be a bare --force"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
