# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
#     "pyyaml>=6",
# ]
# ///
"""Tier-1 unit tests for `verify-reconcile` (REQ-PLAN-074 / REQ-CLI-018, plan-043 #136).

Run from anywhere:  uv run skills/yf-plan/scripts/test_verify_reconcile.py

`gh` is NEVER shelled out to — `_gh_issue_view` is monkeypatched. No network, in any test.

Covers (tagged REQ-PLAN-074):
  (a) each disposition's pass AND fail case (include / supersede / partial);
  (b) THE historical scenario — state is correct but NO plan-id mention — FAILING.
      This is the case that makes the check worth having: asserting state alone would
      pass it, because the issue was closed by a human 15 h later as manual repair;
  (c) `exclude` rows skipped entirely;
  (d) a `gh` error yielding `inconclusive`, NOT `fail`, at exit 0 (R1);
  (e) the MIXED case — one row `fail`, one row `inconclusive` -> aggregate `fail` (C9);
  (f) row-shape variants (`[#N](url)` vs `#N` vs `owner/repo#N`) pinning the SHARED
      parser, so `verify-reconcile` and the reconciler cannot disagree (R9);
  (g) envelope conformance on every path (REQ-COMPLETE-003).
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

PLAN_ID = "plan-999-tester-abc123"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _write_plan(tmp_path: Path, rows: str) -> Path:
    pdir = tmp_path / PLAN_ID
    pdir.mkdir()
    (pdir / "plan.md").write_text(
        f"---\ntype: Plan\nid: {PLAN_ID}\n---\n"
        f"# Plan: tester\n\n**ID:** {PLAN_ID}\n\n"
        "## Objective\n\ntest\n\n"
        "## Upstream Issues\n\n"
        "| Issue | Title | Disposition | Notes | Resolved By |\n"
        "| :-- | :-- | :-- | :-- | :-- |\n"
        f"{rows}\n"
        "## Success Criteria\n\n1. x\n",
        encoding="utf-8",
    )
    return pdir


def _gh(state="CLOSED", reason="COMPLETED", comments=None):
    return {"state": state, "stateReason": reason,
            "comments": [{"body": b} for b in (comments or [])], "title": "t"}


def _run(pdir: Path) -> tuple[int, dict]:
    res = CliRunner().invoke(pm.cli, ["verify-reconcile", str(pdir), "--json"])
    assert res.output.strip(), "envelope must be on stdout on EVERY path"
    return res.exit_code, json.loads(res.output)


def _assert_envelope(payload: dict):
    """REQ-COMPLETE-003 shape checks applied to every result in this file."""
    assert payload["verdict"] in ("pass", "fail", "inconclusive")
    assert payload["passed"] == (payload["verdict"] == "pass"), \
        "`passed` is a DERIVED key and must agree with `verdict`"
    assert payload["reason"]
    if payload["verdict"] != "pass":
        assert payload["remediation"], "a non-pass verdict must carry remediation"


# ---------------------------------------------------------------------------
# (a) per-disposition pass and fail
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("disposition,gh_payload", [
    ("include", _gh("CLOSED", "COMPLETED", [f"Resolved by {PLAN_ID}"])),
    ("supersede", _gh("CLOSED", "NOT_PLANNED", [])),
    ("partial", _gh("OPEN", None, [f"{PLAN_ID} landed the audit half"])),
])
def test_disposition_pass(tmp_path, monkeypatch, disposition, gh_payload):
    pdir = _write_plan(tmp_path, f"| #42 | t | {disposition} | n | Issue 1.1 |")
    monkeypatch.setattr(pm, "_gh_issue_view", lambda n: (gh_payload, None))
    rc, out = _run(pdir)
    _assert_envelope(out)
    assert out["verdict"] == "pass", out["rows"]
    assert rc == 0


@pytest.mark.parametrize("disposition,gh_payload,why", [
    ("include", _gh("OPEN", None, [f"{PLAN_ID}"]), "include row left OPEN"),
    ("supersede", _gh("CLOSED", "COMPLETED", []), "supersede closed as COMPLETED not NOT_PLANNED"),
    ("partial", _gh("CLOSED", "COMPLETED", [f"{PLAN_ID}"]), "partial row wrongly CLOSED"),
])
def test_disposition_fail(tmp_path, monkeypatch, disposition, gh_payload, why):
    pdir = _write_plan(tmp_path, f"| #42 | t | {disposition} | n | Issue 1.1 |")
    monkeypatch.setattr(pm, "_gh_issue_view", lambda n: (gh_payload, None))
    rc, out = _run(pdir)
    _assert_envelope(out)
    assert out["verdict"] == "fail", f"{why} must fail: {out['rows']}"
    assert rc != 0, "a halting step's `fail` must exit non-zero"


# ---------------------------------------------------------------------------
# (b) THE historical scenario — correct state, NO plan-id mention
# ---------------------------------------------------------------------------

def test_state_correct_but_no_mention_fails(tmp_path, monkeypatch):
    """The case that justifies the whole check (plan-043 D6 / SC3).

    All three `include` issues are CLOSED — closed by a human, long after the plan
    reported complete. A state-only assertion PASSES this. It must fail.
    """
    rows = "\n".join(f"| #{n} | t | include | n | Issue 1.1 |" for n in (108, 112, 114))
    pdir = _write_plan(tmp_path, rows)
    # CLOSED, but every comment is from an unrelated human repair.
    monkeypatch.setattr(
        pm, "_gh_issue_view",
        lambda n: (_gh("CLOSED", "COMPLETED", ["closing, this looks done"]), None),
    )
    rc, out = _run(pdir)
    _assert_envelope(out)
    assert out["verdict"] == "fail"
    assert rc != 0
    assert len(out["rows"]) == 3
    assert all(r["verdict"] == "fail" for r in out["rows"])
    assert all("no comment mentions" in r["detail"] for r in out["rows"])


def test_include_open_variant_of_the_scenario(tmp_path, monkeypatch):
    """The as-it-actually-was variant: the three issues are still OPEN."""
    rows = "\n".join(f"| #{n} | t | include | n | Issue 1.1 |" for n in (108, 112, 114))
    pdir = _write_plan(tmp_path, rows)
    monkeypatch.setattr(pm, "_gh_issue_view", lambda n: (_gh("OPEN", None, []), None))
    rc, out = _run(pdir)
    assert out["verdict"] == "fail" and rc != 0
    assert all("must be CLOSED" in r["detail"] for r in out["rows"])


# ---------------------------------------------------------------------------
# (c) exclude rows skipped
# ---------------------------------------------------------------------------

def test_exclude_rows_are_skipped(tmp_path, monkeypatch):
    pdir = _write_plan(
        tmp_path,
        "| #41 | t | exclude | not ours | — |\n| #42 | t | include | n | Issue 1.1 |",
    )
    seen: list[str] = []

    def fake(n):
        seen.append(n)
        return _gh("CLOSED", "COMPLETED", [PLAN_ID]), None

    monkeypatch.setattr(pm, "_gh_issue_view", fake)
    rc, out = _run(pdir)
    assert seen == ["42"], f"an `exclude` row must never be queried; queried {seen}"
    assert out["verdict"] == "pass" and rc == 0


def test_no_rows_at_all_is_a_clean_pass(tmp_path, monkeypatch):
    pdir = _write_plan(tmp_path, "| #41 | t | exclude | not ours | — |")
    monkeypatch.setattr(pm, "_gh_issue_view",
                        lambda n: pytest.fail("should not be called"))
    rc, out = _run(pdir)
    assert out["verdict"] == "pass" and rc == 0 and out["rows"] == []


# ---------------------------------------------------------------------------
# (d) a checker error is INCONCLUSIVE, not FAIL — and does NOT halt (R1)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("err", [
    "`gh` not found on PATH",
    "`gh` timed out after 30s",
    "HTTP 403: API rate limit exceeded",
])
def test_gh_error_is_inconclusive_and_does_not_halt(tmp_path, monkeypatch, err):
    pdir = _write_plan(tmp_path, "| #42 | t | include | n | Issue 1.1 |")
    monkeypatch.setattr(pm, "_gh_issue_view", lambda n: (None, err))
    rc, out = _run(pdir)
    _assert_envelope(out)
    assert out["verdict"] == "inconclusive", "a checker failure is NEVER `fail`"
    assert rc == 0, "SC4: `gh` unavailability must not halt completion"
    assert out["rows"][0]["verdict"] == "inconclusive"


# ---------------------------------------------------------------------------
# (e) MIXED — one row fail + one row inconclusive -> aggregate FAIL (C9)
# ---------------------------------------------------------------------------

def test_mixed_fail_and_inconclusive_aggregates_to_fail(tmp_path, monkeypatch):
    """The stated aggregate rule. A collapsed verdict would either halt on an outage
    or mask a real regression; this pins that it does neither."""
    pdir = _write_plan(
        tmp_path,
        "| #42 | t | include | n | Issue 1.1 |\n| #43 | t | include | n | Issue 1.2 |",
    )

    def fake(n):
        if n == "42":
            return _gh("OPEN", None, []), None          # definitely wrong
        return None, "HTTP 502: bad gateway"            # unknown

    monkeypatch.setattr(pm, "_gh_issue_view", fake)
    rc, out = _run(pdir)
    _assert_envelope(out)
    assert out["verdict"] == "fail", "any row `fail` wins over `inconclusive`"
    assert rc != 0
    verdicts = {r["issue"]: r["verdict"] for r in out["rows"]}
    assert verdicts == {"42": "fail", "43": "inconclusive"}


def test_inconclusive_only_does_not_halt(tmp_path, monkeypatch):
    pdir = _write_plan(
        tmp_path,
        "| #42 | t | include | n | Issue 1.1 |\n| #43 | t | partial | n | Issue 2.1 |",
    )
    monkeypatch.setattr(pm, "_gh_issue_view", lambda n: (None, "offline"))
    rc, out = _run(pdir)
    assert out["verdict"] == "inconclusive" and rc == 0


# ---------------------------------------------------------------------------
# (f) row-shape variants pin the SHARED parser (R9)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cell", [
    "#42",
    "[#42](https://github.com/o/r/issues/42)",
    "o/r#42",
    "**[#42](https://github.com/o/r/issues/42)**",
])
def test_row_shape_variants(tmp_path, monkeypatch, cell):
    pdir = _write_plan(tmp_path, f"| {cell} | t | include | n | Issue 1.1 |")
    monkeypatch.setattr(pm, "_gh_issue_view",
                        lambda n: (_gh("CLOSED", "COMPLETED", [PLAN_ID]), None))
    rc, out = _run(pdir)
    assert [r["issue"] for r in out["rows"]] == ["42"], f"row shape {cell!r} not parsed"
    assert out["verdict"] == "pass"


def test_one_parser_only(tmp_path):
    """`_plan_non_exclude_upstream_numbers` must be a VIEW over the shared parser.

    Two parsers of one table can disagree, and this step is fail-loud, so the
    disagreement surfaces as a false positive that halts healthy work (R9).
    """
    text = (
        "## Upstream Issues\n\n"
        "| Issue | Title | Disposition | Notes | Resolved By |\n"
        "| :-- | :-- | :-- | :-- | :-- |\n"
        "| [#10](https://github.com/o/r/issues/10) | a | include | n | 1.1 |\n"
        "| #11 | b | exclude | n | — |\n"
        "| o/r#12 | c | partial | n | 2.1 |\n\n"
        "## Next\n"
    )
    rows = pm.parse_upstream_rows(text)
    assert [r["issue"] for r in rows] == ["10", "11", "12"]
    assert pm._plan_non_exclude_upstream_numbers(text) == ["10", "12"]
    non_exclude = [r["issue"] for r in rows if r["disposition"] != "exclude"]
    assert non_exclude == pm._plan_non_exclude_upstream_numbers(text), \
        "the view disagrees with the parser it is supposed to be a view over"


def test_table_ends_at_next_section(tmp_path):
    """A `#N` after the table must not be swept in."""
    text = (
        "## Upstream Issues\n\n"
        "| Issue | Title | Disposition | Notes | Resolved By |\n"
        "| :-- | :-- | :-- | :-- | :-- |\n"
        "| #10 | a | include | n | 1.1 |\n\n"
        "## Scope\n\n| #99 | not | include | a | table-in-upstream |\n"
    )
    assert [r["issue"] for r in pm.parse_upstream_rows(text)] == ["10"]


# ---------------------------------------------------------------------------
# (g) tracker rows carry no end-state contract
# ---------------------------------------------------------------------------

def test_tracker_row_is_inconclusive_not_fail(tmp_path, monkeypatch):
    """The coarse tracker is closed by the land-the-plane sweep, not by reconcile."""
    pdir = _write_plan(tmp_path, "| #148 | tracker | tracker | coarse | — |")
    monkeypatch.setattr(pm, "_gh_issue_view", lambda n: (_gh("OPEN", None, []), None))
    rc, out = _run(pdir)
    assert out["rows"][0]["verdict"] == "inconclusive"
    assert rc == 0, "an open coarse tracker must never halt completion"


def test_missing_plan_md_is_fail_on_stdout(tmp_path):
    empty = tmp_path / "nope"
    empty.mkdir()
    rc, out = _run(empty)
    _assert_envelope(out)
    assert out["verdict"] == "fail" and rc != 0


# ---------------------------------------------------------------------------
# normalized matching, but never a time window (R2 / C10)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("body,expected", [
    (f"Resolved by {PLAN_ID}", True),
    (f"resolved by {PLAN_ID.upper()}", True),
    (f"see `{PLAN_ID}`.", True),
    ("resolved by plan-998-other-xyz999", False),
    ("2.2/REQ-AGENT-046 shipped", False),   # E1's exact "shipped" tell
])
def test_normalized_mention_matching(body, expected):
    assert pm._mentions_plan_id(_gh(comments=[body]), PLAN_ID) is expected


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
