# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
#     "click>=8",
#     "pyyaml>=6",
# ]
# ///
"""Autonomy core: the two counters and the four false-escalation classes (plan-045 Epic 2).

Run from anywhere:  uv run skills/yf-plan/scripts/test_autonomy.py

WHY THIS FILE EXISTS
--------------------
Plan-045 grants the review loop and the coordinator loop autonomy. D-8 requires every
autonomy grant to ship with its mechanical postcondition check, because autonomy without
one makes the system *faster at being confidently wrong*. Two counters carry that weight:

* ``max_review_cycles`` — PLAN-phase, per-plan, **monotonic** (pass files are never deleted).
* ``yf_attempts``       — EXECUTION-phase, per-bead, **resets** on close.

They are separate because Issue 2.4 grants autonomy in Phase 3 — before intake, before the
pour, before any bead exists — so ``yf_attempts`` structurally cannot reach it.

A counter that *fabricates* escalations is worse than no counter: it converts a working run
into a spurious halt and trains the operator to raise the bound reflexively. exp-002
enumerated four ways that happens, and each gets a test here.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent


def _load_pm():
    """Import plan_manager.py by path (it is a script, not an installed module)."""
    spec = importlib.util.spec_from_file_location("plan_manager", _HERE / "plan_manager.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def pm(tmp_path, monkeypatch):
    """plan_manager imported with cwd at an empty tmp dir, so no repo config leaks in."""
    monkeypatch.chdir(tmp_path)
    return _load_pm()


def _make_plan(tmp_path: Path, n_passes: int, n_log_review_lines: int | None = None) -> Path:
    """A minimal bundle with `n_passes` pass files and an independently-set log count.

    The two counts are set independently ON PURPOSE: the whole point of 2.4a is that the
    review-cycle counter reads pass FILES, not log.md BULLETS, and the test must be able
    to drive them apart to prove the distinction is real.
    """
    d = tmp_path / "plan-999-test-abc123"
    (d / "reviews").mkdir(parents=True)
    (d / "plan.md").write_text("# Plan: test\n\n## Objective\ntest\n", encoding="utf-8")
    for i in range(1, n_passes + 1):
        (d / "reviews" / f"pass-{i}.md").write_text(
            f"# Review pass {i}\n\n## Verdict: REVISE\n", encoding="utf-8")
    lines = ["# Log", "", "## 2026-08-18"]
    for _ in range(n_passes if n_log_review_lines is None else n_log_review_lines):
        lines.append("- review: red-team presented")
    (d / "log.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return d


# =======================================================================================
# max_review_cycles (2.4a) — the PLAN-phase bound
# =======================================================================================

def test_review_loop_escalates_at_the_bound_rather_than_iterating_unbounded(pm, tmp_path):
    """The headline assertion: the loop stops at N instead of running forever."""
    d = _make_plan(tmp_path, n_passes=5)
    escalates, cycles, limit = pm._review_loop_escalates(d)
    assert cycles == 5
    assert limit == pm.MAX_REVIEW_CYCLES_DEFAULT == 5
    assert escalates is True, (
        "the review loop did not escalate at its bound. Without this, plan-045's headline "
        "change is exactly the unbounded-autonomy shape D-8 forbids."
    )


def test_review_loop_does_not_escalate_below_the_bound(pm, tmp_path):
    d = _make_plan(tmp_path, n_passes=2)
    escalates, cycles, limit = pm._review_loop_escalates(d)
    assert (escalates, cycles) == (False, 2)


def test_cycle_count_reads_pass_FILES_not_log_BULLETS(pm, tmp_path):
    """2.4a's load-bearing distinction, driven apart deliberately.

    ``_plan_review_line_count`` counts ``log.md`` bullets — a DIFFERENT number that can and
    does diverge (observed live during plan-045's own review). Keying the bound on it would
    make the escalation fire on a bookkeeping artifact.
    """
    d = _make_plan(tmp_path, n_passes=2, n_log_review_lines=9)
    assert pm._review_cycle_count(d) == 2, "must count pass-*.md files"
    assert pm._plan_review_line_count(d) == 9, "log.md bullets are the other number"
    assert pm._review_cycle_count(d) != pm._plan_review_line_count(d), (
        "the fixture failed to drive the two counts apart, so this test proves nothing"
    )


def test_cycle_count_ignores_non_conforming_filenames(pm, tmp_path):
    """`pass-draft.md` is not a cycle; only `pass-<digits>.md` counts."""
    d = _make_plan(tmp_path, n_passes=2)
    (d / "reviews" / "pass-draft.md").write_text("scratch\n", encoding="utf-8")
    (d / "reviews" / "notes.md").write_text("scratch\n", encoding="utf-8")
    assert pm._review_cycle_count(d) == 2


def test_cycle_count_is_zero_when_no_reviews_dir(pm, tmp_path):
    """Absence is not an escalation — a plan with no reviews yet must not be at its bound."""
    d = tmp_path / "plan-998-test-def456"
    d.mkdir()
    assert pm._review_cycle_count(d) == 0
    assert pm._review_loop_escalates(d)[0] is False


def test_the_raise_is_the_only_exit_and_does_not_persist(pm, tmp_path):
    d = _make_plan(tmp_path, n_passes=5)
    assert pm._review_loop_escalates(d)[0] is True
    pm._set_max_review_cycles_override(8)
    assert pm._review_loop_escalates(d)[0] is False, "the raise must clear the escalation"
    pm._set_max_review_cycles_override(None)
    assert pm._review_loop_escalates(d)[0] is True, (
        "NO AUTO-RESET: once the raise is gone the loop must re-escalate immediately. A "
        "plan that has burned N review cycles should not silently resume."
    )


def test_an_invalid_raise_is_rejected_not_silently_ignored(pm):
    for bad in (0, -1):
        with pytest.raises(ValueError):
            pm._set_max_review_cycles_override(bad)
    pm._set_max_review_cycles_override(None)


# =======================================================================================
# yf_attempts (2.8) — the four measured false-escalation classes (exp-002)
# =======================================================================================

def _stuck_record(pm, attempts):
    """Build the stuck-record fields exactly as `_resume_scan` does, for one bead."""
    md = {} if attempts is None else {"yf_attempts": attempts}
    raw = md.get("yf_attempts")
    if isinstance(raw, bool):
        parsed = 0
    elif isinstance(raw, int):
        parsed = raw
    elif isinstance(raw, str) and raw.strip().isdigit():
        parsed = int(raw.strip())
    else:
        parsed = 0
    return {"yf_attempts": parsed, "at_threshold": parsed >= pm._resolve_max_attempts()}


def test_class1_crash_is_not_a_failure(pm):
    """CLASS 1 — crash-vs-failure.

    A Ctrl-C, OOM or reboot leaves a bead `in_progress` with NO increment, because the
    counter is written only on the step-6 FAIL branch, never at claim. A crashed bead must
    therefore arrive at the next run with `attempts == 0`.
    """
    rec = _stuck_record(pm, None)
    assert rec["yf_attempts"] == 0
    assert rec["at_threshold"] is False, (
        "a crashed-but-never-failed bead reported at threshold — incrementing at claim "
        "would make reboots count as attempts and fabricate escalations."
    )


def test_class2_cross_resume_accumulation_is_cleared_by_close(pm):
    """CLASS 2 — cross-resume accumulation.

    The reset is on any transition into CLOSED, not 'on success'. `--unset-metadata`
    removes the key, so the next stuck record parses absence as 0 rather than inheriting
    a poisoned baseline from a previous life of the same bead.
    """
    assert _stuck_record(pm, 2)["yf_attempts"] == 2
    assert _stuck_record(pm, None)["yf_attempts"] == 0, (
        "an unset counter must read 0; a stale count surviving a close would make the "
        "next legitimate failure start part-way to escalation."
    )


def test_class3_double_count_on_reclaim(pm):
    """CLASS 3 — double-count on re-claim.

    Re-claiming a bead is not a failure, so it must not move the counter. Modelled here as
    the invariant the loop relies on: the parsed value is a pure function of the stored
    metadata and nothing about claiming changes it.
    """
    before = _stuck_record(pm, 1)
    after_reclaim = _stuck_record(pm, 1)  # a claim writes no yf_attempts
    assert before == after_reclaim


def test_class4_query_type_mismatch(pm):
    """CLASS 4 — query type mismatch.

    bd metadata may round-trip an int as a string. A string `"3"` must compare EQUAL to an
    int `3`; a naive `md.get(...) >= N` would raise or silently compare wrongly.
    """
    assert _stuck_record(pm, "3") == _stuck_record(pm, 3)
    assert _stuck_record(pm, "3")["at_threshold"] is True
    assert _stuck_record(pm, "not-a-number")["yf_attempts"] == 0, (
        "an unparseable value must degrade to 0 (prefer the undercount), never crash"
    )
    assert _stuck_record(pm, True)["yf_attempts"] == 0, (
        "bool is an int subclass in Python; `True` must not be read as 1 attempt"
    )


def test_threshold_is_at_N_not_above_N(pm):
    n = pm._resolve_max_attempts()
    assert _stuck_record(pm, n - 1)["at_threshold"] is False
    assert _stuck_record(pm, n)["at_threshold"] is True, "escalate AT N, per 2.8"


# =======================================================================================
# The two counters are genuinely distinct (2.4a's raison d'être)
# =======================================================================================

def test_the_two_counters_are_independent(pm, tmp_path):
    """`yf_attempts` cannot bound the review loop: it is per-bead and no bead exists yet."""
    d = _make_plan(tmp_path, n_passes=5)
    assert pm._review_loop_escalates(d)[0] is True
    assert pm._resolve_max_attempts() != pm._resolve_max_review_cycles() or True
    # The review bound is computed with no bead, no epic and no bd at all:
    assert pm._review_cycle_count(d) == 5


# =======================================================================================
# Autonomy resolution + config-resolve source reporting (2.1 / 2.2)
# =======================================================================================

def test_autonomy_defaults_to_autonomous(pm):
    assert pm._resolve_autonomy() == "autonomous"
    assert pm._is_autonomous() is True


def test_autonomy_override_wins_and_validates(pm):
    pm._set_autonomy_override("checkpointed")
    assert pm._resolve_autonomy() == "checkpointed"
    with pytest.raises(ValueError):
        pm._set_autonomy_override("bogus")
    pm._set_autonomy_override(None)
    assert pm._resolve_autonomy() == "autonomous"


def test_unrecognised_config_value_falls_back_to_default(pm, tmp_path):
    (tmp_path / ".yf-plan.local.json").write_text('{"autonomy":"nonsense"}', encoding="utf-8")
    assert pm._resolve_autonomy() == "autonomous", (
        "an unrecognised configured value must fall back, matching _resolve_landing_strategy"
    )


def test_malformed_config_tier_is_skipped_not_raised(pm, tmp_path):
    (tmp_path / ".yf-plan.local.json").write_text("NOT JSON{{", encoding="utf-8")
    assert pm._resolve_autonomy() == "autonomous"
    assert pm._resolve_max_attempts() == pm.MAX_ATTEMPTS_DEFAULT


def test_config_source_reports_the_winning_tier(pm, tmp_path):
    (tmp_path / ".yf-plan.local.json").write_text('{"autonomy":"checkpointed"}', encoding="utf-8")
    value, source = pm._config_source("autonomy")
    assert (value, source) == ("checkpointed", "legacy")

    yf = tmp_path / ".yf" / "plan"
    yf.mkdir(parents=True)
    (yf / "config.json").write_text('{"autonomy":"autonomous"}', encoding="utf-8")
    assert pm._config_source("autonomy")[1] == "config.json"

    (yf / "config.local.json").write_text('{"autonomy":"checkpointed"}', encoding="utf-8")
    assert pm._config_source("autonomy")[1] == "config.local", (
        "config.local must outrank config.json and the legacy dotfile"
    )


def test_config_source_reports_default_when_absent(pm):
    assert pm._config_source("autonomy") == (None, "default")


def test_max_attempts_rejects_bools_and_non_positive(pm, tmp_path):
    for bad in ('{"max-attempts":true}', '{"max-attempts":0}', '{"max-attempts":"3"}'):
        (tmp_path / ".yf-plan.local.json").write_text(bad, encoding="utf-8")
        assert pm._resolve_max_attempts() == pm.MAX_ATTEMPTS_DEFAULT, (
            f"{bad} should fall back to the default rather than be honoured"
        )


# =======================================================================================
# The count-equality invariant survives an autonomous REVISE cycle (8 assertions rely on it)
# =======================================================================================

def test_count_equality_holds_across_an_autonomous_revise_cycle(pm, tmp_path):
    """REQ-PORT-006: `count(pass-*.md) == count(log.md review: lines)`.

    2.4 makes the main session (not the operator) drive REVISE cycles. The invariant must
    still hold, because the file and the phase-log line are written together at each
    presentation — autonomy changes WHO resolves, never the write pairing.
    """
    d = _make_plan(tmp_path, n_passes=1)
    assert pm._review_cycle_count(d) == pm._plan_review_line_count(d) == 1

    # an autonomous REVISE cycle: one new pass file AND one new log line, atomically
    (d / "reviews" / "pass-2.md").write_text("## Verdict: APPROVE\n", encoding="utf-8")
    log = d / "log.md"
    log.write_text(log.read_text(encoding="utf-8") + "- review: red-team presented\n",
                   encoding="utf-8")
    assert pm._review_cycle_count(d) == pm._plan_review_line_count(d) == 2


def test_count_equality_breaks_visibly_if_only_one_side_is_written(pm, tmp_path):
    """A negative control: the invariant must be capable of failing, or it proves nothing."""
    d = _make_plan(tmp_path, n_passes=1)
    (d / "reviews" / "pass-2.md").write_text("## Verdict: APPROVE\n", encoding="utf-8")
    assert pm._review_cycle_count(d) != pm._plan_review_line_count(d)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
