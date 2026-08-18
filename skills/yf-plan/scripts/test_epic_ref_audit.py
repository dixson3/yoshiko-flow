# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
#     "pyyaml>=6",
# ]
# ///
"""Tier-1 unit tests for audit check #9 — the `**Epic:**` ref resolves.

REQ-CLI-020 / plan-044 #143. Run from anywhere:

    uv run skills/yf-plan/scripts/test_epic_ref_audit.py

`bd` is NEVER shelled out to — `_all_plan_beads` is monkeypatched. No subprocess, no
network, in any test.

Covers all THREE states the requirement distinguishes:

  (fail) a dangling ref on a NON-grandfathered plan. This is the defect: a
         dangling-but-PRESENT field makes `resume-scan` report
         `found: true, total: 0`, so a resumed execute session reads "no open
         work" and skips the plan entirely — a silent false success.
  (warn) `bd` unavailable. A plan bundle is portable by contract; hard-failing its
         own audit merely for being read on a beads-less machine would punish the
         portability it is designed for.
  (pass) a ref that resolves.

Plus the severity choice that makes the check useful at all: it keys on
`missing_level`, NOT `okf_missing_level`. The latter downgrades every legacy bundle
to `warn` — which would have silently suppressed all 14 real dangling refs.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pm = _load("plan_manager", "plan_manager.py")

PLAN_ID = "plan-999-tester-abc123"
# After the portability activation date, so the plan is NOT grandfathered and
# `missing_level` is `fail` — the configuration under which check #9 must bite.
RECENT = "2026-08-01"


def _write_plan(tmp_path: Path, epic: str | None, scoped: str = RECENT) -> Path:
    pdir = tmp_path / PLAN_ID
    pdir.mkdir()
    epic_line = f"**Epic:** {epic}\n" if epic else ""
    (pdir / "plan.md").write_text(
        f"---\ntype: Plan\nid: {PLAN_ID}\n---\n"
        f"# Plan: tester\n\n**ID:** {PLAN_ID}\n**Status:** executing\n{epic_line}"
        f"**Phase log:**\n- {scoped} scoping: initial scope captured\n\n"
        "## Objective\n\ntest\n\n"
        "## Motivation\n\nbecause\n\n"
        "## Success Criteria\n\n1. x\n",
        encoding="utf-8",
    )
    return pdir


def _findings(pdir: Path, item: str):
    res = pm._audit_plan(pdir)
    return [f for f in res["findings"] if f["item"] == item]


def test_dangling_ref_is_a_hard_fail(tmp_path, monkeypatch):
    """The 14-bundle defect. A present-but-unresolvable ref must FAIL loudly."""
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-real": {"id": "yf-real"}})
    pdir = _write_plan(tmp_path, "beads-skills-mol-s3x")
    hits = _findings(pdir, "epic-ref")
    assert len(hits) == 1, "a dangling ref must produce exactly one finding"
    assert hits[0]["status"] == "fail"
    assert "does not resolve" in hits[0]["detail"]


def test_bd_unavailable_is_warn_not_fail(tmp_path, monkeypatch):
    """A portable bundle on a beads-less machine must not hard-fail its own audit."""
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {})
    pdir = _write_plan(tmp_path, "yf-anything")
    hits = _findings(pdir, "epic-ref")
    assert len(hits) == 1
    assert hits[0]["status"] == "warn", "bd absence is not the plan's fault"
    assert "unavailable" in hits[0]["detail"]


def test_resolving_ref_produces_no_finding(tmp_path, monkeypatch):
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-9c09122b": {"id": "yf-9c09122b"}})
    pdir = _write_plan(tmp_path, "yf-9c09122b")
    assert _findings(pdir, "epic-ref") == []


def test_absent_epic_field_is_not_this_checks_business(tmp_path, monkeypatch):
    """No `**Epic:**` at all is a different condition — check #9 stays silent."""
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-real": {"id": "yf-real"}})
    pdir = _write_plan(tmp_path, None)
    assert _findings(pdir, "epic-ref") == []


def test_severity_is_missing_level_not_okf_missing_level(tmp_path, monkeypatch):
    """The choice that makes the check useful.

    All 14 real dangling refs live in OKF-LEGACY bundles (no plan.md frontmatter).
    Keying severity on `okf_missing_level` would downgrade every one of them to
    `warn` and suppress exactly what the check exists to surface. This asserts a
    legacy bundle still FAILS, provided it is not date-grandfathered.
    """
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-real": {"id": "yf-real"}})
    pdir = tmp_path / PLAN_ID
    pdir.mkdir()
    # NO frontmatter -> okf_legacy, so okf_missing_level would be "warn".
    (pdir / "plan.md").write_text(
        f"# Plan: tester\n\n**ID:** {PLAN_ID}\n**Status:** executing\n"
        f"**Epic:** beads-skills-mol-nxk\n**Phase log:**\n"
        f"- {RECENT} scoping: initial scope captured\n\n"
        "## Objective\n\ntest\n\n## Motivation\n\nbecause\n\n"
        "## Success Criteria\n\n1. x\n",
        encoding="utf-8",
    )
    res = pm._audit_plan(pdir)
    hits = [f for f in res["findings"] if f["item"] == "epic-ref"]
    assert len(hits) == 1
    assert hits[0]["status"] == "fail", (
        "a legacy bundle's dangling ref must still FAIL — using okf_missing_level "
        "here would have hidden all 14"
    )


# ---------------------------------------------------------------------------
# resume-scan's `epic_resolves` (REQ-CLI-013, plan-044 Issue 3.9)
# ---------------------------------------------------------------------------

def test_resume_scan_reports_epic_resolves_false_on_a_dangling_ref(tmp_path, monkeypatch):
    """The signal the EXECUTE path needs.

    `found` reports only that an id was RECORDED, so a dangling ref yields
    `found: true` with zero descendants — indistinguishable from a legitimately
    completed plan. `resume-scan` is the only verb the execute path consults, so
    without this the session reads "no open work" and skips the plan silently.
    """
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-real": {"id": "yf-real"}})
    pdir = _write_plan(tmp_path, "beads-skills-mol-GONE")
    res = pm._resume_scan(pdir)
    assert res["found"] is True, "the misleading signal is unchanged (a ref IS recorded)"
    assert res["epic_resolves"] is False, "the new signal must discriminate"
    assert res.get("total", 0) == 0


def test_resume_scan_epic_resolves_true_when_the_bead_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-ok": {"id": "yf-ok"}})
    pdir = _write_plan(tmp_path, "yf-ok")
    assert pm._resume_scan(pdir)["epic_resolves"] is True


def test_resume_scan_epic_resolves_is_none_when_unknowable(tmp_path, monkeypatch):
    """None, not False — `bd` unreadable must not libel a healthy plan.

    "No beads at all" cannot distinguish an absent database from an empty one.
    """
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {})
    pdir = _write_plan(tmp_path, "yf-whatever")
    assert pm._resume_scan(pdir)["epic_resolves"] is None
    # And with no `**Epic:**` field at all there is nothing to resolve.
    (tmp_path / "b").mkdir()
    pdir2 = _write_plan(tmp_path / "b", None)
    monkeypatch.setattr(pm, "_all_plan_beads", lambda: {"yf-real": {"id": "yf-real"}})
    assert pm._resume_scan(pdir2)["epic_resolves"] is None


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
