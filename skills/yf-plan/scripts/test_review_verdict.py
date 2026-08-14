# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
#     "pyyaml>=6",
# ]
# ///
"""Tier-1 unit tests for the review verdict-line contract (plan-037, #116).

Run from anywhere:  uv run skills/yf-plan/scripts/test_review_verdict.py

Covers:
  (a) REQ-PLAN-071 — the parser accepts the canonical `## Verdict:` and, as defence
      in depth, a level-3 `### Verdict:`; it rejects `#` and `####`, and is
      case-insensitive. Also asserts the red-team TEMPLATE emits the canonical form,
      which is the half of the fix that keeps `###` a tolerance rather than a second
      idiom;
  (b) REQ-PLAN-072 — `ready-check` distinguishes an absent review from a malformed
      one, names the offending file, and never reports the
      `review_pass > 0 && verdict == null` contradiction as a bare absent verdict;
  (c) last-recorded-verdict selection (REQ-PLAN-030) still keys on the highest
      `pass-N.md`, including across the relaxed heading forms.

`bd` is never shelled out to. Plan bundles are built on disk in a tmp dir; the
portability audit is stubbed where the test is about the verdict, not the audit.
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
# Fixtures / helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def plan_dir(tmp_path):
    """A minimal plan bundle with an empty `reviews/` dir."""
    pd = tmp_path / "docs" / "plans" / PLAN_ID
    (pd / "reviews").mkdir(parents=True)
    (pd / "plan.md").write_text(
        f"# Plan: test\n\n**ID:** {PLAN_ID}\n**Status:** review\n\n"
        "## Objective\nA plan.\n\n## Success Criteria\nDone.\n"
    )
    return pd


def _review(pd: Path, n: int, body: str) -> Path:
    f = pd / "reviews" / f"pass-{n}.md"
    f.write_text(f"# Red-Team Review — pass-{n}\n\n{body}\n")
    return f


@pytest.fixture
def audit_passes(monkeypatch):
    """Stub the portability audit green so a test isolates the verdict axis."""
    monkeypatch.setattr(pm, "_audit_plan", lambda _pd: {"status": "pass", "findings": []})


def _ready_check(pd: Path) -> tuple[dict, int]:
    res = CliRunner().invoke(pm.cli, ["ready-check", str(pd), "--json"])
    assert res.output.strip(), f"no output; exception={res.exception!r}"
    return json.loads(res.output), res.exit_code


# ---------------------------------------------------------------------------
# (a) REQ-PLAN-071 — accepted and rejected verdict heading forms
# ---------------------------------------------------------------------------

def test_canonical_h2_verdict_parses(plan_dir):
    _review(plan_dir, 1, "## Verdict: APPROVE")
    n, verdict, path = pm._latest_review_verdict(plan_dir)
    assert (n, verdict) == (1, "APPROVE")
    assert path is not None and path.name == "pass-1.md"


def test_h3_verdict_parses_as_defence_in_depth(plan_dir):
    """A `###` review is a tolerance, not the canonical form — but it must parse.

    This is the half of #116 that a template-only fix would leave broken: if the
    template ever drifts back to `###`, the failure must not be a silent null.
    """
    _review(plan_dir, 1, "### Verdict: REVISE")
    n, verdict, path = pm._latest_review_verdict(plan_dir)
    assert (n, verdict) == (1, "REVISE")
    assert path is not None


def test_verdict_is_case_insensitive(plan_dir):
    _review(plan_dir, 1, "## verdict: approve")
    _, verdict, _ = pm._latest_review_verdict(plan_dir)
    assert verdict == "APPROVE"


def test_hyphenated_verdict_parses(plan_dir):
    _review(plan_dir, 1, "## Verdict: INVESTIGATE-MORE")
    _, verdict, _ = pm._latest_review_verdict(plan_dir)
    assert verdict == "INVESTIGATE-MORE"


@pytest.mark.parametrize("line", [
    "# Verdict: APPROVE",       # h1 — too shallow
    "#### Verdict: APPROVE",    # h4 — too deep
    "**Verdict:** APPROVE",     # bold, not a heading (the pre-#116 legacy corpus form)
    "## Verdict",               # heading present, value absent
    "Verdict: APPROVE",         # no heading at all
])
def test_non_conformant_verdict_forms_do_not_parse(plan_dir, line):
    f = _review(plan_dir, 1, line)
    n, verdict, path = pm._latest_review_verdict(plan_dir)
    # Malformed, NOT absent: N and the path are still reported so the caller can
    # name the file (REQ-PLAN-072).
    assert verdict is None
    assert n == 1
    assert path == f


def test_red_team_template_emits_the_canonical_form():
    """The template half of the fix (REQ-PLAN-071).

    Guards the exact regression #116 was: a template emitting a form its own parser
    rejects. Asserted against the shipped agent file, not a copy.
    """
    tmpl = (_HERE.parent / "agents" / "red-team.md").read_text(encoding="utf-8")
    lines = tmpl.splitlines()
    assert any(l.strip() == "## Verdict: APPROVE | REVISE | INVESTIGATE-MORE" for l in lines)
    # No EMITTED `###` verdict heading. Checked at line-start so the file may still
    # discuss the non-conformant form in prose (it does, deliberately).
    assert not any(l.startswith("### Verdict:") for l in lines)


# ---------------------------------------------------------------------------
# (b) REQ-PLAN-072 — malformed vs absent
# ---------------------------------------------------------------------------

def test_absent_review_reports_no_verdict_found(plan_dir, audit_passes):
    out, code = _ready_check(plan_dir)
    assert code == 3
    assert out["ready"] is False
    assert out["verdict"] is None
    assert out["review_pass"] is None
    assert out["malformed_review"] is None
    assert any("no red-team verdict found" in r for r in out["reasons"])


def test_malformed_review_fails_loud_and_names_the_file(plan_dir, audit_passes):
    f = _review(plan_dir, 2, "**Verdict:** APPROVE")
    out, code = _ready_check(plan_dir)
    assert code == 3
    assert out["ready"] is False
    assert out["malformed_review"] == str(f)
    joined = " ".join(out["reasons"])
    assert "malformed review" in joined
    assert "pass-2.md" in joined
    # It must NOT be reported as a merely-absent verdict.
    assert "no red-team verdict found" not in joined


def test_review_pass_and_null_verdict_contradiction_is_never_silent(plan_dir, audit_passes):
    """The exact observed symptom: review_pass: N alongside verdict: null.

    That pairing is a contradiction — a review exists. It must always come with a
    malformed_review path and a naming reason, never a bare null.
    """
    _review(plan_dir, 3, "no verdict line here at all")
    out, _ = _ready_check(plan_dir)
    assert out["review_pass"] == 3 and out["verdict"] is None
    assert out["malformed_review"] is not None
    assert any("malformed review" in r for r in out["reasons"])


def test_wellformed_approve_is_ready(plan_dir, audit_passes):
    _review(plan_dir, 1, "## Verdict: APPROVE")
    out, code = _ready_check(plan_dir)
    assert code == 0
    assert out["ready"] is True
    assert out["verdict"] == "APPROVE"
    assert out["malformed_review"] is None


def test_revise_blocks_without_being_called_malformed(plan_dir, audit_passes):
    _review(plan_dir, 1, "## Verdict: REVISE")
    out, code = _ready_check(plan_dir)
    assert code == 3
    assert out["malformed_review"] is None
    assert any("last red-team verdict is REVISE" in r for r in out["reasons"])


# ---------------------------------------------------------------------------
# (c) last-recorded-verdict selection (REQ-PLAN-030) across the relaxed forms
# ---------------------------------------------------------------------------

def test_highest_pass_wins_even_when_earlier_pass_approved(plan_dir, audit_passes):
    _review(plan_dir, 1, "## Verdict: APPROVE")
    _review(plan_dir, 2, "## Verdict: REVISE")
    out, code = _ready_check(plan_dir)
    assert code == 3
    assert out["review_pass"] == 2 and out["verdict"] == "REVISE"


def test_highest_pass_wins_when_it_is_the_h3_form(plan_dir):
    _review(plan_dir, 1, "## Verdict: REVISE")
    _review(plan_dir, 2, "### Verdict: APPROVE")
    n, verdict, _ = pm._latest_review_verdict(plan_dir)
    assert (n, verdict) == (2, "APPROVE")


def test_malformed_latest_masks_an_earlier_good_verdict(plan_dir, audit_passes):
    """Readiness keys on the LAST cycle; a malformed latest must not silently
    fall back to an earlier APPROVE."""
    _review(plan_dir, 1, "## Verdict: APPROVE")
    _review(plan_dir, 2, "**Verdict:** APPROVE")
    out, code = _ready_check(plan_dir)
    assert code == 3
    assert out["review_pass"] == 2
    assert out["verdict"] is None
    assert out["malformed_review"] is not None


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
