# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
#     "pyyaml>=6",
# ]
# ///
"""Tier-1 unit tests for the REQ-PLAN-069 completion criterion (plan-030).

Run from anywhere:  uv run skills/yf-plan/scripts/test_complete_gate.py

Covers (tagged REQ-PLAN-069):
  (a) classify-deliverable signal detection + `standard` default + confidence levels;
  (b) complete-gate — ci-release halt with neither; pass with a `log.md` `- validated:`
      bullet; pass with an out-of-tree open `deferred-validation` bead; no-op for
      `standard`/absent;
  (c) C3 round-trip — write `deliverable_class`, call `update-status`, assert the marker
      survives the field-block rewrite;
  (d) C1 agreement — cascade-close (dry-run) + complete-gate agree that an out-of-tree
      open deferred bead does NOT appear as a plan-tree open child;
  (e) C4 — a `- validated:` bullet perturbs neither `_plan_review_line_count` nor the
      grandfather-date (`_plan_first_scoping_date`) parser.

`bd` is never shelled out to: `_bd_list` (pm) and `_bd_show`/`_node_children` (close_cascade)
are monkeypatched. Plan bundles are built on disk in a tmp dir.
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
cc = _load("close_cascade", "close_cascade.py")


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

PLAN_ID = "plan-999-tester-abc123"


@pytest.fixture
def plan_dir(tmp_path):
    """A minimal OKF-ish plan bundle at docs/plans/<plan-id>/ under tmp_path."""
    pd = tmp_path / "docs" / "plans" / PLAN_ID
    pd.mkdir(parents=True)
    (pd / "plan.md").write_text(
        f"# Plan: test\n\n**ID:** {PLAN_ID}\n**Status:** reconciling\n\n"
        "## Objective\nA plan.\n\n## Success Criteria\nDone.\n"
    )
    return pd


def _set_class(pd: Path, value: str) -> None:
    pm._write_plan_fields(pd, {"deliverable_class": value})


def _write_body(pd: Path, body: str) -> None:
    (pd / "plan.md").write_text(f"# Plan: test\n\n**ID:** {PLAN_ID}\n\n{body}\n")


# ---------------------------------------------------------------------------
# (a) classify-deliverable — signal detection, default, confidence
# ---------------------------------------------------------------------------

def test_classify_standard_default(plan_dir):
    _write_body(plan_dir, "## Objective\nRefactor the parser and tidy imports.\n")
    r = pm._classify_deliverable(plan_dir)
    assert r["suggested_class"] == "standard"
    assert r["signals"] == []


def test_classify_high_on_release_keyword(plan_dir):
    _write_body(plan_dir, "## Objective\nCut a release and notarize the artifact.\n")
    r = pm._classify_deliverable(plan_dir)
    assert r["suggested_class"] == "ci-release"
    assert r["confidence"] == "high"
    assert "release" in r["signals"] and "notarize" in r["signals"]


def test_classify_high_on_workflow_path(plan_dir):
    _write_body(plan_dir, "## Objective\nAdd a build job.\n")
    r = pm._classify_deliverable(plan_dir, changed=(".github/workflows/ci.yml",))
    assert r["suggested_class"] == "ci-release"
    assert r["confidence"] == "high"
    assert any(s.startswith("path:.github/workflows/") for s in r["signals"])


def test_classify_low_on_keyword_only(plan_dir):
    _write_body(plan_dir, "## Objective\nUpdate the deploy pipeline runner notes.\n")
    r = pm._classify_deliverable(plan_dir)
    assert r["suggested_class"] == "ci-release"
    assert r["confidence"] == "low"


def test_classify_no_false_positive_on_signal_word(plan_dir):
    # "signals" must not trip the `sign` high keyword (trailing-boundary regex).
    _write_body(plan_dir, "## Objective\nDetect ci-release signals in the plan text.\n")
    r = pm._classify_deliverable(plan_dir)
    assert "sign" not in r["signals"]


# ---------------------------------------------------------------------------
# (b) complete-gate — no-op / halt / pass paths
# ---------------------------------------------------------------------------

def _run_gate(pd: Path) -> tuple[int, dict]:
    res = CliRunner().invoke(pm.cli, ["complete-gate", str(pd), "--json"])
    # stdout carries the JSON verdict on both pass and fail (err=True still prints).
    payload = json.loads(res.output.strip().splitlines()[-1])
    return res.exit_code, payload


def test_gate_noop_for_standard(plan_dir, monkeypatch):
    monkeypatch.setattr(pm, "_bd_list", lambda *a: [])
    _set_class(plan_dir, "standard")
    rc, v = _run_gate(plan_dir)
    assert rc == 0 and v["passed"] is True and v["noop"] is True


def test_gate_noop_for_absent_class(plan_dir, monkeypatch):
    monkeypatch.setattr(pm, "_bd_list", lambda *a: [])
    rc, v = _run_gate(plan_dir)  # no class written at all
    assert rc == 0 and v["passed"] is True and v["noop"] is True
    assert v["deliverable_class"] == "standard"


def test_gate_halts_ci_release_with_neither(plan_dir, monkeypatch):
    monkeypatch.setattr(pm, "_bd_list", lambda *a: [])
    _set_class(plan_dir, "ci-release")
    rc, v = _run_gate(plan_dir)
    assert rc != 0 and v["passed"] is False
    assert "remediation" in v


def test_gate_passes_with_validated_bullet(plan_dir, monkeypatch):
    monkeypatch.setattr(pm, "_bd_list", lambda *a: [])
    _set_class(plan_dir, "ci-release")
    pm.okf.append_log(plan_dir, "validated: https://ci/run/1 — green build", date="2026-07-20")
    rc, v = _run_gate(plan_dir)
    assert rc == 0 and v["passed"] is True and v["evidence"] == "validated-bullet"


def test_gate_passes_with_out_of_tree_deferred_bead(plan_dir, monkeypatch):
    deferred = {"id": "bd-defer-1", "status": "open",
                "labels": ["deferred-validation"],
                "metadata": json.dumps({"plan": PLAN_ID})}
    monkeypatch.setattr(pm, "_bd_list", lambda *a: [deferred])
    _set_class(plan_dir, "ci-release")
    rc, v = _run_gate(plan_dir)
    assert rc == 0 and v["passed"] is True
    assert v["evidence"] == "deferred-bead" and v["deferred_bead"] == "bd-defer-1"


def test_gate_ignores_closed_or_other_plan_deferred_bead(plan_dir, monkeypatch):
    beads = [
        {"id": "closed", "status": "closed", "labels": ["deferred-validation"],
         "metadata": json.dumps({"plan": PLAN_ID})},
        {"id": "otherplan", "status": "open", "labels": ["deferred-validation"],
         "metadata": json.dumps({"plan": "plan-000-other"})},
    ]
    monkeypatch.setattr(pm, "_bd_list", lambda *a: beads)
    _set_class(plan_dir, "ci-release")
    rc, v = _run_gate(plan_dir)
    assert rc != 0 and v["passed"] is False  # neither bead counts


# ---------------------------------------------------------------------------
# (c) C3 round-trip — deliverable_class survives a field-block rewrite
# ---------------------------------------------------------------------------

def test_deliverable_class_survives_update_status(plan_dir):
    _set_class(plan_dir, "ci-release")
    assert pm._read_deliverable_class((plan_dir / "plan.md").read_text()) == "ci-release"
    # update-status rewrites the **Field:** block via _rebuild_field_block, which
    # re-emits ONLY registered fields — a registered field must survive.
    CliRunner().invoke(pm.cli, ["update-status", str(plan_dir), "complete", "-m", "done"])
    text = (plan_dir / "plan.md").read_text()
    assert pm._read_deliverable_class(text) == "ci-release"
    assert "**Deliverable-class:** ci-release" in text


def test_deliverable_class_ordered_after_status(plan_dir):
    _set_class(plan_dir, "ci-release")
    text = (plan_dir / "plan.md").read_text()
    assert text.index("**Status:**") < text.index("**Deliverable-class:**")


# ---------------------------------------------------------------------------
# (d) C1 agreement — out-of-tree deferred bead is not a plan-tree open child
# ---------------------------------------------------------------------------

def test_cascade_and_gate_agree_deferred_is_out_of_tree(plan_dir, monkeypatch):
    # Plan tree: epic → one closed child. The deferred bead is standalone (not in tree).
    tree = {
        "epic-1": {"id": "epic-1", "issue_type": "epic", "status": "open", "parent": None},
        "task-1": {"id": "task-1", "issue_type": "task", "status": "closed",
                   "parent": "epic-1"},
    }
    children = {"epic-1": [tree["task-1"]], "task-1": []}
    monkeypatch.setattr(cc, "_bd_show", lambda i: tree.get(i))
    monkeypatch.setattr(cc, "_node_children", lambda i: children.get(i, []))

    # cascade dry-run: the tree walk never sees the deferred bead → no blocked children.
    result = cc.cascade("epic-1", reason="test", dry_run=True)
    assert result["blocked"] == []
    assert "epic-1" in result["closed"]

    # complete-gate: the deferred bead IS visible by label filter → gate passes.
    deferred = {"id": "bd-defer-x", "status": "open", "labels": ["deferred-validation"],
                "metadata": json.dumps({"plan": PLAN_ID})}
    monkeypatch.setattr(pm, "_bd_list", lambda *a: [deferred])
    _set_class(plan_dir, "ci-release")
    rc, v = _run_gate(plan_dir)
    assert rc == 0 and v["evidence"] == "deferred-bead"


# ---------------------------------------------------------------------------
# (e) C4 — `validated:` is inert to review-count and grandfather-date parsers
# ---------------------------------------------------------------------------

def test_validated_bullet_is_non_status_token(plan_dir):
    # Build a log.md with scoping + review + validated entries.
    pm.okf.append_log(plan_dir, "scoping: initial", date="2026-07-01")
    pm.okf.append_log(plan_dir, "review: pass-1 presented", date="2026-07-02")
    pm.okf.append_log(plan_dir, "review: pass-2 presented", date="2026-07-03")
    before_reviews = pm._plan_review_line_count(plan_dir)
    before_scoping = pm._plan_first_scoping_date(plan_dir)

    pm.okf.append_log(plan_dir, "validated: https://ci/run/9 — green", date="2026-07-04")

    assert pm._plan_review_line_count(plan_dir) == before_reviews == 2
    assert pm._plan_first_scoping_date(plan_dir) == before_scoping == "2026-07-01"
    assert pm._has_validated_bullet(plan_dir) is True


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-q"]))
