# /// script
# requires-python = ">=3.11"
# dependencies = ["click", "pytest"]
# ///
"""Tests for research_manager.py — record-epic write + idempotency."""
import json

from click.testing import CliRunner

from research_manager import cli


def _write_plan(tmp_path, body):
    (tmp_path / "plan.yaml").write_text(body)
    return tmp_path


def _run(research_dir, epic_id):
    return CliRunner().invoke(cli, ["record-epic", str(research_dir), epic_id])


def test_record_epic_appends_when_absent(tmp_path):
    d = _write_plan(tmp_path, "topic: x\nmode: standard\n")
    res = _run(d, "bd-7")
    assert res.exit_code == 0, res.output
    assert json.loads(res.output) == {"epic_id": "bd-7", "epic_field": "appended"}
    assert (d / "plan.yaml").read_text() == "topic: x\nmode: standard\nepic: bd-7\n"


def test_record_epic_replaces_commented_placeholder(tmp_path):
    body = (
        "topic: x\nmode: standard\n\n"
        "# epic: <id>             # added at pour (Phase 3) — durable resume pointer\n"
    )
    d = _write_plan(tmp_path, body)
    res = _run(d, "bd-42")
    assert res.exit_code == 0, res.output
    assert json.loads(res.output) == {"epic_id": "bd-42", "epic_field": "written"}
    text = (d / "plan.yaml").read_text()
    assert "epic: bd-42" in text
    # placeholder collapsed to exactly one live epic line, no leftover comment
    assert text.count("epic:") == 1
    assert "# epic:" not in text


def test_record_epic_replaces_existing_line(tmp_path):
    d = _write_plan(tmp_path, "topic: x\nepic: bd-1\nmode: standard\n")
    res = _run(d, "bd-2")
    assert res.exit_code == 0, res.output
    text = (d / "plan.yaml").read_text()
    assert "epic: bd-2" in text
    assert "epic: bd-1" not in text
    assert text.count("epic:") == 1


def test_record_epic_idempotent(tmp_path):
    body = "topic: x\nmode: standard\n\n# epic: <id>   # placeholder\n"
    d = _write_plan(tmp_path, body)
    assert _run(d, "bd-9").exit_code == 0
    after_first = (d / "plan.yaml").read_text()
    assert _run(d, "bd-9").exit_code == 0
    after_second = (d / "plan.yaml").read_text()
    assert after_first == after_second  # re-run is a byte-identical no-op


def test_record_epic_missing_plan_yaml_errors(tmp_path):
    res = _run(tmp_path, "bd-1")
    assert res.exit_code == 1
    assert "plan.yaml not found" in res.output
