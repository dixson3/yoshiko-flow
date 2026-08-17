# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
#     "pyyaml>=6",
# ]
# ///
"""Tier-1 unit tests for `update-status` idempotence (REQ-DATA-017, plan-043 Issue 3.2).

Run from anywhere:  uv run skills/yf-plan/scripts/test_update_status_idempotent.py

Re-running §6.4 is a DOCUMENTED recovery path — every halting step's fail-loud banner ends
with "resolve … then re-run §6.4". So duplicate `- complete:` bullets were produced by the
normal remediation flow, not by misuse. They are not cosmetic: `log.md` bullets are what the
status, review-count (REQ-PORT-006) and grandfather-date parsers read.

Covers (tagged REQ-DATA-017):
  (a) SC7 — running §6.4 twice leaves exactly ONE `- complete:` bullet;
  (b) the guard is narrow: a different message, or a later date, still appends;
  (c) the review-count and grandfather-date parsers are unperturbed;
  (d) the verdict reports whether it appended or deduped.
"""
from __future__ import annotations

import importlib.util
import json
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

PLAN_ID = "plan-995-idem-tester-abc123"


@pytest.fixture
def plan_dir(tmp_path) -> Path:
    pdir = tmp_path / PLAN_ID
    pdir.mkdir()
    (pdir / "plan.md").write_text(
        f"---\ntype: Plan\nid: {PLAN_ID}\nstatus: reconciling\n---\n"
        f"# Plan: t\n\n**ID:** {PLAN_ID}\n**Status:** reconciling\n\n"
        "## Objective\n\nt\n",
        encoding="utf-8",
    )
    (pdir / "log.md").write_text(
        "# Log\n\n## 2026-01-01\n\n- scoping: initial scope captured\n", encoding="utf-8")
    return pdir


def _update(pdir: Path, status: str, msg: str) -> dict:
    res = CliRunner().invoke(pm.cli, ["update-status", str(pdir), status, "-m", msg])
    assert res.exit_code == 0, res.output
    return json.loads(res.output)


def _bullets(pdir: Path, token: str) -> list[str]:
    return [l for l in (pdir / "log.md").read_text(encoding="utf-8").splitlines()
            if l.strip().startswith(f"- {token}:")]


# ---------------------------------------------------------------------------
# (a) SC7
# ---------------------------------------------------------------------------

def test_running_close_twice_leaves_one_complete_bullet(plan_dir):
    """SC7 — the documented 'resolve and re-run §6.4' recovery must not duplicate."""
    first = _update(plan_dir, "complete", "plan complete")
    second = _update(plan_dir, "complete", "plan complete")
    assert len(_bullets(plan_dir, "complete")) == 1, (
        "re-running §6.4 duplicated the `- complete:` bullet"
    )
    assert first["appended"] is True and first["deduped"] is False
    assert second["appended"] is False and second["deduped"] is True


def test_many_reruns_still_leave_one(plan_dir):
    for _ in range(5):
        _update(plan_dir, "complete", "plan complete")
    assert len(_bullets(plan_dir, "complete")) == 1


def test_status_field_is_still_written_on_a_deduped_run(plan_dir):
    """Dedupe suppresses the LOG APPEND only — the status dual-write still happens,
    so a re-run cannot leave the field and the log disagreeing."""
    _update(plan_dir, "complete", "plan complete")
    (plan_dir / "plan.md").write_text(
        (plan_dir / "plan.md").read_text().replace("status: complete", "status: reconciling")
                                          .replace("**Status:** complete", "**Status:** reconciling"),
        encoding="utf-8")
    _update(plan_dir, "complete", "plan complete")
    text = (plan_dir / "plan.md").read_text(encoding="utf-8")
    assert "status: complete" in text and "**Status:** complete" in text
    assert len(_bullets(plan_dir, "complete")) == 1


# ---------------------------------------------------------------------------
# (b) the guard is narrow — it suppresses re-emission, not history
# ---------------------------------------------------------------------------

def test_a_different_message_still_appends(plan_dir):
    _update(plan_dir, "complete", "plan complete")
    _update(plan_dir, "complete", "plan complete (after remediation)")
    assert len(_bullets(plan_dir, "complete")) == 2, (
        "a genuinely different message was suppressed — the guard is too broad"
    )


def test_a_different_status_still_appends(plan_dir):
    _update(plan_dir, "reconciling", "post-execution reconciliation")
    _update(plan_dir, "complete", "plan complete")
    assert len(_bullets(plan_dir, "reconciling")) == 1
    assert len(_bullets(plan_dir, "complete")) == 1


def test_a_later_date_still_appends(plan_dir, monkeypatch):
    """The same status on a later date is real history, not a re-emission."""
    _update(plan_dir, "complete", "plan complete")

    real = pm.datetime

    class _Later(real):
        @classmethod
        def now(cls, *a, **k):
            return real(2099, 1, 1)

    monkeypatch.setattr(pm, "datetime", _Later)
    _update(plan_dir, "complete", "plan complete")
    assert len(_bullets(plan_dir, "complete")) == 2, (
        "the same status on a later date was suppressed — the guard is date-blind"
    )


# ---------------------------------------------------------------------------
# (c) the parsers that read log.md are unperturbed
# ---------------------------------------------------------------------------

def test_review_count_and_grandfather_parsers_unperturbed(plan_dir):
    before_reviews = pm._plan_review_line_count(plan_dir)
    before_scoping = pm._plan_first_scoping_date(plan_dir)
    for _ in range(3):
        _update(plan_dir, "complete", "plan complete")
    assert pm._plan_review_line_count(plan_dir) == before_reviews
    assert pm._plan_first_scoping_date(plan_dir) == before_scoping, (
        "the grandfather-date parser's `scoping:` anchor was disturbed"
    )


def test_dedupe_does_not_drop_scoping_entries(plan_dir):
    """E3's ordering constraint: a close-time `log.md` write that drops `scoping:`
    entries silently promotes audit warns to fails."""
    for _ in range(3):
        _update(plan_dir, "complete", "plan complete")
    assert len(_bullets(plan_dir, "scoping")) == 1


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
